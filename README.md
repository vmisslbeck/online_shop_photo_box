# online_shop_photo_box

Eine Photo Box Anwendung mit Live-Kamera-Display und gphoto2 Integration.

## Features

- **Live Kamera-Display**: Zeigt Live-Vorschau der angeschlossenen Kamera
- **gphoto2 Integration**: Professionelle Kamera-Steuerung über gphoto2
- **Dummy-Modus**: Automatische Entwicklungsumgebung ohne echte Kamera
- **Photo Capture**: Foto-Aufnahme mit einem Klick
- **GPIO Support**: Hardware-Button Integration
- **Network Config**: IP-Adresse konfigurierbar

## Installation

### Linux (Produktionsumgebung)

```bash
# gphoto2 installieren
sudo apt-get update
sudo apt-get install gphoto2 libgphoto2-dev

# Python-Abhängigkeiten
pip install -r requirements.txt
```

### Windows (Entwicklungsumgebung)

```bash
# Nur Python-Abhängigkeiten (Dummy-Modus wird automatisch aktiviert)
pip install -r requirements.txt
```

## Kamera-Funktionalität

### Automatische Modus-Erkennung

Das System erkennt automatisch:
- **Windows**: Dummy-Modus (simulierte Kamera)
- **Linux ohne gphoto2**: Dummy-Modus
- **Linux mit gphoto2**: Echter Kamera-Modus

### Dummy-Modus Features

- Simulierte Live-Vorschau mit Zeitstempel
- Frame-Counter
- Simulierte Kamera-Informationen (ISO, Blende, Verschlusszeit)
- Fadenkreuz-Overlay
- Foto-Simulation

### Unterstützte Kameras

Alle von gphoto2 unterstützten Kameras:
- Canon DSLR/Mirrorless
- Nikon DSLR/Mirrorless
- Sony Alpha Serie
- Und viele mehr

## Verwendung

```python
python src/main.py
```

### UI-Bedienung

1. **Live View starten**: Startet die Kamera-Vorschau
2. **Foto aufnehmen**: Macht ein Foto und speichert es
3. **IP einstellen**: Konfiguriert die Netzwerk-IP
4. **GPIO Events**: Hardware-Buttons triggern Aktionen