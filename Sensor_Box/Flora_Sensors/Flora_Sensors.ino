#include <Arduino.h>
#include <Arduino_FreeRTOS.h>
#include <Wire.h>
#include "Adafruit_SGP30.h"
#include "DHT.h"
#include <RTClib.h>
#include "GravityTDS.h"
#include "queue.h" // Include queue.h for FreeRTOS Queue
#include <SD.h>    // Include SD library for SD card functionality
#include <EEPROM.h>

#define DHTPIN 30
#define DHTTYPE DHT22
#define SD_CS_PIN 53    // Chip select pin for SD card module
#define MOISTURE_PIN 49 // Change to pin 49 to avoid conflict with SPI pins
#define SLAVE_ADDRESS 9 // I2C communication

// Define relay pins
#define RELAY_PIN_1 2
#define RELAY_PIN_2 3
#define RELAY_PIN_3 4
#define RELAY_PIN_4 5
#define RELAY_PIN_5 6
#define RELAY_PIN_6 7
#define RELAY_PIN_7 8
#define RELAY_PIN_8 9

Adafruit_SGP30 sgp;
RTC_DS3231 rtc;
DHT dht(DHTPIN, DHTTYPE);
GravityTDS gravityTds;

QueueHandle_t screenQueue;

struct SensorData {
  float temperature;
  float humidity;
  float moisture;
  float pH;
  float tdsValue;
  uint16_t co2;
  uint16_t tvoc;
  DateTime timestamp;
};

TaskHandle_t dataReadingTaskHandle;
TaskHandle_t dataWritingTaskHandle;
QueueHandle_t dataQueue;

File dataFile;

void Task_SerialCommandHandler(void* pvParameter);
void Task_DataReading(void* pvParameter);
void Task_DataWriting(void* pvParameter);
void Task_Send_To_Screen(void *pvParameters);

// Return absolute humidity [mg/m^3] with approximation formula
uint32_t getAbsoluteHumidity(float temperature, float humidity) {
  const float absoluteHumidity = 216.7f * ((humidity / 100.0f) * 6.112f * exp((17.62f * temperature) / (243.12f + temperature)) / (273.15f + temperature)); // [g/m^3]
  const uint32_t absoluteHumidityScaled = static_cast<uint32_t>(1000.0f * absoluteHumidity); // [mg/m^3]
  return absoluteHumidityScaled;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  dataQueue = xQueueCreate(5, sizeof(SensorData)); // Create queue for sensor data

  if (!sgp.begin()) {
    Serial.println("SGP30 not found");
    while (1);
  }
  Serial.print("Found SGP30 serial #");
  Serial.print(sgp.serialnumber[0], HEX);
  Serial.print(sgp.serialnumber[1], HEX);
  Serial.println(sgp.serialnumber[2], HEX);

  dht.begin();

  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  if (rtc.lostPower()) {
    Serial.println("RTC lost power, please set the time!");
    // Adjust to the correct time if RTC lost power
    Serial.println("Use the format YYYY MM DD HH MM SS to set the time.");
    while (!Serial.available()) {
      // Wait for user input
    }
    int year = Serial.parseInt();
    int month = Serial.parseInt();
    int day = Serial.parseInt();
    int hour = Serial.parseInt();
    int minute = Serial.parseInt();
    int second = Serial.parseInt();
    rtc.adjust(DateTime(year, month, day, hour, minute, second));
    Serial.println("RTC time set.");
  }

  gravityTds.setPin(A1);
  gravityTds.setAref(5.0);
  gravityTds.setAdcRange(1024);
  gravityTds.begin();

  pinMode(MOISTURE_PIN, OUTPUT);  // Set the moisture control pin as output
  pinMode(RELAY_PIN_1, OUTPUT);
  pinMode(RELAY_PIN_2, OUTPUT);
  pinMode(RELAY_PIN_3, OUTPUT);
  pinMode(RELAY_PIN_4, OUTPUT);
  pinMode(RELAY_PIN_5, OUTPUT);
  pinMode(RELAY_PIN_6, OUTPUT);
  pinMode(RELAY_PIN_7, OUTPUT);
  pinMode(RELAY_PIN_8, OUTPUT);

  // Read relay states from EEPROM and initialize relays
  readRelayStates();

  // Initialize the SD card
  Serial.print("Initializing SD card...");
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("initialization failed!");
    while (1);
  }
  Serial.println("initialization done.");

  xTaskCreate(Task_Send_To_Screen, "SenderTask", 128, NULL, 2, NULL);
  xTaskCreate(Task_DataReading, "Data Reading", 1000, NULL, 3, &dataReadingTaskHandle);
  xTaskCreate(Task_DataWriting, "Data Writing", 1000, NULL, 1, &dataWritingTaskHandle);
  xTaskCreate(Task_SerialCommandHandler, "SerialCommandHandler", 2048, NULL, 1, NULL);

  screenQueue = xQueueCreate(5, sizeof(float)); // Change the size if needed
}


