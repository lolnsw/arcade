#!/usr/bin/python
import RPi.GPIO as GPIO
import serial
import time
import threading
import signal
import datetime
import sys
import subprocess
from Adafruit_LED_Backpack import SevenSegment


### OPTIONS

DEFAULT_COUNTDOWN = 120 # Initial countdown value (after the pi starts)
CLOCK_ON_SECONDS = 120 # if the time remaining is less than this value, the clock is turned on
TIME_ALTERATION = 15 # time to add or remove from the countdown
SESSION_END_HARD = False # If true, shutdown both client and server pis when the countdown reaches 0. If false, the TV screen will be turned off instead

############


class ControllerClient:
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/serial0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def send_msg(self, msg):
        self.ser.write(msg + "\n")
        self.ser.write("hi\n")

class AdminWatcher:
    def __init__(self):
        self.kill_received = False
        self.ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.2
	)
        self.admin_countdown = 0
        self.admin_mode = False
        self.admin_mode_previous = False

    def button_push(self, button):
        if self.admin_mode:
            self.reset_admin_countdown()

    def reset_admin_countdown(self):
        self.admin_countdown = 5
        #print("reset admin countdown")

    def add_admin_countdown(self, sec):
        self.admin_countdown = self.admin_countdown + sec

    def del_admin_countdown(self, sec):
        self.admin_countdown = self.admin_countdown - sec

    def set_admin_mode(self, mode):
        if mode:
            #print("Entering Admin mode")
            self.reset_admin_countdown()
            GPIO.output(ADD_TIME_LED,GPIO.HIGH)
            GPIO.output(DEL_TIME_LED,GPIO.HIGH)
            self.admin_mode = True
        else:
            #print("Exiting Admin mode")
            GPIO.output(ADD_TIME_LED,GPIO.LOW)
            GPIO.output(DEL_TIME_LED,GPIO.LOW)
            self.admin_mode = False

    def run(self):
        while not self.kill_received:
            x=self.ser.readline()
            if "MSG: ADMIN" in x:
                self.set_admin_mode(True)
                disp.signal("admin_mode", True)


            self.del_admin_countdown(0.20)
            #time.sleep(0.20)
            # print("Admin Countdown: "+str(self.admin_countdown))
            # print("Admin mode: "+str(self.admin_mode))
            if self.admin_countdown <=0:
                self.admin_countdown = 0
                self.admin_mode = False
                if self.admin_mode != self.admin_mode_previous:
                    disp.signal("admin_mode", False)
                self.set_admin_mode(False)

            self.admin_mode_previous = self.admin_mode


class Countdown:
    def __init__(self):
        self._running = True
        self._seconds = DEFAULT_COUNTDOWN
        self.seconds_previous = DEFAULT_COUNTDOWN
        self.kill_received = False
        self.session_live = True

    def add_time(self, sec):
        self._seconds = self._seconds + sec
        print("New ct: "+str(self._seconds))

    def del_time(self, sec):
        self._seconds = self._seconds - sec
        if self._seconds < 0:
            self._seconds = 0
        #print("New ct: "+str(self._seconds))

    def button_push(self, button):
        if button == "add" and aw.admin_mode:
            self.add_time(TIME_ALTERATION)
        elif button == "del" and aw.admin_mode:
            self.del_time(TIME_ALTERATION)
        elif button == "coin":
            self.add_time(TIME_ALTERATION)
            disp.signal("temporary_on", 5)

    def run(self):
        while not self.kill_received:
            time.sleep(1)
            self.del_time(1)
            #self._seconds -= 1

            nb_minutes = int(self._seconds/60)
            nb_minutes_d1 = int(nb_minutes/10)
            nb_minutes_d2 = nb_minutes % 10

            nb_sec = self._seconds % 60
            nb_sec_d1 = int(nb_sec/10)
            nb_sec_d2 = nb_sec % 10

            disp.set_digits(nb_minutes_d1, nb_minutes_d2, nb_sec_d1, nb_sec_d2)

            #print("                   [prev:"+str(self.seconds_previous)+"]["+str(self._seconds)+"]")
            if self.seconds_previous >= CLOCK_ON_SECONDS and self._seconds < CLOCK_ON_SECONDS:
                print("Sending countown low")
                disp.signal("countdown_low", True)


            if self._seconds > 0:
                self.session_live = True

            if self._seconds <=0 and self.session_live:
                # Ending session
                self.session_live = False

                if SESSION_END_HARD:
                    # Stop raspberry
                    print("Stopping Client Raspberry")
                    disp.signal("end_session","")
                    cc.send_msg("MSG: SHUTDOWN")
                    print("Stopping Server Raspberry")
                    cmd = "sudo shutdown -h now"
                    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    # Switch Screen off via CEC
                    print("Switching TV off")
                    disp.signal("end_session","")

            self.seconds_previous = self._seconds


