#!/usr/bin/python
import time
import serial
import subprocess


try:

    ser = serial.Serial(
        port='/dev/serial0',
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

    # on start-up, default to kids mode
    cmd = "sed -i 's/emulationstation.menu=.*/emulationstation.menu=none/'  /recalbox/share/system/recalbox.conf"
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd = "sed -i 's/emulationstation.hidesystemview=.*/emulationstation.hidesystemview=1/'  /recalbox/share/system/recalbox.conf"
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    while (True):
        x=ser.readline()
        if x == "MSG: ADMIN":
            output = subprocess.Popen(['grep',"emulationstation.menu",'/recalbox/share/system/recalbox.conf'], stdout=subprocess.PIPE).communicate()[0]
            marray = output.split("=")
            mode = marray[1]
            print("Current modei: "+mode)
            if mode.startswith("default"):
                print("Changing mode to nomenu")
                cmd = "sed -i 's/emulationstation.menu=.*/emulationstation.menu=none/'  /recalbox/share/system/recalbox.conf"
                subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmd = "sed -i 's/emulationstation.hidesystemview=.*/emulationstation.hidesystemview=1/'  /recalbox/share/system/recalbox.conf"
                subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                print("Changing mode to default")
                cmd = "sed -i 's/emulationstation.menu=.*/emulationstation.menu=default/'  /recalbox/share/system/recalbox.conf"
                subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmd = "sed -i 's/emulationstation.hidesystemview=.*/emulationstation.hidesystemview=0/'  /recalbox/share/system/recalbox.conf"
                subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # reload emulation station
            cmd = "/etc/init.d/S31emulationstation restart"
            subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


except KeyboardInterrupt:
    print("Exiting program")