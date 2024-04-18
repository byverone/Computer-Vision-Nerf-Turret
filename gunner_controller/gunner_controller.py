"""Recieves commands and sends out GPIO signals to control the nerf gun"""

# standard library imports
import time
import socket

# third party imports
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import RPi.GPIO as GPIO

kit = MotorKit()

# Constants

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

# Motor location
Z_AXIS = 180
Z_AXIS_LIMITS = [0, 360]


def move_motor(direction):
    if direction == "left":
        kit.stepper1.onestep(direction=stepper.FORWARD)  # style=stepper.DOUBLE
        return b"Moved left"
    elif direction == "right":
        kit.stepper1.onestep(direction=stepper.BACKWARD)  # style=stepper.DOUBLE
        return b"Moved right"
    return b"Invalid command"


def fire():
    GPIO.output(24, True)
    time.sleep(1)
    GPIO.output(24, False)
    return b"Fired"


def rev():
    GPIO.output(27, True)


def main():
    IP_ADDRESS = "0.0.0.0"  # listen on all available network interfaces
    PORT = 6969  # use any free port number

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the IP address and port
    sock.bind((IP_ADDRESS, PORT))

    # Listen for incoming connections
    sock.listen()

    # Wait for a client to connect
    conn, addr = sock.accept()

    rev()

    # Receive and process commands from the sender
    while True:
        data = conn.recv(1024)
        command = data.decode().strip()
        print("Received command:", command)
        # Process the command here (e.g. move a robot)
        if command == "fire":
            confirmation_message = fire()
        elif command == "left" or command == "right":
            confirmation_message = move_motor(command)
        elif command == "exit":
            conn.sendall(b"Exiting...")
            break
        else:
            confirmation_message = b"Invalid command"
        # send confirmation back to the sender
        conn.sendall(confirmation_message)
