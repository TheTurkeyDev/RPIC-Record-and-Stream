import subprocess
from os import listdir, makedirs
from os.path import isfile, exists, join
import shlex
from time import sleep, strftime
from gpiozero import Button, LED
from signal import pause
import settings as Settings
import stream as Stream
from web_blueprint import api
from flask import Flask

button = Button(3, hold_time=3)
red_led = LED(2)

was_held = False
recording = False
wifi = True

app = Flask(__name__)
app.register_blueprint(api)


def toggle_Capture():
    global recording, was_held
    if not was_held:
        recording = not recording
        if recording:
            start_capture()
        else:
            stop_capture()

    was_held = False


def start_capture():
    if Settings.videoType == "Recording":
        Stream.start_record()
    else:
        Stream.start_stream('flv', Settings.stream_link)

    red_led.blink()


def stop_capture():
    Stream.stop()
    red_led.off()


def toggle_wireless():
    global wifi, was_held
    was_held = True
    red_led.blink(on_time=0.25, off_time=0.25, n=5)
    wifi = not wifi
    if wifi:
        turn_on_wifi()
    else:
        turn_on_ap()


def turn_on_ap():
    # Blue LED?
    print("Enabling AP Connection...")
    subprocess.run(['sudo', 'auto-hotspot', '--start-ap'])


def turn_on_wifi():
    # Blue LED?
    print("Enabling WIFI Connection...")
    subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
    subprocess.run(['sudo', 'auto-hotspot', '--stop-ap'])


if __name__ == "__main__":
    button.when_held = toggle_wireless
    button.when_released = toggle_Capture

    Stream.init()

    red_led.off()

    print("Running!")

    app.run(host='0.0.0.0', debug=True, use_reloader=False)