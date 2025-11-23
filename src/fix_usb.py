#!/usr/bin/env python3
"""
Canon DSLR USB-Konflikt Behebung
Speziell für "Could not claim the USB device" Fehler
"""

import subprocess
import sys
import time
import os

def run_command(cmd, timeout=10, show_output=False):
    """Führt Kommando aus und gibt Ergebnis zurück"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        if show_output and result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        if show_output and result.stderr:
            print(f"   Error: {result.stderr.strip()}")
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def kill_gvfs_processes():
    """Stoppt alle gvfs-Prozesse die die Kamera blockieren"""
    print("🔧 Stoppe gvfs-Prozesse...")
    
    processes_to_kill = [
        "gvfs-gphoto2-volume-monitor",
        "gvfs-mtp-volume-monitor", 
        "gvfs-afc-volume-monitor",
        "gvfs-goa-volume-monitor"
    ]
    
    killed_any = False
    
    for process in processes_to_kill:
        # Prüfe ob Prozess läuft
        rc, out, err = run_command(f"pgrep -f {process}")
        if rc == 0 and out.strip():
            print(f"• Stoppe {process}...")
            
            # Verschiedene Kill-Methoden
            commands = [
                f"pkill -f {process}",
                f"killall {process}",
                f"systemctl --user stop {process}.service"
            ]
            
            for cmd in commands:
                run_command(cmd, timeout=5)
                time.sleep(0.5)
            
            killed_any = True
        else:
            print(f"• {process} läuft nicht")
    
    if killed_any:
        print("⏳ Warte 3 Sekunden...")
        time.sleep(3)
        return True
    else:
        print("✅ Keine gvfs-Prozesse gefunden")
        return False

def disable_gvfs_auto_mount():
    """Deaktiviert automatisches Mounten von Kameras"""
    print("\n🔧 Deaktiviere gvfs Auto-Mount...")
    
    # Erstelle gsettings override
    commands = [
        "gsettings set org.gnome.desktop.media-handling automount false",
        "gsettings set org.gnome.desktop.media-handling automount-open false",
        "gsettings set org.gnome.desktop.media-handling autorun-never true"
    ]
    
    for cmd in commands:
        rc, out, err = run_command(cmd)
        if rc == 0:
            setting = cmd.split()[-2:]
            print(f"✅ {' '.join(setting)}")
        else:
            print(f"⚠️ Fehler bei: {cmd}")

def create_udev_rules():
    """Erstellt udev-Regeln für besseren Kamera-Zugriff"""
    print("\n🔧 Erstelle udev-Regeln...")
    
    udev_rule = '''# Canon DSLR udev rules for gphoto2
# Verhindert automatisches Mounten und gibt gphoto2 Priorität

# Canon Kameras (Vendor ID 04a9)
SUBSYSTEM=="usb", ATTRS{idVendor}=="04a9", MODE="0664", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04a9", TAG+="uaccess"

# Verhindere automatisches Mounten von Kameras
SUBSYSTEM=="usb", ATTRS{idVendor}=="04a9", ENV{UDISKS_IGNORE}="1"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04a9", ENV{GVFS_IGNORE}="1"

# Nikon Kameras (falls vorhanden)
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b0", MODE="0664", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b0", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b0", ENV{UDISKS_IGNORE}="1"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b0", ENV{GVFS_IGNORE}="1"
'''
    
    rule_file = "/tmp/99-camera-gphoto2.rules"
    
    try:
        with open(rule_file, 'w') as f:
            f.write(udev_rule)
        
        print(f"✅ udev-Regel erstellt: {rule_file}")
        print("\n📋 Um zu installieren, führe aus:")
        print(f"   sudo cp {rule_file} /etc/udev/rules.d/")
        print("   sudo udevadm control --reload-rules")
        print("   sudo udevadm trigger")
        
        # Versuche automatisch zu installieren (mit sudo)
        if os.geteuid() == 0:  # Als root
            run_command(f"cp {rule_file} /etc/udev/rules.d/")
            run_command("udevadm control --reload-rules")
            run_command("udevadm trigger")
            print("✅ udev-Regeln automatisch installiert")
        else:
            print("\n💡 Für automatische Installation führe als root aus:")
            print("   sudo python fix_usb.py")
            
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der udev-Regel: {e}")

def reset_usb_device():
    """Setzt USB-Geräte zurück"""
    print("\n🔧 Setze USB-Geräte zurück...")
    
    # Finde Canon USB-Geräte
    rc, out, err = run_command("lsusb | grep -i canon")
    if rc == 0 and out.strip():
        print("Canon USB-Geräte gefunden:")
        for line in out.strip().split('\n'):
            print(f"   {line}")
        
        # USB reset versuchen (falls usbreset verfügbar)
        rc, out, err = run_command("which usbreset")
        if rc == 0:
            print("• Verwende usbreset...")
            run_command("usbreset 'Canon'")
        else:
            print("• usbreset nicht verfügbar, verwende alternative Methode...")
            
            # Alternative: USB-Port über sysfs zurücksetzen
            rc, out, err = run_command("find /sys/bus/usb/devices/ -name '*Canon*' -type l")
            if rc == 0 and out.strip():
                for device_path in out.strip().split('\n'):
                    try:
                        base_path = device_path.rsplit('/', 1)[0]
                        authorized_file = f"{base_path}/authorized"
                        
                        if os.path.exists(authorized_file):
                            run_command(f"echo 0 | sudo tee {authorized_file}")
                            time.sleep(1)
                            run_command(f"echo 1 | sudo tee {authorized_file}")
                            print(f"✅ USB-Device zurückgesetzt: {device_path}")
                    except:
                        pass
    else:
        print("⚠️ Keine Canon USB-Geräte gefunden")

def test_gphoto2_access():
    """Testet gphoto2-Zugriff nach dem Fix"""
    print("\n🧪 Teste gphoto2-Zugriff...")
    
    # Kurz warten
    time.sleep(2)
    
    # Auto-detect Test
    rc, out, err = run_command("gphoto2 --auto-detect", timeout=10)
    if rc == 0 and "usb:" in out.lower():
        print("✅ Kamera-Erkennung funktioniert")
        for line in out.strip().split('\n'):
            if 'usb:' in line.lower():
                print(f"   {line}")
    else:
        print("❌ Kamera-Erkennung fehlgeschlagen")
        print(f"   Fehler: {err}")
        return False
    
    # Summary Test
    rc, out, err = run_command("gphoto2 --summary", timeout=15)
    if rc == 0:
        print("✅ Kamera-Zusammenfassung funktioniert")
        lines = out.split('\n')[:5]
        for line in lines:
            if line.strip():
                print(f"   {line.strip()}")
    else:
        print("❌ Kamera-Zusammenfassung fehlgeschlagen")
        if "could not claim" in err.lower():
            print("   ⚠️ Immer noch USB-Konflikt!")
            return False
        else:
            print(f"   Fehler: {err}")
    
    return True

def main():
    print("🚨 Canon DSLR USB-Konflikt Reparatur-Tool")
    print("=" * 50)
    print("Behebt 'Could not claim the USB device' Fehler")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test-only":
        # Nur Test, keine Änderungen
        test_gphoto2_access()
        return
    
    try:
        # Schritt 1: gvfs-Prozesse stoppen
        step1_success = kill_gvfs_processes()
        
        # Schritt 2: Auto-Mount deaktivieren
        disable_gvfs_auto_mount()
        
        # Schritt 3: udev-Regeln erstellen
        create_udev_rules()
        
        # Schritt 4: USB-Reset
        reset_usb_device()
        
        # Schritt 5: Test
        print("\n" + "=" * 30)
        print("🧪 FINAL TEST")
        print("=" * 30)
        
        if test_gphoto2_access():
            print("\n🎉 ERFOLG! USB-Konflikt behoben!")
            print("\n💡 Tipps für dauerhaften Fix:")
            print("• udev-Regeln installieren (siehe oben)")
            print("• Bei Problemen: Kamera aus/ein + USB neu verbinden")
            print("• Script bei Bedarf erneut ausführen")
        else:
            print("\n😞 Problem nicht vollständig behoben")
            print("\n🔧 Weitere Schritte:")
            print("1. Kamera ausschalten")
            print("2. USB-Kabel trennen") 
            print("3. 10 Sekunden warten")
            print("4. USB wieder verbinden")
            print("5. Kamera einschalten")
            print("6. python fix_usb.py erneut ausführen")
            
    except KeyboardInterrupt:
        print("\n⏹️ Abgebrochen")
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")

if __name__ == "__main__":
    main()
