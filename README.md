# YouTube Video Downloader

A Python-based YouTube video downloader that allows you to download complete videos or specific segments from YouTube. This tool supports progress tracking and automatic segmentation of long videos.

## Features

- Download complete YouTube videos
- Download specific segments of videos by specifying start time and duration
- Automatic segmentation of long videos into smaller parts
- Progress tracking with download status
- Time formatting in HH:MM:SS format
- Customizable output path

## Requirements

- Python 3.x
- yt-dlp

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the script using Python:

```bash
python youtube_downloader.py
```

The program will prompt you to:
1. Enter the YouTube video URL
2. Choose whether to download the entire video or a specific segment
3. Specify the output path (optional)

### For Segment Downloads
If you choose to download a specific segment, you'll need to provide:
- Start time (in HH:MM:SS format)
- Duration (in seconds)

## Notes

- Videos longer than 30 minutes will be automatically split into multiple parts
- Downloads are saved in a 'downloads' folder by default
- Progress is displayed during download

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to fork this repository and submit pull requests for any improvements.
