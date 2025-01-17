

#include <Arduino.h>

#define USE_TINYUSB 1

#define LED LED_BUILTIN

#ifdef USE_TINYUSB
#include <Adafruit_TinyUSB.h>
#endif

#ifdef CFG_TUSB_CONFIG_FILE
#include CFG_TUSB_CONFIG_FILE
#else
#include "tusb_config.h"
#endif

#include "ArduinoStuff.h"
#include "JumperlessDefinesRP2040.h"
#include "NetManager.h"
#include "MatrixStateRP2040.h"

#include "NetsToChipConnections.h"
#include "LEDs.h"
// #include "CH446Q.h"
#include "Peripherals.h"
#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#include "MachineCommands.h"
// #include <EEPROM.h>

#ifdef EEPROMSTUFF
#include <EEPROM.h>
#endif

#ifdef PIOSTUFF
#include "CH446Q.h"
#endif

#include "FileParsing.h"

#ifdef FSSTUFF
#include "LittleFS.h"

#endif

Adafruit_USBD_CDC USBSer1;

int supplySwitchPosition = 0;

void machineMode(void);
// int machineMode = 0;

volatile int sendAllPathsCore2 = 0; // this signals the core 2 to send all the paths to the CH446Q

// https://wokwi.com/projects/367384677537829889

void setup()
{
  pinMode(0, OUTPUT);
  pinMode(2, INPUT);
  pinMode(3, INPUT);

  // debugFlagInit();
  USBDevice.setProductDescriptor("Jumperless");
  USBDevice.setManufacturerDescriptor("Architeuthis Flux");
  USBDevice.setSerialDescriptor("0");
  USBDevice.setID(0xACAB, 0x1312);
  USBSer1.setStringDescriptor("Jumperless USB Serial");

  USBSer1.begin(115200);

#ifdef EEPROMSTUFF
  EEPROM.begin(256);
  debugFlagInit();

#endif

  initADC();
  delay(1);
  initDAC(); // also sets revisionNumber
  delay(1);
  initINA219();
  delay(1);
  Serial.begin(115200);

  initArduino();
  delay(4);
#ifdef FSSTUFF
  LittleFS.begin();
#endif
  setDac0_5Vvoltage(0.0);
  setDac1_8Vvoltage(1.9);

  clearAllNTCC();
  delay(4);
}

void setup1()
{

#ifdef PIOSTUFF
  initCH446Q();
#endif

  // delay (4);
  initLEDs();
  delay(4);
  startupColors();
  delay(4);
  lightUpRail();

  delay(4);
  showLEDsCore2 = 1;
}

char connectFromArduino = '\0';

char input;

int serSource = 0;
int readInNodesArduino = 0;

