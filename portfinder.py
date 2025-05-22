# ppuc_example.py erweitern (um Zeile 15 hinzufügen)
import glob

def find_available_ports():
    """Findet alle verfügbaren seriellen Ports"""
    ports = []
    # Linux USB-Serial-Adapter
    ports.extend(glob.glob('/dev/ttyUSB*'))
    ports.extend(glob.glob('/dev/ttyACM*'))
    # Traditionelle serielle Ports
    ports.extend(glob.glob('/dev/ttyS[0-9]*'))
    
    return sorted(ports)

# In der main() Funktion (um Zeile 85 ersetzen):
def main():
    # ... (andere Code bleibt gleich)
    
    # Verfügbare Ports finden
    available_ports = find_available_ports()
    
    if not available_ports:
        print("FEHLER: Keine seriellen Ports gefunden!")
        print("Mögliche Ursachen:")
        print("1. RS485-USB-Adapter nicht angeschlossen")
        print("2. Adapter wird nicht erkannt (Treiber-Problem)")
        print("3. Falscher Adapter-Typ")
        print("\nVersuchen Sie:")
        print("- Adapter ab- und wieder anstecken")
        print("- dmesg | tail prüfen")
        print("- lsusb ausführen")
        return
    
    print(f"Gefundene Ports: {available_ports}")
    
    # Ersten gefundenen Port verwenden
    serial_port = available_ports[0]
    print(f"Verwende Port: {serial_port}")
    
    ppuc.set_serial(serial_port)
    # ... (Rest bleibt gleich)
