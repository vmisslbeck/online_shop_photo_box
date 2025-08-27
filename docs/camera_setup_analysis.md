# Canon DSLR Studio Setup - Kamera-Modi Analyse

## USB-Verbindung Modi bei Canon DSLRs:

### 1. **PTP-Modus (Picture Transfer Protocol)**
- ✅ Kamera bleibt manuell bedienbar
- ✅ Physische Einstellungen (Blende, ISO, etc.) funktionieren normal
- ✅ gphoto2 kann Live-View und Auslösung
- ❌ Begrenzte Software-Steuerung der Kamera-Einstellungen

### 2. **PC-Remote-Modus** 
- ✅ Vollständige Software-Steuerung über gphoto2
- ✅ Alle Parameter programmierbar (ISO, Blende, Verschluss, AF)
- ❌ Kamera-Bedienung oft gesperrt
- ❌ Komplexeres Interface nötig

### 3. **Hybrid-Lösung (Best Practice)**
- Kamera in PTP-Modus
- Wichtige Einstellungen manuell an der Kamera
- Software nur für Live-View und Auslösung
- Bei Bedarf: Schnelle Parameter-Anpassung via gphoto2

## Empfohlene Studio-Konfiguration:

```bash
# Kamera-Fähigkeiten prüfen
gphoto2 --abilities

# Verfügbare Einstellungen anzeigen
gphoto2 --list-config

# Wichtige Parameter abfragen
gphoto2 --get-config iso
gphoto2 --get-config aperture
gphoto2 --get-config shutterspeed
```

## Parameter die typisch via Software steuerbar sind:
- ISO (meist voll steuerbar)
- Blende (bei kompatiblen Objektiven)
- Verschlusszeit
- Autofokus-Modi
- Weißabgleich
- Bildqualität/Format
- Live-View-Einstellungen
