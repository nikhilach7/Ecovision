const int trigPin = 9;
const int echoPin = 10;

long duration;
float distanceCm;

// ThingSpeak field mapping for EcoVision AI:
// field1 = fill level
// field2 = waste level
// field3 = distance
// field4 = bin status

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distanceCm = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.println(distanceCm);
  delay(2000);
}
