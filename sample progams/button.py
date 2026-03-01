from robot import led, button

def main():
    while True:
    
        #check btton 0 state and set LED state to match
        if button.getState(0) == True:
            led.on(0)
        else:
            led.off(0)
        
        #check btton 1 state and set LED state to match
        if button.getState(1) == True:
            led.on(1)
        else:
            led.off(1)
