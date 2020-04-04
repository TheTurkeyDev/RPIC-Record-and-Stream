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
11. Setup config
    - TODO:
12. Setup as service for on startup
    - TODO: