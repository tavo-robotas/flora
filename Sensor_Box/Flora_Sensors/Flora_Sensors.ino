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

// Initialize sensors
Adafruit_SGP30 sgp;
RTC_DS3231 rtc;
DHT dht(DHTPIN, DHTTYPE);
GravityTDS gravityTds;

// Create a queue to hold sensor data
QueueHandle_t dataQueue;

// File for SD card operations
File dataFile;

// Flag to send data to serial
bool sendDataToSerial = false;

// Structure to hold sensor data
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

// Task handles for FreeRTOS tasks
TaskHandle_t dataReadingTaskHandle;
TaskHandle_t dataWritingTaskHandle;

// Function prototypes
void Task_SerialCommandHandler(void* pvParameter);
void Task_DataReading(void* pvParameter);
void Task_DataWriting(void* pvParameter);
void Task_Send_To_Screen(void* pvParameters);
uint32_t getAbsoluteHumidity(float temperature, float humidity);

void setup() {
  Serial.begin(115200);
  Serial1.begin(9600); // Begin Serial1 for communication with NodeMCU
  Wire.begin();

  // Create queue for sensor data
  dataQueue = xQueueCreate(5, sizeof(SensorData));

  // Initialize SGP30 sensor
  if (!sgp.begin()) {
    Serial.println("SGP30 not found");
    while (1);
  }
  Serial.print("Found SGP30 serial #");
  Serial.print(sgp.serialnumber[0], HEX);
  Serial.print(sgp.serialnumber[1], HEX);
  Serial.println(sgp.serialnumber[2], HEX);

  // Initialize DHT sensor
  dht.begin();

  // Initialize RTC
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  if (rtc.lostPower()) {
    Serial.println("RTC lost power, please set the time!");
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

  // Initialize GravityTDS sensor
  gravityTds.setPin(A1);
  gravityTds.setAref(5.0);
  gravityTds.setAdcRange(1024);
  gravityTds.begin();

  // Initialize relay pins
  pinMode(MOISTURE_PIN, OUTPUT);
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
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD card initialization failed!");
    while (1);
  }

  // Test SD card by creating a file
  dataFile = SD.open("test.txt", FILE_WRITE);
  if (dataFile) {
    dataFile.println("SD card initialization successful.");
    dataFile.close();
  } else {
    Serial.println("Error creating test file on SD card.");
  }

  // Create FreeRTOS tasks
  xTaskCreate(Task_Send_To_Screen, "SenderTask", 128, NULL, 5, NULL);
  xTaskCreate(Task_DataReading, "Data Reading", 1000, NULL, 3, &dataReadingTaskHandle);
  xTaskCreate(Task_DataWriting, "Data Writing", 1500, NULL, 4, &dataWritingTaskHandle);
  xTaskCreate(Task_SerialCommandHandler, "SerialCommandHandler", 2048, NULL, 1, NULL);
}

void loop() {
  // Nothing to be done here because we're using FreeRTOS tasks
}

// Function to calculate absolute humidity
uint32_t getAbsoluteHumidity(float temperature, float humidity) {
  const float absoluteHumidity = 216.7f * ((humidity / 100.0f) * 6.112f * exp((17.62f * temperature) / (243.12f + temperature)) / (273.15f + temperature)); // [g/m^3]
  const uint32_t absoluteHumidityScaled = static_cast<uint32_t>(1000.0f * absoluteHumidity); // [mg/m^3]
  return absoluteHumidityScaled;
}

void Task_DataReading(void* pvParameter) {
  while (1) {
    SensorData sensorData;

    // DHT sensor readings
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

    // SGP30 sensor readings
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

    // Moisture sensor readings
    digitalWrite(MOISTURE_PIN, HIGH);  // Turn on the moisture sensor
    delay(10);
    int sensor_analog = analogRead(A2);
    digitalWrite(MOISTURE_PIN, LOW);   // Turn off the moisture sensor
    sensorData.moisture = 100.0 - ((float)sensor_analog / 1023.0) * 100.0;

    // pH sensor readings
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

    // TDS sensor readings
    gravityTds.setTemperature(sensorData.temperature);
    gravityTds.update();
    sensorData.tdsValue = gravityTds.getTdsValue();

    // RTC timestamp
    sensorData.timestamp = rtc.now();

    // Send sensor data to the queue
    if (xQueueSend(dataQueue, &sensorData, portMAX_DELAY) != pdPASS) {
      Serial.println("Failed to send data to queue.");
    }

    // Print the sensor data to the serial monitor if required
    if (sendDataToSerial) {
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
      Serial.println();
    }

    vTaskDelay(2000 / portTICK_PERIOD_MS);
  }
}

void Task_DataWriting(void* pvParameter) {
  while (1) {
    SensorData sensorData;

    // Receive data from the queue
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
    vTaskDelay(1000 / portTICK_PERIOD_MS); // Non-blocking delay
  }
}

void Task_Send_To_Screen(void* pvParameters) {
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
  } else if (strcmp(command, "SEND DATA ON") == 0) {
    sendDataToSerial = true;
    Serial.println("Data sending to serial enabled");
  } else if (strcmp(command, "SEND DATA OFF") == 0) {
    sendDataToSerial = false;
    Serial.println("Data sending to serial disabled");
  } else if (strncmp(command, "DATA ", 5) == 0) {
    char* params = command + 5;
    char* first = strtok(params, " ");
    char* second = strtok(NULL, " ");
    if (first && second) {
      long startTime = atol(first);
      long endTime = atol(second);
      readDataInRange(startTime, endTime);
    } else if (strcmp(first, "ALL") == 0) {
      plotAllData();
    } else if (strcmp(first, "FLUSH") == 0) {
      flushData();
    } else {
      Serial.println("Invalid command format. Use DATA <start> <end>, DATA ALL, or DATA FLUSH");
    }
  } else if (strncmp(command, "PWM ", 4) == 0) {
    Serial.println("Received PWM command:");
    Serial.println(command);
    Serial1.println(command); // Forward PWM commands to NodeMCU
    Serial.println("PWM command forwarded to NodeMCU");
  } else {
    Serial.println("Invalid command");
  }
}

void plotAllData() {
  File dataFile = SD.open("data.txt", FILE_READ);
  if (!dataFile) {
    Serial.println("Error opening data file!");
    return;
  }

  while (dataFile.available()) {
    String line = dataFile.readStringUntil('\n');
    Serial.println(line);
  }

  dataFile.close();
}

void flushData() {
  if (SD.exists("data.txt")) {
    SD.remove("data.txt");
  }

  dataFile = SD.open("data.txt", FILE_WRITE);
  if (!dataFile) {
    Serial.println("Error creating data file after flushing!");
    return;
  }

  dataFile.close();
  Serial.println("All data flushed from data.txt");
}

void readDataInRange(long startTime, long endTime) {
  File dataFile = SD.open("data.txt", FILE_READ);
  if (!dataFile) {
    Serial.println("Error opening data file!");
    return;
  }

  // Temporary storage for data outside the specified range
  String tempData = "";

  while (dataFile.available()) {
    String line = dataFile.readStringUntil('\n');
    long timestamp = line.substring(0, line.indexOf(',')).toInt();
    if (timestamp >= startTime && timestamp <= endTime) {
      Serial.println(line); // Send the line through serial
    } else {
      tempData += line + "\n"; // Store lines outside the range
    }
  }

  dataFile.close();

  // Reopen the file for writing to clear and update it
  dataFile = SD.open("data.txt", FILE_WRITE);
  if (!dataFile) {
    Serial.println("Error opening data file for writing!");
    return;
  }

  dataFile.print(tempData); // Write back the data outside the specified range
  dataFile.close();
}