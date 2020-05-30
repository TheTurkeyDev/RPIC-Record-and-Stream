import subprocess
from os import listdir, makedirs
from os.path import isfile, exists, join
import shlex
from time import sleep, strftime
from gpiozero import Button, LED
from signal import pause
from settings import *
from web_blueprint import api
from flask import Flask

button = Button(2, hold_time=5)
red_led = LED(3)

process = []

recording = False
wifi = True

app = Flask(__name__)
app.register_blueprint(api)


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

    fileName = video_folder + "/RPICRecord%04d.mkv"
    if videoType == "Recording":
        ffmpeg_cmd = "ffmpeg -f alsa -ar 44100 -ac 1 -i hw:2,0 -vcodec h264 "

        if camera_type is "CSI":
            raspivid = subprocess.Popen(shlex.split("raspivid -o - -n -md 4 -fps 30 -t 0"), stdout=subprocess.PIPE)
            ffmpeg_cmd += "-i - -pix_fmt yuv420p "
        elif camera_type is "USB":
            ffmpeg_cmd += "-s 1920x1080 -r 30 -i /dev/video0 -copyinkf "

        # Get all of the video #'s
        video_nums = [f.replace("RPICRecord", "").replace(".mkv", "") for f in listdir(video_folder) if isfile(join(video_folder, f))]
        video_nums.sort()

        # change start_num to be the first video number not used so that we don't overwrite existing videos
        start_num = 0
        while str(start_num).zfill(4) in video_nums:
            start_num += 1

        ffmpeg_cmd += "-vcodec copy -codec:a aac -ab 128k -af \"volume=25dB\" -f segment -segment_time " + str(segment_size) + " -segment_start_number " + str(start_num) + " " + fileName
        args = shlex.split(ffmpeg_cmd)
    else:
        ffmpeg_cmd = "ffmpeg -f alsa -ar 44100 -ac 1 -i hw:2,0 "
        if camera_type is "CSI":
            raspivid = subprocess.Popen(shlex.split("raspivid -o - -n -md 4 -fps 30 -t 0 -b 3000000"), stdout=subprocess.PIPE)
            ffmpeg_cmd += "-f h264 -i - "
        elif camera_type is "USB":
            ffmpeg_cmd += "-f v4l2 -codec:v h264 -r 30 -video_size 1920x1080 -i /dev/video0 "

        # TODO: Make Ingest Server Configurable
        ffmpeg_cmd += '-vcodec copy -codec:a aac -ab 128k -af \"volume=25dB\" -f flv rtmp://live-iad05.twitch.tv/app/' + stream_key
        args = shlex.split(ffmpeg_cmd)

        # Red : 1.7375      0.5755
        # Blue: 1.3625      0.7339

    red_led.blink()

    if raspivid is not None:
        process.append(raspivid)
        process.append(subprocess.Popen(args, stdin=raspivid.stdout))
    else:
        process.append(subprocess.Popen(args))


def stop_capture():
    global process
    red_led.off()
    for proc in process:
        proc.terminate()
    process = []


def toggle_wireless():
    global wifi
    wifi = not wifi
    if wifi:
        turn_on_wifi()
    else:
        turn_on_ap()


def turn_on_ap():
    # Blue LED?
    print("Enabling AP Connection...")
    subprocess.run(['sudo', 'echo', 'interface wlan0', '>', '/etc/dhcpcd.conf'])
    subprocess.run(['sudo', 'echo', 'static ip_address=192.168.11.1/24', '>>', '/etc/dhcpcd.conf'])
    subprocess.run(['wpa_cli', '-i', 'wlan0', 'disable_network', '0'])
    subprocess.run(['wpa_cli', '-i', 'wlan0', 'enable_network', '1'])
    subprocess.run(['sudo', 'systemctl', 'enable', 'dnsmasq'])
    subprocess.run(['sudo', 'systemctl', 'start', 'dnsmasq'])
    subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'])



def turn_on_wifi():
    # Blue LED?
    print("Enabling WIFI Connection...")
    subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq'])
    subprocess.run(['sudo', 'systemctl', 'disable', 'dnsmasq'])
    subprocess.run(['sudo', 'true', '>', 'etc/dhcpcd.conf'])
    subprocess.run(['wpa_cli', '-i', 'wlan0', 'enable_network', '0'])
    subprocess.run(['wpa_cli', '-i', 'wlan0', 'disable_network', '1'])
    subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'])


if __name__ == "__main__":
    # button.when_pressed = toggle_Capture
    button.when_held = toggle_wireless
    red_led.off()

    print("Running!")

    app.run(host='0.0.0.0', debug=True, use_reloader=False)