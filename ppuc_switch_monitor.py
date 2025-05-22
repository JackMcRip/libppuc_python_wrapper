#!/usr/bin/env python3
"""
PPUC Switch Event Monitor
Überwacht kontinuierlich alle Switch-Ereignisse von PPUC-Boards
"""

import sys
import time
import signal
import os
from ppuc_wrapper import PPUC

class PPUCSwitchMonitor:
    def __init__(self):
        self.ppuc = None
        self.running = False
        
        # Signal-Handler für sauberes Beenden (Ctrl+C)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Signal-Handler für sauberes Beenden"""
        print(f"\nSignal {signum} empfangen. Beende Monitor...")
        self.running = False
    
    def setup_logging_callback(self):
        """Setzt einen Logging-Callback für Debug-Ausgaben"""
        def log_callback(message):
            print(f"[PPUC LOG] {message}")
        
        try:
            self.ppuc.set_log_message_callback(log_callback)
            print("Logging-Callback erfolgreich gesetzt")
        except Exception as e:
            print(f"Warnung: Konnte Logging-Callback nicht setzen: {e}")
    
    def connect_to_boards(self, config_file="config.yaml", serial_port="/dev/ttyUSB0", debug=True):
        """
        Stellt Verbindung zu den PPUC-Boards her
        
        Args:
            config_file: Pfad zur YAML-Konfigurationsdatei
            serial_port: Serieller Port für RS485-Kommunikation
            debug: Debug-Modus aktivieren
        """
        try:
            # PPUC-Instanz erstellen
            print("Erstelle PPUC-Instanz...")
            self.ppuc = PPUC()
            
            # Debug-Modus setzen
            print(f"Setze Debug-Modus: {debug}")
            self.ppuc.set_debug(debug)
            
            # Logging-Callback setzen (optional)
            self.setup_logging_callback()
            
            # Prüfe ob Konfigurationsdatei existiert
            if not os.path.exists(config_file):
                print(f"Warnung: Konfigurationsdatei '{config_file}' nicht gefunden!")
                print("Versuche trotzdem fortzufahren...")
            else:
                print(f"Lade Konfiguration aus: {config_file}")
                self.ppuc.load_configuration(config_file)
            
            # Seriellen Port setzen
            print(f"Setze seriellen Port: {serial_port}")
            self.ppuc.set_serial(serial_port)
            
            # Verbindung herstellen
            print("Verbinde mit PPUC-Boards...")
            if self.ppuc.connect():
                print("✓ Verbindung erfolgreich hergestellt!")
                
                # Updates starten
                print("Starte Event-Updates...")
                self.ppuc.start_updates()
                print("✓ Event-Updates gestartet!")
                
                return True
            else:
                print("✗ Verbindung fehlgeschlagen!")
                return False
                
        except Exception as e:
            print(f"✗ Fehler beim Verbinden: {e}")
            return False
    
    def monitor_switch_events(self):
        """Überwacht kontinuierlich Switch-Ereignisse"""
        print("\n" + "="*60)
        print("SWITCH EVENT MONITOR GESTARTET")
        print("Drücken Sie Ctrl+C zum Beenden")
        print("="*60)
        print("Format: Switch <Nummer>: <Zustand> (AKTIV/INAKTIV)")
        print("="*60)
        
        self.running = True
        last_event_time = time.time()
        
        try:
            while self.running:
                # Nächstes Switch-Event abrufen
                event = self.ppuc.get_next_switch_state()
                
                if event:
                    switch_number, switch_state = event
                    state_text = "AKTIV" if switch_state else "INAKTIV"
                    timestamp = time.strftime("%H:%M:%S")
                    
                    print(f"[{timestamp}] Switch {switch_number:3d}: {state_text}")
                    last_event_time = time.time()
                else:
                    # Kleine Pause wenn keine Events vorliegen
                    time.sleep(0.001)  # 1ms Pause
                    
                    # Lebenszeichen alle 10 Sekunden wenn keine Events
                    if time.time() - last_event_time > 10:
                        print(f"[{time.strftime('%H:%M:%S')}] Monitoring läuft... (keine Events)")
                        last_event_time = time.time()
                        
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt empfangen")
        except Exception as e:
            print(f"\nFehler während Monitoring: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Saubere Bereinigung der Verbindung"""
        if self.ppuc:
            try:
                print("\nBeende Updates...")
                self.ppuc.stop_updates()
                
                print("Trenne Verbindung...")
                self.ppuc.disconnect()
                
                print("✓ Cleanup abgeschlossen")
            except Exception as e:
                print(f"Fehler beim Cleanup: {e}")
    
    def get_switch_info(self):
        """Zeigt Informationen über konfigurierte Switches"""
        try:
            switches = self.ppuc.get_switches()
            if switches:
                print(f"\nGefundene Switches ({len(switches)}):")
                print("-" * 60)
                for switch in switches:
                    print(f"Switch {switch['number']:3d}: {switch['description']} "
                          f"(Board {switch['board']}, Port {switch['port']})")
                print("-" * 60)
            else:
                print("Keine Switches konfiguriert")
        except Exception as e:
            print(f"Fehler beim Abrufen der Switch-Informationen: {e}")


def main():
    """Hauptfunktion"""
    print("PPUC Switch Event Monitor v1.0")
    print("=" * 40)
    
    # Kommandozeilenargumente (einfache Implementierung)
    config_file = "config.yaml"
    serial_port = "/dev/ttyUSB0"
    debug = False
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    if len(sys.argv) > 2:
        serial_port = sys.argv[2]
    if len(sys.argv) > 3:
        debug = sys.argv[3].lower() in ['true', '1', 'yes']
    
    # Monitor erstellen
    monitor = PPUCSwitchMonitor()
    
    # Verbindung herstellen
    if monitor.connect_to_boards(config_file, serial_port, debug):
        # Switch-Informationen anzeigen
        monitor.get_switch_info()
        
        # Monitoring starten
        monitor.monitor_switch_events()
    else:
        print("Konnte keine Verbindung zu den PPUC-Boards herstellen!")
        sys.exit(1)


if __name__ == "__main__":
    main()
