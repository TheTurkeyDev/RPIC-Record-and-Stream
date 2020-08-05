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

button = Button(3, hold_time=5)
red_led = LED(2)

process = []

recording = False
wifi = True

audio = False

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
    ffmpeg_cmd = "ffmpeg "
    if videoType == "Recording":
        if audio:
            ffmpeg_cmd += "-f alsa -ar 44100 -ac 1 -i hw:2,0 "
        ffmpeg_cmd += "-vcodec h264 "

        if camera_type is "CSI":
            raspivid = subprocess.Popen(shlex.split("raspivid -o - -n -md 1 -b 17000000 -fps 30 -t 0"), stdout=subprocess.PIPE)
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

        ffmpeg_cmd += "-preset ultrafast -crf 0 -r 30 -vcodec copy "
        if audio:
            ffmpeg_cmd += "-codec:a aac -ab 128k -af \"volume=25dB\" "
        ffmpeg_cmd += "-f segment -segment_time " + str(segment_size) + " -segment_start_number " + str(start_num) + " " + fileName
    else:
        if audio:
            ffmpeg_cmd += "-f alsa -ar 44100 -ac 1 -i hw:2,0 "
        else:
            ffmpeg_cmd += "-ar 44100 -ac 2 -acodec pcm_s16le -f s16le -i /dev/zero "

        if camera_type is "CSI":
            raspivid = subprocess.Popen(shlex.split("raspivid -o - -n -md 1 -fps 30 -t 0 -b 5000000"), stdout=subprocess.PIPE)
            ffmpeg_cmd += "-f h264 -i - "
        elif camera_type is "USB":
            ffmpeg_cmd += "-f v4l2 -codec:v h264 -r 30 -video_size 1920x1080 -i /dev/video0 "

        ffmpeg_cmd += "-vcodec copy"
        if audio:
             ffmpeg_cmd += "-codec:a aac -ab 128k -af \"volume=25dB\" "
        else:
            ffmpeg_cmd += "-c:a libmp3lame "

        # TODO: Make Ingest Server Configurable
        ffmpeg_cmd += '-f flv rtmp://live-iad05.twitch.tv/app/' + stream_key
    
    args = shlex.split(ffmpeg_cmd)

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
    button.when_pressed = toggle_Capture
    button.when_held = toggle_wireless
    red_led.off()

    print("Running!")

    app.run(host='0.0.0.0', debug=True, use_reloader=False)