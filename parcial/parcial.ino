#include <Arduino.h>
#include <DHT.h>
#include "MQ135.h"
#include <Thread.h>

//Iniciamos el hilo 
Thread myThread = Thread();

// Definir pines para los sensores
#define DHT_PIN 15
#define LM35_PIN 4
#define MQ135_PIN 2

// Definir objetos para los sensores
DHT dht(DHT_PIN, DHT22);
MQ135 gasSensor = MQ135(MQ135_PIN);
// Variables globales para almacenar los datos de los sensores

//inicializamos variables para el filtro de media movil
const int numReadings = 10;
int readings[numReadings];
int readIndex = 0;
float promedio = 0;
float total = 0;

float humidity = 0;
float lm35Temp = 0;
float mq135Value = 0;

//inicializamos variables para el filtro de kalman
float kalmanGain;
float estimate = 0;
float error_estimate = 1;
float error_measurement = 0.5;
float measurement =0;


// Función para leer el sensor DHT22
void niceCallback() {
  // Lectura de temperatura y humedad

  measurement = dht.readHumidity();
  kalmanGain=error_estimate/(error_estimate + error_measurement);
  estimate = estimate + kalmanGain * (measurement - estimate);
  error_estimate = (1-kalmanGain)*error_estimate;
  humidity = estimate;
  Serial.print(humidity);

}

// Función para leer el sensor LM35
void readLM35() {
  // Lectura de temperatura del sensor LM35
  int lm35_value = analogRead(LM35_PIN);
  total = total - readings[readIndex];
  readings[readIndex] = analogRead(LM35_PIN);
  total = total + readings[readIndex];
  readIndex = (readIndex + 1) % numReadings;
  promedio = total / numReadings;
  lm35Temp = (promedio * 5.0 / 4096.0) * 100.0;
}
void readMQ135() {
  // Lectura del valor del sensor MQ135

  mq135Value = gasSensor.getPPM();
}

// Función para convertir ppm a concentración de CO2 (en %)
float ppm_to_co2(float ppm_value) {
    // Relación específica entre ppm y CO2 (por ejemplo, 1 ppm = 0.0004% de CO2)
    float co2_percentage = ppm_value * 0.0004;
    return co2_percentage;
}

// Función para convertir ppm a concentración de NH3 (en %)
float ppm_to_nh3(float ppm_value) {
    // Relación específica entre ppm y NH3 (por ejemplo, 1 ppm = 0.0002% de NH3)
    float nh3_percentage = ppm_value * 0.0002;
    return nh3_percentage;
}




void setup() {
  // Inicializar comunicación serial
  Serial.begin(9600);
    for(int i = 0; i < numReadings; i++){
      readings[i];
    }

  // Inicializar sensor DHT22
  dht.begin();
  myThread.onRun(niceCallback);
	myThread.setInterval(500);
}

void loop() {
  if(myThread.shouldRun())
		myThread.run();
  // Leer los sensores en hilos separados
  
  readLM35();
  readMQ135();

  // Convertir valores de ppm a concentraciones de CO2 y NH3
  float co2_concentration = ppm_to_co2(mq135Value);
  float nh3_concentration = ppm_to_nh3(mq135Value);

  // Enviar los datos por comunicación serial

  Serial.print(",");
  Serial.print(lm35Temp);
  Serial.print(",");
  Serial.print(co2_concentration);
  Serial.print(",");
  Serial.println(nh3_concentration);

  delay(500); // Esperar 5 segundos antes de la próxima lectura
}