# Notas del Proyecto: Procesamiento de Imágenes para Detectar el Iris

Aquí voy a dejar anotado todo lo que hice para que funcione el programa de Python con la simulación en Proteus, por si me olvido de cómo correrlo después o para cuando lo tenga que presentar.

## 1. El código de Python

El script principal se llama `procesamiento_ojos.py`. Tuve que usar la librería de OpenCV para leer el video y detectar dónde están los ojos. Me pareció más fácil usar los *Haar Cascades* que ya vienen con OpenCV (`haarcascade_frontalface_default.xml` y `haarcascade_eye.xml`) en lugar de entrenar algo desde cero.

La lógica es simple:
1. Detecto la cara, y dentro de la cara busco los ojos.
2. Agarro la imagen de un ojo, la paso a blanco y negro (escala de grises) y le aplico un *threshold* (umbralización) para que el iris, que es la parte más oscura, quede resaltado.
3. Calculo el centro de esa mancha oscura (con los momentos de Hu/OpenCV) y veo en qué tercio del ojo cae (izquierda, centro o derecha).
4. **La persistencia:** Puse un temporizador. Si la mirada se queda en la izquierda o derecha por más de 0.5 segundos, entonces recién ahí se genera la "orden" y se manda una letra por el puerto serial (`I` para izquierda, `D` para derecha).

### Dependencias para instalar en Python:
Si lo voy a correr en otra compu, necesito instalar esto en la terminal:
```bash
pip install opencv-python numpy pyserial
```

## 2. El código de Arduino (Simulino)

Hice un script cortito en C++ llamado `control_leds.ino`. Lo único que hace es quedarse escuchando el puerto serial. Si recibe una 'I', prende el pin 13 (que será mi LED izquierdo en Proteus). Si recibe una 'D', prende el pin 12 (LED derecho). Si recibe una 'A', apaga los dos.

Tengo que compilar este `.ino` desde el IDE de Arduino (asegurándome de exportar el binario `.hex`) para poder cargarlo en el Simulino dentro de Proteus.

## 3. Conectando Python con Proteus (Puertos Seriales Virtuales)

Como Proteus es una simulación y mi Python corre en mi compu real, necesito un "cable virtual" que los conecte. Para eso usé el programa **Free Virtual Serial Ports** de HHD Software.

**Pasos que seguí:**
1. Abro el *Free Virtual Serial Ports*.
2. En la ventana principal, voy a la sección para crear un nuevo par de puertos o puente local ("Local Bridge").
3. Selecciono el primer puerto virtual como **COM3** y el segundo puerto como **COM4**.
4. Le doy a crear o aplicar ("Create"). Listo, el programa empieza a emular la conexión y el COM3 queda directamente conectado al COM4.

**Configuración en mi código:**
- En mi script de Python, le puse que se conecte al `COM3`.

**Configuración en Proteus:**
1. En mi diseño de Proteus con el Simulino, tengo que agregar un componente llamado **COMPIM**.
2. Hago doble clic en el componente COMPIM y lo configuro para que se conecte al `COM4`.
3. Me tengo que acordar de poner el *Baud Rate* (tanto físico como virtual en las propiedades del COMPIM) a **9600** para que coincida con lo que puse en el Arduino y en Python.
4. Conecto el pin TXD y RXD del COMPIM a los pines RX y TX del Simulino, respectivamente.

Con todo esto andando, corro Proteus y después corro mi script de Python. Al poner el video `vpregunta1.mp4` (tiene que estar en la misma carpeta que el `.py`), Python va a procesar la imagen, y cuando la persona mire a un lado, los LEDs en mi Proteus se van a prender. ¡Listo!
