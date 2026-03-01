import time
from robot import motor
from robot import sensor

def main():
    while True:
        
        #run motor 0 while touch sensor D0 is pressed in
        if sensor.touchValue("D0") == True:
            motor.run(0, 100)
        else:
            motor.stop(0)
        
        #change motor 1's speed to reflect the current light value
        speed = sensor.lightValue("A0")
        print(speed)
        motor.run(1, speed)
