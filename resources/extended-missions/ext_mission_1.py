# Daniel
import cv2
import numpy as np
from djitellopy import Tello

# Inicjalizacja drona
tello = Tello()
tello.connect()
tello.streamon()

# Pobranie klatki w celu uzyskania wymiarów obrazu
frame_read = tello.get_frame_read()

# Wczytanie klasyfikatora twarzy (standardowy model OpenCV)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Parametry lotu i PID (uproszczone)
p_gain = 0.4  # Współczynnik proporcjonalny (czułość reakcji)
target_center = [960 // 2, 720 // 2]  # Środek kadru dla rozdzielczości 720p

tello.takeoff()

try:
    while True:
        # 1. Pobranie obrazu z drona
        img = frame_read.frame
        img = cv2.resize(img, (960, 720))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Wykrywanie twarzy
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Domyślnie dron wisi w miejscu
        fb_speed = 0  # przód/tył
        lr_speed = 0  # lewo/prawo
        ud_speed = 0  # góra/dół
        yaw_speed = 0 # obrót

        if len(faces) > 0:
            # Bierzemy pierwszą wykrytą twarz (największą)
            (x, y, w, h) = faces[0]
            cx = x + w // 2
            cy = y + h // 2

            # Rysowanie ramki wokół twarzy
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)

            # 3. Obliczanie błędów (odchylenia od środka)
            error_x = cx - target_center[0]
            error_y = cy - target_center[1]

            # 4. Sterowanie obrotem (Yaw) i wysokością (Góra/Dół)
            # Jeżeli twarz jest na lewo od środka -> obróć w lewo
            yaw_speed = int(np.clip(p_gain * error_x, -50, 50))
            # Jeżeli twarz jest powyżej środka -> leć w górę
            ud_speed = int(np.clip(-p_gain * error_y, -40, 40))

            # 5. Utrzymywanie odległości (opcjonalne)
            # Przykładowo: chcemy, aby twarz zajmowała ok. 15-20% szerokości kadru
            target_w = 150
            error_w = target_w - w
            fb_speed = int(np.clip(p_gain * error_w, -20, 20))

        # Wysłanie komend do drona
        tello.send_rc_control(0, fb_speed, ud_speed, yaw_speed)

        # Wyświetlanie obrazu
        cv2.imshow("Tello Tracking", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()