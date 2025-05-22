"""
PPUC Beispielprogramm

Dieses Programm demonstriert die Verwendung der PPUC-Bibliothek in Python.
"""

import time
import sys
from ppuc_wrapper import PPUC

def log_callback(message):
    """Callback-Funktion für Lognachrichten"""
    print(f"PPUC Log: {message}")

def main():
    # PPUC-Instanz erstellen
    ppuc = PPUC()
    
    # Debug-Modus aktivieren
    ppuc.set_debug(True)
    
    # Log-Callback setzen
    ppuc.set_log_message_callback(log_callback)
    
    # Konfigurationsdatei laden (falls vorhanden)
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        print(f"Lade Konfiguration aus {config_file}")
        ppuc.load_configuration(config_file)
    
    # Seriellen Port setzen
    # Unter Windows typischerweise COMx, unter Linux /dev/ttyUSBx oder /dev/ttyACMx
    serial_port = "/dev/ttyUSB0"  # Ändere dies entsprechend deinem System
    ppuc.set_serial(serial_port)
    print(f"Verwende seriellen Port: {ppuc.get_serial()}")
    
    # Verbinden mit den PPUC-Boards
    print("Verbinde mit PPUC-Boards...")
    if ppuc.connect():
        print("Verbindung hergestellt!")
        
        # Starte Updates
        ppuc.start_updates()
        
        try:
            print("Drücke Ctrl+C zum Beenden")
            
            # Hauptschleife
            while True:
                # Schalter-Zustände abfragen
                switch_state = ppuc.get_next_switch_state()
                if switch_state:
                    number, state = switch_state
                    print(f"Schalter {number} ist {state}")
                
                # Spule kurz aktivieren (Nummer 10 als Beispiel)
                # Vorsicht: Stelle sicher, dass die Nummer existiert!
                # ppuc.set_solenoid_state(10, 1)
                # time.sleep(0.1)
                # ppuc.set_solenoid_state(10, 0)
                
                time.sleep(0.01)  # Kurze Pause
                
        except KeyboardInterrupt:
            print("\nBeende Programm...")
        finally:
            # Stoppe Updates und trenne Verbindung
            ppuc.stop_updates()
            ppuc.disconnect()
    else:
        print("Verbindung fehlgeschlagen!")

if __name__ == "__main__":
    main()
