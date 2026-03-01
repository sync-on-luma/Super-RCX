import os
import machine
from machine import Pin, I2C, PWM, ADC
import time
import math
import statistics
from neopixel import NeoPixel
import micropython
import ssd1306
import predefs
import graphics
from DIYables_MicroPython_Keypad import Keypad
import _thread

micropython.alloc_emergency_exception_buf(100)

#initalize LEDs
LED = NeoPixel(Pin(23, Pin.OUT), 2)
LED[0] = (0,0,0)
LED[1] = (0,0,0)
LED.write()

#initalize speaker
SPEAKER = Pin(22, Pin.OUT)

#initalize buttons
BUTTON = [
    Pin(20, Pin.IN),
    Pin(21, Pin.IN),
    ]

#initalize keypad
row_pins = [4, 5]
column_pins = [6, 7]
keymap = ['UP', 'DOWN', 'SELECT', 'CANCEL']
KEYPAD = Keypad(keymap, row_pins, column_pins, 2, 2)

#initalize display
i2c = I2C(sda=Pin(16), scl=Pin(17))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

#initalize motors
M1A = PWM(Pin(8), freq=10000, duty_u16=0)
M1B = PWM(Pin(9), freq=10000, duty_u16=0)
M2A = PWM(Pin(10), freq=10000, duty_u16=0)
M2B = PWM(Pin(11), freq=10000, duty_u16=0)
M3A = PWM(Pin(12), freq=10000, duty_u16=0)
M3B = PWM(Pin(13), freq=10000, duty_u16=0)
M4A = PWM(Pin(14), freq=10000, duty_u16=0)
M4B = PWM(Pin(15), freq=10000, duty_u16=0)
M5A = PWM(Pin(2), freq=10000, duty_u16=0)
M5B = PWM(Pin(3), freq=10000, duty_u16=0)
M6A = PWM(Pin(0), freq=10000, duty_u16=0)
M6B = PWM(Pin(1), freq=10000, duty_u16=0)
MOTOR = [
    [M1A, M1B, "Forward"],
    [M2A, M2B, "Forward"],
    [M3A, M3B, "Forward"],
    [M4A, M4B, "Forward"],
    [M5A, M5B, "Forward"],
    [M6A, M6B, "Forward"],
    ]

#initalize sensors
SENSOR = [
    [29, 1],
    [28, 1],
    [27, 1],
    [26, 1],
    Pin(19, Pin.IN, Pin.PULL_UP),
    Pin(18, Pin.IN, Pin.PULL_UP),
    ]
try:
    with open(".calibration_data", "r") as f:
        lines = f.readlines()
        index = 0
        for line in lines:
            if line != "" and index < 4:
                SENSOR[index][1] = line
                index = index + 1
        f.close()
except: pass


class speaker_class:
    def playTone(self, freq, dur):
        freq = 1 / (freq * 2)
        ms = dur*1000
        deadline = time.ticks_add(time.ticks_ms(), int(ms))
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            SPEAKER.value(1)
            time.sleep(freq)
            SPEAKER.value(0)
    
    def playNote(self, note, dur, *args):
        try:
            octave = args[0]
            if octave < 1 or octave > 8:
               raise ValueError("playNote()\nInvalid octave") 
        except IndexError:
            octave = 4
            
        for n in predefs.notes:
            if note == n[0]:
                self.playTone(n[1] * 2 ** octave, dur)
                time.sleep(0.01)
                break
            elif n[0] == predefs.notes[len(predefs.notes) - 1][0]:
                raise ValueError("playNote()\nInvalid note")
        
class button_class:
    def getState(self, index):
        if index > -1 and index < 2:
            if BUTTON[index].value() == 0:
                return True
            else:
                return False
        else:
            raise ValueError("getState()\nInvalid button")

