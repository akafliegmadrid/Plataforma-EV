// *****************************************
// ***     PLATAFORMA EV ARDUINO         ***
// ***        AKAFLIEG MADRID            ***
// *** UNIVERSIDAD POLITECNICA DE MADRID ***
// *****************************************

#include <Adafruit_BME280.h>

typedef struct {
  uint32_t timestamp;
  float temperature;
  float pressure;
  float humidity;
} data_t;

const uint32_t sampleTime = 500;  // [ms]
uint32_t readingTime;
data_t data;
Adafruit_BME280 sensor;

void setup () {

  Serial.begin(9600);
  if (!sensor.begin()) {
    Serial.println("----- Sensor not found -----");
    while(true);
  }

}

void loop () {

  readingTime = millis();
  read_data(data);
  send_data(data);

  // Delay para que se envien datos cada 'sampleTime' ms
  while ((uint32_t)(millis()-readingTime) < sampleTime) {}

}

void read_data (data_t &data) {

  data.timestamp   = millis();
  data.temperature = sensor.readTemperature();
  data.pressure    = sensor.readPressure();
  data.humidity    = sensor.readHumidity();

}

void send_data (data_t data) {

  Serial.print(data.timestamp);   Serial.print(',');
  Serial.print(data.temperature); Serial.print(',');
  Serial.print(data.pressure);    Serial.print(',');
  Serial.println(data.humidity);

}
