from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from video_transformer.core import FFmpegWrapper, VideoError

SAMPLE_VIDEO = Path("tests/Whathappenedontwentythirdstreet-thomasedisoninc.ogv.240p.vp9.webm")


def test_metadata():
    """metadata inferred from a sample video is correct"""
    wrapper = FFmpegWrapper(SAMPLE_VIDEO)
    md = wrapper.metadata
    assert md.codec == "vp9"
    assert md.pixel_format == "yuv420p"
    assert md.duration.total_seconds() == 49.713
    assert md.resolution == (320, 240)


def test_process():
    """process() creates a video file"""
    wrapper = FFmpegWrapper(SAMPLE_VIDEO)
    with TemporaryDirectory() as td:
        output_file = Path(td) / "result.mp4"
        statuses = list(wrapper.process(to=output_file))
        assert wrapper.returncode == 0
        assert output_file.exists()
        assert len(output_file.read_bytes()) > 0
        assert len(statuses) > 0
        size, secs = 0, 0
        for s in statuses:
            new_size = int(s.size[:-2])
            new_secs = s.time.total_seconds()
            assert new_size >= size
            size = new_size
            assert new_secs >= secs


def test_stop():
    """Tests that a ffmpeg wrapper can be stopped"""
    wrapper = FFmpegWrapper(SAMPLE_VIDEO)

    # Cannot stop when not running
    with pytest.raises(RuntimeError) as err:
        wrapper.stop()
    assert str(err.value) == "ffmpeg is not running"

    with TemporaryDirectory() as td:
        output_file = Path(td) / "result.mp4"
        for status in wrapper.process(to=output_file):
            if status.time.total_seconds() > 0:
                # video processing started, stop it
                wrapper.stop()
        assert wrapper.returncode == 255
        assert not output_file.exists()


def test_invalid_video():
    with pytest.raises(VideoError) as err:
        FFmpegWrapper(Path(__file__))
    assert str(err.value).endswith("Invalid data found when processing input")
