import subprocess
from os import listdir, makedirs
from os.path import isfile, exists, join
import shlex
from time import sleep, strftime
from gpiozero import Button, LED
from signal import pause
from flask import Flask
from flask import render_template
from settings import *

app = Flask(__name__)

button = Button(2)
videoType = Button(3)
switch = Button(4)
red_led = LED(17)

process = None

recording = False


@app.route("/")
def hello():
    status = "Streaming"
    if videoType.is_pressed:
        status = "Recording"
    return render_template('index.html', status=status)


def toggle_Capture():
    global recording
    recording = not recording
    if recording:
        start_capture()
    else:
        stop_capture()


def start_capture():
    global process
    video_folder = "/opt/rpic/videos"
    if not exists(video_folder):
        makedirs(video_folder)

    fileName = video_folder + "/RPICRecord%04d.mp4"
    if videoType.is_pressed:
        ffmpeg_cmd = "ffmpeg -vcodec h264 "

        if camera_type is "CSI":
            raspivid = subprocess.Popen(shlex.split("raspivid -o - -n -md 1 -fps 30 -t 0"), stdout=subprocess.PIPE)
            ffmpeg_cmd += "-i - -vcodec copy "
        elif camera_type is "USB":
            ffmpeg_cmd += "-s 1920x1080 -r 30 -i /dev/video0 -copyinkf -vcodec copy "

        # Get all of the video #'s
        video_nums = [f.replace("RIPZRecord", "").replace(".mp4", "") for f in listdir(video_folder) if isfile(join(video_folder, f))]
        video_nums.sort()

        # change start_num to be the first video number not used so that we don't overwrite existing videos
        start_num = 0
        while str(start_num).zfill(4) in video_nums:
            start_num += 1

        ffmpeg_cmd += "-f segment -segment_time " + str(segment_size) + " -segment_start_number " + str(start_num) + " " + fileName
        args = shlex.split(ffmpeg_cmd)
    else:
        args = shlex.split('ffmpeg -ar 44100 -acodec pcm_s16le -f s16le -ac 2 -channel_layout 2.1 -i /dev/zero -f v4l2 -codec:v h264 -framerate 30 -video_size 1920x1080 -i /dev/video0 -c:v copy -c:a libmp3lame -f flv ' + stream_key)

    red_led.blink()

    if raspivid is not None:
        process = subprocess.Popen(args, stdin=raspivid.stdout)
    else:
        process = subprocess.Popen(args)


def stop_capture():
    red_led.off()
    if process is not None:
        process.terminate()


def turn_on_ap():
    # Blue LED?
    print("Enabling AP Connection...")
    subprocess.run(['wpa_cli', '-i', 'wlan0', 'disable_network', '0'])
    subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', 'wlan0', 'down'])
    subprocess.run(['sudo', 'ip', 'addr', 'add', '192.168.0.1/24', 'dev', 'wlan0'])
    subprocess.run(['sudo', 'service', 'dhcpcd', 'restart'])
    subprocess.run(['sudo', 'systemctl', 'start', 'dnsmasq.service'])
    subprocess.run(['sudo', 'systemctl', 'start', 'hostapd'])


def turn_on_wifi():
    # Blue LED?
    print("Enabling WIFI Connection...")
    subprocess.run(['sudo', 'systemctl', 'stop', 'hostapd.service'])
    subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq.service'])
    subprocess.Popen(['wpa_cli', '-i', 'wlan0', 'enable_network', '0'])


if __name__ == "__main__":
    switch.when_pressed = turn_on_ap
    switch.when_released = turn_on_wifi
    button.when_pressed = toggle_Capture

    print("Running!")
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
