from datetime import timedelta
from logging import getLogger
from pathlib import Path
from typing import ClassVar, Optional

from PyQt5 import QtWidgets  # type: ignore
from PyQt5.QtCore import QThread, pyqtSignal  # type: ignore

from video_transformer.core import FFmpegWrapper, Progress
from video_transformer.ui import Ui_MainWindow  # type: ignore

LOG = getLogger("video-transformer-ui")


class ProcessThread(QThread):
    """QThread used to control the ffmpeg process"""
    finished: ClassVar[pyqtSignal] = pyqtSignal(int)
    progress: ClassVar[pyqtSignal] = pyqtSignal(Progress)

    def __init__(self, ffmpeg_wrapper: FFmpegWrapper, **options):
        QThread.__init__(self)
        self.ffmpeg_wrapper = ffmpeg_wrapper
        self.options = options

    # run method gets called when we start the thread
    def run(self):
        for progress in self.ffmpeg_wrapper.process(**self.options):
            self.progress.emit(progress)
        self.finished.emit(self.ffmpeg_wrapper.returncode)

    def stop(self):
        self.ffmpeg_wrapper.stop()


class VideoTransformerInterface(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Connect buttons with their actions
        self.ui.file_select_button.clicked.connect(self.select_file)
        self.ui.process_button.clicked.connect(self.process)
        self.ui.speed_spinbox.valueChanged.connect(self.speed_changed)
        # Set initial state
        self.ui.statusbar.showMessage("Choose a video")
        self.selected_file: Optional[Path] = None
        self.thread: Optional[ProcessThread] = None
        self.ffmpeg: Optional[FFmpegWrapper] = None
        self.reset_state()

    @property
    def speed(self) -> float:
        """The currently selected speed"""
        return self.ui.speed_spinbox.value()

    @property
    def output_file(self) -> Path:
        """The ouput file (<input file name>.<speed>.mp4)"""
        # FIXME set extension from format
        if not self.selected_file:
            raise AttributeError("No file selected yet")
        return self.selected_file.with_suffix(f".{self.speed}.mp4")

    @property
    def output_duration(self) -> timedelta:
        """The output file target duration"""
        if not self.ffmpeg:
            raise AttributeError("No output_duration when no file is selected")
        return self.ffmpeg.metadata.duration * (1 / self.speed)

    def select_file(self):
        """Callback when the video selection button is pressed"""
        selected: Optional[str] = QtWidgets.QFileDialog.getOpenFileName()[0]
        if selected:
            self.selected_file = Path(selected)
            self.ffmpeg = FFmpegWrapper(self.selected_file)
            self.ui.statusbar.showMessage(
                f"{self.selected_file.name!r} selected ({self.ffmpeg.metadata.duration})"
            )
            self.ui.process_button.setEnabled(True)
            self.speed_changed()

    def error(self, message):
        """Shortcut to show an error popup"""
        QtWidgets.QErrorMessage(self).showMessage(message)

    def processing_done(self, ffmpeg_returncode: int):
        """Called when the ffmpeg thread's `finished` event fires."""
        if ffmpeg_returncode == 255:
            # ffmpeg was interrupted
            # https://ffmpeg.org/doxygen/0.6/ffmpeg_8c-source.html
            self.ui.statusbar.showMessage("Processing stopped")
        elif ffmpeg_returncode != 0:
            # ffmpeg exited on error
            self.ui.statusbar.showMessage(f"Error while processing video ({ffmpeg_returncode})")
        else:
            # ffpmeg exited successfully
            self.ui.statusbar.showMessage(f"{self.output_file.name!r}: Processing finished")
        self.reset_state(success=ffmpeg_returncode == 0)

    def reset_state(self, success: Optional[bool] = None):
        self.thread = None
        # Can select a file
        self.ui.file_select_button.setEnabled(True)
        self.ui.speed_spinbox.setEnabled(True)
        self.ui.process_button.setText("Process video")
        self.ui.file_select_button.setText("Select video...")
        if success is True:
            # Processing was finished successfully, so let's say 100%
            self.ui.progress_bar.setValue(100)
            self.ui.resulting_duration.setText("")
            # And reset the video too
            self.ffmpeg = None
            self.selected_file = None
            self.ui.process_button.setEnabled(True)

    def update_progress(self, progress: Progress):
        """Called when the ffmpeg thread's `progress` event fires"""
        percentage = (progress.time.total_seconds() / self.output_duration.total_seconds()) * 100
        self.ui.progress_bar.setValue(percentage)
        self.ui.statusbar.showMessage(
            f"Processing: {progress.fps} FPS, {progress.bitrate}, {progress.size} written"
        )

    def process(self):
        if self.selected_file is None:
            self.error("Select a video first")
            return
        if self.thread:
            self.ui.statusbar.showMessage("Stopping...")
            self.thread.stop()
            return

        self.ui.statusbar.showMessage(f"{self.output_file.name!r}: Processing...")
        # Create the thread
        self.thread = ProcessThread(self.ffmpeg, to=self.output_file, by=self.speed)
        self.thread.finished.connect(self.processing_done)
        self.thread.progress.connect(self.update_progress)
        self.thread.start()
        self.ui.file_select_button.setEnabled(False)
        self.ui.speed_spinbox.setEnabled(False)
        self.ui.process_button.setText("Stop")

    def speed_changed(self):
        duration = str(self.output_duration).split(".")[0]
        self.ui.resulting_duration.setText(f"({duration})")


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = VideoTransformerInterface()
    window.show()
    sys.exit(app.exec_())
