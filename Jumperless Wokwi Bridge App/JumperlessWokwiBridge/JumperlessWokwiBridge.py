from bs4 import BeautifulSoup


import requests
import json
import serial
import time

import sys
import codecs
import os
import pyduinocli
#import platform

#from watchedserial import WatchedReaderThread

import serial.tools.list_ports


debug = False


justreconnected = 0

global serialconnected
serialconnected = 0

portSelected = 0

stringified = 0
lastDiagram = 1


menuEntered = 0

portName = ' '

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


#arduino = pyduinocli.Arduino("arduino-cli")

#### If you're running this in thonny, make sure you download arduino-cli and put it in the same folder as this script
#### then uncomment this below and comment the one above
# arduino = pyduinocli.Arduino("./arduino-cli")


arduino = pyduinocli.Arduino(resource_path("arduino-cli"))

arduinoPort = 0

disableArduinoFlashing = 0


def openSerial():
    global portName
    global ser
    global arduinoPort
    serialconnected = 0

    portSelected = 0
    foundports = []
    
    print("\n")

    while portSelected == False:
        autodetected = -1
        ports = serial.tools.list_ports.comports()
        i = 0
        for port, desc, hwid in ports:
            i = i + 1
            print("{}: {} [{}]".format(i, port, desc))
            if desc == "Jumperless":
                autodetected = i
                foundports.append(ports[autodetected-1][0])
                
        selection = -1
        sortedports = sorted(foundports,key = lambda x:x[-1])
        #print (foundports)
        #print(sortedports)
        print ("\n\n")
        
        if autodetected != -1:
        #if False:    
            
            selection = autodetected
            #portName = ports[int(selection) - 1].device
            portName = sortedports[0]
            arduinoPort = sortedports[1]
            portSelected = True
            serialconnected = 1
            
            print("\nAutodetected Jumperless at", end=" ")
            print(portName)
            
            print ("Autodetected USB-Serial at ", end="")
            print (arduinoPort)


            

        else:
            selection = input(
                "\n\nSelect the port connected to your Jumperless   ('r' to rescan)\n\n(Choose the lower numbered port, the other is routable USB-Serial)\n\n")
            
            
            if selection.isdigit() == True and int(selection) <= i:
                portName = ports[int(selection) - 1].device
                print("\n\n")
                i = 0
                
                for port, desc, hwid in ports:
                    i = i + 1
                    print("{}: {} [{}]".format(i, port, desc))

                        
                ArduinoSelection = -1
                sortedports = sorted(foundports,key = lambda x:x[-1])
                #print (foundports)
                #print(sortedports)
                print ("\n\n")
                ArduinoSelection = input(
                        "\n\nChoose the Arduino port   ('x' to skip)\n\n(Choose the higher numbered port)\n\n")
                
                if (ArduinoSelection == 'x' or ArduinoSelection == 'X'):
                    disableArduino
                if ArduinoSelection.isdigit() == True and int(ArduinoSelection) <= i:
                    arduinoPort = ports[int(ArduinoSelection) - 1].device
                    aPortSelected = True
                    print(ports[int(ArduinoSelection) - 1].device)
                
                
                portSelected = True
                print(ports[int(selection) - 1].device)
                
                
                
                serialconnected = 1
                
                

        


#portName =  '/dev/cu.usbmodem11301'

    ser = serial.Serial(portName, 115200, timeout=None)


openSerial()


justChecked = 0
reading = 0


def check_presence(correct_port, interval=.15):
    global ser
    global justreconnected
    global serialconnected
    global justChecked
    global reading

    portFound = 0
    while True:
        
       
        if (reading == 0):
            
            portFound = 0

            for port in serial.tools.list_ports.comports():

                if portName in port.device:
                    
                    portFound = 1

            #print (portFound)

            if portFound == 1:
                try:
                    #print (portName)
                    #ser = serial.Serial(portName, 115200)
                    #print (portName)
                    #ser.open(portName)
                    justChecked = 1
                    serialconnected = 1
                    time.sleep(0.1)
                    justChecked = 0
                    
                    
                except:
                    
                    continue

            else:
                justreconnected = 1
                justChecked = 0
                serialconnected = 0

                ser.close()

            time.sleep(interval)


