# arcade_controller

Client installation:
curl https://raw.githubusercontent.com/lolnsw/arcade_controller/master/client/install.sh |  bash

Server installation:
0) Burn Raspbian Buster lite to sd card
1) cd /Volumes/boot (on MAC)
2) touch ssh
3) vi wpa_supplicant.conf:<BR>
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev<BR>
network={
    ssid="xxxxx"
    psk="xxxxx"
    key_mgmt=WPA-PSK
}

4) edit boot/config.txt and add
gpu_mem=16

5) boot raspberry and ssh to it
6) sudo raspi-config
   enable I2C
   enable Serial & no serial console

7) curl https://raw.githubusercontent.com/lolnsw/arcade_controller/master/server/install.sh| sudo bash
