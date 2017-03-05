import sys
from cx_Freeze import setup, Executable

setup(  name = "mp3 crawler",
        version = "1.0",
        description = "crawling recent mp3 in melon top 100",
        author = "innocentree",
        executables = [Executable("main.py")]
        )

# python setup.py build
