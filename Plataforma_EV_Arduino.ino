// *****************************************
// ***     PLATAFORMA EV ARDUINO         ***
// ***        AKAFLIEG MADRID            ***
// *** UNIVERSIDAD POLITECNICA DE MADRID ***
// *****************************************

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

/* Parametros */
const uint32_t sampleTime = 500;  // [ms]

/* Variables locales */
typedef struct {
  uint32_t timestamp;
  float temperature;
  float pressure;
  float humidity;
} data_t;

uint32_t readingTime;
data_t data;
Adafruit_BME280 sensor;

/* Setup */
void setup () {

#ifdef ARDUINO_AVR_NANO_EVERY
  Serial1.begin(9600);
#elif ARDUINO_AVR_NANO
  Serial.begin(9600);
#endif

  if (!sensor.begin(0x76)) {
#ifdef ARDUINO_AVR_NANO_EVERY
    Serial1.println("----- Sensor not found -----");
#elif ARDUINO_AVR_NANO
    Serial.println("----- Sensor not found -----");
#endif
    while(true);
  }

}

/* Bucle principal */
void loop () {

  readingTime = millis();
  read_data(data);
  send_data(data);

  // Delay para que se envien datos cada 'sampleTime' ms
  while ((uint32_t)(millis()-readingTime) < sampleTime) {}

}

/* Funcion de lectura */
void read_data (data_t &data) {

  data.timestamp   = millis();
  data.temperature = sensor.readTemperature();
  data.pressure    = sensor.readPressure();
  data.humidity    = sensor.readHumidity();

}

/* Funcion de escritura */
void send_data (data_t data) {

#ifdef ARDUINO_AVR_NANO_EVERY
  Serial1.print(data.timestamp);   Serial1.print(',');
  Serial1.print(data.temperature); Serial1.print(',');
  Serial1.print(data.pressure);  Serial1.print(',');
  Serial1.println(data.humidity);
#elif ARDUINO_AVR_NANO
  Serial.print(data.timestamp);   Serial.print(',');
  Serial.print(data.temperature); Serial.print(',');
  Serial.print(data.pressure);  Serial.print(',');
  Serial.println(data.humidity);
#endif

}