class led_class:
    def setColor(self, index, color):
        if index > -1 and index < 2:
            for c in predefs.colors:
                if color == c[0]:
                    LED[index] = c[1]
                    LED.write()
                    break
                elif c[0] == predefs.colors[len(predefs.colors) - 1][0]:
                    raise ValueError("led.setColor()\nInvalid color")
        else:
            raise ValueError("led.setColor()\nInvalid LED")
    
    def fadeColor(self, index, color1, color2, *args):
        try:
            speed = args[0]
        except IndexError:
            speed = 1
        
        if index > -1 and index < 2:
            for c in predefs.colors:
                if color1 == c[0]:
                    color1 = c[1]
                if color2 == c[0]:
                    color2 = c[1]
                if type(color1) is tuple and type(color2) is tuple:
                    break
                elif c[0] == predefs.colors[len(predefs.colors) - 1][0]:
                    raise ValueError("led.fadeColor()\nInvalid color(s)")

            steps = 4900 * speed
            RS = (color2[0] - color1[0]) / steps
            GS = (color2[1] - color1[1]) / steps
            BS = (color2[2] - color1[2]) / steps
            R = color1[0] 
            G = color1[1] 
            B = color1[2]
            RA = R
            GA = G
            BA = B
            for step in range(steps):
                LED[index] = (R, G, B)
                LED.write()
                RA = RA + RS
                GA = GA + GS
                BA = BA + BS
                R = int(RA)
                G = int(GA)
                B = int(BA)
                #print(str(R) + " " + str(B) + " " + str(G))
        else:
            raise ValueError("led.fadeColor()\nInvalid LED")
    
    def on(self, index):
        if index > -1 and index < 6:
            LED[index] = (255, 255, 255)
            LED.write()
        else:
            raise ValueError("led.on()\nInvalid LED")
    
    def off(self, index):
        if index > -1 and index < 6:
            LED[index] = (0, 0, 0)
            LED.write()
        else:
            raise ValueError("led.off()\nInvalid LED")

class motor_class:
    def setDirection(self, index, direction):
        if index > -1 and index < 6:
            if direction == "Forward" or direction == "Reverse":
                MOTOR[index][2] = direction
            else:
                raise ValueError("Invalid motor\ndirection")
        else:
            raise ValueError("setDirection()\nInvalid motor")
            
    def getDirection(self, index):
        if index > -1 and index < 6:
            return MOTOR[index][2]
        else:
            raise ValueError("getDirection()\nInvalid motor")

    def getSpeed(self, index):
        if index > -1 and index < 6:
            return int(((MOTOR[index][0].duty_u16() + MOTOR[index][1].duty_u16()) * 100) / 65535)
        raise ValueError("getSpeed()\nInvalid motor")

    def stop(self, index):
        if index > -1 and index < 6:
            MOTOR[index][0].duty_u16(0)
            MOTOR[index][1].duty_u16(0)
        else:
            raise ValueError("motor.stop()\nInvalid motor")

    def run(self, index, speed):
        if index > -1 and index < 6:
            self.stop(index)
            if speed > 0:
                pwm = 0
            elif speed < 0:
                pwm = 1
            else:
                self.stop(index)
                return
            if MOTOR[index][2] == "Reverse":
                pwm = abs(pwm - 1)
            duty = int((abs(speed) * 65535) / 100)
            MOTOR[index][pwm].duty_u16(duty)
        else:
            raise ValueError("motor.run()\nInvalid motor")
    
    def setDriveMotors(self, L, R):
        try:
            if L < 6 and L > -1:
                drive.DRIVE_L = L
            else:
                raise ValueError("Left drive\nmotor invalid")
            if R < 6 and R > -1:
                drive.DRIVE_R = R
            else:
                raise ValueError("Right drive\nmotor invalid")
        except Exception as ex:
            raise ValueError(str(type(ex).__name__) + "\nin\nsetDriveMotors()")
        
