const int PWM = 8;
const int STEERING_1 = 12;
const int STEERING_2 = 6;
const int FOWARD_RIGHT_1 = 10;
const int FOWARD_RIGHT_2 = 4;
const int FOWARD_LEFT_1 = 8;
const int FOWARD_LEFT_2 = 2;
const int POT = A4;
const int front_echo = 46;
const int front_trig = 47;

//check variable resistance value!!!!!!!!!!!!!!!!!!!
const int most_left = 874;
const int most_right = 754;
//check this too!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
const int set_init_steering = 1;


const int STEERING_SPEED = 128;
const int FOWARD_SPEED = 255;
int angle = 0, straight = 0, str_spd = 100, resistance = 0, mapped_resistance = 0;
int is_out = 0;
char aaa = 'q', sss = 'w', ooo = 'e';

long front_distance = 0;
int avoid_flag = 0;
void right(){
  analogWrite(STEERING_1, STEERING_SPEED);
  analogWrite(STEERING_2, LOW);
}

void left(){
  analogWrite(STEERING_1, LOW);
  analogWrite(STEERING_2, STEERING_SPEED);
}

void stay(){
  analogWrite(STEERING_1, LOW);
  analogWrite(STEERING_2, LOW);
}

void foward(int st){
//  analogWrite(FOWARD_RIGHT_1, FOWARD_SPEED);
  analogWrite(FOWARD_RIGHT_1, st);
  analogWrite(FOWARD_RIGHT_2, LOW);
//  analogWrite(FOWARD_LEFT_1, FOWARD_SPEED);
  analogWrite(FOWARD_LEFT_1, st);
  analogWrite(FOWARD_LEFT_2, LOW);
}

void reverse(int st){
  analogWrite(FOWARD_RIGHT_1, LOW);
//  analogWrite(FOWARD_RIGHT_2, FOWARD_SPEED);
  analogWrite(FOWARD_RIGHT_2, st);
  analogWrite(FOWARD_LEFT_1, LOW);
//  analogWrite(FOWARD_LEFT_2, FOWARD_SPEED);
  analogWrite(FOWARD_LEFT_2, st);
}

void hold(){
  analogWrite(FOWARD_RIGHT_1, LOW);
  analogWrite(FOWARD_RIGHT_2, LOW);
  analogWrite(FOWARD_LEFT_1, LOW);
  analogWrite(FOWARD_LEFT_2, LOW);
}

long ultra(int TRIG, int ECHO){
    long distance, duration; 
    digitalWrite(TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);
    duration = pulseIn(ECHO, HIGH);
    distance = duration*17/1000;

    return distance;

}


void setup() {  
  Serial.begin(9600);
  pinMode(POT, INPUT);
  pinMode(STEERING_1, OUTPUT);
  pinMode(STEERING_2, OUTPUT);
  pinMode(FOWARD_RIGHT_1, OUTPUT);
  pinMode(FOWARD_RIGHT_2, OUTPUT);
  pinMode(FOWARD_LEFT_1, OUTPUT);
  pinMode(FOWARD_LEFT_2, OUTPUT);
  pinMode(PWM, OUTPUT);
  digitalWrite(PWM, HIGH);

  pinMode(front_echo, INPUT);
  pinMode(front_trig, OUTPUT);
}


void loop() {

  //front_distance = ultra(front_trig, front_echo);

  if (Serial.available()){
    if(Serial.peek() == 'a'){
      aaa = Serial.read();
      angle = Serial.parseInt();
      
    }
    if(Serial.peek() == 's'){
      sss = Serial.read();
      straight = Serial.parseInt();
    }
  
  if(0){
      
    if (angle >= 50 || angle <= -50){
      int straight_temp = angle;
      angle = straight;
      straight = straight_temp;
    }

    if ( (-15 <= straight && straight < 0) || (0 < straight && straight <= 15)){
      int angle_temp = straight;
      straight = angle;
      angle = angle_temp;
    }
    }
    if(0){
    Serial.print("straight: "); 
    Serial.print(sss);
    Serial.println(straight);
    Serial.print(" angle: ");
    Serial.print(aaa);
    Serial.print(angle);
    }
    resistance = analogRead(POT);
    mapped_resistance = map(resistance, most_left, most_right-3, -7, 8);
    
    if(0){
    Serial.print(" Read/Map [A1]/[b]: ");  
    Serial.print(resistance);
    Serial.print(" / ");
    Serial.println(mapped_resistance);
    Serial.print(" ultra: ");
    Serial.println(front_distance);
    }
    
    if (straight > 0){
      //Serial.println("-----------");
      foward(straight);
    }
    else if (straight == 0){
      hold();
    }
    else if (straight < 0){
      //Serial.println("-----------");
      reverse(abs(straight));
    }

    if (mapped_resistance == angle){
      stay();
    }
    else if (mapped_resistance > angle){
      left();
    }
    else if (mapped_resistance < angle){
      right();
    }

    
  }
  else{
    foward(0);
    resistance = analogRead(POT);
    mapped_resistance = map(resistance, most_left, most_right-3, -7, 8);
    angle = 0;
    if(set_init_steering){
      if (mapped_resistance == angle){
    stay();
       //Serial.print(" stay ");  
    
    }
    else if (mapped_resistance > angle){
       //Serial.print(" low angle: ");  
    
      left();
    }
    else if (mapped_resistance < angle){
      //Serial.print(" high angle: ");  
    
      right();
    }
    }
       Serial.print(" Read/Map [A1]/[b]: ");  
    Serial.print(resistance);
    Serial.print(" / ");
    Serial.println(mapped_resistance);
//    resistance = analogRead(POT);
//    mapped_resistance = map(resistance, 160, 275, -5, 5);
//
//    if (straight > 0){
//      Serial.println("-----------");
//      foward(straight);
//    }
//    else if (straight == 0){
//      hold();
//    }
//    else if (straight < 0){
//      Serial.println("-----------");
//      reverse(abs(straight));
//    }
//
//    if (mapped_resistance == angle){
//      stay();
//    }
//    else if (mapped_resistance > angle){
//      left();
//    }
//    else if (mapped_resistance < angle){
//      right();
//    }
  }
}
