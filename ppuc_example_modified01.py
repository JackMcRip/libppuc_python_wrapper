"""
PPUC Beispielprogramm

Dieses Programm demonstriert die Verwendung der PPUC-Bibliothek in Python.
Es wartet auf 10 Switch-Zustandsänderungen, schaltet LEDs 1-50 an und führt dann einen Coil Test durch.
"""

import time
import sys
import threading
from ppuc_wrapper import PPUC

def log_callback(message):
    """Callback-Funktion für Lognachrichten"""
    print(f"PPUC Log: {message}")

def enable_leds(ppuc, start_led=1, end_led=50):
    """
    Schaltet LEDs/Lampen in einem bestimmten Bereich an.
    
    Args:
        ppuc: PPUC-Instanz
        start_led: Erste LED-Nummer
        end_led: Letzte LED-Nummer
    """
    print(f"\n=== Schalte LEDs {start_led}-{end_led} an ===")
    
    success_count = 0
    for led_num in range(start_led, end_led + 1):
        try:
            ppuc.set_lamp_state(led_num, 1)  # LED anschalten
            success_count += 1
            
            # Fortschrittsanzeige alle 10 LEDs
            if led_num % 10 == 0 or led_num == end_led:
                print(f"LEDs 1-{led_num} angeschaltet... ({success_count}/{end_led} erfolgreich)")
                time.sleep(0.1)  # Kurze Pause für sichtbaren Effekt
                
        except Exception as e:
            print(f"⚠ Fehler beim Anschalten von LED {led_num}: {e}")
    
    print(f"✓ {success_count} von {end_led} LEDs erfolgreich angeschaltet")

def wait_for_switch_changes(ppuc, max_changes=10):
    """
    Wartet auf Switch-Zustandsänderungen und gibt sie aus.
    Echte Zustandsänderungen werden gezählt.
    Kann durch Tastendruck vorzeitig beendet werden.
    
    Args:
        ppuc: PPUC-Instanz
        max_changes: Anzahl der Zustandsänderungen, auf die gewartet werden soll
    
    Returns:
        int: max_changes wenn erfolgreich abgeschlossen oder durch Tastendruck beendet
    """
    print(f"\n=== Warte auf {max_changes} Switch-Zustandsänderungen ===")
    print("Aktiviere/Deaktiviere Schalter am Flipperautomat...")
    print("ODER drücke ENTER zum Überspringen...")
    print("Das Programm wartet, bis echte Zustandsänderungen auftreten!")
    
    change_count = 0
    start_time = time.time()
    last_activity_time = start_time
    
    # Shared variable für Thread-Kommunikation
    keyboard_interrupt = {"pressed": False}
    
    def keyboard_listener():
        """Lauscht auf Tastatura-Eingaben in separatem Thread"""
        try:
            input()  # Wartet auf ENTER
            keyboard_interrupt["pressed"] = True
        except:
            # Bei Fehler (z.B. EOF) einfach ignorieren
            pass
    
    # Tastatur-Listener-Thread starten
    listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
    listener_thread.start()
    
    try:
        while change_count < max_changes and not keyboard_interrupt["pressed"]:
            # get_next_switch_state() gibt nur bei echten Zustandsänderungen ein Ergebnis zurück
            switch_state = ppuc.get_next_switch_state()
            
            if switch_state is not None:
                # Es wurde eine echte Zustandsänderung empfangen
                number, state = switch_state
                change_count += 1
                last_activity_time = time.time()
                
                # Switch-Zustandsänderung formatiert ausgeben
                status = "AKTIV" if state else "INAKTIV"
                change_type = "aktiviert" if state else "deaktiviert"
                elapsed = time.time() - start_time
                
                print(f"[{change_count:2d}/{max_changes}] [{elapsed:6.2f}s] Schalter {number:3d}: {status} ({change_type})")
            else:
                # Keine Zustandsänderung verfügbar - kleine Pause um CPU zu entlasten
                time.sleep(0.01)  # 10ms Pause
                
                # Status-Update alle 5 Sekunden wenn keine Aktivität
                current_time = time.time()
                if current_time - last_activity_time > 5.0:
                    elapsed = current_time - start_time
                    print(f"[{change_count:2d}/{max_changes}] [{elapsed:6.2f}s] Warte auf Switch-Aktivität... (ENTER zum Überspringen)")
                    last_activity_time = current_time
            
            # Timeout nach 120 Sekunden, falls keine Änderungen kommen
            if time.time() - start_time > 120:
                print(f"\nTimeout! Nur {change_count} von {max_changes} Zustandsänderungen empfangen.")
                print("Aktiviere/Deaktiviere Schalter am Flipperautomat, um fortzufahren.")
                break
        
        # Bestimme den Grund für das Ende der Schleife
        total_time = time.time() - start_time
        if keyboard_interrupt["pressed"]:
            print(f"\n=== Switch Test durch Tastendruck beendet nach {total_time:.2f} Sekunden ===")
            print(f"Empfangen: {change_count} Switch-Zustandsänderungen")
            print("Setze fort, als wären alle 10 Switches erkannt worden...")
            return max_changes  # Simuliere erfolgreichen Abschluss
        elif change_count >= max_changes:
            print(f"\n=== {change_count} Switch-Zustandsänderungen in {total_time:.2f} Sekunden empfangen ===")
            return change_count
        else:
            print(f"\n=== Test beendet: {change_count} von {max_changes} Zustandsänderungen in {total_time:.2f} Sekunden ===")
            return change_count
            
    except KeyboardInterrupt:
        # Ctrl+C wurde gedrückt
        print(f"\n=== Switch Test durch Ctrl+C beendet ===")
        print("Setze fort, als wären alle 10 Switches erkannt worden...")
        return max_changes