import threading
port_controller = threading.Thread(
    target=check_presence, args=(portName, .15,), daemon=True)
# port_controller.daemon(True)
port_controller.start()


# 555 project

# https://wokwi.com/projects/369024970682423297


# the website URL
#url_link = "https://wokwi.com/projects/369024970682423297"

url_link = 0


def openProject():
    global url_link
    global disableArduinoFlashing
    url_entered = 0
    url_selected = 0
    entryType = -1  # 0 for index, 1 for name, 2 for link
        
    while (url_selected == 0):

        print('\n\nChoose from saved projects or paste the link to you Wokwi project:\n\n')

        try:
            f = open("savedWokwiProjects.txt", "r")
        except:
            f = open("savedWokwiProjects.txt", "x")
            f = open("savedWokwiProjects.txt", "r")

        index = 0

        lines = f.readlines()

        for line in lines:
            if (line != '\n'):
                index += 1
                print(index, end="\t")

                print(line)

        linkInput = input('\n\n')

        if (linkInput.startswith("http") == True):
            entryType = 2
        elif (linkInput.isdigit() == True) and (int(linkInput) <= len(lines)):
            otherIndex = 0
            for idx in lines:
                if (idx != '\n'):
                    otherIndex += 1
                    if (otherIndex == int(linkInput)):
                        idx = idx.rsplit('\t\t')
                        idxLink = idx[1].rstrip('\n')
                        #print("\n\nRunning project ", end='')
                        #print(idx[0])
                        entryType = 2

                        linkInput = idxLink.rstrip('\n')

                        break

        else:
            for name in lines:
                if name != '\n':
                    name = name.rsplit('\t\t')
                    nameText = name[0]
                    #print (nameText)
                    if (nameText == linkInput):
                        entryType = 2
                        linkInput = name[1].rstrip('\n')
                        break

        checkurl = ' '
        url_link = linkInput

#         print("\n\n linkInput = ", end='')
#         print(linkInput)
#         print("\n\n url_link = ", end='')
#         print(url_link)

        #checkurl = requests.get(url_link)
        #print(checkurl.status_code)
        try:
            checkurl = requests.get(url_link)
            #print(checkurl.status_code)
            if (checkurl.status_code == requests.codes.ok):
                url_selected = 1
                # break
            else:
                print("\n\nBad Link")
                url_link = 0
                linkInput = 0
                #url_link = input('\n\nBad link\n\nPaste the link to you Wokwi project here:\n\n')
                continue

        except:
            print("\n\nBad Link!!!")
            url_link = 0
            #url_link = input('\n\nBad link\n\nPaste the link to you Wokwi project here:\n\n')
            continue

        matchFound = 0
        line = 0
        index = 0

        for line in lines:
            if (line != '\n'):
                line = line.rsplit('\t\t')
                name = line[0]
                line = line[1]
                
                line = line.rstrip('\n')
                index += 1

                if line == linkInput:
                    #print ( "Match Found at index ", end = '')
                    matchFound = index
                    print("\n\nRunning project ", end='')
                    print(name)
                    #print (matchFound)
                    #print (line)
                    break
                #index += 1
                #print(index, end="\t")

                # print(line)

        if matchFound == 0:
            name = input("\n\nEnter a name for this new project\n\n")
            f.close()
            f = open("savedWokwiProjects.txt", "a")
            f.write(name)
            f.write('\t\t')
            f.write(linkInput)
            f.write("\n")

            
            
            
            
        url_link = linkInput
            
        autoFlash = input("\n\nDo you want to enable Auto-flashing the Arduino from Wokwi? y/n\n\n")
        if (autoFlash == 'y' or autoFlash == 'Y'):
            disableArduinoFlashing = 0
        else:
            disableArduinoFlashing = 1
        

    f.close()
    
openProject()

print("\n\nSave your Wokwi project to update the Jumperless\n\nEnter 'menu' for Bridge App menu\n\n")



