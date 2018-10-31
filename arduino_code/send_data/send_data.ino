#include <Wire.h>
#include <Servo.h>

int RightMotor = 9; //5    // pin maping according to schematics 
int LeftMotor = 10;  //7
int R_dir = 8; 
int L_dir = 12;
const int pwm1 = 3;
String c ;


int ch5,ch6,ch7;
float ch4;
float min = 828 ;
float max = 37630;
float sonar_const = ( 254.0 * 2.54 ) / ( max - min ) ;
int Buzer_pin = 11;

void setup() {
  Serial.begin(9600);
  pinMode(7,INPUT);
  pinMode(3,INPUT);
  pinMode(4,INPUT); //Ultrasonic sensor
  pinMode(5,INPUT);
  pinMode(6,INPUT);
  pinMode(2,INPUT);
  TCCR1B = TCCR1B & 0B11111000 | 0B00000100;  
  pinMode(RightMotor,OUTPUT); 
  pinMode(LeftMotor,OUTPUT);
  pinMode(R_dir,OUTPUT); 
  pinMode(L_dir,OUTPUT); 
  pinMode(Buzer_pin,OUTPUT);
}

String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
void Forward(unsigned int Pwm) 
{ 
   digitalWrite(R_dir,LOW); 
   digitalWrite(L_dir,LOW); 
   analogWrite(RightMotor,Pwm);  
   analogWrite(LeftMotor,Pwm-4); 
} 
void Backward(unsigned int Pwm) 
{ 
   digitalWrite(R_dir,HIGH); 
   digitalWrite(L_dir,HIGH); 
   analogWrite(RightMotor,Pwm);  
   analogWrite(LeftMotor,Pwm); 
} 
void Left(unsigned int Pwm) 
{ 
   //digitalWrite(R_dir,LOW); 
   //digitalWrite(L_dir,HIGH); 
   //analogWrite(RightMotor,Pwm);  
   //analogWrite(LeftMotor,Pwm); 

   digitalWrite(R_dir,HIGH); //changed
   digitalWrite(L_dir,LOW); 
   analogWrite(RightMotor,Pwm);  //changed
   analogWrite(LeftMotor,Pwm); 
} 
void Right(unsigned int Pwm) 
{ 
   //digitalWrite(R_dir,HIGH); 
   //digitalWrite(L_dir,LOW); 
   //analogWrite(RightMotor,Pwm);  
   //analogWrite(LeftMotor,Pwm); 
//    Serial.println("in right function");
   digitalWrite(R_dir,LOW); 
   digitalWrite(L_dir,HIGH); // changed
   analogWrite(RightMotor,Pwm);  
   analogWrite(LeftMotor,Pwm); // changed
} 
void Stop() 
{ 
   digitalWrite(RightMotor,LOW);  
   digitalWrite(LeftMotor,LOW);
   analogWrite(RightMotor,0);  
   analogWrite(LeftMotor,0); 
} 

void Move_Turn(unsigned int left_pwm,unsigned int right_pwm) 
{ 
   digitalWrite(R_dir,LOW); 
   digitalWrite(L_dir,LOW); 
   analogWrite(RightMotor,right_pwm);  
   analogWrite(LeftMotor,left_pwm); 
} 
int flag = 0;
void loop() {
  ch7 = pulseIn(6,HIGH,30000);  //Done
  ch6 = pulseIn(7,HIGH,30000); //Done
  ch5 = pulseIn(5,HIGH,30000); //Done //Green

  ch4 = pulseIn(4,HIGH);
//  Serial.println(ch5);
  if(ch5>1600){
    
     manual();
   }
    else{
      autonomous();
    }
  
  
  
}


void manual(){
    if(ch7>1600){
      Forward(30);
    }
    else if(ch7<1400){
     Backward(50);
    }
    else if(ch6>1600){
    // Left(50);
      Right(50);
    }
    else if(ch6<1400){
     
     //Right(50);
     Left(50);
    }
    else{
     Stop();
    }
}




void autonomous(){
  int measurement = (float(ch4) - min) *sonar_const+17.0;
  if (measurement == 17 ) measurement=0;
  if (Serial.available()) {
        String myString = Serial.readString();
        
    
        String xval = getValue(myString, ',', 0);
        String yval = getValue(myString, ',', 1);
        //float time_delay = xval.toFloat()*1000;
//        Serial.print("value0");
        
        if ( yval[0] == 'r' || yval[0]  == 'l' )
        {
            if (yval[0]  == 'r' ) 
              yval = "R";
            else
              yval  = "L";
          
        }

        else
        {
        if(measurement < 80 && measurement >1 && flag == 0){
         Stop();
         digitalWrite(Buzer_pin,HIGH);
         delay(3000);
         digitalWrite(Buzer_pin,LOW);
         flag = 1;
         yval="X" + String(measurement);
          }
        else if(measurement < 80 && measurement >1 && flag ==1 ){
          flag = 0;
          yval="U" + String(measurement);
          Stop();
         }
       
        }
        
        if(yval[0]  == 'F'){
        Forward(xval.toInt());
        flag = 0;
        //delay(1000);
        //Stop();
        }
        else if(yval[0] == 'L') {
        Left(xval.toInt());
        }
        else if(yval[0] == 'R') {
//        Serial.println("in R function");
//        Serial.println(xval);
        Right(xval.toInt());
        }
        else if(yval[0] == 'S') {
        Stop();
        }
//        else if (yval == "l"){
//        Move_Turn(xval.toInt(),(xval.toInt()/2));
//        delay(time_delay);
//        
//        }
//        else if (yval == "r"){
//        Move_Turn((xval.toInt()/2),xval.toInt());
//        delay(time_delay);
//        }
//        
        
        Serial.println(yval);
    }
//    Serial.print("Measurement");
//    Serial.print(measurement);
    else if(measurement < 80 && measurement >1 ){
         Stop();
    
  
}
}