class drive_class:
    DRIVE_L = -1
    DRIVE_R = -1
    
    def stop(self):
        if self.DRIVE_L > -1 and self.DRIVE_L < 6 and self.DRIVE_R > -1 and self.DRIVE_R < 6:
            motor.stop(self.DRIVE_L)
            motor.stop(self.DRIVE_R)
        else:
            raise ValueError("Drive motor(s)\nnot assigned")
    
    def straight (self, speed):
        if self.DRIVE_L > -1 and self.DRIVE_L < 6 and self.DRIVE_R > -1 and self.DRIVE_R < 6:
            if abs(speed) != 0:
                #self.stop()
                motor.run(self.DRIVE_L, speed)
                motor.run(self.DRIVE_R, speed)
            else:
                self.stop()
        else:
            raise ValueError("Drive motor(s)\nnot assigned")
    
    
    def turn(self, direction, speed):
        if self.DRIVE_L > -1 and self.DRIVE_L < 6 and self.DRIVE_R > -1 and self.DRIVE_R < 6:
            if direction == "L" or direction == "Left":
                #self.stop()
                motor.run(self.DRIVE_L, -speed)
                motor.run(self.DRIVE_R, speed)
            elif direction == "R" or direction == "Right":
                #self.stop()
                motor.run(self.DRIVE_L, speed)
                motor.run(self.DRIVE_R, -speed)
            else:
                raise ValueError("Turn direction\nis not valid")
        else:
            raise ValueError("Drive motor(s)\nnot assigned")

class sensor_class:
    pulse = 0.0029
    
    def getPin(self, sensor):
        if type(sensor) is int:
            return sensor
        if sensor[0:1] == "A":
            return int(sensor[1:2])
        elif sensor[0:1] == "D":
            return int(sensor[1:2]) + 4
    
    def rawValue(self, sensor):
        index = self.getPin(sensor)
        if index > 3 and index < 6:
            value = abs(SENSOR[index].value() - 1)
        elif index > -1 and index < 4:
            adc = Pin(SENSOR[index][0], Pin.OUT)
            ratio = SENSOR[index][1]
            if type(ratio) is str:
                ratio = float(ratio[:-1])
            adc.high()
            time.sleep(self.pulse)
            adc.low()
            adc = ADC(Pin(SENSOR[index][0], Pin.IN, Pin.PULL_UP))
            r = adc.read_u16()
            r = int(r * ratio)
            if r > 65535:
                r = 65535
            r = (r >> 8) << 8
            value = abs(((r / 65535) * 100) - 100)
        else:
            raise ValueError("rawValue()\nInvalid sensor")
        return value
    
    def touchValue(self, sensor, *args):
        mode = "Digital"
        try:
            if args[0] == "Analog":
                mode = "Analog"
        except IndexError: pass
    
        sensor = self.getPin(sensor)
        if sensor > -1 and sensor < 6:
            value = self.rawValue(sensor)
            if mode == "Digital":
                if value > 50 or value == 1:
                    value = 1
                else:
                    value = 0
            value = int(value)
            return value
        else:
            raise ValueError("touchValue()\nInvalid sensor")
    
    def lightValue(self, sensor):
        sensor = self.getPin(sensor)
        if sensor > -1 and sensor < 6:
            
            values = [self.rawValue(sensor), self.rawValue(sensor), self.rawValue(sensor), self.rawValue(sensor)]
            
            for v in range(len(values)):
                if values[v] > 14:
                    values[v] = 14
                elif values[v] < 0.4:
                    values[v] = 0
                values[v] = int(values[v] * 7.14)
                
            value = int(statistics.median(values))
            return value
        else:
            raise ValueError("lightValue()\nInvalid sensor")
    
    def calibrate(self):
        try:
            os.remove(".calibration_data")
        except OSError: pass
        
        text = ""
        for i in range(4):
            drawWindow("Please Wait", "Calibrating:\nSensor A" + str(i))
            buff = []
            while len(buff) < 1000:
                adc = Pin(SENSOR[i][0], Pin.OUT)
                adc.high()
                time.sleep(self.pulse)
                adc.low()
                adc = ADC(Pin(SENSOR[i][0], Pin.IN, Pin.PULL_UP))
                r = adc.read_u16()
                buff.append(r)
            ratio = 65535 / statistics.median(buff)
            SENSOR[i][1] = ratio
            text = text + str(ratio) + "\n"
            
        drawWindow("", "Done")
        with open(".calibration_data", "w") as output:
            output.write(text)
            output.close()
        drawMenu()
        
    
    #def lightValue:
        
                    
speaker = speaker_class()
button = button_class()
led = led_class()
motor = motor_class()
drive = drive_class()
sensor = sensor_class()