void loop() {
  // Nothing to be done here because we're using FreeRTOS tasks
}

void Task_DataReading(void* pvParameter) {
  while (1) {
    SensorData sensorData;

    // DHT
    sensorData.temperature = dht.readTemperature();
    sensorData.humidity = dht.readHumidity();

    if (isnan(sensorData.temperature) || isnan(sensorData.humidity)) {
      Serial.println("Failed to read from DHT sensor!");
      vTaskDelay(500 / portTICK_PERIOD_MS);
      continue; // Skip the rest of this loop iteration
    }

    // Calculate absolute humidity and set it to SGP30
    uint32_t absoluteHumidity = getAbsoluteHumidity(sensorData.temperature, sensorData.humidity);
    sgp.setHumidity(absoluteHumidity);

    // SGP30
    if (!sgp.IAQmeasure()) {
      Serial.println("Failed to read from SGP30 sensor");
      vTaskDelay(500 / portTICK_PERIOD_MS); // Wait before trying again
      continue; // Skip the rest of this loop iteration
    }

    sensorData.co2 = sgp.eCO2;
    sensorData.tvoc = sgp.TVOC;

    if (!sgp.IAQmeasureRaw()) {
      Serial.println("Raw Measurement failed");
    }

    // Moisture
    digitalWrite(MOISTURE_PIN, HIGH);  // Turn on the moisture sensor
    delay(10);
    int sensor_analog = analogRead(A2);
    digitalWrite(MOISTURE_PIN, LOW);   // Turn off the moisture sensor
    sensorData.moisture = 100.0 - ((float)sensor_analog / 1023.0) * 100.0;

    // pH
    int buf[10], temp;
    unsigned long int avgValue = 0;
    for (int i = 0; i < 10; i++) {
      buf[i] = analogRead(A0);
      delay(10);
    }
    for (int i = 0; i < 9; i++) {
      for (int j = i + 1; j < 10; j++) {
        if (buf[i] > buf[j]) {
          temp = buf[i];
          buf[i] = buf[j];
          buf[j] = temp;
        }
      }
    }
    for (int i = 2; i < 8; i++) {
      avgValue += buf[i];
    }
    float phValue = (float)avgValue * 5.0 / 1024 / 6;
    phValue = 3.5 * phValue;
    sensorData.pH = phValue;

    // TDS
    gravityTds.setTemperature(sensorData.temperature);
    gravityTds.update();
    sensorData.tdsValue = gravityTds.getTdsValue();

    // RTC
    sensorData.timestamp = rtc.now();

    // Send sensor data to the queue
    xQueueSend(dataQueue, &sensorData, portMAX_DELAY);

    // Print the sensor data to the serial monitor
    Serial.print(sensorData.timestamp.unixtime());
    Serial.print(",");
    Serial.print(sensorData.temperature);
    Serial.print(",");
    Serial.print(sensorData.humidity);
    Serial.print(",");
    Serial.print(sensorData.moisture);
    Serial.print(",");
    Serial.print(sensorData.pH);
    Serial.print(",");
    Serial.print(sensorData.tdsValue);
    Serial.print(",");
    Serial.print(sensorData.co2);
    Serial.print(",");
    Serial.print(sensorData.tvoc);
    Serial.println(",");

    vTaskDelay(2000 / portTICK_PERIOD_MS);
  }
}

void Task_DataWriting(void* pvParameter) {
  while (1) {
    SensorData sensorData;

    if (xQueueReceive(dataQueue, &sensorData, portMAX_DELAY) == pdTRUE) {
      // Open data file for appending
      dataFile = SD.open("data.txt", FILE_WRITE);
      if (dataFile) {
        // Write sensor data to file
        dataFile.print(sensorData.timestamp.unixtime());
        dataFile.print(",");
        dataFile.print(sensorData.temperature);
        dataFile.print(",");
        dataFile.print(sensorData.humidity);
        dataFile.print(",");
        dataFile.print(sensorData.moisture);
        dataFile.print(",");
        dataFile.print(sensorData.pH);
        dataFile.print(",");
        dataFile.print(sensorData.tdsValue);
        dataFile.print(",");
        dataFile.print(sensorData.co2);
        dataFile.print(",");
        dataFile.println(sensorData.tvoc);

        // Close the file
        dataFile.close();
      } else {
        Serial.println("Error opening data file!");
      }
    }
    vTaskDelay(10 / portTICK_PERIOD_MS); // Non-blocking delay
  }
}

