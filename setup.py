"""simple ffmpeg & pyqt based video processing gui."""

import setuptools

try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except IOError:
    long_description = __doc__

setuptools.setup(
    name="video-transformer",
    version="0.0.1",
    author="etene",
    author_email="etienne.noss+pypi@gmail.com",
    description=__doc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/etene/video-transformer",
    packages=["video_transformer"],
    install_requires=["PyQt5==5.13.2", "ffmpeg-python==0.2.0"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        # TODO
    ],
    package_data={"video_transformer": ["py.typed"]}
)