def keyClick(key):
    if key == "UP" or key == "DOWN":
        speaker.playTone(60, 0.03)
        speaker.playTone(300, 0.01)
        speaker.playTone(600, 0.01)
    elif key == "SELECT":
        speaker.playTone(500, 0.01)
        speaker.playTone(200, 0.01)
    elif key == "CANCEL":
        speaker.playTone(200, 0.03)
        speaker.playTone(600, 0.01)
        speaker.playTone(1000, 0.01)

#initialize menu
menu = {}
def initMenu():
    global menu
    menu[0] = {}
    menu[0]["Title"] = "Menu"
    menu[0]["Items"] = {}
    menu[0]["Items"][0] = {}
    menu[0]["Items"][0]["Name"] = "Programs"
    menu[0]["Items"][0]["Link"] = 1
    menu[0]["Items"][1] = {}
    menu[0]["Items"][1]["Name"] = "Sensors"
    menu[0]["Items"][1]["Link"] = 2
    menu[0]["Items"][2] = {}
    menu[0]["Items"][2]["Name"] = "Motors"
    menu[0]["Items"][2]["Link"] = 3
    menu[0]["Items"][3] = {}
    menu[0]["Items"][3]["Name"] = "LEDs"
    menu[0]["Items"][3]["Link"] = 4
    menu[0]["Items"][4] = {}
    menu[0]["Items"][4]["Name"] = "Buttons"
    menu[0]["Items"][4]["Link"] = 5
    menu[1] = {}
    menu[1]["Title"] = "Programs"
    menu[1]["Items"] = {}
    menu[2] = {}
    menu[2]["Title"] = "Sensors"
    menu[2]["Items"] = {}
    for i in range(4):
        menu[2]["Items"][i] = {}
        menu[2]["Items"][i]["Name"] = "Sensor A" + str(i)
        menu[2]["Items"][i]["Link"] = 20 + i
        menu[20 + i] = {}
        menu[20 + i]["Title"] = "Sensor A" + str(i)
        menu[20 + i]["Items"] = {}
        menu[20 + i]["Items"][0] = {}
        menu[20 + i]["Items"][0]["Name"] = "Touch"
        menu[20 + i]["Items"][1] = {}
        menu[20 + i]["Items"][1]["Name"] = "Light"
        #menu[20 + i]["Items"][2] = {}    
        # menu[20 + i]["Items"][2]["Name"] = "Rotation"
        # menu[20 + i]["Items"][3] = {}
        # menu[20 + i]["Items"][3]["Name"] = "Temperature"
        # menu[20 + i]["Items"][4] = {}
        # menu[20 + i]["Items"][4]["Name"] = "Raw"
        menu[20 + i]["Items"][2] = {}
        menu[20 + i]["Items"][2]["Name"] = "Raw"
        menu[20 + i]["Sensor"] = "A" + str(i)
    for i in range(2):
        menu[2]["Items"][i + 4] = {}
        menu[2]["Items"][i + 4]["Name"] = "Sensor D" + str(i)
        menu[2]["Items"][i + 4]["Link"] = 24 + i
        menu[24 + i] = {}
        menu[24 + i]["Title"] = "Sensor D" + str(i)
        menu[24 + i]["Items"] = {}
        menu[24 + i]["Items"][0] = {}
        menu[24 + i]["Items"][0]["Name"] = "Touch"
        menu[24 + i]["Items"][1] = {}
        menu[24 + i]["Items"][1]["Name"] = "Raw"
        menu[24 + i]["Sensor"] = "D" + str(i)
    menu[2]["Items"][6] = {}
    menu[2]["Items"][6]["Name"] = "Calibrate"
    menu[2]["Items"][6]["Link"] = 29
    menu[3] = {}
    menu[3]["Title"] = "Motors"
    menu[3]["Items"] = {}
    for i in range(6):
        menu[3]["Items"][i] = {}
        menu[3]["Items"][i]["Name"] = "Motor " + str(i)
        menu[3]["Items"][i]["Link"] = 30 + i
        menu[30 + i] = {}
        menu[30 + i]["Title"] = "Motor " + str(i)
        menu[30 + i]["Items"] = {}
        menu[30 + i]["Items"][0] = {}
        menu[30 + i]["Items"][0]["Name"] = "Forward"
        menu[30 + i]["Items"][1] = {}
        menu[30 + i]["Items"][1]["Name"] = "Reverse"
        menu[30 + i]["Motor"] = i
    menu[4] = {}
    menu[4]["Title"] = "LEDs"
    menu[4]["Items"] = {}
    for i in range(2):
        menu[4]["Items"][i] = {}
        menu[4]["Items"][i]["Name"] = "LED " + str(i)
        menu[4]["Items"][i]["Link"] = 40 + i
        menu[40 + i] = {}
        menu[40 + i]["Title"] = "LED " + str(i)
        menu[40 + i]["Items"] = {}
        e = 0
        for c in predefs.colors:
            menu[40 + i]["Items"][e] = {}
            menu[40 + i]["Items"][e]["Name"] = c[0]
            menu[40 + i]["LED"] = i
            e = e + 1
    menu[5] = {}
    menu[5]["Title"] = "Buttons"
    menu[5]["Items"] = {}
    i = 1
    for i in range(2):
        menu[5]["Items"][i] = {}
        menu[5]["Items"][i]["Name"] = "Button " + str(i)
        menu[5]["Items"][i]["Button"] = i
    menu[10] = {}
    menu[10]["Title"] = "Run"
    menu[10]["Items"] = {}
    menu[10]["Items"][0] = {}
    menu[10]["Items"][0]["Name"] = "Run Program"
    #menu[10]["Items"][1] = {}
    #menu[10]["Items"][1]["Name"] = "Delete"
    #menu[10]["Items"][1]["Link"] = 11
    menu[11] = {}
    menu[11]["Title"] = "Are You Sure?"
    menu[11]["Items"] = {}
    menu[11]["Items"][0] = {}
    menu[11]["Items"][0]["Name"] = "Yes"
    menu[11]["Items"][1] = {}
    menu[11]["Items"][1]["Name"] = "No"
    menu[11]["Items"][1]["Link"] = 10
    menu[29]={}
    menu[29]["Title"] = "Unplug Sensors"
    menu[29]["Items"] = {}
    menu[29]["Items"][0] = {}
    menu[29]["Items"][0]["Name"] = "Continue"
    menu[29]["Items"][1] = {}
    menu[29]["Items"][1]["Name"] = "Cancel"
    menu[29]["Items"][1]["Link"] = 2
        
