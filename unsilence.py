import subprocess, re, sys

def print_help():
    print('''
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
    ''')

def parse_time(line):
    return re.search('.*?:\s([\d\.]*)', line).group(1)

if __name__ == "__main__":
    if '-h' in sys.argv or '--help' in sys.argv or 'help' in sys.argv:
        print_help()
        sys.exit(1)
     
    if '-i' in sys.argv:  
        input_filename = sys.argv[sys.argv.index('-i') + 1]
    else:
        print_help()
        sys.exit(1)
        
    if '-o' in sys.argv:
        output_filename = sys.argv[sys.argv.index('-o') + 1]
    else:
        output_filename = re.search('(.*)\.', input_filename).group(1) + '_out.mp4'
    
    if '-t' in sys.argv:
        threshold = sys.argv[sys.argv.index('-t') + 1]
    else:
        threshold = -40
    
    if '-t' in sys.argv:
        duration = sys.argv[sys.argv.index('-d') + 1]
    else:
        duration = -40
    
    # Create mp3 ffrom audio for silence detection
    subprocess.call('ffmpeg -i ' + input_filename + ' fileaudio.mp3', shell=True)

    # Silence detection 
    subprocess.call('ffmpeg -i fileaudio.mp3 -af silencedetect=n=' + str(threshold) + 'dB:d=' + \
                    str(duration) + ' -f null - 2> sdout.txt', shell=True)

    # Create list for temporary clip names
    sdout = open('sdout.txt','r')
    clipsout = open('clips.txt','w')

    lineno = 0
    clipcount = 0

    starts = []
    ends = []
    concat_list = []

    content = sdout.read().replace('\r', '\n').split('\n')

    # Read silence clip times
    for line in content:
        if 'silence_start' in line:
            starts += [parse_time(line)]
        if 'silence_end' in line: 
            ends += [parse_time(line)]     
        
    # Create temporary clips that contain audio 
    for i in range(0,len(starts)):
        if i == 0:
            clipstring = 'ffmpeg -ss ' + '0' + ' -i ' + input_filename + ' -t ' + \
                        starts[i] + ' -c copy tempclip' + str(i) + '.mp4'
            subprocess.call(clipstring, shell=True)
        elif i < len(starts) - 1:
            clipstring = 'ffmpeg -ss ' + ends[i - 1] + ' -i ' + input_filename + ' -t ' + \
                        str(float(starts[i]) - float(ends[i - 1])) + ' -c copy tempclip' + str(i) + '.mp4'
            subprocess.call(clipstring, shell=True)
        else:
            if len(starts) != len(ends): 
                clipstring = 'ffmpeg -ss ' + ends[i - 1] + ' -i ' + input_filename + ' -t ' + \
                            str(float(starts[i]) - float(ends[i - 1])) + ' -c copy tempclip' + str(i) + '.mp4'
                subprocess.call(clipstring, shell=True)
            else:
                duration_find_string = 'ffprobe -v error -show_entries format=duration \
                                            -of default=noprint_wrappers=1:nokey=1 ' + input_filename
                duration = subprocess.check_output(duration_find_string, shell=True)
                clipstring = 'ffmpeg -ss ' + ends[i - 1] + ' -i ' + input_filename + ' -t ' + \
                            str(float(duration) - float(ends[i - 1])) + ' -c copy tempclip' + str(i) + '.mp4'
                subprocess.call(clipstring, shell=True)
        clipsout.write('file \'tempclip' + str(i) + '.mp4\'\n')
        clipcount += 1

    clipsout.close()

    # Create final file
    concat_cmd = 'ffmpeg -f concat -i clips.txt -c copy ' + output_filename
    subprocess.call(concat_cmd, shell=True)

    # Clean up temp files
    subprocess.call('rm sdout.txt clips.txt', shell=True)
    subprocess.call('rm fileaudio.mp3', shell=True)

    for i in range(0,clipcount):
        subprocess.call('rm tempclip' + str(i) + '.mp4', shell=True)


