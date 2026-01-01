"""Setup configuration for easy-wallpaper package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="easy-wallpaper",
    version="1.0.0",
    author="Nimuthu Ganegoda",
    description="A simple CLI tool to download and set desktop wallpapers from Unsplash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NimuthuGanegoda/AutoWallpaper",
    py_modules=["easy_wallpaper"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "easy-wallpaper=easy_wallpaper:main",
        ],
    },
)