def bridgeMenu():
    global menuEntered
    global ser

    while(menuEntered == 1):

        print("\t\t\tBridge App Menu\n\n")
        print("\t\tf = Disable Auto-flashing Arduino\n")
        print("\t\td = Delete Saved Projects\n")
        print("\t\tr = Restart Bridge App\n")
        print("\t\ts = Restart Serial\n")
        print("\t\tl = Load Project\n")
        print("\t\tj = Go Back To Jumperless\n")

        menuSelection = input("\n\n")
        
        if(menuSelection == 'f'):
            disableArduinoFlashing = 1
            break

        if (menuSelection == 's'):
            ser.close()
            openSerial()
            #time.sleep(1)
            menuEntered = 0
            time.sleep(.5)
            ser.write(b'm')
            break
        
        if (menuSelection == 'l'):
            openProject()
            #time.sleep(1)
            menuEntered = 0
            time.sleep(.75)
            ser.write(b'm')
            
            break
        
        if (menuSelection == 'r'):
            ser.close()
            openSerial()
            openProject()
            #time.sleep(1)
            menuEntered = 0
            time.sleep(.5)
            ser.write(b'm')
            
            break
            
        if(menuSelection == 'j'):
            menuEntered = 0
            time.sleep(.5)
            ser.write(b'm')
            break
        
        
        while (menuSelection == 'd'):
            
            print('\n\nEnter the index of the project you\'d like to delete:\n\nr = Return To Menu\ta = Delete All\n\n')

            try:
                f = open("savedWokwiProjects.txt", "r")
            except:
                f = open("savedWokwiProjects.txt", "x")
                f = open("savedWokwiProjects.txt", "r")

            index = 0

            lines = f.readlines()

            for line in lines:
                if (line != '\n'):
                    index += 1
                    print(index, end="\t")

                    print(line)

            linkInput = input('\n\n')
            
            if (linkInput == 'a'):
                f.close()
                f = open("savedWokwiProjects.txt", "w")
                f.close()
            
            
            
            if (linkInput.isdigit() == True) and (int(linkInput) <= index):
                otherIndex = 0
                realIndex = 0
                for idx in lines:
                    
                    if (idx != '\n'):
                        
                        otherIndex += 1
                        
                        if (otherIndex == int(linkInput)):
                            print(idx)
                            del lines[realIndex]
                            #del lines[idx+1]
                            idx = idx.rsplit('\t\t')
                            idxLink = idx[1].rstrip('\n')
                            print("\n\nDeleting project ", end='')
                            print(idx[0])
                            break
                        
                    realIndex += 1
                        
                f.close()
                f = open("savedWokwiProjects.txt", "w")
                
                for line in lines:
                
                    f.write(line)
                f.close()
                f = open("savedWokwiProjects.txt", "r")
                print (f.read())
                f.close()
                #menuEntered = 0
            else:
                break

                            
portNotFound = 1
                            
            



def serialTermIn():
    global serialconnected
    global ser
    global justChecked
    global reading
    global menuEntered
    global portNotFound
    while True:
        readLength = 0
        
        
        while menuEntered == 0:
            try:
                if (ser.in_waiting > 0):
                    #justChecked = 0
                    #reading = 1
                    inputBuffer = b' '

                    waiting = ser.in_waiting

                    while (serialconnected >= 0):
                        inByte = ser.read()

                        inputBuffer += inByte

                        if (ser.in_waiting == 0):
                            time.sleep(0.05)

                            if (ser.in_waiting == 0):
                                break
                            else:
                                continue

                    inputBuffer = str(inputBuffer)

                    inputBuffer.encode()
                    decoded_string = codecs.escape_decode(
                        bytes(inputBuffer, "utf-8"))[0].decode("utf-8")

                    decoded_string = decoded_string.lstrip("b' ")
                    decoded_string = decoded_string.rstrip("'")

                    print(decoded_string, end='')
                    #print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    readlength = 0
                    #justChecked = 0
                    reading = 0
                    portNotFound = 0

            except:
                
                ser.close()
                print("Disconnected")
                portNotFound = 1
                while (portNotFound == 1):
                    portFound = 0
                   
                    time.sleep(0.3)
                    for port in serial.tools.list_ports.comports():

                        if portName in port.device:

                            portFound = 1
                            portNotFound = 0
                            #print ("found ")
                            #print (port.device)

                    if portFound == 1:
                        try:
                            ser = serial.Serial(portName, 115200, timeout=None)
                            justChecked = 1
                            serialconnected = 1
                            time.sleep(0.2)
                            justChecked = 0
                            portNotFound = 0
                            justreconnected = 1
                        except:
                            portFound = 0
                            portNotFound = 1
                            time.sleep(0.25)

                    else:
                        #justreconnected = 1
                        justChecked = 0
                        serialconnected = 0

                        #ser.close()
                        portNotFound = 1
                        time.sleep(.1)


