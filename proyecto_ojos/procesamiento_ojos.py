import cv2
import numpy as np
import serial
import time

# --- Configuración del Puerto Serial ---
# CAMBIAR ESTO SEGÚN LOS PUERTOS QUE HAYAS CREADO EN EL VIRTUAL SERIAL PORTS EMULATOR
PUERTO_COM = 'COM1'
BAUDRATE = 9600

try:
    arduino = serial.Serial(PUERTO_COM, BAUDRATE, timeout=1)
    time.sleep(2) # Esperamos a que se estabilice la conexión
    print(f"Conectado exitosamente al puerto {PUERTO_COM}")
except Exception as e:
    print(f"Advertencia: No se pudo conectar al puerto serial {PUERTO_COM}. Verifica la simulación.")
    arduino = None

# --- Configuración de OpenCV ---
# Usamos los cascades que vienen por defecto con OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Abrimos el video de prueba
cap = cv2.VideoCapture('vpregunta1.mp4')

# Variables para medir la "persistencia" (medio segundo)
tiempo_necesario = 0.5
estado_actual = "CENTRO"
tiempo_inicio_mirada = 0
orden_enviada = False

def obtener_direccion_iris(ojo_frame):
    """
    Procesa la imagen del ojo para encontrar el iris y determinar hacia dónde mira.
    Devuelve 'IZQUIERDA', 'DERECHA' o 'CENTRO'.
    """
    # Convertir a escala de grises
    gray_eye = cv2.cvtColor(ojo_frame, cv2.COLOR_BGR2GRAY)

    # Aplicar un poco de desenfoque para reducir ruido
    gray_eye = cv2.GaussianBlur(gray_eye, (7, 7), 0)

    # Umbralización para aislar los píxeles oscuros (el iris)
    # Puede que necesite ajustar este valor (ej. 40, 50, 60) dependiendo de la luz en el video
    _, umbral = cv2.threshold(gray_eye, 45, 255, cv2.THRESH_BINARY_INV)

    # Encontrar contornos
    contornos, _ = cv2.findContours(umbral, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contornos:
        # Asumimos que el contorno más grande es el iris
        contorno_iris = max(contornos, key=cv2.contourArea)
        M = cv2.moments(contorno_iris)

        if M['m00'] != 0:
            # Calcular el centro (x, y) del iris
            cx = int(M['m10'] / M['m00'])

            # Dibujar el centro para debug visual
            cv2.circle(ojo_frame, (cx, int(M['m01'] / M['m00'])), 2, (0, 0, 255), -1)

            # Ancho del ojo para dividir en zonas
            ancho_ojo = ojo_frame.shape[1]

            # Dividir en 3 zonas: 0-33% (Izquierda), 33-66% (Centro), 66-100% (Derecha)
            limite_izquierdo = ancho_ojo * 0.35
            limite_derecho = ancho_ojo * 0.65

            if cx < limite_izquierdo:
                return "DERECHA" # Invertido porque la cámara actúa como espejo
            elif cx > limite_derecho:
                return "IZQUIERDA"
            else:
                return "CENTRO"

    return "CENTRO"

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fin del video o no se pudo leer.")
        break

    # Redimensionar para que vaya más fluido y sea más fácil de ver
    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar el rostro
    rostros = face_cascade.detectMultiScale(gray, 1.3, 5)

    direccion_detectada = "CENTRO"

    for (x, y, w, h) in rostros:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Recortar la región del rostro para buscar los ojos dentro
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        # Detectar ojos
        ojos = eye_cascade.detectMultiScale(roi_gray)

        # Si detectamos al menos un ojo, procesamos el primero
        for (ex, ey, ew, eh) in ojos:
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            ojo_recorte = roi_color[ey:ey+eh, ex:ex+ew]

            direccion_detectada = obtener_direccion_iris(ojo_recorte)
            break # Solo procesamos un ojo para no complicarnos

    # Lógica de Persistencia (0.5 segundos)
    if direccion_detectada != "CENTRO":
        if estado_actual != direccion_detectada:
            # Empezó a mirar hacia un nuevo lado
            estado_actual = direccion_detectada
            tiempo_inicio_mirada = time.time()
            orden_enviada = False
        else:
            # Sigue mirando hacia el mismo lado
            tiempo_transcurrido = time.time() - tiempo_inicio_mirada

            if tiempo_transcurrido >= tiempo_necesario and not orden_enviada:
                print(f"¡ORDEN GENERADA! Mirada detectada hacia: {direccion_detectada} por 0.5s")
                cv2.putText(frame, f"ORDEN: {direccion_detectada}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                # Enviar comando por serial
                if arduino:
                    if direccion_detectada == "IZQUIERDA":
                        arduino.write(b'I')
                    elif direccion_detectada == "DERECHA":
                        arduino.write(b'D')

                orden_enviada = True
    else:
        # Volvió al centro
        estado_actual = "CENTRO"
        if orden_enviada:
            # Apagamos los LEDs si vuelve al centro (opcional, dependiendo de lo que pida el profe)
            print("Mirada al centro, reseteando orden.")
            if arduino:
                arduino.write(b'A') # A de Apagar
        orden_enviada = False

    # Mostrar dirección actual en pantalla
    cv2.putText(frame, f"Detectado: {direccion_detectada}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow('Procesamiento Digital - Orden por Iris', frame)

    # Presionar 'q' para salir
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
if arduino:
    arduino.close()
cv2.destroyAllWindows()
