"""
PPUC Python Binding mit C-Wrapper
Verwendet alle Funktionen der PPUC-Bibliothek über einen C-Wrapper.
"""

import ctypes
import os
import platform
from typing import Optional, Tuple, List

# Strukturen
class PPUCSwitchState(ctypes.Structure):
    _fields_ = [
        ("number", ctypes.c_int),
        ("state", ctypes.c_int)
    ]

class PPUCSwitch(ctypes.Structure):
    _fields_ = [
        ("board", ctypes.c_uint8),
        ("port", ctypes.c_uint8),
        ("number", ctypes.c_uint8),
        ("description", ctypes.c_char_p)
    ]

class PPUCCoil(ctypes.Structure):
    _fields_ = [
        ("board", ctypes.c_uint8),
        ("port", ctypes.c_uint8),
        ("type", ctypes.c_uint8),
        ("number", ctypes.c_uint8),
        ("description", ctypes.c_char_p)
    ]

class PPUCLamp(ctypes.Structure):
    _fields_ = [
        ("board", ctypes.c_uint8),
        ("port", ctypes.c_uint8),
        ("type", ctypes.c_uint8),
        ("number", ctypes.c_uint8),
        ("description", ctypes.c_char_p)
    ]

# Callback-Typ
PPUC_LogMessageCallback = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
    ctypes.c_void_p,
    ctypes.c_void_p
)

# Konstanten
LED_TYPE_LAMP = 1
LED_TYPE_FLASHER = 2
LED_TYPE_GI = 3

PWM_TYPE_SOLENOID = 1
PWM_TYPE_FLASHER = 2
PWM_TYPE_LAMP = 3
PWM_TYPE_MOTOR = 4

PLATFORM_WPC = 0
PLATFORM_DATA_EAST = 1
PLATFORM_SYS4 = 2
PLATFORM_SYS11 = 3