currentMenu = 0
currentItem = 0
topItem = 0
scrollSize = 0
scrollPos = 0
history = []
currentProgram = ""
currentMotor = 0
currentSensor = ""
screenMode = "Menu"
prevTime = time.ticks_ms()

initMenu()

# Load programs
f = 0
root = os.listdir("/")
root.sort()
for file in root:
    if file.endswith(".py") and file != "main.py":
        menu[1]["Items"][f] = {}
        menu[1]["Items"][f]["Name"] = file
        menu[1]["Items"][f]["File"] = file
        f += 1
        
#resume on reset
try:
    f = open(".resume", "r")
    lines = f.readlines()
    currentMenu = int(lines[0])
    menu[currentMenu]["Title"] = lines[1][:-1] 
    history = [[0,0], [1, int(lines[2])]]
    f.close()
except: pass


def execProgram():     
    global screenMode
    try:
        currentProgram.main()
        endProgram()
        screenMode = "Menu"
        drawMenu()
    except AttributeError:
        drawWindow("Error", "No function\nmain() in file\n" + menu[currentMenu]["Title"])
    except ValueError as error:
        endProgram()
        drawWindow("Error", error.args[0])

def endProgram():
    for m in range(6):
        motor.stop(m)
        motor.setDirection(m, "Forward")
    for l in range(2):
        led.off(l)
    