port_controller = threading.Thread(target=serialTermIn, daemon=True)
# port_controller.daemon(True)
port_controller.start()


def serialTermOut():
    global serialconnected
    global ser
    global justChecked
    global justreconnected
    global menuEntered

    while True:
        resetEntered = 0

        while (menuEntered == 0):

            outputBuffer = input()

            if (outputBuffer == 'menu') or (outputBuffer == 'Menu'):
                print("Menu Entered")
                menuEntered = 1
                continue

            if outputBuffer == b'r':
                resetEntered = 1

            if (serialconnected == 1):
                #justChecked = 0
                while (justChecked == 0):
                    time.sleep(0.01)
                else:

                    #print (outputBuffer)
                    if (outputBuffer != " "):
                        try:
                            #print (outputBuffer.encode('ascii'))
                            ser.write(outputBuffer.encode('ascii'))
                        except:
#                             portNotFound = 1

                            while (portNotFound == 1):
                                portFound = 0

                                for port in serial.tools.list_ports.comports():

                                    if portName in port.device:

                                        portFound = 1
                                        print (port.device)

                                    if portFound >= 1:
                                        #
                                        justChecked = 1
                                        serialconnected = 1
                                        time.sleep(0.05)
                                        justChecked = 0
                                        portNotFound = 0

                                    else:
                                        justreconnected = 0
                                        justChecked = 0
                                        serialconnected = 0

                                        ser.close()
                                        portNotFound = 1
                                        time.sleep(.1)
                            print(outputBuffer.encode('ascii'))
                            ser.write(outputBuffer.encode('ascii'))

                        if (resetEntered == 1):
                            time.sleep(.5)
                            print("reset")
                            justreconnected = 1

    # time.sleep(.5)
    
def removeLibraryLines(line):
    
    if "#" in line:
        return False
    if (len(line) == 0):
        return False
    else:
        return True
        
    

port_controller = threading.Thread(target=serialTermOut, daemon=True)

port_controller.start()

time.sleep(.75)

lastsketch = 0
lastlibraries = 0

#print (arduino.board.attach(arduinoPort,None,"WokwiSketch"))
#print (arduinoPort)