class PPUC:
    """
    PPUC Python-Wrapper mit vollständiger Funktionalität über C-Wrapper.
    """
    
    def __init__(self):
        """Initialisiert die PPUC-Bibliothek über den C-Wrapper."""
        # Lade die Wrapper-Bibliothek
        lib_path = os.path.join(os.path.dirname(__file__), "libppuc_wrapper.so")
        try:
            self.lib = ctypes.CDLL(lib_path)
        except OSError as e:
            raise RuntimeError(f"Konnte die PPUC-Wrapper-Bibliothek nicht laden: {e}") from e
        
        # Definiere alle Funktionssignaturen
        self._setup_function_signatures()
        
        # Erstelle PPUC-Instanz
        self.obj = self.lib.ppuc_new()
        if not self.obj:
            raise RuntimeError("Konnte keine PPUC-Instanz erstellen")
        
        # Callback-Speicher
        self._log_callback = None
    
    def _setup_function_signatures(self):
        """Setzt alle Funktionssignaturen für den C-Wrapper."""
        
        # Konstruktor/Destruktor
        self.lib.ppuc_new.restype = ctypes.c_void_p
        self.lib.ppuc_new.argtypes = []
        
        self.lib.ppuc_delete.restype = None
        self.lib.ppuc_delete.argtypes = [ctypes.c_void_p]
        
        # Logging
        self.lib.ppuc_set_log_message_callback.restype = None
        self.lib.ppuc_set_log_message_callback.argtypes = [ctypes.c_void_p, PPUC_LogMessageCallback, ctypes.c_void_p]
        
        # Konfiguration
        self.lib.ppuc_load_configuration.restype = None
        self.lib.ppuc_load_configuration.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        
        self.lib.ppuc_set_debug.restype = None
        self.lib.ppuc_set_debug.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        
        self.lib.ppuc_get_debug.restype = ctypes.c_bool
        self.lib.ppuc_get_debug.argtypes = [ctypes.c_void_p]
        
        self.lib.ppuc_set_rom.restype = None
        self.lib.ppuc_set_rom.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        
        self.lib.ppuc_get_rom.restype = ctypes.c_char_p
        self.lib.ppuc_get_rom.argtypes = [ctypes.c_void_p]
        
        self.lib.ppuc_set_serial.restype = None
        self.lib.ppuc_set_serial.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        
        self.lib.ppuc_get_serial.restype = ctypes.c_char_p
        self.lib.ppuc_get_serial.argtypes = [ctypes.c_void_p]
        
        # Verbindung
        self.lib.ppuc_connect.restype = ctypes.c_bool
        self.lib.ppuc_connect.argtypes = [ctypes.c_void_p]
        
        self.lib.ppuc_disconnect.restype = None
        self.lib.ppuc_disconnect.argtypes = [ctypes.c_void_p]
        
        self.lib.ppuc_start_updates.restype = None
        self.lib.ppuc_start_updates.argtypes = [ctypes.c_void_p]
        
        self.lib.ppuc_stop_updates.restype = None
        self.lib.ppuc_stop_updates.argtypes = [ctypes.c_void_p]
        
        # Steuerung
        self.lib.ppuc_set_solenoid_state.restype = None
        self.lib.ppuc_set_solenoid_state.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        
        self.lib.ppuc_set_lamp_state.restype = None
        self.lib.ppuc_set_lamp_state.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        
        self.lib.ppuc_get_next_switch_state.restype = ctypes.POINTER(PPUCSwitchState)
        self.lib.ppuc_get_next_switch_state.argtypes = [ctypes.c_void_p]
        
        # Spezielle Getter
        self.lib.ppuc_get_coin_door_closed_switch.restype = ctypes.c_uint8
        self.lib.ppuc_get_coin_door_closed_switch.argtypes = [ctypes.c_void_p]
        
        self.lib.ppuc_get_game_on_solenoid.restype = ctypes.c_uint8
        self.lib.ppuc_get_game_on_solenoid.argtypes = [ctypes.c_void_p]
        
        # Tests
        self.lib.ppuc_coil_test.restype = None
        self.lib.ppuc_coil_test.argtypes = [ctypes.c_void_p]
        
        self.lib.ppuc_lamp_test.restype = None
        self.lib.ppuc_lamp_test.argtypes = [ctypes.c_void_p]
        
        self.lib.ppuc_switch_test.restype = None
        self.lib.ppuc_switch_test.argtypes = [ctypes.c_void_p]
        
        # Listen-Funktionen
        self.lib.ppuc_get_coils.restype = ctypes.POINTER(PPUCCoil)
        self.lib.ppuc_get_coils.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        
        self.lib.ppuc_free_coils.restype = None
        self.lib.ppuc_free_coils.argtypes = [ctypes.POINTER(PPUCCoil)]
        
        self.lib.ppuc_get_lamps.restype = ctypes.POINTER(PPUCLamp)
        self.lib.ppuc_get_lamps.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        
        self.lib.ppuc_free_lamps.restype = None
        self.lib.ppuc_free_lamps.argtypes = [ctypes.POINTER(PPUCLamp)]
        
        self.lib.ppuc_get_switches.restype = ctypes.POINTER(PPUCSwitch)
        self.lib.ppuc_get_switches.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        
        self.lib.ppuc_free_switches.restype = None
        self.lib.ppuc_free_switches.argtypes = [ctypes.POINTER(PPUCSwitch)]
    
    def __del__(self):
        """Säubert die PPUC-Instanz."""
        if hasattr(self, 'obj') and self.obj:
            self.lib.ppuc_delete(self.obj)
    
    def set_log_message_callback(self, callback):
        """Setzt einen Logging-Callback."""
        def c_log_callback(format_str, va_list, user_data):
            try:
                message = ctypes.string_at(format_str).decode('utf-8')
                callback(message)
            except Exception as e:
                print(f"Fehler im Log-Callback: {e}")
        
        self._log_callback = PPUC_LogMessageCallback(c_log_callback)
        self.lib.ppuc_set_log_message_callback(self.obj, self._log_callback, None)
    
    def load_configuration(self, config_file: str):
        """Lädt eine Konfigurationsdatei."""
        self.lib.ppuc_load_configuration(self.obj, config_file.encode('utf-8'))
    
    def set_debug(self, debug: bool):
        """Setzt den Debug-Modus."""
        self.lib.ppuc_set_debug(self.obj, debug)
    
    def get_debug(self) -> bool:
        """Gibt den Debug-Modus zurück."""
        return self.lib.ppuc_get_debug(self.obj)
    
    def set_rom(self, rom: str):
        """Setzt den ROM-Namen."""
        self.lib.ppuc_set_rom(self.obj, rom.encode('utf-8'))
    
    def get_rom(self) -> str:
        """Gibt den ROM-Namen zurück."""
        return self.lib.ppuc_get_rom(self.obj).decode('utf-8')
    
    def set_serial(self, serial: str):
        """Setzt den seriellen Port."""
        self.lib.ppuc_set_serial(self.obj, serial.encode('utf-8'))
    
    def get_serial(self) -> str:
        """Gibt den seriellen Port zurück."""
        return self.lib.ppuc_get_serial(self.obj).decode('utf-8')
    
    def connect(self) -> bool:
        """Verbindet mit den PPUC-Boards."""
        return self.lib.ppuc_connect(self.obj)
    
    def disconnect(self):
        """Trennt die Verbindung."""
        self.lib.ppuc_disconnect(self.obj)
    
    def start_updates(self):
        """Startet Updates."""
        self.lib.ppuc_start_updates(self.obj)
    
    def stop_updates(self):
        """Stoppt Updates."""
        self.lib.ppuc_stop_updates(self.obj)
    
    def set_solenoid_state(self, number: int, state: int):
        """Setzt den Zustand einer Spule."""
        self.lib.ppuc_set_solenoid_state(self.obj, number, state)
    
    def set_lamp_state(self, number: int, state: int):
        """Setzt den Zustand einer Lampe."""
        self.lib.ppuc_set_lamp_state(self.obj, number, state)
    
    def get_next_switch_state(self) -> Optional[Tuple[int, int]]:
        """Gibt den nächsten Schalter-Zustand zurück."""
        switch_state_ptr = self.lib.ppuc_get_next_switch_state(self.obj)
        if not switch_state_ptr:
            return None
        
        switch_state = switch_state_ptr.contents
        return (switch_state.number, switch_state.state)
    
    def get_coin_door_closed_switch(self) -> int:
        """Gibt die Münztür-Schalter-Nummer zurück."""
        return self.lib.ppuc_get_coin_door_closed_switch(self.obj)
    
    def get_game_on_solenoid(self) -> int:
        """Gibt die Game-On-Spulen-Nummer zurück."""
        return self.lib.ppuc_get_game_on_solenoid(self.obj)
    
    def coil_test(self):
        """Führt einen Spulentest durch."""
        self.lib.ppuc_coil_test(self.obj)
    
    def lamp_test(self):
        """Führt einen Lampentest durch."""
        self.lib.ppuc_lamp_test(self.obj)
    
    def switch_test(self):
        """Führt einen Schaltertest durch."""
        self.lib.ppuc_switch_test(self.obj)
    
    def get_coils(self) -> List[dict]:
        """Gibt alle Spulen zurück."""
        count = ctypes.c_int()
        coils_ptr = self.lib.ppuc_get_coils(self.obj, ctypes.byref(count))
        
        coils = []
        for i in range(count.value):
            coil = coils_ptr[i]
            coils.append({
                'board': coil.board,
                'port': coil.port,
                'type': coil.type,
                'number': coil.number,
                'description': coil.description.decode('utf-8') if coil.description else ""
            })
        
        self.lib.ppuc_free_coils(coils_ptr)
        return coils
    
    def get_lamps(self) -> List[dict]:
        """Gibt alle Lampen zurück."""
        count = ctypes.c_int()
        lamps_ptr = self.lib.ppuc_get_lamps(self.obj, ctypes.byref(count))
        
        lamps = []
        for i in range(count.value):
            lamp = lamps_ptr[i]
            lamps.append({
                'board': lamp.board,
                'port': lamp.port,
                'type': lamp.type,
                'number': lamp.number,
                'description': lamp.description.decode('utf-8') if lamp.description else ""
            })
        
        self.lib.ppuc_free_lamps(lamps_ptr)
        return lamps
    
    def get_switches(self) -> List[dict]:
        """Gibt alle Schalter zurück."""
        count = ctypes.c_int()
        switches_ptr = self.lib.ppuc_get_switches(self.obj, ctypes.byref(count))
        
        switches = []
        for i in range(count.value):
            switch = switches_ptr[i]
            switches.append({
                'board': switch.board,
                'port': switch.port,
                'number': switch.number,
                'description': switch.description.decode('utf-8') if switch.description else ""
            })
        
        self.lib.ppuc_free_switches(switches_ptr)
        return switches

# Exportiere alle Konstanten
__all__ = [
    'PPUC',
    'LED_TYPE_LAMP', 'LED_TYPE_FLASHER', 'LED_TYPE_GI',
    'PWM_TYPE_SOLENOID', 'PWM_TYPE_FLASHER', 'PWM_TYPE_LAMP', 'PWM_TYPE_MOTOR',
    'PLATFORM_WPC', 'PLATFORM_DATA_EAST', 'PLATFORM_SYS4', 'PLATFORM_SYS11'
]
