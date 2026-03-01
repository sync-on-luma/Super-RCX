import time
from robot import motor

def main():

    #run motors 0 and 1 forward for 10 seconds
    motor.run(0, 100)
    motor.run(1, 100)
    time.sleep(10)

    #stop motors
    motor.stop(0)
    motor.stop(1)

    #reverse motor 1
    motor.setDirection(1, "Reverse")

    #run both motors backward for 15 seconds at 75% speed
    motor.run(0, -75)
    motor.run(1, 75)
    time.sleep(15)
