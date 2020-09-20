import subprocess
from os import listdir, makedirs
from os.path import isfile, exists, join
import shlex
from settings import *

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


def start_stream(out_format, out_link):
    global process, is_active
    print("Starting Stream")

    #ffmpeg_cmd = "ffmpeg -f alsa -ar 44100 -ac 1 -i hw:2,0 "
    ffmpeg_cmd = "ffmpeg -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -i /dev/zero "
    if camera_type is "CSI":
        raspivid = subprocess.Popen(shlex.split("raspivid -o - -awb greyworld -n -md 4 -fps 30 -t 0 -b 5000000"), stdout=subprocess.PIPE)
        ffmpeg_cmd += "-f h264 -framerate 30 -i - "
    elif camera_type is "USB":
        ffmpeg_cmd += "-f v4l2 -codec:v h264 -r 30 -video_size 1920x1080 -i /dev/video0 "

    # TODO: Make Ingest Server Configurable
    #ffmpeg_cmd += '-vcodec copy -codec:a aac -ab 128k -af \"volume=25dB\" -f flv rtmp://live-iad05.twitch.tv/app/' + stream_key
    ffmpeg_cmd += '-vcodec copy -c:a libmp3lame -f ' + out_format + ' ' + out_link
    args = shlex.split(ffmpeg_cmd)
    if raspivid is not None:
        process.append(raspivid)
        process.append(subprocess.Popen(args, stdin=raspivid.stdout))
    else:
        process.append(subprocess.Popen(args))

    is_active = True

    # TODO: Add thread to check that the processes are still alive via proc.poll()


def start_record():
    global process, video_folder, is_active
    print("Starting Video Recording")

    fileName = video_folder + "/RPICRecord%04d.mkv"

    #ffmpeg_cmd = "ffmpeg -f alsa -ar 44100 -ac 1 -i hw:2,0 -vcodec h264 "
    ffmpeg_cmd = "ffmpeg -vcodec h264 "

    if camera_type is "CSI":
        raspivid = subprocess.Popen(shlex.split("raspivid -o - -awb greyworld -n -md 4 -b 17000000 -fps 30 -t 0"), stdout=subprocess.PIPE)
        ffmpeg_cmd += "-framerate 30 -i - -pix_fmt yuv420p "
    elif camera_type is "USB":
        ffmpeg_cmd += "-s 1920x1080 -r 30 -i /dev/video0 -copyinkf "

    # Get all of the video #'s
    video_nums = [f.replace("RPICRecord", "").replace(".mkv", "") for f in listdir(video_folder) if isfile(join(video_folder, f))]
    video_nums.sort()

    # change start_num to be the first video number not used so that we don't overwrite existing videos
    start_num = 0
    while str(start_num).zfill(4) in video_nums:
        start_num += 1

    #ffmpeg_cmd += "-vcodec copy -codec:a aac -ab 128k -af \"volume=25dB\" -f segment -segment_time " + str(segment_size) + " -segment_start_number " + str(start_num) + " " + fileName
    ffmpeg_cmd += "-preset ultrafast -crf 0 -vcodec copy -f segment -segment_time " + str(segment_size) + " -segment_start_number " + str(start_num) + " " + fileName
    args = shlex.split(ffmpeg_cmd)
    if raspivid is not None:
        process.append(raspivid)
        process.append(subprocess.Popen(args, stdin=raspivid.stdout))
    else:
        process.append(subprocess.Popen(args))

    is_active = True

    # TODO: Add thread to check that the processes are still alive via proc.poll()


def stop():
    global process, isActive
    for proc in process:
        proc.terminate()
    process = []
    is_active = False
