import subprocess
from os import listdir, makedirs
from os.path import isfile, exists, join
import shlex
from config import getConfig
import sys

process = []
video_folder = ""
image_folder = ""
is_active = False


def init():
    global video_folder, image_folder
    video_folder = "/opt/rpic/videos"
    if not exists(video_folder):
        makedirs(video_folder)
    image_folder = "/opt/rpic/images"
    if not exists(image_folder):
        makedirs(image_folder)


def snap_shot():
    global image_folder
    print("Taking snapshot!")
    subprocess.Popen(shlex.split("sudo raspistill -o " + image_folder + "/snapshot.png -awb greyworld -n -md 4"))


def start_record():
    global process, video_folder, is_active
    raspivid = None
    settings = getConfig()['Recording']
    print("Starting Video Recording\n")

    fileName = video_folder + "/RPICRecord%04d.mkv"
    ffmpeg_cmd = "ffmpeg "

    if settings['audio'] == 'none':
        ffmpeg_cmd += "-ar 44100 -ac 2 -acodec pcm_s16le -f s16le -i /dev/zero "
    elif settings['audio'] == 'i2s':
        ffmpeg_cmd += "-f alsa -ar 44100 -ac 2 -c:a pcm_s32le -i default:CARD=sndrpii2scard "

    ffmpeg_cmd += "-vcodec h264 "

    if getConfig()['General']['cameraType'] == "CSI":
        raspivid = subprocess.Popen(shlex.split(
            f'raspivid -o - -t 0 -n -md 4 -awb greyworld -ex {settings["exposure"]} -b {settings["bitrate"]} -fps {settings["fps"]} -ae 32,0x00,0x808000,1,100,100 -a "{settings["overlayText"]}"'), stdout=subprocess.PIPE)
        ffmpeg_cmd += f'-framerate {settings["fps"]} -i - -pix_fmt yuv420p '
    elif getConfig()['General']['cameraType'] == "USB":
        ffmpeg_cmd += f'-s 1920x1080 -r {settings["fps"]} -i /dev/video0 -copyinkf '
    else:
        print("Invalid camera type!\n", file=sys.stderr)
        return False

    # Get all of the video #'s
    video_nums = [f.replace("RPICRecord", "").replace(".mkv", "") for f in listdir(video_folder) if isfile(join(video_folder, f))]
    video_nums.sort()

    # change start_num to be the first video number not used so that we don't overwrite existing videos
    start_num = 0
    while str(start_num).zfill(4) in video_nums:
        start_num += 1

    ffmpeg_cmd += "-preset ultrafast -crf 0 -vcodec copy "

    if settings['audio'] == 'none':
        ffmpeg_cmd += ""
    elif settings['audio'] == 'i2s':
        ffmpeg_cmd += '-codec:a aac '
    #  -af "volume=1dB, highpass=f=200, lowpass=f=3000"

    ffmpeg_cmd += "-f segment -segment_time " + str(settings['segmentSize']) + " -segment_start_number " + str(start_num) + " " + fileName

    args = shlex.split(ffmpeg_cmd)
    if raspivid is not None:
        process.append(raspivid)
        process.append(subprocess.Popen(args, stdin=raspivid.stdout))
    else:
        process.append(subprocess.Popen(args))

    is_active = True
    return True
    # TODO: Add thread to check that the processes are still alive via proc.poll()


def start_stream(out_format, out_link):
    global process, is_active
    raspivid = None
    settings = getConfig()['Streaming']
    print("Starting Stream\n")

    ffmpeg_cmd = "ffmpeg "
    if settings['audio'] == 'none':
        ffmpeg_cmd += "-ar 44100 -ac 2 -acodec pcm_s16le -f s16le -i /dev/zero "
    elif settings['audio'] == 'i2s':
        ffmpeg_cmd += "-f alsa -ar 44100 -ac 2 -c:a pcm_s32le -i default:CARD=sndrpii2scard "

    if getConfig()['General']['cameraType'] == "CSI":
        raspivid = subprocess.Popen(shlex.split(
            f'raspivid -o - -t 0 -n -md 4 -awb greyworld -ex {settings["exposure"]} -fps {settings["fps"]} -b {settings["bitrate"]} -ae 32,0x00,0x808000,1,100,100 -a "{settings["overlayText"]}"'), stdout=subprocess.PIPE)
        ffmpeg_cmd += f'-f h264 -framerate {settings["fps"]} -i - '
    elif getConfig()['General']['cameraType'] == "USB":
        ffmpeg_cmd += f'-f v4l2 -codec:v h264 -r {settings["fps"]} -video_size 1920x1080 -i /dev/video0 '
    else:
        print("Invalid camera type!\n", file=sys.stderr)
        return False

    ffmpeg_cmd += '-vcodec copy '

    if settings['audio'] == 'none':
        ffmpeg_cmd += '-c:a libmp3lame '
    elif settings['audio'] == 'i2s':
        ffmpeg_cmd += '-codec:a aac -ab 128k -af "volume=15dB" '
    #  -af "volume=15dB, highpass=f=200, lowpass=f=3000"

    # TODO: Make Ingest Server Configurable
    ffmpeg_cmd += '-f ' + out_format + ' ' + out_link

    args = shlex.split(ffmpeg_cmd)
    if raspivid is not None:
        process.append(raspivid)
        process.append(subprocess.Popen(args, stdin=raspivid.stdout))
    else:
        process.append(subprocess.Popen(args))

    is_active = True
    return True

    # TODO: Add thread to check that the processes are still alive via proc.poll()


def start_rtsp():
    global process, is_active
    settings = getConfig()['Streaming']
    print("Starting RTSP\n")

    # if getConfig()['General']['cameraType'] is "CSI":
    raspivid = subprocess.Popen(shlex.split(
        f'raspivid -o - -t 0 -n -md 4 -awb greyworld -ex {settings["exposure"]} -fps {settings["fps"]} -b {settings["bitrate"]} -ae 32,0x00,0x808000,1,100,100 -a "{settings["overlayText"]}"'), stdout=subprocess.PIPE)

    # raspivid -t 0 -fps 30 -o - --nopreview | nc -l 5050
    args = shlex.split("raspivid -t 0 -fps 30 -o - --nopreview | ffmpeg -framerate 30 -f h264 -i - -preset ultrafast -vcodec copy -tune zerolatency -f mpegts udp://192.168.1.94:1234")
    if raspivid is not None:
        process.append(raspivid)
        process.append(subprocess.Popen(args, stdin=raspivid.stdout))
    else:
        process.append(subprocess.Popen(args))

    is_active = True
    return True

    # TODO: Add thread to check that the processes are still alive via proc.poll()


def stop():
    global process, is_active
    for proc in process:
        proc.terminate()
    process = []
    is_active = False
