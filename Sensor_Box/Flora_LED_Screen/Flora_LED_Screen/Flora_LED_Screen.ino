#include <Arduino.h>
#include <RGBmatrixPanel.h>
#include <Fonts/Picopixel.h>
#include <Wire.h>

#define CLK 11 
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3
RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, false, 64);

#define SLAVE_ADDRESS 9

int received_data[7] = {0}; 
void updateDisplay();
void receiveEvent(int byteCount);

void setup() {
  Serial.begin(115200);
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveEvent);
  matrix.begin();
  matrix.setFont(&Picopixel);
}

void loop() {
  // Update display with received data
  updateDisplay();

  delay(2000); // Delay for 1 second
}

void updateDisplay() {
  // Clear screen (fill with black color)
  matrix.fillScreen(matrix.Color333(0, 0, 0));

  // Set text color
  matrix.setTextColor(matrix.Color333(255, 0, 0)); // White for text

  // Print sensor data on screen
  matrix.setCursor(2, 6);
  matrix.print("Temp: ");
  matrix.print(received_data[0]);

  matrix.setCursor(2, 13);
  matrix.print("Hum: ");
  matrix.print(received_data[1]);

  matrix.setCursor(33, 13);
  matrix.print("Moist: ");
  matrix.print(received_data[2]);

  matrix.setCursor(2, 20);
  matrix.print("pH: ");
  matrix.print(received_data[3]);

  matrix.setCursor(33, 20);
  matrix.print("TDS: ");
  matrix.print(received_data[4]);

  matrix.setCursor(2, 27);
  matrix.print("CO2: ");
  matrix.print(received_data[5]);

  matrix.setCursor(33, 27);
  matrix.print("TVOC: ");
  matrix.print(received_data[6]);
}

void receiveEvent(int byteCount) {
  if (byteCount >= sizeof(int) * 7) {
    // Read the received data into the array
    for (int i = 0; i < 7; i++) {
      Wire.readBytes((uint8_t*)&received_data[i], sizeof(received_data[i]));
    }
  }
}
