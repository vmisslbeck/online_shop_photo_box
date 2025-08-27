# Studio-Setup Anleitung

## 🎯 **Für Ihr Canon DSLR Studio-Setup**

### **1. Kamera-Steuerung: Hybrid-Ansatz (Empfohlen)**

```bash
# Starten Sie die Anwendung im Studio-Modus
python src/main.py --studio
```

#### **Empfohlene Konfiguration:**
- **Kamera-Modus**: PTP (Picture Transfer Protocol)
- **Manuelle Bedienung**: ✅ Blende, ISO, Verschluss direkt an der Kamera
- **Software-Steuerung**: ✅ Live-View, Auslösung, Spezial-Einstellungen

#### **Vorteile dieses Ansatzes:**
- 🎛️ **Gewohnte Bedienung**: Photographer kann weiterhin direkt an der Kamera arbeiten
- ⚡ **Schnelle Anpassungen**: Keine Software-Menüs für Standard-Einstellungen
- 🔧 **Software-Power**: Erweiterte Funktionen wie Bracketing, Intervall-Timer via UI
- 🛡️ **Ausfallsicher**: Kamera funktioniert auch bei Software-Problemen

### **2. Lightroom-Integration: Network-Share Lösung**

#### **Setup-Schritte:**

1. **Netzwerk-Ordner erstellen** (auf Lightroom-PC):
   ```
   Erstellen Sie: \\LIGHTROOM-PC\PhotoBox-Import\
   Rechte: Photo-Box-System braucht Schreibzugang
   ```

2. **Photo-Box konfigurieren**:
   - Studio-Kontrollpanel öffnen
   - "Studio-Modus aktivieren" ✅
   - Lightroom-Ordner: `\\LIGHTROOM-PC\PhotoBox-Import\`

3. **Lightroom Auto-Import konfigurieren**:
   ```
   Lightroom → Datei → Auto-Import-Einstellungen
   Überwachter Ordner: \\LIGHTROOM-PC\PhotoBox-Import\
   Zielkatalog: Aktueller Katalog
   Zielsammlung: "Studio Session [Datum]"
   ```

#### **Workflow:**
```
[Canon DSLR] --USB--> [Photo-Box] --Network--> [Lightroom-PC]
                          ↓
                   [Lokale Kopie]
                          ↓
                    [Auto-Sync Script]
```

### **3. Alternative: Professionelle Tethering-Lösung**

Für maximale Kompatibilität mit bestehenden Workflows:

#### **Option A: Capture One Pro**
- Nativ USB-over-Network Support
- Direktes Tethering über Netzwerk möglich
- Lightroom-Plugin für Sync verfügbar

#### **Option B: USB-over-Network Tools**
```bash
# USB Network Gate (Windows)
# Teilt USB-Geräte über Netzwerk
# Lightroom sieht Kamera als "lokal angeschlossen"
```

### **4. Praktische Empfehlung für Ihr Studio**

#### **Phase 1: Einfach starten**
1. Beginnen Sie mit **Hybrid-Ansatz** (PTP-Modus)
2. Nutzen Sie **Network-Share** für Lightroom
3. Behalten Sie manuelle Kamera-Bedienung bei

#### **Phase 2: Bei Bedarf erweitern**
- Teste Sie Software-Steuerung für spezielle Shots
- Implementieren Sie Bracketing/HDR-Automatik
- Erweitern Sie um Remote-Monitoring

### **5. Test-Kommandos für Ihre Canon DSLR**

```bash
# Kamera-Fähigkeiten prüfen
gphoto2 --auto-detect
gphoto2 --abilities

# Verfügbare Einstellungen
gphoto2 --list-config

# Wichtige Parameter testen
gphoto2 --get-config iso
gphoto2 --get-config aperture
gphoto2 --get-config shutterspeed

# Live-View testen
gphoto2 --capture-preview --filename=test.jpg

# Tethered Shooting testen
gphoto2 --capture-image-and-download --filename="test_%Y%m%d_%H%M%S.jpg"
```

### **6. Erwartete Canon DSLR Kompatibilität**

| **Funktion** | **Verfügbarkeit** |
|---|---|
| Live-View | ✅ Alle modernen DSLRs |
| Remote-Auslösung | ✅ Alle modernen DSLRs |
| ISO-Steuerung | ✅ Software-steuerbar |
| Verschlusszeit | ✅ Software-steuerbar |
| Blende | ⚠️ Abhängig vom Objektiv |
| Autofokus | ✅ Basic AF-Modi |
| Weißabgleich | ✅ Alle Presets |
| Bildformat | ✅ RAW/JPEG-Einstellungen |

**Tipp**: Testen Sie zuerst alle Funktionen mit `gphoto2` direkt, bevor Sie das UI verwenden!
