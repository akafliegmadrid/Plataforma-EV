// *****************************************
// ***     PLATAFORMA EV ARDUINO         ***
// ***        AKAFLIEG MADRID            ***
// *** UNIVERSIDAD POLITECNICA DE MADRID ***
// *****************************************

#include <SoftwareSerial.h>

//Módulo Bluetooh
SoftwareSerial mySerial(2,3); //Pines (Tx,Rx). Ojo conectar a 3.3V no 5V

//Sensor temperatura
int tempPin = 0; // Pin analógico

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
 
	//Sensor temperatura
	 int tempReading = analogRead(tempPin);
  
   double tempK = log(10000.0 * ((1024.0 / tempReading - 1)));
   
		tempK = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * tempK * tempK )) * tempK );       //  Temp Kelvin
  
   float tempC = tempK - 273.15;            // Convert Kelvin to Celcius
 
  /*  replaced
    float tempVolts = tempReading * 5.0 / 1024.0;
    float tempC = (tempVolts - 0.5) * 10.0;
    float tempF = tempC * 9.0 / 5.0 + 32.0;
  */	
		
  Serial.print("Temp (C):", tempC);
	
	delay (500);
}
