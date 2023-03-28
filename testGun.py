import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)

GPIO.output(27,True)
time.sleep(2)

for i in range(3):
    GPIO.output(24,True)
    #GPIO.output(13,True)
    time.sleep(2)
    GPIO.output(24,False)
    time.sleep(2)
    
GPIO.output(27,False)
GPIO.cleanup()