void loop()
{

  unsigned long timer = 0;

menu:
  // showMeasurements();

  Serial.print("\n\n\r\t\t\tMenu\n\n\r");
  Serial.print("\tn = show netlist\n\r");
  Serial.print("\tb = show bridge array\n\r");
  Serial.print("\tw = waveGen\n\r");
  Serial.print("\tv = toggle show current/voltage\n\r");
  Serial.print("\tf = load formatted nodeFile\n\r");
  Serial.print("\tp = paste new Wokwi diagram\n\r");
  Serial.print("\tl = LED brightness / test\n\r");
  Serial.print("\td = toggle debug flags\n\r");
  Serial.print("\tr = reset Arduino\n\r");
  Serial.print("\n\n\r");

dontshowmenu:
  connectFromArduino = '\0';

  while (Serial.available() == 0 && connectFromArduino == '\0')
    ;

  {
    if (showReadings >= 1)
    {
      showMeasurements();
    }
  }

  if (connectFromArduino != '\0')
  {
    input = 'f';
    // connectFromArduino = '\0';
  }
  else
  {
    input = Serial.read();
    Serial.print("\n\r");
  }

  // Serial.print(input);
skipinput:
  switch (input)
  {
  case 'v':

    if (showReadings >= 3)
    {
      showReadings = 0;
      // goto dontshowmenu;
      break;
    }
    else
    {
      showReadings++;
      chooseShownReadings();
      // Serial.write("\033"); //these VT100/ANSI commands work on some terminals and not others so I took it out
      // Serial.write("\x1B\x5B");
      // Serial.write("1F");//scroll up one line
      // Serial.write("\x1B\x5B");
      // Serial.write("\033");
      // Serial.write("2K");//clear line
      // Serial.write("\033");
      // Serial.write("\x1B\x5B");
      // Serial.write("1F");//scroll up one line
      // Serial.write("\x1B\x5B");
      // Serial.write("\033");
      // Serial.write("2K");//clear line

      goto dontshowmenu;
      // break;
    }

  case 'n':

    Serial.print("\n\n\rnetlist\n\n\r");
    listSpecialNets();
    listNets();
    break;
  case 'b':
    Serial.print("\n\n\rBridge Array\n\r");
    printBridgeArray();
    Serial.print("\n\n\n\rPaths\n\r");
    printPathsCompact();
    Serial.print("\n\n\rChip Status\n\r");
    printChipStatus();
    Serial.print("\n\n\r");
    Serial.print("Revision ");
    Serial.print(revisionNumber);
    Serial.print("\n\n\r");
    break;

  case 'm':

    break;

  case 'w':

    if (waveGen() == 1)
    {
      break;
    }

    // case 'a':
    // {
    //   resetArduino(); // reset works
    //   // uploadArduino(); //this is unwritten
    // }

  case 'f':
    readInNodesArduino = 1;
    clearAllNTCC();

    // sendAllPathsCore2 = 1;
    timer = millis();

    clearNodeFile();

    if (connectFromArduino != '\0')
    {
      serSource = 1;
    }
    else
    {
      serSource = 0;
    }

    savePreformattedNodeFile(serSource);

    // Serial.print("savePFNF\n\r");
    openNodeFile();
    getNodesToConnect();
    // Serial.print("openNF\n\r");
    digitalWrite(RESETPIN, HIGH);
    bridgesToPaths();
    clearLEDs();
    assignNetColors();
    // Serial.print("bridgesToPaths\n\r");
    digitalWrite(RESETPIN, LOW);
    // showNets();

    sendAllPathsCore2 = 1;

    if (debugNMtime)
    {
      Serial.print("\n\n\r");
      Serial.print("took ");
      Serial.print(millis() - timer);
      Serial.print("ms");
    }

    if (connectFromArduino != '\0')
    {
      connectFromArduino = '\0';
      // Serial.print("connectFromArduino\n\r");
      //  delay(2000);
      input = ' ';
      readInNodesArduino = 0;
      goto dontshowmenu;
    }

    readInNodesArduino = 0;
    break;

  case '\n':
    goto menu;
    break;

  case 'p':

    // case '{':  //I had this so you could paste a wokwi diagram from the main menu but it kinda makes a mess of other things

    digitalWrite(RESETPIN, HIGH);
    delay(1);
#ifdef FSSTUFF
    clearNodeFile();
#endif
    digitalWrite(RESETPIN, LOW);
    clearAllNTCC();
    clearLEDs();

    timer = millis();

#ifdef FSSTUFF

    parseWokwiFileToNodeFile();

    openNodeFile();
    getNodesToConnect();
#endif
    Serial.println("\n\n\rnetlist\n\n\r");

    bridgesToPaths();
    assignNetColors();

#ifdef PIOSTUFF

    sendAllPaths();
#endif

    if (debugNMtime)
    {
      Serial.print("\n\n\r");
      Serial.print("took ");
      Serial.print(millis() - timer);
      Serial.print("ms");
    }
    break;

  case 't':
#ifdef FSSTUFF
    clearNodeFile();
#endif

#ifdef EEPROMSTUFF
    lastCommandWrite(input);

    runCommandAfterReset('t');
#endif

#ifdef FSSTUFF
    openNodeFile();
    getNodesToConnect();
#endif
    Serial.println("\n\n\rnetlist\n\n\r");

    bridgesToPaths();

    listSpecialNets();
    listNets();
    printBridgeArray();
    Serial.print("\n\n\r");
    Serial.print(numberOfNets);

    Serial.print("\n\n\r");
    Serial.print(numberOfPaths);

    assignNetColors();
#ifdef PIOSTUFF
    sendAllPaths();
#endif

    break;

  case 'l':
    if (LEDbrightnessMenu() == '!')
    {
      clearLEDs();
      delayMicroseconds(9200);
      sendAllPathsCore2 = 1;
    }
    break;

  case 'r':

    resetArduino();

    break;

  case 'd':
  {
    debugFlagInit();

  debugFlags:

    Serial.print("\n\r0.   all off");
    Serial.print("\n\r9.   all on");
    Serial.print("\n\ra-z. exit\n\r");

    Serial.print("\n\r1. file parsing           =    ");
    Serial.print(debugFP);
    Serial.print("\n\r2. file parsing time      =    ");
    Serial.print(debugFPtime);

    Serial.print("\n\r3. net manager            =    ");
    Serial.print(debugNM);
    Serial.print("\n\r4. net manager time       =    ");
    Serial.print(debugNMtime);

    Serial.print("\n\r5. chip connections       =    ");
    Serial.print(debugNTCC);
    Serial.print("\n\r6. chip conns alt paths   =    ");
    Serial.print(debugNTCC2);
    Serial.print("\n\r7. LEDs                   =    ");
    Serial.print(debugLEDs);

    Serial.print("\n\n\r");

    while (Serial.available() == 0)
      ;

    int toggleDebug = Serial.read();
    Serial.write(toggleDebug);
    toggleDebug -= '0';

    if (toggleDebug >= 0 && toggleDebug <= 9)
    {

      debugFlagSet(toggleDebug);

      delay(10);

      goto debugFlags;
    }
    else
    {
      break;
    }
  }

  case ':':

    if (Serial.read() == ':')
    {
      // Serial.print("\n\r");
      // Serial.print("entering machine mode\n\r");
      machineMode();
      // showLEDsCore2 = 1;
      goto dontshowmenu;  
      break;
    }
    else
    {
      break;
    }

  default:
    while (Serial.available() > 0)
    {
      int f = Serial.read();
      delayMicroseconds(50);
    }

    break;
  }

  goto menu;
}

