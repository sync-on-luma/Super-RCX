import time
from robot import speaker

def main():
    
    #play scale
    speaker.playNote("C", 0.5)
    speaker.playNote("D", 0.5)
    speaker.playNote("E", 0.5)
    speaker.playNote("F", 0.5)
    speaker.playNote("G", 0.5)
    speaker.playNote("A", 0.5)
    speaker.playNote("B", 0.5)
    speaker.playNote("C", 0.5, 5)
    
    #pause for 2 seconds
    time.sleep(2)
    
    #play 50Hz tone for 3 seconds
    speaker.playTone(50, 3)
