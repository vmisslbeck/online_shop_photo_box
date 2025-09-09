#!/usr/bin/env python3
"""
Canon DSLR Diagnose-Tool
Hilft bei der Fehlersuche für Live-View und manuelle Bedienung
"""

import subprocess
import sys
import time

def run_command(cmd, timeout=10):
    """Führt Kommando aus und gibt Ergebnis zurück"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def diagnose_camera():
    """Führt umfassende Kamera-Diagnose durch"""
    print("Canon DSLR Diagnose-Tool")
    print("=" * 50)
    
    # 1. gphoto2 Installation prüfen
    print("\n Prüfe gphoto2 Installation...")
    rc, out, err = run_command("gphoto2 --version")
    if rc == 0:
        version = out.split('\n')[0] if out else "Unbekannt"
        print(f"gphoto2 installiert: {version}")
    else:
        print("gphoto2 nicht gefunden!")
        print("   Installieren mit: sudo apt-get install gphoto2")
        return False
    
    # 2. Kamera-Erkennung
    print("\n Erkenne angeschlossene Kameras...")
    rc, out, err = run_command("gphoto2 --auto-detect")
    if rc == 0 and "usb:" in out.lower():
        print("Kamera erkannt:")
        for line in out.strip().split('\n'):
            if 'usb:' in line.lower():
                print(f"   {line}")
    else:
        print("Keine Kamera erkannt!")
        print(" Überprüfen Sie USB-Verbindung")
        return False
    
    # 3. Kamera-Zusammenfassung
    print("\n Lade Kamera-Informationen...")
    rc, out, err = run_command("gphoto2 --summary", 15)
    if rc == 0:
        print("Kamera-Zusammenfassung verfügbar")
        # Wichtige Informationen extrahieren
        lines = out.split('\n')
        for line in lines[:10]:
            if any(keyword in line.lower() for keyword in ['model', 'serial', 'firmware', 'battery']):
                print(f"   {line.strip()}")
    else:
        print("Kamera-Zusammenfassung nicht verfügbar")
        print(f"   Fehler: {err}")
    
    # 4. Live-View Test
    print("\n Teste Live-View Funktionalität...")
    rc, out, err = run_command("gphoto2 --capture-preview --filename=test_preview.jpg", 8)
    if rc == 0:
        print(" Live-View Preview funktioniert")
        try:
            import os
            if os.path.exists("test_preview.jpg"):
                size = os.path.getsize("test_preview.jpg")
                print(f"   Preview-Datei: {size} Bytes")
                os.remove("test_preview.jpg")
        except:
            pass
    else:
        print(" Live-View Preview fehlgeschlagen!")
        print(f"   Fehler: {err}")
        print("\n   Mögliche Lösungen:")
        print("   • Kamera in M/Av/Tv-Modus stellen (nicht Auto/Scene)")
        print("   • Live-View an der Kamera aktivieren")
        print("   • Objektiv-Kappe entfernen")
    
    # 5. Verfügbare Konfigurationen
    print("\n Prüfe verfügbare Einstellungen...")
    rc, out, err = run_command("gphoto2 --list-config", 10)
    if rc == 0:
        configs = out.strip().split('\n')
        important_configs = [c for c in configs if any(key in c for key in ['iso', 'aperture', 'shutterspeed', 'capture'])]
        print(f"{len(configs)} Einstellungen verfügbar")
        print("   Wichtige Einstellungen:")
        for config in important_configs[:5]:
            print(f"   • {config}")
    else:
        print("Konnte Konfigurationen nicht abrufen")
    
    # 6. Capture-Test
    print("\n Teste Foto-Aufnahme...")
    rc, out, err = run_command("gphoto2 --capture-image --filename=test_capture.jpg", 10)
    if rc == 0:
        print(" Foto-Aufnahme funktioniert")
        try:
            import os
            if os.path.exists("test_capture.jpg"):
                size = os.path.getsize("test_capture.jpg")
                print(f"   Foto-Datei: {size} Bytes")
                os.remove("test_capture.jpg")
        except:
            pass
    else:
        print("Foto-Aufnahme fehlgeschlagen!")
        print(f"   Fehler: {err}")
    
    # 7. Manuelle Bedienung Check
    print("\n Prüfe manuelle Bedienbarkeit...")
    rc, out, err = run_command("gphoto2 --get-config capture")
    if rc == 0:
        if "current: 0" in out.lower():
            print(" Kamera in PTP-Modus (manuell bedienbar)")
        elif "current: 1" in out.lower():
            print("Kamera in PC-Remote-Modus (nicht manuell bedienbar)")
            print("   Lösung: gphoto2 --set-config capture=0")
        else:
            print("Capture-Modus unbekannt")
    else:
        print("Konnte Capture-Modus nicht prüfen")
    
    print("\n" + "=" * 50)
    print("Diagnose abgeschlossen!")
    
    return True

def fix_common_issues():
    """Versucht häufige Probleme zu beheben"""
    print("\n Versuche häufige Probleme zu beheben...")
    
    # Kamera in manuellen Modus setzen
    print("• Setze Kamera in manuellen Modus...")
    rc, out, err = run_command("gphoto2 --set-config capture=0")
    if rc == 0:
        print("  Manueller Modus aktiviert")
    else:
        print(f"  Fehler: {err}")
    
    # Kamera-Verbindung zurücksetzen
    print("• Setze Kamera-Verbindung zurück...")
    run_command("gphoto2 --exit")
    time.sleep(2)
    
    rc, out, err = run_command("gphoto2 --auto-detect")
    if rc == 0:
        print("  Kamera-Verbindung zurückgesetzt")
    else:
        print("    Problem beim Zurücksetzen")

if __name__ == "__main__":
    try:
        if diagnose_camera():
            if "--fix" in sys.argv:
                fix_common_issues()
            
            print("\n Tipps für optimale Funktion:")
            print("• Kamera in M, Av oder Tv-Modus stellen")
            print("• Live-View an der Kamera aktivieren") 
            print("• Bei Problemen: python diagnose.py --fix")
        
    except KeyboardInterrupt:
        print("\n\n Diagnose abgebrochen")
    except Exception as e:
        print(f"\n Unerwarteter Fehler: {e}")
