# io_subsystem/device_manager.py
import wmi
import pythoncom

class DeviceManager:
    def __init__(self):
        self.devices_cache = []

    def scan_hardware(self):
        """Escanea hardware real omitiendo componentes lógicos y genéricos (Sin deduplicar por nombre)."""
        pythoncom.CoInitialize()
        
        try:
            c = wmi.WMI()
            pnp_devices = c.Win32_PnPEntity(Present=True)
            
            # Forzamos el ID del controlador a mayúsculas para asegurar el cruce de datos
            drivers = {}
            for drv in c.Win32_PnPSignedDriver():
                if drv.DeviceID:
                    drivers[drv.DeviceID.upper()] = drv
            
            results = []
            
            target_classes = [
                "MOUSE", "KEYBOARD", "MEDIA", "AUDIOENDPOINT", 
                "IMAGE", "CAMERA", "DISKDRIVE", "WPD", 
                "BLUETOOTH", "MONITOR"
            ]

            ignored_keywords = [
                "proxy", "controlador", "compatible", "input device", 
                "entrada usb", "control del consumidor", "composite", 
                "compuesto", "hub", "enumerador", "virtual", 
                "software", "redirector", "bus", "hid-compliant"
            ]

            for d in pnp_devices:
                try:
                    if not d.Name or not d.PNPClass or not d.DeviceID:
                        continue
                        
                    pnp_class = d.PNPClass.upper()
                    device_id = d.DeviceID.upper()
                    name_lower = d.Name.lower()
                    
                    if pnp_class not in target_classes:
                        continue

                    is_generic = any(keyword in name_lower for keyword in ignored_keywords)
                    if is_generic:
                        continue
                        
                    if device_id.startswith("ROOT\\") or device_id.startswith("SWD\\") or device_id.startswith("HTREE\\"):
                        if not device_id.startswith("SWD\\MMDEVAPI"):
                            continue
                            
                    # ELIMINADO: Se quitó la lógica de "seen_signatures" para que todos 
                    # los dispositivos físicos reales (incluso si comparten nombre) aparezcan.
                    
                    driver = drivers.get(device_id)
                    
                    results.append({
                        "name": d.Name,
                        "category": self._categorize(d.PNPClass),
                        "manufacturer": d.Manufacturer or "Desconocido",
                        "connection": self._detect_connection(d.DeviceID),
                        "driver_name": d.Service or "No disponible",
                        "driver_provider": driver.DriverProviderName if driver else "No disponible",
                        "driver_version": driver.DriverVersion if driver else "No disponible",
                        "status": d.Status or "OK",
                        "device_id": d.DeviceID
                    })
                except Exception:
                    continue
            
            results.sort(key=lambda x: (x["category"], x["name"]))
            self.devices_cache = results
            return results
            
        finally:
            pythoncom.CoUninitialize()

    def _categorize(self, pnp_class):
        if not pnp_class: return "Otros"
        pnp = pnp_class.upper()
        if pnp in ["MOUSE", "KEYBOARD"]: return "Entrada"
        if pnp in ["MEDIA", "AUDIOENDPOINT"]: return "Audio"
        if pnp in ["IMAGE", "CAMERA"]: return "Cámaras e imagen"
        if pnp in ["DISKDRIVE", "WPD"]: return "Almacenamiento"
        if pnp == "BLUETOOTH": return "Bluetooth"
        if pnp in ["MONITOR", "DISPLAY"]: return "Pantallas y monitores"
        return "Otros"

    def _detect_connection(self, device_id):
        if not device_id: return "Desconocida"
        did = device_id.upper()
        if did.startswith("USB\\"): return "USB"
        if did.startswith("BTHENUM\\") or did.startswith("BTH\\"): return "Bluetooth"
        if did.startswith("PCI\\"): return "PCI / PCIe"
        if did.startswith("HDAUDIO\\") or did.startswith("INTELAUDIO\\"): return "Audio Interno"
        if did.startswith("SWD\\MMDEVAPI"): return "Audio Virtual/Endpoint"
        if did.startswith("ACPI\\"): return "Integrada (Placa Base)"
        return "Externa / Otra"