def disable_all_leds(ppuc, start_led=1, end_led=50):
    """
    Schaltet alle LEDs/Lampen wieder aus.
    
    Args:
        ppuc: PPUC-Instanz
        start_led: Erste LED-Nummer
        end_led: Letzte LED-Nummer
    """
    print(f"\n=== Schalte LEDs {start_led}-{end_led} aus ===")
    
    for led_num in range(start_led, end_led + 1):
        try:
            ppuc.set_lamp_state(led_num, 0)  # LED ausschalten
        except Exception as e:
            print(f"⚠ Fehler beim Ausschalten von LED {led_num}: {e}")
    
    print(f"✓ LEDs {start_led}-{end_led} ausgeschaltet")

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
            # === Phase 1: LEDs anschalten ===
            enable_leds(ppuc, start_led=1, end_led=50)
            
            # === Phase 2: Auf Switch-Zustandsänderungen warten ===
            changes_received = wait_for_switch_changes(ppuc, max_changes=10)
            
            if changes_received >= 10:
                print("✓ Alle 10 Switch-Zustandsänderungen empfangen (oder übersprungen)!")
                
                # === Phase 3: Coil Test durchführen ===
                perform_coil_test(ppuc)
            else:
                print("⚠ Nicht genügend Switch-Zustandsänderungen empfangen für Coil Test.")
                print("Führe Coil Test trotzdem durch...")
                perform_coil_test(ppuc)
                
        except KeyboardInterrupt:
            print("\n⚠ Programm durch Benutzer abgebrochen...")
        except Exception as e:
            print(f"\n✗ Fehler aufgetreten: {e}")
        finally:
            # === Bereinigung ===
            print("\n=== Bereinigung ===")
            
            # LEDs ausschalten
            try:
                disable_all_leds(ppuc, start_led=1, end_led=50)
            except Exception as e:
                print(f"⚠ Fehler beim Ausschalten der LEDs: {e}")
            
            # PPUC ordnungsgemäß beenden
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
