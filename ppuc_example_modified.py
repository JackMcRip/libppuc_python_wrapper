"""
PPUC Beispielprogramm

Dieses Programm demonstriert die Verwendung der PPUC-Bibliothek in Python.
Es wartet auf 10 Switch-Ereignisse und führt dann einen Coil Test durch.
"""

import time
import sys
from ppuc_wrapper import PPUC

def log_callback(message):
    """Callback-Funktion für Lognachrichten"""
    print(f"PPUC Log: {message}")

def wait_for_switch_events(ppuc, max_events=10):
    """
    Wartet auf Switch-Ereignisse und gibt sie aus.
    
    Args:
        ppuc: PPUC-Instanz
        max_events: Anzahl der Events, auf die gewartet werden soll
    
    Returns:
        int: Anzahl der empfangenen Events
    """
    print(f"\n=== Warte auf {max_events} Switch-Ereignisse ===")
    print("Aktiviere Schalter am Flipperautomat...")
    
    event_count = 0
    start_time = time.time()
    
    while event_count < max_events:
        # Schalter-Zustände abfragen
        switch_state = ppuc.get_next_switch_state()
        if switch_state:
            number, state = switch_state
            event_count += 1
            
            # Switch-Event formatiert ausgeben
            status = "AKTIV" if state else "INAKTIV"
            elapsed = time.time() - start_time
            print(f"[{event_count:2d}/10] [{elapsed:6.2f}s] Schalter {number:3d}: {status}")
        
        # Kurze Pause, um CPU-Last zu reduzieren
        time.sleep(0.001)
        
        # Timeout nach 60 Sekunden, falls keine Events kommen
        if time.time() - start_time > 60:
            print(f"\nTimeout! Nur {event_count} von {max_events} Events empfangen.")
            break
    
    total_time = time.time() - start_time
    print(f"\n=== {event_count} Switch-Ereignisse in {total_time:.2f} Sekunden empfangen ===")
    
    return event_count

def perform_coil_test(ppuc):
    """
    Führt den automatischen Coil Test durch.
    
    Args:
        ppuc: PPUC-Instanz
    """
    print("\n=== Starte Coil Test ===")
    print("WARNUNG: Alle konfigurierten Spulen werden kurz aktiviert!")
    print("Stelle sicher, dass:")
    print("- Niemand in der Nähe der Maschine ist")
    print("- Alle beweglichen Teile frei sind")
    print("- Die Stromversorgung ausreichend ist")
    
    # 5 Sekunden warten, um dem Benutzer Zeit zu geben
    for i in range(5, 0, -1):
        print(f"Test startet in {i} Sekunden... (Ctrl+C zum Abbrechen)")
        time.sleep(1)
    
    try:
        print("\n>>> Führe Coil Test durch... <<<")
        ppuc.coil_test()
        print(">>> Coil Test abgeschlossen! <<<")
    except KeyboardInterrupt:
        print("\n>>> Coil Test abgebrochen! <<<")
    except Exception as e:
        print(f">>> Fehler beim Coil Test: {e} <<<")

def main():
    # PPUC-Instanz erstellen
    ppuc = PPUC()
    
    # Debug-Modus aktivieren
    ppuc.set_debug(False)
    
    # Log-Callback setzen
    ppuc.set_log_message_callback(log_callback)
    
    # Konfigurationsdatei laden (falls vorhanden)
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        print(f"Lade Konfiguration aus {config_file}")
        ppuc.load_configuration(config_file)
    else:
        print("Hinweis: Keine Konfigurationsdatei angegeben.")
        print("Verwendung: python3 ppuc_example.py [config.yaml]")
    
    # Seriellen Port setzen
    # Unter Windows typischerweise COMx, unter Linux /dev/ttyUSBx oder /dev/ttyACMx
    serial_port = "/dev/ttyUSB0"  # Ändere dies entsprechend deinem System
    ppuc.set_serial(serial_port)
    print(f"Verwende seriellen Port: {ppuc.get_serial()}")
    
    # Verbinden mit den PPUC-Boards
    print("\nVerbinde mit PPUC-Boards...")
    if ppuc.connect():
        print("✓ Verbindung hergestellt!")
        
        # Starte Updates für Switch-Events
        ppuc.start_updates()
        print("✓ Event-Updates gestartet")
        
        try:
            # === Phase 1: Auf Switch-Events warten ===
            events_received = wait_for_switch_events(ppuc, max_events=10)
            
            if events_received >= 10:
                print("✓ Alle 10 Switch-Events empfangen!")
                
                # === Phase 2: Coil Test durchführen ===
                perform_coil_test(ppuc)
            else:
                print("⚠ Nicht genügend Switch-Events empfangen für Coil Test.")
                print("Beende Programm...")
                
        except KeyboardInterrupt:
            print("\n⚠ Programm durch Benutzer abgebrochen...")
        except Exception as e:
            print(f"\n✗ Fehler aufgetreten: {e}")
        finally:
            # Ordnungsgemäß beenden
            print("\n=== Bereinigung ===")
            print("Stoppe Updates...")
            ppuc.stop_updates()
            print("Trenne Verbindung...")
            ppuc.disconnect()
            print("✓ Programm beendet")
    else:
        print("✗ Verbindung fehlgeschlagen!")
        print("Überprüfe:")
        print("- PPUC-Hardware ist eingeschaltet")
        print("- Serieller Port ist korrekt (/dev/ttyUSB0)")
        print("- Benutzer hat Berechtigungen (dialout-Gruppe)")
        print("- Kabel-Verbindung ist ok")

if __name__ == "__main__":
    main()
