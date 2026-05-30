// Definición de pines para los LEDs
const int pinLedIzquierda = 13;
const int pinLedDerecha = 12;

void setup() {
  // Inicializamos la comunicación serial a 9600 baudios (debe coincidir con Python)
  Serial.begin(9600);

  // Configuramos los pines como salidas
  pinMode(pinLedIzquierda, OUTPUT);
  pinMode(pinLedDerecha, OUTPUT);

  // Nos aseguramos de que empiecen apagados
  digitalWrite(pinLedIzquierda, LOW);
  digitalWrite(pinLedDerecha, LOW);
}

void loop() {
  // Verificamos si hay datos disponibles en el puerto serial
  if (Serial.available() > 0) {
    // Leemos el byte recibido
    char comando = Serial.read();

    // Evaluamos el comando recibido desde Python
    switch (comando) {
      case 'I': // Orden para la izquierda
        digitalWrite(pinLedIzquierda, HIGH);
        digitalWrite(pinLedDerecha, LOW);
        break;

      case 'D': // Orden para la derecha
        digitalWrite(pinLedIzquierda, LOW);
        digitalWrite(pinLedDerecha, HIGH);
        break;

      case 'A': // Orden para apagar ambos (cuando la mirada vuelve al centro)
        digitalWrite(pinLedIzquierda, LOW);
        digitalWrite(pinLedDerecha, LOW);
        break;
    }
  }
}
