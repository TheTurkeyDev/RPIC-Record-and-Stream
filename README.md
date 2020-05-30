# Installation
1. Flash Rasbian Lite OS onto SD card
2. Enable SSH and wifi - https://www.raspberrypi.org/documentation/configuration/wireless/headless.md
    - For the wpa_supplicant.conf set the contents to the below and you won't have to later
        ```
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=US

        network={
            ssid="<Your Home WiFi Name>"
            psk="<Your Home WiFi Password>"
            id_str="wifi"
        }

        network={
            ssid="<Name Your AP Connection>"
            mode=2
            key_mgmt=WPA-PSK
            psk="<Your AP Connection Password>"
            frequency=2437
            id_str="ap"
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
    - Via git:
        - Install git onto the raspberry `sudo apt install git`
        - Run `git clone https://github.com/Turkey2349/RPIC-Record-and-Stream.git /opt/rpic`
    - Via file transfer:
        - Copy and transfer files to `/opt/rpic`
9. Install FFmpeg with `sudo apt install ffmpeg`
10. Setup python
    - Run `sudo apt install python3-pip python3-gpiozero`
    - Install the python requirements `sudo pip3 install -r /opt/rpic/requirements.txt`
11. Setup for switching to AP Mode
    - Run `sudo apt install dnsmasq`



    - Run `sudo nano /etc/udhcpd.conf`
    - Edit `interface eth0` to `interface wlan0`
    - Run `sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`
    - File contents:
        ```
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=US

        network={
            ssid="<Your Home WiFi Name>"
            psk="<Your Home WiFi Password>"
            id_str="wifi"
        }

        network={
            ssid="<Name Your AP Connection>"
            mode=2
            key_mgmt=WPA-PSK
            psk="<Your AP Connection Password>"
            frequency=2437
            id_str="ap"
        }
        ```
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