def drawMenu():
    display.fill(0)
    i = 0
    if len(menu[currentMenu]["Items"]) > 0:
        cursor = True
    else:
        cursor = False

    while i < 128:
        display.pixel(i, 8, 1)
        if cursor == True and i < 127:
            j = 0
            while j < 10:
                display.pixel(i, 10 + 10 * currentItem + j - 10 * topItem, 1)
                j += 1
        i += 1

    display.text(
        menu[currentMenu]["Title"],
        int((19 - len(menu[currentMenu]["Title"])) / 2) * 6,
        0,
        1,
    )
    
    if cursor == False:
        display.text("No Entries", 36, 27, 1)
    else:
        i = 0
        while i < scrollSize:
            display.pixel(128, i + 10 + int(scrollPos), 1)
            display.pixel(127, i + 10 + int(scrollPos), 1)
            i = i + 1

    for i in menu[currentMenu]["Items"]:
        if i == currentItem:
            color = 0
        else:
            color = 1
        if i >= topItem:
            display.text(
                menu[currentMenu]["Items"][i]["Name"][0:15],
                5,
                (10 * i) + 11 - 10 * topItem,
                color,
            )
    display.show()

def drawWindow(title, *args):
    for arg in args:
        if type(arg) is list:
            graphic = arg
        elif type(arg) is bool or int and type(arg) is not str:
            flip = arg
        elif type(arg) is str:
            text = arg
            for char in range(len(text)):
                if text[char - 1] == "\n":
                    text2 = text[char:]
                    text = text[0:char - 1]
                    break
            try:
                for char in range(len(text2)):
                    if text2[char - 1] == "\n":
                        text3 = text2[char:]
                        text2 = text2[0:char - 1]
                        break
            except NameError: pass
            
    display.fill(0)
    
    i = 0
    display.text(title, int((19 - len(menu[currentMenu]["Title"])) / 2) * 6, 0, 1,)
    while i < 128:
        display.pixel(i, 8, 1)
        i = i + 1
    
    try:
        display.text(text[0:14], int((19 - len(text)) / 2) * 3, 27, 1)
        display.text(text2[0:14], int((19 - len(text2)) / 2) * 3, 37, 1)
        display.text(text3[0:14], int((19 - len(text2)) / 2) * 3, 47, 1)
    except NameError: pass
    
    try:
        if flip == False:
            p = 0
        else:
            p = len(graphic) -1
        for row in range(56):
            for col in range(128):
                if p >= len(graphic) or p < 0:
                    break
                if graphic[p] == 1:
                    display.pixel(col + 2 - (4 * flip), row + 9, 1)
                if flip == False:
                    p = p + 1
                else:
                    p = p - 1
    except NameError: pass
                
    display.show()
    
def moveCursor(amount):
    global currentItem
    global topItem
    global scrollPos
    oldTop = topItem
    
    if currentItem + amount > len(menu[currentMenu]["Items"]) - 1:
        currentItem = 0
        topItem = 0
    elif currentItem + amount < 0:
        currentItem = len(menu[currentMenu]["Items"]) - 1
        topItem = len(menu[currentMenu]["Items"]) - 5
    else:
        currentItem = currentItem + amount
        if currentItem - topItem > 4 or currentItem < topItem:
            topItem = topItem + amount
    if len(menu[currentMenu]["Items"]) - 1 < 5:
        topItem = 0
        
    if topItem != oldTop:
        scrollPos = currentItem * (55 - scrollSize) / len(menu[currentMenu]["Items"])

