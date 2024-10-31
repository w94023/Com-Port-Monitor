void setup()
{
  Serial.begin(115200);
}

int analog_pins[8] = {A0, A1, A2, A3, A4, A5, A6, A7};

// the loop routine runs over and over again forever:
void loop() {

  for (int i = 0; i < 8; i++) {
    write_analog_value_in_byte(analogRead(analog_pins[i]));
  }
  Serial.write(255);

  delay(1);
}

void write_analog_value_in_byte(int value)
{
  // 몫과 나머지를 계산
  int quotient = value / 254;
  int remainder = value % 254;

  Serial.write(quotient);
  Serial.write(remainder);
}