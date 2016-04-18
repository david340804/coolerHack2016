//set up the RGB LED pins
int rPin = 2;
int gPin = 3;
int bPin = 4;

//photo detector pin
int photoPin = A0;
int readStepLightDelay = 50;

//row sensor setup
int rowSensorPin = A1;
int raw = 0;
float Vin = 5; 
float Vout = 0;
float Rset = 216;
float Rvar = 0;
float buffer = 0;

//time between reads of the data
int readStepDelay = 100;

void setup() {
  // put your setup code here, to run once:
  pinMode(rPin,OUTPUT);
  pinMode(gPin,OUTPUT);
  pinMode(bPin,OUTPUT);

  Serial.begin(9600);
}

void loop() {
  //Detect the RGB LED reflection for the different colors
  int photoVal = analogRead(photoPin);

  setColor("r");
  delay(readStepLightDelay);
  int rVal = analogRead(photoPin);
  delay(readStepDelay);

  setColor("g");
  delay(readStepLightDelay);
  int gVal = analogRead(photoPin);
  delay(readStepDelay);

  setColor("b");
  delay(readStepLightDelay);
  int bVal = analogRead(photoPin);
  delay(readStepDelay);

  //row sensor reading
  raw = analogRead(rowSensorPin);
  Rvar = 0;
  if(raw){
    buffer = raw * Vin;
    Vout = (buffer)/1024.0;
    buffer = (Vin/Vout) - 1;
    Rvar = Rset * buffer;
  }
  Rvar = int(Rvar);


  //send off the serialized data to the python script
  String ser = "Fingerprint: r: " + String(rVal) + " g: " + gVal + " b: " + bVal + " row: " + int(Rvar);
  Serial.println(ser);

  //turn off LED between reads
  setColor("0");
  
  delay(readStepDelay);
}

/**
 * Set the color of the RGB LED using booleans for red green and blue pins
 */
void writeColor(boolean r, boolean g, boolean b){
  digitalWrite(rPin,r);
  digitalWrite(gPin,g);
  digitalWrite(bPin,b);
}

/**
 * set the color of the RGB LED using string tokens
 */
void setColor(String str){
  
  int r = 0;
  int g = 0;
  int b = 0;
  if(str.indexOf('r') != -1){
    r = 1;
  }
  if(str.indexOf('g') != -1){
    g = 1;
  }
  if(str.indexOf('b') != -1){
    b = 1;
  }
  if(str.indexOf('0') != -1){
    r = 0;
    g = 0;
    b = 0;
  }
  writeColor(r,g,b);
}

