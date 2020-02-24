import datetime
import fcntl
import os
import re
import signal
import subprocess

from dataclasses import dataclass
from distutils.spawn import find_executable
from enum import Enum, unique
from logging import getLogger
from pathlib import Path
from select import select
from tempfile import TemporaryDirectory
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Optional,
                    Pattern, Sequence, Tuple)

import ffmpeg  # type: ignore

LOGGER = getLogger(__name__)

FFMPEG: Optional[str] = find_executable("ffmpeg")

#: Regex used to parse progress lines with multiple key=value pairs
PROGRESS_RE: Pattern = re.compile(r"(\w+)=\s*([^ ]+) ?")


def parse_timestamp(as_str: str) -> datetime.timedelta:
    """Parses a timestamp in HH:MM:SS format"""
    kwargs = dict(zip(
        ("hours", "minutes", "seconds"),
        map(int, as_str.split(".")[0].split(":"))
    ))
    return datetime.timedelta(days=0, **kwargs)


def parse_speed(as_str: str) -> float:
    """Parses a speed in N.NNx format"""
    return float(as_str.rstrip("x"))


def unbuffer_fd(fileno: int):
    """Makes the fd with the given number unbuffered"""
    fcntl.fcntl(fileno, fcntl.F_SETFL, fcntl.fcntl(fileno, fcntl.F_GETFL) | os.O_NONBLOCK)


class VideoError(Exception):
    """Raised when a video cannot be processed"""


@dataclass
class Progress:
    fps: float
    size: str
    time: datetime.timedelta
    bitrate: str
    speed: Optional[float] = None  # Not always available

    #: Which function to use to parse which field in from_raw_dict()
    _PARSERS: ClassVar[Dict[str, Callable[[str], Any]]] = {
        "fps": float,
        "time": parse_timestamp,
        "speed": parse_speed,
    }

    @classmethod
    def from_raw_dict(cls, data: Dict[str, str]):
        """Creates a new `Progress` instance from a raw unparsed dict."""
        print(data)
        return cls(**{field: cls._PARSERS.get(field, str)(data[field])
                      for field in cls.__dataclass_fields__  # type: ignore
                      if field in data})


@dataclass
class VideoMetadata:
    """Metadata parsed by analyzing the video with ffmpeg"""
    #: Video codec
    codec: str
    #: pixel format
    pixel_format: str
    #: Video duration
    duration: datetime.timedelta
    #: Resolution
    resolution: Optional[Tuple[int, int]]


@unique
class Format(Enum):
    """Available output formats"""
    MP4 = "libx264"


class FFmpegWrapper:
    #: Human readable representation of the available output formats
    FORMATS: ClassVar[Dict[str, str]] = {
        "mp4": "libx264",
    }

    def __init__(self, input_file: Path):
        assert input_file.exists()
        self.input_file = input_file
        self.metadata: VideoMetadata = self.fetch_video_metadata()
        self.returncode: Optional[int] = None
        self.ffmpeg: Optional[subprocess.Popen] = None

    @staticmethod
    def process_logs(lines: Sequence[str]) -> Optional[Progress]:
        """Parses log lines and try to find the most recent progress log"""
        for line in reversed(lines):
            raw_status = dict(PROGRESS_RE.findall(line))
            if raw_status:
                LOGGER.debug(raw_status)
                try:
                    return Progress.from_raw_dict(raw_status)
                except (TypeError, ValueError) as ver:
                    LOGGER.debug("Invalid log line %r: %s", line, ver)

    def fetch_video_metadata(self) -> VideoMetadata:
        """Runs ffpmpeg (blocking) to get the video's metadata"""
        try:
            probe: dict = ffmpeg.probe(str(self.input_file))
        except ffmpeg.Error as err:
            raise VideoError(err.stderr.splitlines()[-1].decode())
        video_streams: List[Dict[str, str]] = list(
            filter(lambda y: y.get("codec_type") == "video", probe["streams"])
        )
        if not video_streams:
            raise VideoError("No video streams found in {self.input_file}")
        if len(video_streams) > 1:
            LOGGER.warning("More than one video stream in %s, using the first one", self.input_file)
        video_stream: Dict[str, str] = video_streams[0]
        return VideoMetadata(
            codec=video_stream["codec_name"],
            pixel_format=video_stream["pix_fmt"],
            duration=datetime.timedelta(seconds=float(probe["format"]["duration"])),
            resolution=(int(video_stream['width']), int(video_stream['height'])),
        )

    def stop(self):
        """
        Sends a stop signal the running ffmpeg process.
        Raises `RuntimeError` if ffmpeg is not running.
        """
        if not self.ffmpeg:
            raise RuntimeError("ffmpeg is not running")
        self.ffmpeg.send_signal(signal.SIGINT)

    def process(self, to: Path, by: float = 2.0, fmt: Format = Format.MP4) -> Iterable[Progress]:
        """Runs ffmpeg (blocking). Yields `Progress` instances when logs are received."""
        try:
            # Clear previous returncode
            self.returncode = None
            with TemporaryDirectory("video-transformer") as td:
                temp_to = Path(td) / to.name
                args: Tuple = (
                    FFMPEG,
                    *ffmpeg
                    .input(str(self.input_file))
                    .setpts(f"{1/by}*PTS")
                    .output(str(temp_to), vcodec=fmt.value, preset="slower", crf=17)
                    .get_args(overwrite_output=True)
                )
                # Start the ffmpeg process
                self.ffmpeg = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                # Unbuffer stderr so we get output lines faster
                unbuffer_fd(self.ffmpeg.stderr.fileno())
                yield from self._ffmpeg_loop(self.ffmpeg)
                self.returncode = self.ffmpeg.poll()
                if self.returncode == 0:
                    # if ffmpeg exited successfully, copy the output file
                    temp_to.rename(to)

        finally:
            # The process is not running anymore
            self.ffmpeg = None

    @classmethod
    def _ffmpeg_loop(cls, ffmpeg: subprocess.Popen) -> Iterable[Progress]:
        """Waits for the given ffmpeg process to exit"""
        while ffmpeg.poll() is None:
            rlist, _, _ = select((ffmpeg.stderr, ffmpeg.stdout), (), ())
            # Read logs from stdin
            if ffmpeg.stderr in rlist:
                status = cls.process_logs(ffmpeg.stderr.read().splitlines())
                if status:
                    yield status
            # ignore stdout
            if ffmpeg.stdout in rlist:
                ffmpeg.stdout.read()
