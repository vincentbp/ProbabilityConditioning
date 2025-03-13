// This version works with hfb_lib.py
// This version combines both old behaviorOUT and behaviorIN 
// Only one arduino is needed

// DEFINE OUTPUT PINS
int AirLeft = 4;
int WaterLeft = 8;
int LED = 12;
int TStart = 11;
int THit = 5;
int Laser = 10;
int LaserOff = 9;

#include <SPI.h>

// DEFINE INPUT PINS
const int levInput = A0;
const int xInput = A3;
const int yInput = A4;
const int zInput = A5;
int lickSpout1 = 2;
int lickSpout2 = 3;

// DEFINE Some variables
int val = 0;
int baseX = 0;
int baseY = 0;
int baseZ = 0;
const int sampleSize = 200; // Take multiple samples to calculate base value
int lick1 = 0;
int lick2 = 0;
char lickChar = 'O';
int xRaw = 0;
int yRaw = 0;
int zRaw = 0;
char xChar = 'o';
char yChar = 'o';
char zChar = 'o';
int levRaw = 0;
char levChar1 = 'o';
char levChar2 = 'o';

void setup() {
 // initialize serial communication at 115200 bits per second:
  Serial.begin(115200);
  
  // OUTPUT PINS
  pinMode(AirLeft, OUTPUT);
  pinMode(WaterLeft, OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(TStart, OUTPUT);
  pinMode(THit, OUTPUT);
  pinMode(Laser, OUTPUT);
  pinMode(LaserOff, OUTPUT);
  digitalWrite(LaserOff,HIGH);
  pinMode(LED_BUILTIN, OUTPUT);

   // make the lickspout's pin an input:
  pinMode(lickSpout1, INPUT);
  pinMode(lickSpout2, INPUT);
 
  //  Calculate the baseline value to adjust range of accelerometer data from 0..255
  baseX = ReadAxis(xInput) - round(255 / 2);
  baseY = ReadAxis(yInput) - round(255 / 2);
  baseZ = ReadAxis(zInput) - round(255 / 2);
}

void loop() {
 //wait for a command
  while(!(Serial.available()));

  val = Serial.read();

     switch (val){
      
     case 'R': //READ INPUTS AND SEND THEM
      // Read each spout cover it to (00 01 10 11)+100 to avoid char = 10
      lick1 = digitalRead(lickSpout1);
      lick2 = digitalRead(lickSpout2); // OLD CODE USE TO HAVE TWO LICK SPOUTS
      lickChar = (10 * lick1 + lick2) + 100;
     
      // Read accelerator data and convert
      xRaw = analogRead(xInput) - baseX;
      yRaw = analogRead(yInput) - baseY;
      zRaw = analogRead(zInput) - baseZ;
      xChar = convertAccRead(xRaw);
      yChar = convertAccRead(yRaw);
      zChar = convertAccRead(zRaw);
     
      //  Read lever convert it to two bytes
      levRaw = analogRead(levInput);
      levChar1 = (levRaw - (levRaw % 255)) / 255;
      levChar2 = levRaw % 255;
      if (levRaw % 255 == 10) {
        levChar2 = 11; //Correct for line feed bytes
      }
      else if (levRaw % 255 == 13) {
        levChar2 = 14; //Correct for carriage return bytes
      }
      else {
        levChar2 = levRaw % 255;
     }
     
      Serial.print(levChar1);
      Serial.print(levChar2);
      Serial.print(lickChar);
      Serial.print(xChar);
      Serial.print(yChar);
      Serial.println(zChar);
      delay(2);      
      break;
            
     case 'E':
      digitalWrite(WaterLeft, HIGH);
      digitalWrite(THit,HIGH);
      break;
      
     case 'O':
      digitalWrite(WaterLeft, LOW);
      digitalWrite(THit,LOW);
      break;
      
     case 'L':
      digitalWrite(AirLeft, HIGH);
      break;
      
     case 'M':
      digitalWrite(AirLeft, LOW);
      break;
      
     case 'I':
      digitalWrite(LED, HIGH);
      digitalWrite(LED_BUILTIN, HIGH);
      digitalWrite(TStart,LOW);
      break;
      
     case 'J':
      digitalWrite(LED, LOW);
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(TStart,HIGH); // When LED goes off it is the begining of a trial
      break;
      
     case 'A':
      digitalWrite(Laser,HIGH);
      digitalWrite(LaserOff,LOW);
      delay(2); 
      digitalWrite(Laser,LOW);
      break;
     case 'B':
      digitalWrite(LaserOff,HIGH);
      break;
    }    
}

//
// Make sure the analog read of accelerator is within the 0..255 limit and output as a ASCII character
//
char convertAccRead(int val)
{
  if (val < 0) {
    val = 0;
  }
  if (val > 255) {
    val = 255;
  }
  if (val == 10) {
    val = 11; // avoid char = 10
  }
  if (val == 13) {
    val = 14; // avoid char = 13
  }
 
  char convertedVal = val;
  return convertedVal;
}
 
//
// Read "sampleSize" samples and report the average
//
int ReadAxis(int axisPin)
{
  long reading = 0;
  analogRead(axisPin);
  delay(1);
  for (int i = 0; i < sampleSize; i++)
  {
    reading += analogRead(axisPin);
  }
  return reading / sampleSize;
}
