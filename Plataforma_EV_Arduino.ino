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

  read_data(data);
  send_data(data);

  delay(50);

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
