// *****************************************
// ***     PLATAFORMA EV ARDUINO         ***
// ***        AKAFLIEG MADRID            ***
// *** UNIVERSIDAD POLITECNICA DE MADRID ***
// *****************************************

#include <SoftwareSerial.h>
#include <SimpleDHT.h>

//Módulo Bluetooh
SoftwareSerial mySerial(2,3); //Pines (Tx,Rx). Ojo conectar a 3.3V no 5V

//Termistor
int tempPin = 0; // Pin analógico

//Sensor temperatura y humedad
int pinDHT11 = 2; // Pin digital
SimpleDHT11 dht11;
				
void setup(){
				
  mySerial.begin(9600);
  Serial.begin(9600);
  delay(100);
							
}

void loop(){
 //Modulo Bluetooh
	 if (Serial.available()>0){
		  mySerial.write(Serial.read());
	 }
				
	 if (mySerial.available()>0){
	   Serial.write(mySerial.read());
	 }
 
	//Termistor
				
	 int tempReading = analogRead(tempPin);
  
   double tempK = log(10000.0 * ((1024.0 / tempReading - 1)));
   
		tempK = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * tempK * tempK )) * tempK );       //  Temp Kelvin
  
   float tempC = tempK - 273.15;            // Convert Kelvin to Celcius
 
  /*  replaced
    float tempVolts = tempReading * 5.0 / 1024.0;
    float tempC = (tempVolts - 0.5) * 10.0;
    float tempF = tempC * 9.0 / 5.0 + 32.0;
  */	
		
  Serial.print("Temp termistor(C):", tempC);
	
	 delay (500);
				
	//Módulo temperatura y humedad
	
  Serial.println("=================================");
  Serial.println("Sample DHT11...");
  
  byte temperature = 0;   // (read with raw sample data.
  byte humidity = 0;
  byte data[40] = {0};
  if (dht11.read(pinDHT11, &temperature, &humidity, data)) {
    Serial.print("Read DHT11 failed");
    return;
  }
  
  Serial.print("Sample RAW Bits: ");
  for (int i = 0; i < 40; i++) {
    Serial.print((int)data[i]);
    if (i > 0 && ((i + 1) % 4) == 0) {
      Serial.print(' ');
    }
  }
  Serial.println("");
  
  Serial.print("Sample OK: ");
  Serial.print((int)temperature); Serial.print(" *C, ");
  Serial.print((int)humidity); Serial.println(" %");
  
  delay(1000); 	// DHT11 sampling rate is 1HZ.					
}
