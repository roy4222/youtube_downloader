from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="youtube_downloader",
    version="1.0.0",
    author="YouTube下載器開發團隊",
    author_email="info@example.com",
    description="一個模組化的 YouTube 下載工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube_downloader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "yt-dlp>=2023.3.4",
    ],
    entry_points={
        "console_scripts": [
            "ytdl=youtube_downloader.main:main",
        ],
    },
) 