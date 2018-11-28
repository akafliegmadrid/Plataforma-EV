// *****************************************
// ***     PLATAFORMA EV ARDUINO         ***
// ***        AKAFLIEG MADRID            ***
// *** UNIVERSIDAD POLITECNICA DE MADRID ***
// *****************************************

//Librerías usadas
  
  #include <SoftwareSerial.h>
  #include <dht_nonblocking.h>

//Módulo Bluetooh
  
  SoftwareSerial mySerial(2,3); //Pines (Tx,Rx) del BLE. Ojo conectar a 3.3V no 5V

//Termistor
  
  int tempPin = A0; // Pin data (analógico)

//Sensor temperatura y humedad
  
  #define DHT_SENSOR_TYPE DHT_TYPE_11
  static const int DHT_SENSOR_PIN = 4; //Pin data (digital)
  DHT_nonblocking dht_sensor( DHT_SENSOR_PIN, DHT_SENSOR_TYPE );

//Interruptor principal
  
  int system_recording = 0; // 0: No emite; 1: Emite
  int switch_recording = 5; // Pin 5
				
void setup(){
	
	//Inicializar monitores serial			
    
    mySerial.begin(9600); // Serial del BLE
    Serial.begin(9600); // Serial del monitor PC
  
  //Interruptor principial
    
    pinMode(switch_recording,INPUT_PULLUP);  

  delay(100);       
}

void loop(){

  //Interruptor principal
  
  if( (digitalRead(switch_recording) == LOW)){system_recording = 1;}
  else {system_recording = 0;}

  if( system_recording == 1){
  
  //Modulo Bluetooh
  
    if (Serial.available()>0){
		  mySerial.write(Serial.read());
	  }
				
	  if (mySerial.available()>0){
	    Serial.write(mySerial.read());
	  }
 
  //Termistor
  
	  int tempReading = analogRead(tempPin);
    double tempK_term = log(10000.0 * ((1024.0 / tempReading - 1)));
		  tempK_term = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * tempK_term * tempK_term )) * tempK_term );       //  Temp Kelvin
    float tempC_term = tempK_term - 273.15;            // Convert Kelvin to Celcius
				
  //Módulo temperatura y humedad
	  
    float tempC_DHT;
    float humidity_DHT;

  //Printeo de variables en seriales
  
    if( measure_environment( &tempC_DHT, &humidity_DHT ) == true ){
      Serial.print(tempC_term); 
      Serial.print(";"); 
      Serial.print( tempC_DHT, 1 ); 
      Serial.print(";"); 
      Serial.print( humidity_DHT, 1 ); 
      Serial.println(";");
    }

    if( measure_environment( &tempC_DHT, &humidity_DHT ) == true ){
      mySerial.print(tempC_term); 
      mySerial.print(";"); 
      mySerial.print( tempC_DHT, 1 ); 
      mySerial.print(";"); 
      mySerial.print( humidity_DHT, 1 ); 
      mySerial.println(";");
    }
  }					
}

//Función de confirmación de variables medidas

  static bool measure_environment( float *tempC_DHT, float *humidity_DHT )
  {
    static unsigned long measurement_timestamp = millis( );
  
    /* Measure once every four seconds. */
    if( millis( ) - measurement_timestamp > 3000ul )
    {
      if( dht_sensor.measure( tempC_DHT, humidity_DHT ) == true )
      {
        measurement_timestamp = millis( );
        return( true );
      }
    }
  
    return( false );
  }		
