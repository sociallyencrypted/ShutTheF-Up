// Arduino sketch for voting
// We use a 5x2 button matrix to reduce number of pins used

int pins[10] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11};

void setup(){
    for(int i = 0; i < 10; i++){
        pinMode(pins[i], INPUT);
    }
}

void loop(){
    bool signalSent = false;
    int numberOfButtonsPressed = 0;
    for(int i = 0; i < 10; i++){
        if(digitalRead(pins[i]) == HIGH){
            numberOfButtonsPressed++;
        }
    }
    if (numberOfButtonsPressed > 5 && !signalSent){
        Serial.println("CENSOR");
        signalSent = true;
    }
    delay(100);
}