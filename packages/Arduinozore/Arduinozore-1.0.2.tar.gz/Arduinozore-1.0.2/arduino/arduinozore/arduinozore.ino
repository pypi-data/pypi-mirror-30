bool isOn[NUM_DIGITAL_PINS - NUM_ANALOG_INPUTS];

void setup()
{
  Serial.begin(38400);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }
  for (int i = 0; i < NUM_DIGITAL_PINS - NUM_ANALOG_INPUTS; i++)
  {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
    isOn[i] = false;
  }
}

void loop()
{
  annonce();
  attente();
}

void annonce()
{
  while (Serial.available() == 0)
  {
    Serial.print("My name is Arduinozaure. Send [ok] to start. Number of analogic inputs: ");
    Serial.print(NUM_ANALOG_INPUTS);
    Serial.print(", number of digital outputs: ");
    Serial.println(NUM_DIGITAL_PINS - NUM_ANALOG_INPUTS);
    delay(250);
    String cmd = Serial.readString();
    if (cmd == "ok")
      break;
  }
}

void attente()
{
  char inChar;
  Serial.println("You can now ask for reading [r] or writing [w].");
  while (true)
  {
    inChar = Serial.read();

    if (inChar == 'r') {
      reading();
      Serial.write(".");
    }
    else if (inChar == 'w') {
      writing();
      Serial.write(".");
    }
  }
}

void reading()
{
  unsigned long start = millis();
  int pinNumber = 0;
  while (Serial.available() == 0)
  {
    if (millis() - start > 10000)
      return;
  }
  String m = Serial.readString();
  pinNumber = m.toInt();
  String msg;
  if (pinNumber >= 0 && pinNumber < NUM_ANALOG_INPUTS) {
    pinMode(pinNumber, INPUT);
    long val = analogRead(pinNumber);
    msg = val;
  }
  else
  {
    msg = "Wrong pin number specified..";
  }
  Serial.println(msg);
}

void writing()
{
  unsigned long start = millis();
  int pinNumber = 0;
  while (Serial.available() == 0)
  {
    if (millis() - start > 10000)
      return;
  }
  String m = Serial.readString();
  pinNumber = m.toInt();
  String msg;
  if (pinNumber >= 0 && pinNumber < NUM_DIGITAL_PINS - NUM_ANALOG_INPUTS) {
    if (isOn[pinNumber])
      digitalWrite(pinNumber, LOW);
    else
      digitalWrite(pinNumber, HIGH);
    isOn[pinNumber] = !isOn[pinNumber];
  }
  else
  {
    msg = "Wrong pin number specified..";
  }
  Serial.println(msg);
}