// #include <string> // Include the necessary header file

void machineMode(void) // read in commands in machine readable format
{
  
  enum machineModeInstruction receivedInstruction = parseMachineInstructions();

  switch (receivedInstruction)
  {
  case netlist:
    clearAllNTCC();

    digitalWrite(RESETPIN, HIGH);
    machineNetlistToNetstruct();
    populateBridgesFromNodes();
    bridgesToPaths();

    clearLEDs();
    assignNetColors();
    // showNets();
    digitalWrite(RESETPIN, LOW);
    sendAllPathsCore2 = 1;
    break;

  case bridgelist:
    clearAllNTCC();

    writeNodeFileFromInputBuffer();

    openNodeFile();
    getNodesToConnect();
    // Serial.print("openNF\n\r");
    digitalWrite(RESETPIN, HIGH);
    bridgesToPaths();
    clearLEDs();
    assignNetColors();
    // Serial.print("bridgesToPaths\n\r");
    digitalWrite(RESETPIN, LOW);
    // showNets();

    sendAllPathsCore2 = 1;
    break;

  case lightnode:
    lightUpNodesFromInputBuffer();
    break;

  case lightnet:
    lightUpNetsFromInputBuffer();
    //   lightUpNet();
    //assignNetColors();
    showLEDsCore2 = 1;
      break;

    // case getmeasurement:
    //   showMeasurements();
    //   break;

  case setsupplyswitch:
    
    supplySwitchPosition = setSupplySwitch();
    showLEDsCore2 = 1;
    break;

  // case gpio:
  //   break;
  }

  
}

unsigned long logoFlashTimer = 0;

int arduinoReset = 0;
unsigned long lastTimeReset = 0;

void loop1() // core 2 handles the LEDs and the CH446Q8
{

  // while (1) rainbowBounce(50); //I uncomment this to test the LEDs on a fresh board
  if (showLEDsCore2 >= 1)
  {
    int rails = showLEDsCore2;

    // showNets();
    if (rails == 1)
    {
      lightUpRail(-1, -1, 1, 28, supplySwitchPosition);
    }
    if (rails > 3)
    {
      Serial.print("\n\r");
      Serial.print(rails);
    }
    delayMicroseconds(2200);

    leds.show();
    delayMicroseconds(5200);
    showLEDsCore2 = 0;
  }

  if (sendAllPathsCore2 == 1)
  {
    delayMicroseconds(6200);
    sendAllPaths();
    delayMicroseconds(2200);
    showNets();
    delayMicroseconds(7200);
    sendAllPathsCore2 = 0;
  }

  if (arduinoReset == 0 && USBSer1.peek() == 0x30) // 0x30 is the first thing AVRDUDE sends
  {

    resetArduino();
    arduinoReset = 1;
    lastTimeReset = millis();
  }

  // if (digitalRead(RP_GPIO_0) == 1)
  // {
  //   setDac0_5Vvoltage(5.0);
  // } else
  // {
  //   setDac0_5Vvoltage(0.0);
  // }

  while (arduinoReset == 1)
  {

    if (USBSer1.available())
    {

      char ch = USBSer1.read();
      Serial1.write(ch);
    }

    if (Serial1.available())
    {
      char ch = Serial1.read();
      USBSer1.write(ch);
    }

    if (millis() - lastTimeReset > 3000) // if the arduino hasn't been reset in a second, reset the flag
    {
      arduinoReset = 0;
    }
  }

  if (readInNodesArduino == 0)
  {

    if (USBSer1.available())
    {

      char ch = USBSer1.read();
      Serial1.write(ch);
    }

    if (Serial1.available())
    {
      char ch = Serial1.read();
      USBSer1.write(ch);
      // Serial.print(ch);

      if (ch == 'f' && connectFromArduino == '\0')
      {
        // input = 'f';

        connectFromArduino = 'f';
        // Serial.print("!!!!");
      }
      else
      {
        // connectFromArduino = '\0';
      }
    }
  }

  if (logoFlash == 2)
  {
    logoFlashTimer = millis();
    logoFlash = 1;
  }

  if (logoFlash == 1 && logoFlashTimer != 0 && millis() - logoFlashTimer > 250)
  {
    logoFlash = 0;
    logoFlashTimer = 0;
    // lightUpRail();
    leds.setPixelColor(110, 0x550008);
    leds.show();
  }
}
