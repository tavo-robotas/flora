int valueA7 = 0;
int valueA8 = 0;
#include <RGBmatrixPanel.h>
#include "s300i2c.h"
#include <Wire.h>
#include "DHT.h"
#include <Fonts/Picopixel.h>
//-----------------------------LED MATRIX
S300I2C s3(Wire);
#define CLK 11 // USE THIS ON ARDUINO MEGA
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3
RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, false, 64);
//---------------------------------------
#define DHTPIN 12     
#define DHTTYPE DHT11   // DHT 11
DHT dht(DHTPIN, DHTTYPE);
//---------------------------------------

#include <EEPROM.h>
#include "GravityTDS.h"

#define TdsSensorPin A4
GravityTDS gravityTds;

float temperature = 25,tdsValue = 0;

//--------------------------------------
#define SensorPin 5          //pH meter Analog output to Arduino Analog Input 0
unsigned long int avgValue;  //Store the average value of the sensor feedback
int buf[10],temp;
//-------------------------------------

unsigned int co2;
int h;
int t;
float phValue;
int motorPin = 7;
//-------------------------------------

const byte POTENTIOMETER = 6;
int reading;
int value;
int preVal=0;
int k=0;
int laikmatisFAN = 0;
const byte CONTROL = 8;
unsigned long minutes = 400;
unsigned long laikmatisGLOBAL = 0;

//--------------------------------------

void send_readings_data()
{
    
}

void setup() {
  
  dht.begin();
  //Serial.begin (9600);
 
  Wire.begin();
  s3.begin(S300I2C_ADDR);
  delay(1000); // 10sec wait.
  s3.wakeup();
  s3.end_mcdl();
  s3.end_acdl();
  matrix.begin();
  gravityTds.setPin(TdsSensorPin);
  gravityTds.setAref(5.0);  //reference voltage on ADC, default 5.0V on Arduino UNO
  gravityTds.setAdcRange(1024);  //1024 for 10bit ADC;4096 for 12bit ADC
  gravityTds.begin();  //initialization
  pinMode(motorPin, OUTPUT);
  pinMode(CONTROL, OUTPUT);
  pinMode(6, OUTPUT);
  matrix.setFont(&Picopixel);

  matrix.setTextColor(matrix.Color333(0,0, 255));
  matrix.setCursor(4, 7);    // start at top left, with 8 pixel of spacing
  matrix.print("CO2 =");
  
  matrix.setCursor(47,7); 
  matrix.println("PPM");
  /////////////////////////////////////////
  matrix.setCursor(4,14);    // start at top left, with 8 pixel of spacing
  matrix.print("T =");
  
  matrix.setCursor(23,14); 
  matrix.println("'C");

  matrix.setCursor(34,14);    // start at top left, with 8 pixel of spacing
  matrix.print("H = ");

  matrix.setCursor(54,14); 
  matrix.println("%");
  //////////////////////////////////////////

  matrix.setCursor(4,21);    // start at top left, with 8 pixel of spacing
  matrix.print("TDS =");
      
  matrix.setCursor(47,21); 
  matrix.println("PPM");

  ///////////////////////////////////////////

  matrix.setCursor(4,28);    // start at top left, with 8 pixel of spacing
  matrix.print("PH =");
  digitalWrite(6, HIGH);
}

void loop() {

  smooth();
  
 // Serial.print(valueA7);
 // Serial.print("    ");
 // Serial.println(valueA8);
  
if(valueA8 != 0 and valueA7 !=0)
  {
    while(valueA7 != 0)
    {
     smooth();
     digitalWrite(6, LOW);
    }
  } 
  
  digitalWrite(6, HIGH);

  laikmatisGLOBAL=laikmatisGLOBAL +1;
  reading = analogRead(POTENTIOMETER);
    if (preVal == reading || preVal == reading + 1 || preVal == reading - 1|| preVal == reading + 2 || preVal == reading - 2)
    {
      k=1;
      laikmatisFAN = laikmatisFAN+1;
    }
    else 
    {
      k=0;
      laikmatisFAN=0;
    }
    preVal = reading;
    
    if (k==0) 
    {
      
     reading = analogRead(POTENTIOMETER);
     value = map(reading, 0, 1024, 255, 0);
     analogWrite(CONTROL, value);
    }
    
    if (k==1 && laikmatisFAN > minutes) 
    {
      value = 255;
      analogWrite(CONTROL, value);
     
    }

    if (laikmatisGLOBAL == 150){

      matrix.fillRect(21, 3, 26, 5, matrix.Color333(0, 0, 0));
      matrix.fillRect(21, 17, 26, 5, matrix.Color333(0, 0, 0));
      matrix.fillRect(13, 10, 10, 5, matrix.Color333(0, 0, 0));
      matrix.fillRect(43, 10, 10, 5, matrix.Color333(0, 0, 0));
      matrix.fillRect(17, 24, 25, 5, matrix.Color333(0, 0, 0));
      delay(100);
      Show();
      laikmatisGLOBAL=0;
      
    }
 // Serial.println (laikmatisGLOBAL);
}

  void Show(){  
    
//------------------------------------------

    gravityTds.setTemperature(temperature);  // set the temperature and execute temperature compensation
    gravityTds.update();  //sample and calculate 
    tdsValue = gravityTds.getTdsValue();  // then get the value
 
//---------------------------------------------

    for(int i=0;i<10;i++)       //Get 10 sample value from the sensor for smooth the value
  { 
    buf[i]=analogRead(SensorPin);
    delay(10);
  }
  for(int i=0;i<9;i++)        //sort the analog from small to large
  {
    for(int j=i+1;j<10;j++)
    {
      if(buf[i]>buf[j])
      {
        temp=buf[i];
        buf[i]=buf[j];
        buf[j]=temp;
      }
    }
  }
  avgValue=0;
  for(int i=2;i<8;i++)                      //take the average value of 6 center sample
  avgValue+=buf[i];
  phValue=(float)avgValue*5.0/1024/6; //convert the analog into millivolt
  phValue=3.5*phValue;                      //convert the millivolt into pH value

//-------------------------------------------

  co2 = s3.getCO2ppm();  
  h = dht.readHumidity();
  t = dht.readTemperature();
 
 


  matrix.setTextColor(matrix.Color333(255,0, 0));
  matrix.setCursor(29,7);    // start at top left, with 8 pixel of spacing
  matrix.print(co2);
  
  matrix.setCursor(15,14);    // start at top left, with 8 pixel of spacing
  matrix.print(t);
  
  matrix.setCursor(45,14);    // start at top left, with 8 pixel of spacing
  matrix.print(h);
  
  matrix.setCursor(29,21);    // start at top left, with 8 pixel of spacing
  matrix.print(tdsValue,0);
  
  matrix.setCursor(23,28);    // start at top left, with 8 pixel of spacing
  matrix.print(phValue,2);

  if (tdsValue<200)
    {
       analogWrite(motorPin, 255);
       delay (1000);
       analogWrite(motorPin, 0);
       
    }  
   
  }

  int smooth(){
  int i;

  int numReadings = 50;

  for (i = 0; i < numReadings; i++){
    // Read light sensor data.
    valueA7 = valueA7 + analogRead(A7);
    valueA8 = valueA8 + analogRead(A8);

    delay(1);
  }

  // Take an average of all the readings.
  valueA7 = valueA7 / numReadings;
  valueA8 = valueA8 / numReadings;
  // Scale to 8 bits (0 - 255).
  valueA7 = valueA7 / 4;
  valueA8 = valueA8 / 4;
  return valueA7;
  return valueA8;
}
