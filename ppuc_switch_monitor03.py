#!/usr/bin/env python3
"""
PPUC Switch Monitor - Minimaler Ansatz
Einfache Ausgabe aller Switch-Ereignisse
"""

import sys
import time
import signal
from ppuc_wrapper import PPUC

# Global für Signal-Handler
running = True
ppuc_instance = None

def signal_handler(signum, frame):
    """Signal-Handler für Ctrl+C"""
    global running, ppuc_instance
    print("\nBeende...")
    running = False
    if ppuc_instance:
        try:
            ppuc_instance.stop_updates()
            ppuc_instance.disconnect()
        except:
            pass

# Signal-Handler registrieren
signal.signal(signal.SIGINT, signal_handler)

def main():
    global running, ppuc_instance
    
    # Parameter aus Kommandozeile
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    serial_port = sys.argv[2] if len(sys.argv) > 2 else "/dev/ttyUSB0"
    
    print(f"PPUC Switch Monitor - Minimaler Ansatz")
    print(f"Config: {config_file}")
    print(f"Port: {serial_port}")
    print("-" * 40)
    
    try:
        # PPUC initialisieren
        ppuc_instance = PPUC()
        
        # Debug aus
        ppuc_instance.set_debug(False)
        
        # Konfiguration laden
        ppuc_instance.load_configuration(config_file)
        
        # Seriellen Port setzen
        ppuc_instance.set_serial(serial_port)
        
        # Verbinden
        if not ppuc_instance.connect():
            print("Verbindung fehlgeschlagen!")
            return
        
        print("Verbunden! Starte Updates...")
        
        # Updates starten
        ppuc_instance.start_updates()
        
        print("Monitoring Switch-Ereignisse (Ctrl+C zum Beenden):\n")
        
        # Hauptschleife
        while running:
            # Nächstes Switch-Event abrufen
            event = ppuc_instance.get_next_switch_state()
            
            if event:
                switch_number, switch_state = event
                state_text = "AN" if switch_state else "AUS"
                print(f"Switch {switch_number}: {state_text}")
            else:
                # Kurze Pause wenn keine Events
                time.sleep(0.01)
    
    except Exception as e:
        print(f"Fehler: {e}")
    
    finally:
        # Cleanup
        if ppuc_instance:
            try:
                ppuc_instance.stop_updates()
                ppuc_instance.disconnect()
            except:
                pass
        print("Beendet.")

if __name__ == "__main__":
    main()
