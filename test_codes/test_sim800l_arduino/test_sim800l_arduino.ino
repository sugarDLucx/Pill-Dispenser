/*
  SIM800L UART Passthrough Test for Arduino
  =========================================
  This sketch turns your Arduino into a USB-to-Serial bridge.
  Whatever you type in the Arduino IDE Serial Monitor is sent directly to the SIM800L.
  Whatever the SIM800L replies is printed directly to the Serial Monitor.

  WIRING INSTRUCTIONS (Arduino UNO/Nano/Mega):
  -------------------------------------------
  Arduino 5V  -> DO NOT USE FOR SIM800L VCC! (Use external 5V 2A power supply)
  Arduino GND -> SIM800L GND (AND External Power Supply GND - Common ground is REQUIRED)
  Arduino D10 -> SIM800L TXD (Arduino RX receives from SIM TX)
  Arduino D11 -> SIM800L RXD (Arduino TX transmits to SIM RX)

  SERIAL MONITOR SETTINGS:
  ------------------------
  1. Set Baud Rate to: 9600
  2. Set Line Ending to: "Both NL & CR" (This is required for AT commands!)
  
  HOW TO TEST:
  ------------
  1. Open Serial Monitor.
  2. Type: AT
     (It should reply OK)
  3. Type: AT+CPIN?
     (It should reply +CPIN: READY. If it says ERROR, the SIM is missing/backwards/loose)
  4. Type: AT+CSQ
     (It should reply with a number like +CSQ: 15,0. If it says +CSQ: 0,0, you have no signal/no antenna)
  5. Type: AT+CREG?
     (It should reply +CREG: 0,1 or +CREG: 0,5. If it says 0,0 or 0,2, it is not connected to a network)
*/

#include <SoftwareSerial.h>

// Define SoftwareSerial pins
// RX = 10 (Connect to SIM800L TXD)
// TX = 11 (Connect to SIM800L RXD)
SoftwareSerial sim800l(10, 11); 

void setup() {
  // Start the hardware serial port to communicate with the PC
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect
  }
  
  Serial.println("Arduino to SIM800L Passthrough Started.");
  Serial.println("Type AT commands in the Serial Monitor above.");
  Serial.println("Make sure 'Both NL & CR' is selected next to the baud rate!");
  Serial.println("---------------------------------------------------------");

  // Start the software serial port to communicate with the SIM800L
  // SIM800L default baud rate is usually 9600, sometimes it's auto-bauding.
  sim800l.begin(9600);
}

void loop() {
  // If the SIM800L sends data, read it and print it to the PC Serial Monitor
  if (sim800l.available()) {
    Serial.write(sim800l.read());
  }

  // If you type data in the PC Serial Monitor, read it and send it to the SIM800L
  if (Serial.available()) {
    sim800l.write(Serial.read());
  }
}
