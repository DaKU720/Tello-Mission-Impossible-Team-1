from djitellopy import Tello
import time

def mission_acrobat():
    # Inicjalizacja obiektu drona
    tello = Tello()

    try:
        tello.connect()
        battery = tello.get_battery()
        temp = tello.get_temperature()

        print(f"Połączono z Tello!")
        print(f"Poziom baterii: {battery}%")
        print(f"Temperatura: {temp}")

        # nie startuj, jeśli bateria jest słaba
        if battery < 20:
            print("Bateria poniżej 20%. Wymień baterię przed startem!")
            return

        # start
        print("Startowanie...")
        tello.takeoff()
        time.sleep(1) # Krótka pauza na stabilizację

        # Wznoszenie na 1 metr (100 cm)
        # Domyślnie po starcie dron wisi ok. 80-100cm, ale dla pewności korygujemy
        print("Wznoszenie na bezpieczną wysokość (dodatkowe 50cm)...")
        tello.move_up(50)
        time.sleep(1)

        # Wykonanie Flipa (f=forward, b=back, l=left, r=right)
        print("Wykonuję FLIP do przodu!")
        tello.flip_forward()
        time.sleep(2) # Czas na ustabilizowanie po akrobacji

        # Lądowanie
        print("Lądowanie...")
        tello.land()

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        # Próba awaryjnego lądowania w razie błędu kodu
        tello.land()

    finally:
        # Zawsze kończymy sesję, ważne dla zwalniania portów UDP.
        tello.end()

if __name__ == "__main__":
    mission_acrobat()