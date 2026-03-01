import time
from robot import motor, drive

def main():
    #set up drive motors
    motor.setDriveMotors(0, 1) 
    
    while True:
        #drive forward for 3 seconds
        drive.straight(75)
        time.sleep(2)
        
        #turn right
        drive.turn("Right", 100)
        time.sleep(4)
