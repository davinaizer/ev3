#!/usr/bin/env pybricks-micropython
 
from pybricks.ev3devices import (Motor)
from pybricks.parameters import (Port, SoundFile, Stop)
from pybricks import ev3brick as brick
from pybricks.tools import print
import time
import struct
import sys
import random

random.seed(0)

# Defining stick dead zone which is a minimum amount of stick movement
# from the center position to start motors
stick_deadzone = 5  # deadzone 5%

# Max steering angle for steering motor (in degrees)
max_steering_angle = 300

enable_xbox_detection = True
enable_ps_detection = True

# Clear program title
brick.display.clear()
brick.display.text("Rov3r+", (60, 20))

# Declare motors
try:
    first_motor = Motor(Port.A)
    second_motor = Motor(Port.D)
    steering_motor = Motor(Port.B)
    gearbox_motor = Motor(Port.C)
except:
    brick.display.text("Check motor cables", (0, 80))
    brick.sound.file(SoundFile.ERROR_ALARM)
    time.sleep(10)
    sys.exit(1)

# Constants
gamepad_xbox = 1
gamepad_ps = 2

# Initialize variables. 
# Assuming sticks are in the middle and triggera are not pressed when starting
left_stick_x = 0
left_stick_y = 0
right_trigger = 0
gear = 1

gamepad_device = None
gamepad_type = 0 # gamepad_xbox or gamepad_ps
# True if Xbox or False if PlayStation
xbox = None

def find_controller():
    """
    Checks device list by reading content of virtual file "/proc/bus/input/devices"
    looking for gamepad device.
    """
    global gamepad_type
    with open("/proc/bus/input/devices", "r") as fp:
        line = fp.readline()
        while line:
            if enable_xbox_detection and line.startswith("N: Name=") and line.find("Xbox") > -1:
                gamepad_type = gamepad_xbox
            if enable_ps_detection and line.startswith("N: Name=") and line.find("PLAYSTATION") > -1 and line.find("Motion") == -1:
                gamepad_type = gamepad_ps
            if gamepad_type > 0 and line.startswith("H: Handlers="):
                line = line[len("H: Handlers="):]
                pb = line.find("event")
                pe = line.find(" ", pb)
                return line[pb:pe]
            line = fp.readline()
    return None

def transform_stick(value):
    """
    Transform range 0..max to -100..100, remove deadzone from the range
    """
    max = 65535 if xbox else 255
    half = int((max + 1) / 2)
    deadzone = int((max + 1) / 100 * stick_deadzone)
    value -= half
    if abs(value) < deadzone:
        value = 0
    elif value > 0:
        value = (value - deadzone - 1) / (half - deadzone) * 100
    else:
        value = (value + deadzone) / (half - deadzone) * 100
    return value

def play_horn():
    """
    Plays a horn sound randomly selected from two available sounds
    """
    if random.randint(1, 2) == 1:
        brick.sound.file(SoundFile.HORN_1)
    else:
        brick.sound.file(SoundFile.HORN_2)

def play_sound_effect():
    """
    Plays a random sound effect
    """
    effect = random.randint(1, 4)
    if effect == 1:
        brick.sound.file(SoundFile.AIR_RELEASE)
    elif effect == 2:
        brick.sound.file(SoundFile.AIRBRAKE)
    elif effect == 3:
        brick.sound.file(SoundFile.LASER)
    elif effect == 4:
        brick.sound.file(SoundFile.SONAR)

def calibrate_motors():
    """
    Calibrate gearbox motor: switch to first gear.
    Calibrate steering motor: find the range by steering full to the left and full to the right,
    then center the steering.
    """
    global max_steering_angle

    gearbox_motor.run_until_stalled(360, Stop.COAST, 50)
    gearbox_motor.run_angle(100, -20) # unstress the switcher
    gearbox_motor.reset_angle(0)

    steering_motor.run_until_stalled(360, Stop.COAST, 80)
    steering_motor.reset_angle(0)
    steering_motor.run_until_stalled(-360, Stop.COAST, 80)
    max_steering_angle = steering_motor.angle() / 2
    steering_motor.run_target(360, max_steering_angle)
    steering_motor.reset_angle(0)
    max_steering_angle *= 0.90  # limit max steering angle a little

# Find the gamepad:
# /dev/input/event2 is the usual file handler for the gamepad.
# The contents of /proc/bus/input/devices lists all devices.
gamepad_device = find_controller()
#print("Gamepad device:", gamepad_device, ", type:", gamepad_type)

xbox = gamepad_type == gamepad_xbox

if gamepad_device is None:
    brick.display.text("Gamepad not found", (0, 80))
    brick.sound.file(SoundFile.ERROR_ALARM)
    time.sleep(10)
    sys.exit(1)

brick.display.text(("Xbox" if xbox else "PS") + " gamepad functions:", (0, 40))
brick.display.text("Left Stick: movement", (0, 55))
brick.display.text(("RB/LB" if xbox else "R1/L1") + ": gear up/down", (0, 65))
brick.display.text(("RT" if xbox else "R2") + ": steer. speed bump", (0, 75))
brick.display.text(("X" if xbox else "/\\") + ": horn", (0, 85))
brick.display.text(("Y" if xbox else "[]") + ": sound effect", (0, 95))

infile_path = "/dev/input/" + gamepad_device
in_file = open(infile_path, "rb")

calibrate_motors()

# Read from the file
# long int, long int, unsigned short, unsigned short, long int
FORMAT = 'llHHl'
EVENT_SIZE = struct.calcsize(FORMAT)
event = in_file.read(EVENT_SIZE)

while event:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

    if ev_type == 3 or ev_type == 1:

        if ev_type == 3 and code == 0: # Left Stick Horz. Axis
            left_stick_x = transform_stick(value)

        elif ev_type == 3 and code == 1: # Left Stick Vert. Axis
            left_stick_y = transform_stick(value)

        elif xbox and ev_type == 3 and code == 9: # Xbox Right Trigger
            right_trigger = value / 1024

        elif not xbox and ev_type == 3 and code == 5: # PS R2 paddle
            right_trigger = value / 256

        elif ev_type == 1 and code == 311 and value == 1: # RB pressed
            gear = min(gear + 1, 4)

        elif ev_type == 1 and code == 310 and value == 1:  # LB pressed
            gear = max(gear - 1, 1)

        elif ev_type == 1 and code == 307 and value == 1:  # X pressed
            play_horn()

        elif ev_type == 1 and code == 308 and value == 1:  # Y pressed
            play_sound_effect()

        # Calculate motor power and angles
        propulsion_power = left_stick_y * (1 + right_trigger)
        steering_angle = left_stick_x * max_steering_angle / 100
        gearing_angle = - (gear - 1) * 20 / 12 * 90

        #print(left_stick_y, left_stick_x, gear, propulsion_power, steering_angle, gearing_angle)

        # Set motor power and angles
        first_motor.dc(propulsion_power)
        second_motor.dc(propulsion_power)
        steering_motor.track_target(steering_angle)
        gearbox_motor.track_target(gearing_angle)

    # Finally, read another event
    event = in_file.read(EVENT_SIZE)

in_file.close()