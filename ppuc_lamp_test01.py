#!/usr/bin/env python3
"""
PPUC Lampen Controller - Schaltet Lampen 1-50 an

Dieses Programm verbindet sich mit den PPUC-Boards und schaltet
sequenziell die Lampen von 1-50 an.
"""

import time
import sys
import signal
from ppuc_wrapper import PPUC, PPUCConnectionError, PPUCLibraryError, PPUCConfigurationError

# Globale Variable für sauberes Herunterfahren
ppuc_instance = None
running = True

def signal_handler(signum, frame):
    """Handler für Ctrl+C (SIGINT)"""
    global running
    print("\n\nSIGINT empfangen, fahre sauber herunter...")
    running = False

def log_callback(message):
    """Callback-Funktion für PPUC-Lognachrichten"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] PPUC: {message}")

def test_lamp_sequence(ppuc, start_lamp=1, end_lamp=50, delay=0.5):
    """
    Schaltet Lampen sequenziell an.
    
    Args:
        ppuc: PPUC-Instanz
        start_lamp: Erste Lampen-Nummer
        end_lamp: Letzte Lampen-Nummer  
        delay: Verzögerung zwischen Lampen in Sekunden
    """
    global running
    
    print(f"\n=== Starte Lampen-Sequenz: {start_lamp} bis {end_lamp} ===")
    print(f"Verzögerung zwischen Lampen: {delay}s")
    print("Drücke Ctrl+C zum Beenden\n")
    
    # Alle Lampen zuerst ausschalten
    print("Schalte alle Lampen aus...")
    for lamp_num in range(start_lamp, end_lamp + 1):
        ppuc.set_lamp_state(lamp_num, 0)
        time.sleep(0.01)  # Kurze Pause zwischen Befehlen
    
    current_lamp = start_lamp
    
    try:
        while running:
            # Aktuelle Lampe anschalten
            print(f"💡 Lampe {current_lamp} AN")
            ppuc.set_lamp_state(current_lamp, 1)
            
            # Warten
            sleep_time = 0
            while sleep_time < delay and running:
                time.sleep(0.1)
                sleep_time += 0.1
            
            if not running:
                break
                
            # Lampe ausschalten
            print(f"   Lampe {current_lamp} aus")
            ppuc.set_lamp_state(current_lamp, 0)
            
            # Zur nächsten Lampe
            current_lamp += 1
            if current_lamp > end_lamp:
                current_lamp = start_lamp
                print(f"\n--- Sequenz abgeschlossen, starte von vorn ---\n")
            
    except KeyboardInterrupt:
        print("\nSequenz durch Benutzer unterbrochen")
    
    # Alle Lampen ausschalten
    print("\nSchalte alle Lampen aus...")
    for lamp_num in range(start_lamp, end_lamp + 1):
        ppuc.set_lamp_state(lamp_num, 0)
        time.sleep(0.01)

def all_lamps_on(ppuc, start_lamp=1, end_lamp=50):
    """Schaltet alle Lampen gleichzeitig an"""
    print(f"\n=== Schalte alle Lampen {start_lamp}-{end_lamp} AN ===")
    for lamp_num in range(start_lamp, end_lamp + 1):
        ppuc.set_lamp_state(lamp_num, 1)
        print(f"💡 Lampe {lamp_num} AN")
        time.sleep(0.05)  # Kurze Verzögerung zwischen Befehlen

def all_lamps_off(ppuc, start_lamp=1, end_lamp=50):
    """Schaltet alle Lampen gleichzeitig aus"""
    print(f"\n=== Schalte alle Lampen {start_lamp}-{end_lamp} AUS ===")
    for lamp_num in range(start_lamp, end_lamp + 1):
        ppuc.set_lamp_state(lamp_num, 0)
        print(f"   Lampe {lamp_num} aus")
        time.sleep(0.05)  # Kurze Verzögerung zwischen Befehlen

def show_menu():
    """Zeigt das Hauptmenü"""
    print("\n" + "="*60)
    print("           PPUC LAMPEN CONTROLLER")
    print("="*60)
    print("1. Lampen 1-50 sequenziell anschalten")
    print("2. Alle Lampen 1-50 gleichzeitig anschalten") 
    print("3. Alle Lampen 1-50 ausschalten")
    print("4. Lampen-Test (automatischer Test)")
    print("5. Hardware-Inventar anzeigen")
    print("0. Beenden")
    print("="*60)

def show_hardware_inventory(ppuc):
    """Zeigt verfügbare Hardware an"""
    try:
        print("\n=== HARDWARE INVENTAR ===")
        
        # Lampen anzeigen
        lamps = ppuc.get_lamps()
        if lamps:
            print(f"\n--- LAMPEN ({len(lamps)} gefunden) ---")
            for lamp in lamps:
                print(f"Lampe {lamp['number']:3d}: {lamp['description']}")
                print(f"         Board: {lamp['board']}, Port: {lamp['port']}, Typ: {lamp['type']}")
        else:
            print("\nKeine Lampen konfiguriert.")
            
        # Spulen anzeigen
        coils = ppuc.get_coils()
        if coils:
            print(f"\n--- SPULEN ({len(coils)} gefunden) ---")
            for coil in coils[:10]:  # Nur erste 10 anzeigen
                print(f"Spule {coil['number']:3d}: {coil['description']}")
                print(f"        Board: {coil['board']}, Port: {coil['port']}, Typ: {coil['type']}")
            if len(coils) > 10:
                print(f"... und {len(coils) - 10} weitere Spulen")
                
        # Schalter anzeigen
        switches = ppuc.get_switches()
        if switches:
            print(f"\n--- SCHALTER ({len(switches)} gefunden) ---")
            for switch in switches[:10]:  # Nur erste 10 anzeigen
                print(f"Schalter {switch['number']:3d}: {switch['description']}")
                print(f"           Board: {switch['board']}, Port: {switch['port']}")
            if len(switches) > 10:
                print(f"... und {len(switches) - 10} weitere Schalter")
                
    except Exception as e:
        print(f"Fehler beim Abrufen des Hardware-Inventars: {e}")

def main():
    global ppuc_instance, running
    
    # Signal-Handler für sauberes Herunterfahren registrieren
    signal.signal(signal.SIGINT, signal_handler)
    
    print("PPUC Lampen Controller gestartet")
    print("=" * 50)
    
    try:
        # PPUC-Instanz erstellen
        ppuc_instance = PPUC()
        
        # Debug-Modus aktivieren (optional)
        ppuc_instance.set_debug(True)
        
        # Log-Callback setzen
        ppuc_instance.set_log_message_callback(log_callback)
        
        # Konfigurationsdatei laden (falls als Argument übergeben)
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
            print(f"Lade Konfiguration aus: {config_file}")
            ppuc_instance.load_configuration(config_file)
        else:
            # Standard-Konfiguration (falls keine Datei angegeben)
            print("Hinweis: Keine Konfigurationsdatei angegeben.")
            print("Verwende: python3 ppuc_lamp_controller.py config.yaml")
        
        # Seriellen Port setzen
        # Automatische Erkennung oder manuell setzen
        serial_ports = ["/dev/ttyUSB0", "/dev/ttyACM0", "/dev/ttyUSB1", "COM3", "COM4"]
        
        # Versuche automatisch einen Port zu finden oder verwende Standard
        if len(sys.argv) > 2:
            serial_port = sys.argv[2]
        else:
            serial_port = "/dev/ttyUSB0"  # Standard für Linux
            
        ppuc_instance.set_serial(serial_port)
        print(f"Verwende seriellen Port: {ppuc_instance.get_serial()}")
        
        # Verbinden mit PPUC-Boards
        print("\nVerbinde mit PPUC-Hardware...")
        if ppuc_instance.connect():
            print("✓ Verbindung hergestellt!")
            
            # Event-Updates starten
            ppuc_instance.start_updates()
            print("✓ Event-Updates gestartet")
            
            # Hauptmenü-Schleife
            while running:
                show_menu()
                
                try:
                    choice = input("\nBitte wählen Sie eine Option: ").strip()
                    
                    if choice == "1":
                        # Sequenzielle Lampen
                        delay = float(input("Verzögerung zwischen Lampen (Sekunden, Standard=0.5): ") or "0.5")
                        test_lamp_sequence(ppuc_instance, 1, 50, delay)
                        
                    elif choice == "2":
                        # Alle Lampen an
                        all_lamps_on(ppuc_instance, 1, 50)
                        input("\nDrücke ENTER um fortzufahren...")
                        
                    elif choice == "3":
                        # Alle Lampen aus
                        all_lamps_off(ppuc_instance, 1, 50)
                        input("\nDrücke ENTER um fortzufahren...")
                        
                    elif choice == "4":
                        # Automatischer Lampen-Test
                        print("\nStarte automatischen Lampen-Test...")
                        print("⚠️  Alle Lampen werden getestet!")
                        confirm = input("Fortfahren? (j/n): ").lower()
                        if confirm == 'j':
                            ppuc_instance.lamp_test()
                        
                    elif choice == "5":
                        # Hardware-Inventar
                        show_hardware_inventory(ppuc_instance)
                        input("\nDrücke ENTER um fortzufahren...")
                        
                    elif choice == "0":
                        # Beenden
                        print("Programm wird beendet...")
                        running = False
                        
                    else:
                        print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")
                        
                except ValueError as e:
                    print(f"Eingabefehler: {e}")
                except EOFError:
                    print("\nEOF empfangen, beende Programm...")
                    running = False
                    
        else:
            print("❌ Verbindung zur PPUC-Hardware fehlgeschlagen!")
            print("\nMögliche Ursachen:")
            print("- Hardware nicht eingeschaltet")
            print("- Falscher serieller Port")
            print("- Fehlende Berechtigungen (sudo usermod -a -G dialout $USER)")
            print("- Kabel nicht verbunden")
            return 1
            
    except PPUCLibraryError as e:
        print(f"❌ Bibliotheksfehler: {e}")
        print("Stellen Sie sicher, dass alle .so Dateien vorhanden sind.")
        return 1
        
    except PPUCConfigurationError as e:
        print(f"❌ Konfigurationsfehler: {e}")
        print("Prüfen Sie die YAML-Syntax und Vollständigkeit der Konfiguration.")
        return 1
        
    except PPUCConnectionError as e:
        print(f"❌ Verbindungsfehler: {e}")
        return 1
        
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Saubere Bereinigung
        if ppuc_instance:
            try:
                print("\nFahre System herunter...")
                
                # Alle Lampen ausschalten
                print("Schalte alle Lampen aus...")
                for lamp_num in range(1, 51):
                    ppuc_instance.set_lamp_state(lamp_num, 0)
                    time.sleep(0.01)
                
                # Updates stoppen
                ppuc_instance.stop_updates()
                print("✓ Event-Updates gestoppt")
                
                # Verbindung trennen
                ppuc_instance.disconnect()
                print("✓ Verbindung getrennt")
                
            except Exception as e:
                print(f"Fehler beim Herunterfahren: {e}")
        
        print("Programm beendet.")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)