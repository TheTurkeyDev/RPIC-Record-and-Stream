
from flask import Flask, Blueprint, render_template, request, jsonify, send_file
from config import camera_types_list, getConfig, saveConfig
import subprocess
import stream as Stream

api = Blueprint('api', __name__)


@api.route("/")
def hello():
    return render_template('index.html', settings=getConfig()["General"], cameraTypes=camera_types_list)


@api.route("/network")
def network():
    return render_template('network.html', settings=getConfig()['Network'])


@api.route("/recording")
def recording():
    return render_template('recording.html', settings=getConfig()['Recording'], defaults={'exposureTypes': ['Auto', 'Night', 'Backlight', 'Spotlight', 'Sports', 'Snow', 'Beach', 'Verylong', 'Fixedfps', 'Antishake', 'Fireworks']})


@api.route("/streaming")
def streaming():
    return render_template('streaming.html', settings=getConfig()['Streaming'], defaults={'exposureTypes': ['Auto', 'Night', 'Backlight', 'Spotlight', 'Sports', 'Snow', 'Beach', 'Verylong', 'Fixedfps', 'Antishake', 'Fireworks']})


@api.route("/preview")
def preview():
    return render_template('preview.html')


@api.route("/setnetwork", methods=['POST'])
def setnetwork():
    json_data = request.get_json()
    getConfig()['Network']['ssid'] = json_data['ssid']
    getConfig()['Network']['password'] = json_data['psk']
    saveConfig()
    ssid = '"' + json_data['ssid'] + '"'
    psk = '"' + json_data['psk'] + '"'
    subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'set_network', '1', 'ssid', ssid])
    subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'set_network', '1', 'psk', psk])
    subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'enable_network', '1'])
    subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'save_config'])
    return jsonify(success=True, message="Network data set!")


@api.route("/setvidtype", methods=['POST'])
def set_video_type():
    json_data = request.get_json()
    getConfig()['General']['videoType'] = json_data['type']
    saveConfig()
    return jsonify(success=True, message="Video type set!", type=getConfig()['General']['videoType'])


@api.route("/setstreamurl", methods=['POST'])
def set_stream_url():
    json_data = request.get_json()
    getConfig()['Streaming']['streamLink'] = json_data['url']
    saveConfig()
    return jsonify(success=True, message="Stream URL set!")


@api.route("/snapshot", methods=['GET'])
def get_snapshot():
    return send_file('/opt/rpic/images/snapshot.png', mimetype='image/png')


@api.route("/newsnapshot", methods=['POST'])
def new_snapshot():
    Stream.snap_shot()
    return jsonify(success=True, message="New snapshot taken!")