while True:
   
    if (menuEntered == 1):
        bridgeMenu()

    # while portIsUsable(portName) == True:
     #   print('fuck')
      #  ser.close()
       # time.sleep(.5)
        #ser = serial.Serial(portName, 460800, timeout=0.050)

    while (justreconnected == 1):
        time.sleep(.01)
        #print("just reconnected")
        lastDiagram = '-1'
        ser.close()
        time.sleep(.1)
        #if (portNotFound != 1):
            #ser = serial.Serial(portName, 115200, timeout=None)
        if (serialconnected == 1):
            print('Reconnected')
            portNotFound = 0
            portFound = 1
            break
    else:
        justreconnected = 0

    if (serialconnected == 1):
        #print ("connected!!!")
        result = requests.get(url_link).text
        doc = BeautifulSoup(result, "html.parser")

        s = doc.find('script', type='application/json').get_text()

        stringex = str(s)

        d = json.loads(stringex)

        librariesExist = 0
        
        

        c = d['props']['pageProps']['p']['files'][0]['content']

        try:
            l = d['props']['pageProps']['p']['files'][2]['content']
            libraries = str(l)
            librariesExist = 1
        except:
            pass

        d = d['props']['pageProps']['p']['files'][1]['content']

        f = json.loads(d)

    #    cf = json.loads(c)

        diagram = str(d)
        sketch = str(c)

        if debug == True:
            print("\n\ndiagram.json\n")
            print(diagram)

            print("\n\nsketch.ino\n")
            print(sketch)

            print("\n\nlibraries.txt\n")
            print(libraries)


        justFlashed = 0
            
        if (sketch != lastsketch and disableArduinoFlashing == 0):
            
            
            lastsketch = sketch
            justFlashed = 1
            
            
            try:
                newpath = './WokwiSketch'
                
                if not os.path.exists(newpath):
                    os.makedirs(newpath)


                print("\n\rFlashing Arduino")
                sk = open("./WokwiSketch/WokwiSketch.ino", "w")
                sk.write(sketch)
                sk.close()
                time.sleep(0.1)
                
                ser.write("f 116-70,117-71,".encode())
                time.sleep(0.3)
                
                #ser.write('r\n'.encode())
                #time.sleep(0.3)
                #print (librariesExist)
                

                #time.sleep(0.3) # it fucks up here
                
                if (librariesExist == 1 and lastlibraries != libraries):
                    #print ("librariesExist")
                    lastlibraries = libraries

                    libList = list(libraries.split("\n"))
                                      
                    filteredLibs = list(filter(lambda x: removeLibraryLines(x), libList))     
                    #print ("libs filtered")
                    
                    if (len(filteredLibs) > 0):
                        
                        print ("Installing Arduino Libraries ", end="")

                        liberror = arduino.lib.install(filteredLibs)
                        
                        print (filteredLibs)
                
                
                ser.write('r\n'.encode())
                arduino.compile( "./WokwiSketch" ,port=arduinoPort,fqbn="arduino:avr:nano", upload=True)  
                    
                   
                    
                
            except:
                print ("Couldn't Flash Arduino")

                #continue
            
  
            

        if (lastDiagram != diagram or justFlashed == 1):
            justFlashed = 0
            justreconnected = 0
            length = len(f["connections"])

            p = "{\n"

            for i in range(length):

                conn1 = str(f["connections"][i][0])

                if conn1.startswith('pot1:SIG'):
                    conn1 = "106"
                elif conn1.startswith('pot2:SIG'):
                    conn1 = "107"
                    
                if conn1.startswith('logic1:'):
                    if conn1.endswith('0'):
                        conn1 = "110"
                    elif conn1.endswith('1'):
                        conn1 = "111"
                    elif conn1.endswith('2'):
                        conn1 = "112"
                    elif conn1.endswith('3'):
                        conn1 = "113"
                    elif conn1.endswith('4'):
                        conn1 = "108"
                    elif conn1.endswith('5'):
                        conn1 = "109"
                    elif conn1.endswith('6'):
                        conn1 = "116"                        
                    elif conn1.endswith('7'):
                        conn1 = "117"
                    elif conn1.endswith('D'):
                        conn1 = "114"                        
                        
                if conn1.startswith("bb1:") == True:
                    periodIndex = conn1.find('.')
                    conn1 = conn1[4:periodIndex]

                    if conn1.endswith('t') == True:
                        conn1 = conn1[0:(len(conn1) - 1)]
                    elif conn1.endswith('b') == True:
                        conn1 = conn1[0:(len(conn1) - 1)]
                        conn1 = int(conn1)
                        conn1 = conn1 + 30
                        conn1 = str(conn1)
                    elif conn1.endswith('n') == True:
                        conn1 = "100"
                    elif conn1.startswith("GND") == True:
                        conn1 = "100"
                    elif conn1.endswith('p') == True:
                        if conn1.startswith('t') == True:
                            conn1 = "105"
                        elif conn1.startswith('b') == True:
                            conn1 = "103"

                if conn1.startswith("nano:") == True:
                    periodIndex = conn1.find('.')
                    conn1 = conn1[5:len(conn1)]

                    if conn1.startswith("GND") == True:
                        conn1 = "100"
                    elif conn1 == "AREF":
                        conn1 = "85"
                    elif conn1 == "RESET":
                        conn1 = "84"
                    elif conn1 == "5V":
                        conn1 = "105"
                    elif conn1 == "3.3V":
                        conn1 = "103"
                    elif conn1 == "5V":
                        conn1 = "105"

                    elif conn1.startswith("A") == True:
                        conn1 = conn1[1:(len(conn1))]
                        conn1 = int(conn1)
                        conn1 = conn1 + 86
                        conn1 = str(conn1)
                    elif conn1.isdigit() == True:
                        conn1 = int(conn1)
                        conn1 = conn1 + 70
                        conn1 = str(conn1)

                conn2 = str(f["connections"][i][1])

                if conn2.startswith('pot1:SIG'):
                    conn2 = "106"
                elif conn2.startswith('pot2:SIG'):
                    conn2 = "107"
                    
                if conn2.startswith('logic1:'):
                    if conn2.endswith('0'):
                        conn2 = "110"
                    elif conn2.endswith('1'):
                        conn2 = "111"
                    elif conn2.endswith('2'):
                        conn2 = "112"
                    elif conn2.endswith('3'):
                        conn2 = "113"
                    elif conn2.endswith('4'):
                        conn2 = "108"
                    elif conn2.endswith('5'):
                        conn2 = "109"
                    elif conn2.endswith('6'):
                        conn2 = "116"                        
                    elif conn2.endswith('7'):
                        conn2 = "117"
                    elif conn2.endswith('D'):
                        conn2 = "114"                             

                if conn2.startswith("bb1:") == True:
                    periodIndex = conn2.find('.')
                    conn2 = conn2[4:periodIndex]

                    if conn2.endswith('t') == True:
                        conn2 = conn2[0:(len(conn2) - 1)]
                    elif conn2.endswith('b') == True:
                        conn2 = conn2[0:(len(conn2) - 1)]
                        conn2 = int(conn2)
                        conn2 = conn2 + 30
                        conn2 = str(conn2)
                    elif conn2.endswith('n') == True:
                        conn2 = "100"
                    elif conn2.startswith("GND") == True:
                        conn2 = "100"
                    elif conn2.endswith('p') == True:
                        if conn2.startswith('t') == True:
                            conn2 = "105"
                        elif conn2.startswith('b') == True:
                            conn2 = "103"

                if conn2.startswith("nano:") == True:
                    periodIndex = conn2.find('.')
                    conn2 = conn2[5:len(conn2)]

                    if conn2.startswith("GND") == True:
                        conn2 = "100"
                    elif conn2 == "AREF":
                        conn2 = "85"
                    elif conn2 == "RESET":
                        conn2 = "84"
                    elif conn2 == "5V":
                        conn2 = "105"
                    elif conn2 == "3.3V":
                        conn2 = "103"
                    elif conn2 == "5V":
                        conn2 = "105"

                    elif conn2.startswith("A") == True and conn2 != "AREF":

                        conn2 = conn2[1:(len(conn2))]
                        conn2 = int(conn2)
                        conn2 = conn2 + 86
                        conn2 = str(conn2)
                    elif conn2.isdigit() == True:
                        conn2 = int(conn2)
                        conn2 = conn2 + 70
                        conn2 = str(conn2)

                if conn1.isdigit() == True and conn2.isdigit() == True:

                    p = (p + conn1 + '-')
                    p = (p + conn2 + ',\n')

            p = (p + "}\n{\n}")

            lastDiagram = diagram

            try:
                ser.write('f'.encode())

                time.sleep(0.4)

                ser.write(p.encode())

            except:
                continue
                # waitForReconnect()

                # ser.write('f'.encode())

                # time.sleep(0.05)

                # ser.write(p.encode())

            #print (p)

        
        
        
        
        
        else:
            time.sleep(.75)
