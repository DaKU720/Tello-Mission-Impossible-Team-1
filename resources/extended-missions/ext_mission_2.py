# Kajtek
from djitellopy import Tello
import time
import cv2

def main():
    tello = Tello()

    # 1. Połączenie i sprawdzenie początkowe
    tello.connect()
    start_battery = tello.get_battery()
    print(f"Początkowy poziom baterii: {start_battery}%")

    if start_battery < 20:
        print("Za niski poziom baterii na wykonanie misji! Wymagane min. 20%")
        return

    tello.streamon()
    frame_reader = tello.get_frame_read()

    # KONFIGURACJA
    liczba_powtorzen = 2

    try:
        # KROK 1: Start i wznoszenie
        print("Start drona...")
        tello.takeoff()
        print("Wznoszenie na 1.5m...")
        tello.move_up(60)

        def sekwencja_skanowania(kierunek_powrotny=False):
            # KROK 2: Lot 3m
            print("Lot do przodu 3m...")
            tello.move_forward(300) # UWAGA: Dron nie widzi przeszkód!
            time.sleep(1)

            # KROK 3: Obrót 360 (4x90)
            print("Rozpoczynanie skanowania 360 stopni...")
            for i in range(4):
                tello.rotate_clockwise(90)
                time.sleep(1)

                # Zapis zdjęcia
                frame = frame_reader.frame
                # Dodajemy try-except, żeby błąd zapisu nie przerwał lotu
                if frame is not None:
                    timestamp = time.strftime("%H%M%S")
                    nazwa_pliku = f"scan_{'powrot' if kierunek_powrotny else 'tam'}_{timestamp}_{i}.jpg"
                    cv2.imwrite(nazwa_pliku, frame)
                    print(f"Zrobiono zdjęcie: {nazwa_pliku}")

        # --- LOT TAM ---
        print("--- MAPOWANIE (W STRONĘ KOŃCA) ---")
        for _ in range(liczba_powtorzen):
            sekwencja_skanowania(kierunek_powrotny=False)

        # KROK 5: Nawrót
        print("Nawrót o 180 stopni...")
        tello.rotate_clockwise(180)
        time.sleep(1)

        # --- LOT POWROTNY ---
        print("--- MAPOWANIE (POWRÓT) ---")
        for _ in range(liczba_powtorzen):
            sekwencja_skanowania(kierunek_powrotny=True)

        # KROK 7: Obrót końcowy i lądowanie
        print("Obrót końcowy o 180 stopni (front do bazy)...")
        tello.rotate_clockwise(180)

        print("Lądowanie...")
        tello.land()

        # --- DODANO: Informacja o baterii po lądowaniu ---
        end_battery = tello.get_battery()
        print(f"\n--- MISJA ZAKOŃCZONA ---")
        print(f"Końcowy poziom baterii: {end_battery}%")
        print(f"Zużycie baterii: {start_battery - end_battery}%")

    except Exception as e:
        print(f"AWARYJNE PRZERWANIE MISJI: {e}")
        tello.land()

    finally:
        tello.streamoff()
        tello.end()

if __name__ == "__main__":
    main()