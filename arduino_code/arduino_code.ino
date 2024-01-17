int pinRed = 2;
int pinPedal = 3;
int pinWhite = 4;

int currentStateRed = LOW, currentStatePedal = LOW, currentStateWhite = LOW; 

int readingRed = 0, readingPedal = 0, readingWhite = 0;
int debounceCountRed = 10, debounceCountPedal = 10, debounceCountWhite  = 10;
int counterRed = 0, counterPedal = 0, counterWhite = 0;

long reading_time = 0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);
  Serial.setTimeout(1);
  
  pinMode(pinRed, INPUT); 
  pinMode(pinPedal, INPUT);
  pinMode(pinWhite, INPUT); 
  
}

void loop() {

// If we have gone on to the next millisecond
  if(millis() != reading_time)
  {
    readingRed = digitalRead(pinRed);
    readingPedal = digitalRead(pinPedal);
    readingWhite = digitalRead(pinWhite);

    if(readingRed == currentStateRed && counterRed > 0){
      counterRed--;
    }
    else if(readingRed != currentStateRed){
      counterRed++;
    }

    if(readingPedal == currentStatePedal && counterPedal > 0){
      counterPedal--;
    }
    else if(readingPedal != currentStatePedal){
       counterPedal++;
    }

    if(readingWhite == currentStateWhite && counterWhite > 0){
      counterWhite--;
    }
    else if(readingWhite != currentStateWhite){
       counterWhite++;
    }

    // If any input has shown the same value for long enough, switch it
    if(counterRed >= debounceCountRed){
      counterRed = 0;
      currentStateRed = readingRed;
      if (currentStateRed == HIGH){
        Serial.println("red");
      }
    }
      
    if(counterPedal >= debounceCountPedal){
      counterPedal = 0;
      currentStatePedal = readingPedal;
      if (currentStatePedal == HIGH){
        Serial.println("pedal_high");
      }
      else{
        Serial.println("pedal_low");
      } 
    }

    if(counterWhite >= debounceCountWhite){
      counterWhite = 0;
      currentStateWhite = readingWhite;
      if (currentStateWhite == HIGH){
        Serial.println("white");
      }
    }
        
    reading_time = millis();}
}