class Display:
    def __init__(self):
        self.segment = SevenSegment.SevenSegment(address=0x70)
        self.segment.begin()
        self.kill_received = False
        self.screen_on = True

        self.admin_received = False
        self.admin_received_token_consumed = False

        self.admin_expired = False
        self.admin_expired_token_consumed= False

        self.countdown_passed_through_treshold = False
        self.countdown_passed_through_treshold_token_consumed = False

        self.sig_admin_mode = False
        self.sig_admin_mode_read = True

        self.sig_countdown_low = False
        self.sig_countdown_low_read = True

        self.temporary_on = -1

    def on(self):
        self.screen_on = True

    def off(self):
        self.screen_on = False

    def force_off(self):
        self.segment.clear()
        self.segment.write_display()

    def signal(self, sig, value):
        print("received signal")
        if sig == "admin_mode":
            print("Disp received admin_mode:"+str(value))
            self.sig_admin_mode = value
            self.sig_admin_mode_read = False
        elif sig == "countdown_low":
            print("Disp received low countdown")
            self.sig_countdown_low = value
            self.sig_countdown_low_read = False
        elif sig == "end_session":
            self.off()
        elif sig =="temporary_on":
            self.temporary_on = value
            self.on()

    def button_push(self, button):
        if button == "add":
            print("Switching screen on")
            self.on()
        elif button == "del":
            print("Switching screen off")
            self.off()

    def set_digits(self, d0, d1, d2, d3):
        #print("rcv new digits " + str(d0) + str(d1) +str(d2) +str(d3))
        self.segment.clear()
        self.segment.set_digit(0,d0)
        self.segment.set_digit(1,d1)
        self.segment.set_digit(2,d2)
        self.segment.set_digit(3,d3)
        self.segment.set_colon(1)

    def run(self):
        while not self.kill_received:
            # Wait a quarter second (less than 1 second to prevent colon blinking
            time.sleep(0.25)

            if self.temporary_on >= 0:
                self.temporary_on = self.temporary_on - 0.25
                if self.temporary_on < 0:
                    self.off()


            if not self.sig_admin_mode_read:
                if self.sig_admin_mode:
                    self.on()
                    self.sig_admin_mode_read = True
                else:
                    self.off()
                    self.sig_admin_mode_read = True

            if not self.sig_countdown_low_read:
                if self.sig_countdown_low:
                    self.on()
                    self.sig_countdown_low_read = True

            if self.screen_on:
                #print("Write disp")
                self.segment.write_display()
            else:
                #print("Screen off")
                self.segment.clear()
                self.segment.write_display()





def handler_SIGTSTP(signum, fame):
    print("Received SIGTSTP, exiting program")
    exit()
signal.signal(signal.SIGTSTP, handler_SIGTSTP)

print("Initializing admin display")
aw = AdminWatcher()
t3 = threading.Thread(target=aw.run)
t3.start()

try:
    ADD_TIME = 13
    DEL_TIME = 19
    ADD_TIME_LED = 5
    DEL_TIME_LED = 6
    COIN = 23

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ADD_TIME, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(DEL_TIME, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(COIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(ADD_TIME_LED,GPIO.OUT)
    GPIO.setup(DEL_TIME_LED,GPIO.OUT)

    cc = ControllerClient()

    print("Initializing display")
    disp = Display()
    t1 = threading.Thread(target=disp.run)
    t1.start()

    print("Initializing countdown")
    ctdn = Countdown()
    t2 = threading.Thread(target=ctdn.run)
    t2.start()



    def handle(pin):
        if pin == COIN:
            print("Coin inserted")
            ctdn.button_push("coin")

        if pin == ADD_TIME or pin == DEL_TIME:
            if GPIO.input(ADD_TIME) and GPIO.input(DEL_TIME) and aw.admin_mode:
                print("Both buttons pressed")
                # Let's switch Recalbox mode
                cc.send_msg("MSG: ADMIN")
                aw.button_push("both")

            elif GPIO.input(ADD_TIME):
                print("Button Add time pressed")
                ctdn.button_push("add")
                aw.button_push("add")
                disp.button_push("add")

            elif GPIO.input(DEL_TIME):
                print("Button Del time pressed")
                ctdn.button_push("del")
                aw.button_push("del")
                disp.button_push("del")

    GPIO.add_event_detect(ADD_TIME, GPIO.BOTH, callback=handle, bouncetime=500)
    GPIO.add_event_detect(DEL_TIME, GPIO.BOTH, callback=handle, bouncetime=500)
    GPIO.add_event_detect(COIN, GPIO.BOTH, callback=handle, bouncetime=500)

    while True:
        time.sleep(1)



except KeyboardInterrupt:
    print("Keyboard Interrupt")

except:
    e = sys.exc_info()[0]
    print( "<p>Error: %s</p>" % e)

finally:
    print("Finally exiting")
    disp.force_off()
    ctdn.kill_received = True
    aw.kill_received = True
    disp.kill_received = True
    time.sleep(1.5) # give time to the threads to gracefully stop
    GPIO.cleanup()
