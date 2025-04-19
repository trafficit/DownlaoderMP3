############################################################################
#                                                                          #
# Version 0.1    Created by Alex Filyaev wth AI 19.04.2025                 #
#                                                                          #
############################################################################

# A file is provided for running in the Linux environment.
# Use
# python to run it.   python setup.py build

from cx_Freeze import setup, Executable

setup(
    name="DownloaderMP3",
    version="1.0",
    description="MP3 Downloader",
    executables=[Executable("DownloaderMP3_v1.py")]
)
