# Installation
1. Flash Rasbian Lite OS onto SD card
2. Enable SSH and wifi - https://www.raspberrypi.org/documentation/configuration/wireless/headless.md
    - Add a file named `ssh`
    - Add a file named `wpa_supplicant.conf`
    - For the `wpa_supplicant.conf`, set the contents to the below to establish and initial wifi connection to download what we need
        ```
        country=US
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1

        network={
            ssid="<Your Home WiFi Name>"
            psk="<Your Home WiFi Password>"
        }
        ```
3. Enable SSH over USB (Optional)
    - In `config.txt` append `dtoverlay=dwc2` to the end
    - In `cmdline.txt` append `modules-load=dwc2,g_ether` on the same line after `rootwait` with a single space between the two.
        - NOTE: if you see something like `quiet init=/usr/lib/raspi-config/init_resize.sh` after `rootwait`, just insert it between the two, but still making sure there is a single space between everything
4. Boot up Raspberry Pi
5. SSH into the Raspberry Pi
    - If setup over usb, it'll be `ssh pi@raspberrypi.local`
6. Run `sudo apt update`
7. Enable the camera (If using CSI camera port) with `sudo raspi-config` -> `Interfacing Options` -> `Camera`
7. Setup the project's folder
    - Run `sudo mkdir /opt/rpic`
    - Run `sudo chown pi:pi /opt/rpic`
8. Add the project code to the Raspberry
    - Install git onto the raspberry `sudo apt install git`
    - Run `git clone https://github.com/Turkey2349/RPIC-Record-and-Stream.git /opt/rpic`
9. Install FFmpeg with `sudo apt install ffmpeg`
10. Setup python
    - Run `sudo apt install python3-pip python3-gpiozero`
    - Install the python requirements `sudo pip3 install -r /opt/rpic/requirements.txt`
11. Setup for switching to AP Mode
    - Run `sudo nano /etc/wpa_supplicant/wpa_supplicant-wlan0.conf`
        - Set the filecontents to
        ```
        country=US                          
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev                           
        update_config=1                     
        ap_scan=1

        ### your hotspot ###        # has to be the first network section!
        network={
            priority=0              # Lowest priority, so wpa_supplicant prefers the other networks below 
            ssid="<accesspoint>"    # your access point's name 
            mode=2 
            key_mgmt=WPA-PSK 
            psk="<passphrase>"      # your access point's password 
            frequency=2462
        }

        ### your network(s) ###    
        network={
            ssid="<yourWifi>"
            psk="<passphrase>"
        } 
        ```
    - Run `sudo mkdir /opt/auto-hotspot`
    - Run `sudo git clone https://github.com/0unknwn/auto-hotspot.git /opt/auto-hotspot`
    - Run `cd /opt/auto-hotspot`
    - Run `sudo chmod +x auto-hotspot install.sh`
    - Run `sudo ./install.sh`
12. Setup as service for on startup
    - Run `sudo nano /etc/systemd/system/camera.service`
    - File contents:
        ```
        [Unit]
        Description=RPIC Record and Stream service
        After=multi-user.target

        [Service]
        Type=simple
        ExecStart=/usr/bin/python3 /opt/rpic/record.py

        [Install]
        WantedBy=multi-user.target
        ```
    - Run `sudo systemctl enable camera`
    - Run `sudo systemctl start camera`
