import configparser
from os import path
camera_types_list = ["CSI", "USB"]
config = None


def initConfig():
    global config
    config = configparser.ConfigParser()

    if path.exists('config.ini'):
        config.read('config.ini')
    else:
        config['General'] = {
            'videoType': 'Recording',
            'cameraType': 'CSI',
        }
        config['Network'] = {
            'ssid': 'test',
            'password': 'password123'
        }
        config['Recording'] = {
            'segmentSize': '1800',
            'fps': '30',
            'bitrate': '17000000',
            'exposure': 'sports',
            'audio': 'i2s',
            'overlayText': "TEST\nTest 2"
        }
        config['Streaming'] = {
            'streamLink': 'rtmp://live-iad05.twitch.tv/app/',
            'fps': '30',
            'bitrate': '5000000',
            'audio': 'i2s',
            'exposure': 'sports',
            'overlayText': "TEST\nTest 2"
        }
        saveConfig()


def getConfig():
    return config


def getRaspiMjpegConfig():
    keyValMap = {}
    # with open('/etc/raspimjpeg', 'r') as f:
    #     content = f.readlines()
    #     for line in content:
    #         if len(line) > 0 and not line.startswith('#'):
    #             parts = line.split()
    #             if len(parts) == 2:
    #                 keyValMap[parts[0]] = parts[1]
    return keyValMap


def saveConfig():
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
