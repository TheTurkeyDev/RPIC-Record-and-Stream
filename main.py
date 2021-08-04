import subprocess
from os import listdir, makedirs
from os.path import isfile, exists, join
import shlex
from time import sleep, strftime
from gpiozero import Button, LED
from config import getConfig, initConfig
import stream as Stream
from web_blueprint import api
from flask import Flask
from flask_socketio import SocketIO, emit
import gzip
import threading

button = Button(3, hold_time=3)
red_led = LED(2)

was_held = False
recording = False
wifi = True
thread_running = False

app = Flask(__name__)
app.register_blueprint(api)
socketio = SocketIO(app)


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
    capture_type = getConfig()["General"]["videoType"]
    started = False
    if capture_type == "Recording":
        started = Stream.start_record()
    elif capture_type == "Streaming":
        started = Stream.start_stream('flv', getConfig()['Streaming']['streamLink'])
    elif capture_type == "Preview":
        started = Stream.start_preview()

    if started:
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


@socketio.on('start_preview')
def preview_image():
    global thread_running
    app.logger.info("preview")
    if not thread_running:
        app.logger.info("start thread")
        socketio.start_background_task(target=lambda: broadcast_image())


def broadcast_image():
    global thread_running
    thread_running = True
    while True:
        with open('/dev/shm/mjpeg/cam.jpg', 'rb') as f:
            image_data = f.read()

        socketio.emit('preview_image', {'image_data': image_data}, broadcast=True)
        socketio.sleep(0.01)


if __name__ == "__main__":
    button.when_held = toggle_wireless
    button.when_released = toggle_Capture

    initConfig()

    Stream.init()

    red_led.off()

    print("Running!")

    socketio.run(app, debug=True, use_reloader=False)
