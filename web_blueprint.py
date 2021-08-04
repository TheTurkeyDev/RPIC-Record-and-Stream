
from flask import Flask, Blueprint, render_template, request, jsonify, send_file
from config import camera_types_list, getConfig, saveConfig, getRaspiMjpegConfig
import subprocess
import stream as Stream

api = Blueprint('api', __name__)


exposureTypes = ['Auto', 'Night', 'Backlight', 'Spotlight', 'Sports', 'Snow', 'Beach', 'Verylong', 'Fixedfps', 'Antishake', 'Fireworks']
audio = ['none', 'i2s']


@api.route("/")
def hello():
    return render_template('index.html', settings=getConfig()["General"], cameraTypes=camera_types_list)


@api.route("/network")
def network():
    return render_template('network.html', settings=getConfig()['Network'])


@api.route("/recording")
def recording():
    return render_template('recording.html', settings=getConfig()['Recording'], defaults={'exposureTypes': exposureTypes, 'audio': audio})


@api.route("/streaming")
def streaming():
    return render_template('streaming.html', settings=getConfig()['Streaming'], defaults={'exposureTypes': exposureTypes, 'audio': audio})


@api.route("/preview")
def preview():
    return render_template('preview.html', settings=getRaspiMjpegConfig())


@api.route("/vr")
def vr():
    return render_template('vr.html')


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


@api.route("/saveStreamSettings", methods=['POST'])
def save_stream_settings():
    json_data = request.get_json()
    getConfig()['Streaming']['streamLink'] = json_data['url']
    getConfig()['Streaming']['fps'] = str(json_data['fps'])
    getConfig()['Streaming']['bitrate'] = str(json_data['bitrate'])
    getConfig()['Streaming']['audio'] = json_data['audio']
    getConfig()['Streaming']['exposure'] = json_data['exposure']
    getConfig()['Streaming']['overlayText'] = json_data['overlayText']
    saveConfig()
    return jsonify(success=True, message="Stream settings saved!")


@api.route("/saveRecordingSettings", methods=['POST'])
def save_recording_settings():
    json_data = request.get_json()
    getConfig()['Recording']['segmentSize'] = str(json_data['segmentSize'])
    getConfig()['Recording']['fps'] = str(json_data['fps'])
    getConfig()['Recording']['bitrate'] = str(json_data['bitrate'])
    getConfig()['Recording']['audio'] = json_data['audio']
    getConfig()['Recording']['exposure'] = json_data['exposure']
    getConfig()['Recording']['overlayText'] = json_data['overlayText']
    saveConfig()
    return jsonify(success=True, message="Stream settings saved!")


@api.route("/snapshot", methods=['GET'])
def get_snapshot():
    return send_file('/opt/rpic/images/snapshot.png', mimetype='image/png')


@api.route("/newsnapshot", methods=['POST'])
def new_snapshot():
    Stream.snap_shot()
    return jsonify(success=True, message="New snapshot taken!")
