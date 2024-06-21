#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(1500); // set PWM frequency to 1500Hz
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any trailing whitespace
    if (command.startsWith("PWM ALL")) {
      int dutyCycle = command.substring(8).toInt();
      dutyCycle = map(dutyCycle, 0, 100, 0, 4095); // map duty cycle from 0-100 to 0-4095
      for (int i = 0; i < 8; i++) {
        pwm.setPWM(i, 0, dutyCycle);
      }
      Serial.print("All PWM channels set to ");
      Serial.print(dutyCycle);
      Serial.println(" (out of 4095)");
    } else if (command.startsWith("PWM OFF")) {
      for (int i = 0; i < 8; i++) {
        pwm.setPWM(i, 0, 0);
      }
      Serial.println("All PWM channels turned off");
    } else if (command.startsWith("PWM ")) {
      int spaceIndex = command.indexOf(' ', 4);
      if (spaceIndex > 0) {
        int channel = command.substring(4, spaceIndex).toInt();
        int dutyCycle = command.substring(spaceIndex + 1).toInt();
        dutyCycle = map(dutyCycle, 0, 100, 0, 4095); // map duty cycle from 0-100 to 0-4095
        pwm.setPWM(channel, 0, dutyCycle);
        Serial.print("PWM channel ");
        Serial.print(channel);
        Serial.print(" set to ");
        Serial.print(dutyCycle);
        Serial.println(" (out of 4095)");
      }
    }
  }
}