void Task_Send_To_Screen(void* pvParameter) {
  while (1) {
    SensorData sensorData;
    if (xQueueReceive(dataQueue, &sensorData, portMAX_DELAY) == pdTRUE) {
      // Readings to send to screen
      int temp = (int)(sensorData.temperature);
      int hum = (int)(sensorData.humidity);
      int mos = (int)(sensorData.moisture);
      int ph = (int)(sensorData.pH);
      int tds = (int)(sensorData.tdsValue);
      int co2 = (int)(sensorData.co2);
      int tvoc = (int)(sensorData.tvoc);

      // Sending readings to screen
      Wire.beginTransmission(SLAVE_ADDRESS);
      Wire.write((uint8_t*)&temp, sizeof(temp));
      Wire.write((uint8_t*)&hum, sizeof(hum));
      Wire.write((uint8_t*)&mos, sizeof(mos));
      Wire.write((uint8_t*)&ph, sizeof(ph));
      Wire.write((uint8_t*)&tds, sizeof(tds));
      Wire.write((uint8_t*)&co2, sizeof(co2));
      Wire.write((uint8_t*)&tvoc, sizeof(tvoc));
      Wire.endTransmission();
    }
    vTaskDelay(2000 / portTICK_PERIOD_MS);
  }
}

void Task_SerialCommandHandler(void *pvParameters) {
  char command[32];
  int index = 0;
  char receivedChar;

  while (1) {
    if (Serial.available() > 0) {
      receivedChar = Serial.read();
      if (receivedChar == '\n' || receivedChar == '\r') {
        command[index] = '\0'; // Null terminate the string
        processCommand(command); // Process the complete command
        index = 0; // Reset index for the next command
      } else if (index < 31) {
        command[index++] = receivedChar;
      }
    }
    vTaskDelay(10 / portTICK_PERIOD_MS); // Small delay to allow other tasks
  }
}

void saveRelayStates() {
  for (int i = 0; i < 8; i++) {
    EEPROM.write(i, digitalRead(RELAY_PIN_1 + i));
  }
}

void readRelayStates() {
  for (int i = 0; i < 8; i++) {
    int state = EEPROM.read(i);
    digitalWrite(RELAY_PIN_1 + i, state);
  }
}

void processCommand(char* command) {
  if (strncmp(command, "OFF ALL", 7) == 0) {
    for (int relayNum = 1; relayNum <= 8; relayNum++) {
      digitalWrite(RELAY_PIN_1 + relayNum - 1, HIGH); // Correct pin mapping
    }
    saveRelayStates(); // Save the states after changing
    Serial.println("All relays turned OFF");
  } else if (strncmp(command, "ON ALL", 6) == 0) {
    for (int relayNum = 1; relayNum <= 8; relayNum++) {
      digitalWrite(RELAY_PIN_1 + relayNum - 1, LOW); // Correct pin mapping
    }
    saveRelayStates(); // Save the states after changing
    Serial.println("All relays turned ON");
  } else if (strncmp(command, "OFF ", 4) == 0) {
    int relayNum = atoi(command + 4);
    if (relayNum >= 1 && relayNum <= 8) {
      digitalWrite(RELAY_PIN_1 + relayNum - 1, HIGH); // Correct pin mapping
      saveRelayStates(); // Save the states after changing
      Serial.print("Relay ");
      Serial.print(relayNum);
      Serial.println(" turned OFF");
    }
  } else if (strncmp(command, "ON ", 3) == 0) {
    int relayNum = atoi(command + 3);
    if (relayNum >= 1 && relayNum <= 8) {
      digitalWrite(RELAY_PIN_1 + relayNum - 1, LOW); // Correct pin mapping
      saveRelayStates(); // Save the states after changing
      Serial.print("Relay ");
      Serial.print(relayNum);
      Serial.println(" turned ON");
    }
  } else {
    Serial.println("Invalid command");
  }
}