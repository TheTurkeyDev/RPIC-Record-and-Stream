# Installation
1. Flash Rasbian Lite OS onto SD card
2. Enable SSH and wifi - https://www.raspberrypi.org/documentation/configuration/wireless/headless.md
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
    - Install the python requirements `pip3 install -r /opt/rpic/requirements.txt`
11. Setup for switching to AP Mode
    - For more information on the process and instructions see: https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md
    - Run `sudo apt install dnsmasq hostapd`
    - Run `sudo systemctl stop dnsmasq`
    - Run `sudo systemctl stop hostapd`
    - Run `sudo nano /etc/dhcpcd.conf`
        - At the end of the file add
            ```
            interface wlan0
                static ip_address=192.168.4.1/24
                nohook wpa_supplicant
            ```
    - Run `sudo service dhcpcd restart`
    - Run `sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig`
    - Run `sudo nano /etc/dnsmasq.conf`
        - Set the file's contents to
            ```
            interface=wlan0      # Use the require wireless interface - usually wlan0
            dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
            ```
    - Run `sudo systemctl start dnsmasq`
    - Run `sudo nano /etc/hostapd/hostapd.conf`
        - Set the file's contents to
            ```
            interface=wlan0
            driver=nl80211
            ssid=<Name your network!>
            hw_mode=g
            channel=7
            wmm_enabled=0
            macaddr_acl=0
            auth_algs=1
            ignore_broadcast_ssid=0
            wpa=2
            wpa_passphrase=<Secure your network with a password!>
            wpa_key_mgmt=WPA-PSK
            wpa_pairwise=TKIP
            rsn_pairwise=CCMP
            ```
    - Run `sudo nano /etc/default/hostapd`
    - Find the line with `#DAEMON_CONF` and replace it with `DAEMON_CONF="/etc/hostapd/hostapd.conf"`
    - Run `sudo systemctl unmask hostapd`
    - Run `sudo systemctl enable hostapd`
    - Run `sudo systemctl start hostapd`
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