class selectActions:
    def nextMenu():
        global currentMenu
        global currentItem
        global topItem
        global scrollPos
        global scrollSize
        global history
        try:
            #don't add deltete menu to history
            try:
                if menu[currentMenu]["Items"][currentItem]["Link"] != 11 and currentMenu != 11:
                    history.append([currentMenu, currentItem])
            except KeyError:
                if currentMenu == 1:
                    history.append([currentMenu, currentItem])
            
            #run menu
            try:
                menu[10]["Title"] = menu[currentMenu]["Items"][currentItem]["File"]
                currentMenu = 10
                    
            #standard menus
            except KeyError:
                currentMenu = menu[currentMenu]["Items"][currentItem]["Link"]
            currentItem = 0
            topItem = 0
            scrollPos = 0
            scrollSize = 5 * (55 / len(menu[currentMenu]["Items"]))
            if scrollSize >= 55:
                scrollSize = 0
            drawMenu()
        except KeyError:
            pass

    def runProgram():
        global screenMode
        global currentProgram
        try:
            if currentMenu == 10 and menu[currentMenu]["Items"][currentItem]["Name"] == "Run Program":
                currentProgram = __import__(menu[currentMenu]["Title"][:-3])
                screenMode = "Program"
                drawWindow(menu[currentMenu]["Title"], graphics.arrow_right, 0)
                _thread.start_new_thread(execProgram, ())
        except KeyError: pass
    
    def readSensor():
        global screenMode
        global currentSensor
        try:
            currentSensor = menu[currentMenu]["Sensor"]
            screenMode = "Sensor"
        except KeyError: pass

    def runMotor():
        global screenMode
        global currentMotor
        try:
            currentMotor = menu[currentMenu]["Motor"]
            screenMode = "Motor"
            drawWindow("Motor " + str(currentMotor), graphics.arrow_right, currentItem)
            motor.run(currentMotor, -((currentItem*100) - 100 + (currentItem*100)))
        except KeyError: pass

    def testLED():
        try:
            index = menu[currentMenu]["LED"]
            color = menu[currentMenu]["Items"][currentItem]["Name"]
            led.setColor(index, color)
        except KeyError: pass
        
    def calibrateSensor():
        try:
            if currentMenu == 29 and menu[currentMenu]["Items"][currentItem]["Name"] == "Continue":
                sensor.calibrate()
        except KeyError: pass
            
        

drawMenu()
resetTimer = 0
try:
    os.remove(".resume")
except OSError: pass

#Main loop
while True:
    #quick reset
    if button.getState(0) and button.getState(1):
        resetTimer = resetTimer + 1
    if resetTimer > 1500:
        machine.reset()
    
    #read keypad
    key = KEYPAD.get_key()
    if key:
        keyClick(key)
        prevTime = time.ticks_ms()
    else:
        currentTime = time.ticks_ms()
        if time.ticks_diff(currentTime, prevTime) > KEYPAD._debounce_time + 1:
            KEYPAD.bounce_count = 0
    
    #handle input
    if screenMode == "Program":
        if key == "CANCEL":
            drawWindow(menu[currentMenu]["Title"], "Stopping...")
            text = (str(currentMenu) + "\n" + menu[currentMenu]["Title"]+ "\n" + str(history[len(history) - 1][1]))
            with open(".resume", "w") as output:
                output.write(text)
                output.close()
            endProgram()
            _thread.exit()
            
    elif screenMode == "Sensor":
        _type = menu[currentMenu]["Items"][currentItem]["Name"]
        if _type == "Raw":
            value = sensor.rawValue(currentSensor)
        elif _type == "Touch":
            value = sensor.touchValue(currentSensor)
        elif _type == "Light":
            value = sensor.lightValue(currentSensor)
            
        drawWindow("Sensor " + currentSensor, menu[currentMenu]["Items"][currentItem]["Name"] + "\nValue: " + str(value))
        if key == "CANCEL":
            screenMode = "Menu"
            drawMenu()
            
    elif screenMode == "Motor":
        if key == "CANCEL":
            motor.stop(currentMotor)
            screenMode = "Menu"
            drawMenu()
            
    else:
        if key == "UP":
            moveCursor(-1)
            drawMenu()
        elif key == "DOWN":
            moveCursor(1)
            drawMenu()
        elif key == "SELECT":
            selectActions.runProgram()
            selectActions.readSensor()
            selectActions.runMotor()
            selectActions.testLED()
            selectActions.calibrateSensor()
            selectActions.nextMenu()
        elif key == "CANCEL" and currentMenu > 0:
            if currentMenu != 11:
                currentMenu = history[len(history) - 1][0]
                currentItem = history[len(history) - 1][1]
                history.remove(history[len(history) - 1])
            else:
                currentMenu = 10
            if currentMenu == 4:
                led.setColor(0, "Off")
                led.setColor(1, "Off")
                    
            if currentItem > 4:
                topItem = currentItem - 4
            else:
                topItem = 0
                    
            scrollSize = 5 * (55 / len(menu[currentMenu]["Items"]))
            if scrollSize >= 55:
                scrollSize = 0
            drawMenu()
