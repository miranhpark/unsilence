# Unsilence.py

Unsilence.py takes a video file (MP4) and removes any silent or quiet clips at a threshold/duration of your choosing. Requires ffmpeg (https://ffmpeg.org/). 

## Usage:

```
Usage: 
    python -i <name>
    python unsilence.py -h | --help

Options:
    -h --help      Show this screen.
    -i <name>      Input file name (required).
    -o <name>      Output file name (defaults to <input name>_out.mp4).
    -t threshold   Threshold in dB (default value = -40).
    -d duration    Minimum duration of silence in seconds.
    
Examples:
    python -i video.mp4 
    python -i video.mp4 -o output.mp4
    python -i video.mp4 -t -30 -d 3
```

# To do:
- accomodate other file formats
- add volume normalization preprocess
