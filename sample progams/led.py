import time
from robot import led

def main():
    
    while True:
        #set LED0 color
        led.setColor(0, "Blue")
        
        #start LED1 fade
        led.fadeColor(1, "Blue", "Yellow", 4)
        
        #switch LED0  color
        led.setColor(0, "Yellow")
        
        #reverse LED1 fade 
        led.fadeColor(1, "Yellow", "Blue", 4)
