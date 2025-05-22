#!/usr/bin/env python3
"""
PPUC Lampen Ein-Schalter

Dieses Programm verbindet sich mit PPUC-Boards und schaltet alle Lampen
mit den Nummern 1-50 ein.

Verwendung:
    python3 ppuc_lamps_on.py [config_file]

Beispiel:
    python3 ppuc_lamps_on.py
    python3 ppuc_lamps_on.py my_config.yaml
"""

import time
import sys
from ppuc_wrapper import PPUC

def log_callback(message):
    """Callback-Funktion für PPUC-Lognachrichten"""
    print(f"PPUC Log: {message}")

def main():
    print("PPUC Lampen Ein-Schalter")
    print("========================")
    
    # PPUC-Instanz erstellen
    try:
        ppuc = PPUC()
        print("✓ PPUC-Instanz erstellt")
    except Exception as e:
        print(f"✗ Fehler beim Erstellen der PPUC-Instanz: {e}")
        return False
    
    # Debug-Modus aktivieren für detaillierte Ausgaben
    ppuc.set_debug(False)
    print("✓ Debug-Modus aktiviert")
    
    # Log-Callback setzen
    ppuc.set_log_message_callback(log_callback)
    print("✓ Log-Callback gesetzt")
    
    # Konfigurationsdatei laden (falls angegeben)
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        try:
            print(f"Lade Konfiguration aus {config_file}...")
            ppuc.load_configuration(config_file)
            print("✓ Konfiguration geladen")
        except Exception as e:
            print(f"⚠ Warnung: Konfiguration konnte nicht geladen werden: {e}")
            print("Fortfahren ohne Konfigurationsdatei...")
    
    # Seriellen Port setzen
    # Passe dies entsprechend deinem System an:
    # Linux: "/dev/ttyUSB0", "/dev/ttyACM0", "/dev/ttyS0"  
    # Windows: "COM1", "COM2", "COM3", etc.
    serial_port = "/dev/ttyUSB0"  # Standard für Linux
    
    try:
        ppuc.set_serial(serial_port)
        print(f"✓ Serieller Port gesetzt: {ppuc.get_serial()}")
    except Exception as e:
        print(f"✗ Fehler beim Setzen des seriellen Ports: {e}")
        return False
    
    # Verbinden mit den PPUC-Boards
    print("\nVerbinde mit PPUC-Boards...")
    try:
        if ppuc.connect():
            print("✓ Verbindung zu PPUC-Boards hergestellt!")
        else:
            print("✗ Verbindung zu PPUC-Boards fehlgeschlagen!")
            print("\nTroubleshooting-Tipps:")
            print("1. Prüfe ob PPUC-Hardware eingeschaltet ist")
            print("2. Prüfe Kabelverbindungen")
            print("3. Versuche einen anderen seriellen Port")
            print("4. Prüfe Berechtigungen: sudo usermod -a -G dialout $USER")
            return False
    except Exception as e:
        print(f"✗ Fehler bei der Verbindung: {e}")
        return False
    
    # Updates starten für Event-Handling
    try:
        ppuc.start_updates()
        print("✓ Updates gestartet")
    except Exception as e:
        print(f"✗ Fehler beim Starten der Updates: {e}")
        ppuc.disconnect()
        return False
    
    # Alle Lampen 1-50 einschalten
    print(f"\nSchalte Lampen 1-50 ein...")
    
    successful_lamps = []
    failed_lamps = []
    
    for lamp_number in range(1, 51):  # 1 bis 50 (inklusiv)
        try:
            ppuc.set_lamp_state(lamp_number, 1)  # 1 = ein
            successful_lamps.append(lamp_number)
            print(f"✓ Lampe {lamp_number:2d} eingeschaltet")
            
            # Kurze Pause zwischen den Lampen für sichtbare Sequenz
            time.sleep(0.1)
            
        except Exception as e:
            failed_lamps.append(lamp_number)
            print(f"✗ Fehler bei Lampe {lamp_number}: {e}")
    
    # Zusammenfassung
    print(f"\n" + "="*50)
    print("ZUSAMMENFASSUNG:")
    print(f"Erfolgreich eingeschaltet: {len(successful_lamps)} Lampen")
    if successful_lamps:
        print(f"  Lampen: {', '.join(map(str, successful_lamps))}")
    
    if failed_lamps:
        print(f"Fehlgeschlagen: {len(failed_lamps)} Lampen")
        print(f"  Lampen: {', '.join(map(str, failed_lamps))}")
    
    print(f"\nAlle Lampen sind jetzt eingeschaltet!")
    print("Drücke Ctrl+C um das Programm zu beenden...")
    
    # Hauptschleife - hält das Programm am Laufen
    try:
        while True:
            # Optional: Switch-Events überwachen
            switch_state = ppuc.get_next_switch_state()
            if switch_state:
                number, state = switch_state
                state_text = "AKTIV" if state else "INAKTIV"
                print(f"Switch {number:2d}: {state_text}")
            
            time.sleep(0.01)  # Reduziert CPU-Last
            
    except KeyboardInterrupt:
        print("\n\nProgramm wird beendet...")
    
    # Aufräumen und sauber beenden
    finally:
        print("Räume auf...")
        try:
            # Optional: Alle Lampen wieder ausschalten
            user_input = input("Sollen alle Lampen wieder ausgeschaltet werden? (j/N): ").lower()
            if user_input in ['j', 'ja', 'y', 'yes']:
                print("Schalte alle Lampen aus...")
                for lamp_number in range(1, 51):
                    ppuc.set_lamp_state(lamp_number, 0)  # 0 = aus
                    time.sleep(0.01)  # Kurze Pause
                print("✓ Alle Lampen ausgeschaltet")
            
            # Updates stoppen
            ppuc.stop_updates()
            print("✓ Updates gestoppt")
            
            # Verbindung trennen
            ppuc.disconnect()
            print("✓ Verbindung getrennt")
            
        except Exception as e:
            print(f"⚠ Warnung beim Aufräumen: {e}")
        
        print("✓ Programm sauber beendet")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
