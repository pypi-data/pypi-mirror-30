from setuptools import setup

setup(
    name="pyshuf",
    version="0.0.1",
    author="Jake Kara",
    description="Inexact clone of GNU shuf. Shuffles order of lines in a file.",
    license="GPL-3",
    keywords="shuf",
    url="https://github.org/jakekara/pyshuf",
    repository="https://github.org/jakekara/pyshuf",
    packages=["pyshuf"],
    entry_points = {
        "console_scripts": ["pyshuf=pyshuf.__main__:main"]
    }
)
