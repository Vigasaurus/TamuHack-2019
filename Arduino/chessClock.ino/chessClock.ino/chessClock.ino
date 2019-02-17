#include "SevSeg.h"
float timeStart = 6000;
bool timeOver = false;
bool waiting = true;
int counter = 0;
SevSeg sevseg; //Initiate a seven segment controller object

void setup() {
  // Open serial connection.
  Serial.begin(9600);
  byte numDigits = 4;
  byte digitPins[] = {3, 2, 5, 0};
  byte segmentPins[] = {6, 7, 8, 9, 10, 11, 12, 13};
  sevseg.begin(COMMON_CATHODE, numDigits, digitPins, segmentPins);
  sevseg.setBrightness(90);
  pinMode(4, OUTPUT);
}

void loop() {
  while (Serial.available() > 0) {
    Serial.read();
    if (waiting) {    // if data present
      waiting = false;
    } else {
      timeStart = 6000.0;
      timeOver = false;
    }
  }
  if (!waiting) {

    if (timeStart >= 0) {
      counter = 0;
      digitalWrite(4, LOW);
      if (timeStart >= 5300)
        digitalWrite(4, HIGH);
      timeOver = false;
      sevseg.setNumber((int)timeStart, 2);
      sevseg.refreshDisplay(); // Must run repeatedly
      delay(1);
      timeStart -= .1;
    }
    else {
      timeOver = true;
    }
    if (timeOver) {
      if ( counter <= 10)
        digitalWrite(4,HIGH);
      sevseg.setNumber(0000, 2);
      sevseg.refreshDisplay(); // Must run repeatedly
      delay(75);
      if (counter <= 10)
        digitalWrite(4,LOW);
      delay(75);
      counter++;
    }
  }
}
