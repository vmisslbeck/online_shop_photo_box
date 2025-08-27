# Lightroom Integration Lösungen für USB-gesteuerte Kamera

## Problem:
- Kamera an Photo-Box-System (USB)
- Lightroom/Photoshop läuft auf separatem Rechner
- Workflow muss beibehalten werden

## Lösung 1: **Folder Watching + Network Share**
```python
# Automatische Foto-Weiterleitung
import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PhotoForwarder(FileSystemEventHandler):
    def __init__(self, target_folder):
        self.target_folder = target_folder
    
    def on_created(self, event):
        if event.is_file and event.src_path.lower().endswith(('.jpg', '.raw', '.cr2', '.cr3')):
            # Foto an Lightroom-Ordner weiterleiten
            filename = os.path.basename(event.src_path)
            target_path = os.path.join(self.target_folder, filename)
            shutil.copy2(event.src_path, target_path)
            print(f"Foto weitergeleitet: {filename}")
```

## Lösung 2: **Canon EOS Utility Tunnel**
- Photo-Box als "Proxy" zwischen Kamera und Lightroom
- USB-Over-Network Tools
- Virtual USB Hub Software

## Lösung 3: **Lightroom Plugin Integration**
```lua
-- Lightroom Plugin für Remote-Folder-Import
-- Überwacht Network-Share automatisch
-- Importiert neue Fotos direkt in Sammlung
```

## Lösung 4: **Professionelle Tethering-Software**
- **Capture One Pro**: Nativ USB-over-Network
- **Smart Shooter**: Automatische Weiterleitung
- **DSLR Controller**: Network-Streaming

## Empfohlene Studio-Architektur:

```
[Canon DSLR] --USB--> [Photo-Box-System] --Network--> [Lightroom-PC]
                            |
                       [Local Storage]
                            |
                     [Auto-Sync Script]
```

## Implementation Details:

### Network Share Setup:
1. Photo-Box speichert in lokalen "capture" Ordner
2. Network-Share zu Lightroom-PC
3. Lightroom "Auto-Import" auf Share-Ordner
4. Optional: Automatisches Löschen nach successful import

### Metadata Preservation:
- EXIF-Daten bleiben erhalten
- Dateiname-Konventionen beibehalten
- Timestamp-Synchronisation
