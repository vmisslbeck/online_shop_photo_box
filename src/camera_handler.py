import os
import subprocess
import threading
import time
from PIL import Image, ImageDraw, ImageFont
import tempfile
from datetime import datetime
import platform

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

class CameraHandler:
    def __init__(self, dummy_mode=None, camera_mode="auto"):
        """
        Kamera-Handler für gphoto2, Webcam und Dummy-Modus
        
        Args:
            dummy_mode: None für automatische Erkennung, True für Dummy, False für echte Kamera
            camera_mode: "auto", "gphoto2", "webcam", "dummy"
        """
        self.camera_mode = camera_mode
        self.is_dummy = dummy_mode if dummy_mode is not None else self._should_use_dummy()
        self.camera_connected = False
        self.live_view_active = False
        self.current_image = None
        self.temp_dir = tempfile.mkdtemp()
        self.webcam = None
        
        # Studio-spezifische Einstellungen
        self.studio_mode = False
        self.auto_forward_photos = False
        self.lightroom_folder = None
        self.camera_settings = {
            'iso': None,
            'aperture': None,
            'shutterspeed': None,
            'whitebalance': None,
            'imageformat': None
        }
        
        # Bestimme den tatsächlichen Kamera-Modus
        self._determine_camera_mode()
        
        if self.camera_mode == "gphoto2":
            self._check_gphoto2()
            self._detect_camera()
            self._query_camera_capabilities()
        elif self.camera_mode == "webcam":
            self._init_webcam()
        elif self.camera_mode == "dummy":
            print("Kamera-Handler im Dummy-Modus gestartet")
            self.camera_connected = True
        else:
            print(f"Unbekannter Kamera-Modus: {self.camera_mode}")
    
    def _determine_camera_mode(self):
        """Bestimmt automatisch den besten Kamera-Modus"""
        if self.camera_mode == "auto":
            # Priorität: gphoto2 > webcam > dummy
            if platform.system() != "Windows":
                try:
                    subprocess.run(['gphoto2', '--version'], 
                                 capture_output=True, text=True, timeout=5)
                    self.camera_mode = "gphoto2"
                    return
                except:
                    pass
            
            # Versuche Webcam
            if OPENCV_AVAILABLE:
                test_cap = cv2.VideoCapture(0)
                if test_cap.isOpened():
                    test_cap.release()
                    self.camera_mode = "webcam"
                    return
                test_cap.release()
            
            # Fallback: Dummy
            self.camera_mode = "dummy"
    
    def _init_webcam(self):
        """Initialisiert die Webcam"""
        if not OPENCV_AVAILABLE:
            print("OpenCV nicht verfügbar, wechsle zu Dummy-Modus")
            self.camera_mode = "dummy"
            self.camera_connected = True
            return
        
        try:
            self.webcam = cv2.VideoCapture(0)
            
            # Webcam-Auflösung und FPS setzen
            self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.webcam.set(cv2.CAP_PROP_FPS, 60)  # Versuche 60 FPS
            
            # Buffer-Größe reduzieren für weniger Latenz
            self.webcam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Tatsächliche Werte überprüfen
            actual_width = int(self.webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.webcam.get(cv2.CAP_PROP_FPS))
            print(f"Webcam: {actual_width}x{actual_height} @ {actual_fps} FPS")
            
            if self.webcam.isOpened():
                self.camera_connected = True
                print("Webcam erfolgreich initialisiert")
            else:
                print("Webcam konnte nicht geöffnet werden, wechsle zu Dummy-Modus")
                self.camera_mode = "dummy"
                self.camera_connected = True
        except Exception as e:
            print(f"Fehler bei Webcam-Initialisierung: {e}, wechsle zu Dummy-Modus")
            self.camera_mode = "dummy"
            self.camera_connected = True
    
    def _should_use_dummy(self):
        """Automatische Erkennung ob Dummy-Modus verwendet werden soll"""
        # Unter Windows oder wenn gphoto2 nicht verfügbar ist
        if platform.system() == "Windows":
            return True
        
        try:
            result = subprocess.run(['gphoto2', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode != 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return True
    
    def _check_gphoto2(self):
        """Prüft ob gphoto2 installiert ist"""
        try:
            result = subprocess.run(['gphoto2', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                raise Exception("gphoto2 nicht gefunden")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise Exception("gphoto2 ist nicht installiert")
    
    def _detect_camera(self):
        """Erkennt angeschlossene Kameras"""
        try:
            result = subprocess.run(['gphoto2', '--auto-detect'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and "usb:" in result.stdout.lower():
                self.camera_connected = True
                print("Kamera erkannt und verbunden")
                print(f"Kamera-Info:\n{result.stdout}")
                
                # Kamera-Fähigkeiten abfragen für bessere Kompatibilität
                self._check_camera_capabilities()
                
            else:
                print("Keine Kamera erkannt")
                print(f"gphoto2 output: {result.stdout}")
                self.camera_connected = False
        except subprocess.TimeoutExpired:
            print("Timeout bei Kamera-Erkennung")
            self.camera_connected = False
        except Exception as e:
            print(f"Fehler bei Kamera-Erkennung: {e}")
            self.camera_connected = False
    
    def start_live_view(self):
        """Startet Live-View der Kamera"""
        if not self.camera_connected:
            return False
        
        if self.camera_mode == "webcam":
            self.live_view_active = True
            self._start_webcam_live_view()
        elif self.camera_mode == "dummy":
            self.live_view_active = True
            self._start_dummy_live_view()
        elif self.camera_mode == "gphoto2":
            self.live_view_active = True
            self._start_gphoto_live_view()
        
        return True
    
    def stop_live_view(self):
        """Stoppt Live-View der Kamera"""
        self.live_view_active = False
    
    def _start_dummy_live_view(self):
        """Startet Dummy Live-View mit generierten Bildern"""
        def dummy_loop():
            counter = 0
            while self.live_view_active:
                # Generiere ein Dummy-Bild
                img = Image.new('RGB', (640, 480), color=(50, 50, 50))
                draw = ImageDraw.Draw(img)
                
                # Zeichne ein einfaches Interface
                draw.rectangle([50, 50, 590, 430], outline="white", width=2)
                
                # Zeitstempel
                timestamp = datetime.now().strftime("%H:%M:%S")
                draw.text((60, 60), f"DUMMY KAMERA - {timestamp}", fill="white")
                draw.text((60, 90), f"Frame: {counter}", fill="white")
                
                # Simuliere ein Kamera-Fadenkreuz
                center_x, center_y = 320, 240
                draw.line([center_x-20, center_y, center_x+20, center_y], fill="red", width=2)
                draw.line([center_x, center_y-20, center_x, center_y+20], fill="red", width=2)
                
                # Simuliere Kamera-Info
                draw.text((60, 400), "ISO: 100 | f/5.6 | 1/60s", fill="yellow")
                
                self.current_image = img
                counter += 1
                time.sleep(1/60)  # 60 FPS für Dummy
        
        thread = threading.Thread(target=dummy_loop, daemon=True)
        thread.start()
    
    def _start_webcam_live_view(self):
        """Startet Webcam Live-View"""
        def webcam_loop():
            frame_count = 0
            last_time = time.time()
            
            while self.live_view_active and self.webcam and self.webcam.isOpened():
                try:
                    ret, frame = self.webcam.read()
                    if ret:
                        # FPS-Messung für Debug
                        current_time = time.time()
                        if frame_count % 30 == 0 and frame_count > 0:
                            fps = 30 / (current_time - last_time)
                            print(f"Webcam FPS: {fps:.1f}")
                            last_time = current_time
                        
                        # Debug-Info für erste paar Frames
                        if frame_count < 3:
                            print(f"Webcam Frame {frame_count}: {frame.shape}")
                        
                        # Frame horizontal spiegeln (wie bei einer Selfie-Kamera)
                        frame = cv2.flip(frame, 1)
                        # Farbkonvertierung von BGR zu RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # PIL Image erstellen
                        self.current_image = Image.fromarray(frame_rgb)
                        
                        frame_count += 1
                    else:
                        print("Fehler beim Lesen des Webcam-Frames")
                        break
                except Exception as e:
                    print(f"Fehler in Webcam-Loop: {e}")
                    break
                
                # Keine künstliche Verzögerung - lasse die Webcam mit maximaler FPS laufen
                # time.sleep(1/30) # Entfernt!
        
        thread = threading.Thread(target=webcam_loop, daemon=True)
        thread.start()
        
        # Versuche Thread-Priorität zu erhöhen (Windows)
        try:
            import os
            if os.name == 'nt':  # Windows
                import ctypes
                ctypes.windll.kernel32.SetThreadPriority(
                    ctypes.windll.kernel32.GetCurrentThread(), 2)  # THREAD_PRIORITY_HIGHEST
        except:
            pass  # Ignoriere falls nicht verfügbar
    
    def _start_gphoto_live_view(self):
        """Startet echte Live-View mit gphoto2"""
        def gphoto_loop():
            frame_count = 0
            consecutive_errors = 0
            max_errors = 5
            
            print("Starte gphoto2 Live-View...")
            
            while self.live_view_active:
                try:
                    # Preview-Datei-Pfad
                    preview_path = os.path.join(self.temp_dir, f"preview_{frame_count % 5}.jpg")
                    
                    # Verschiedene Preview-Methoden ausprobieren
                    preview_commands = [
                        ['gphoto2', '--capture-preview', '--filename', preview_path],
                        ['gphoto2', '--capture-preview', '--filename', preview_path, '--force-overwrite'],
                        ['gphoto2', '--capture-preview']  # Default filename
                    ]
                    
                    success = False
                    for cmd in preview_commands:
                        try:
                            result = subprocess.run(cmd, capture_output=True, timeout=3)
                            
                            # Prüfe auf USB-Konflikt
                            if result.returncode != 0 and "could not claim" in result.stderr.lower():
                                print("USB-Konflikt erkannt - versuche automatische Behebung...")
                                if self.diagnose_usb_issue(result.stderr):
                                    print("USB-Konflikt behoben, versuche erneut...")
                                    result = subprocess.run(cmd, capture_output=True, timeout=3)
                            
                            if result.returncode == 0:
                                # Finde Preview-Datei
                                if '--filename' in cmd:
                                    test_path = preview_path
                                else:
                                    # gphoto2 default: preview.jpg im aktuellen Verzeichnis
                                    test_path = "preview.jpg"
                                
                                if os.path.exists(test_path):
                                    try:
                                        img = Image.open(test_path)
                                        # Größe anpassen falls sehr groß
                                        if img.size[0] > 1920:
                                            img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                                        
                                        self.current_image = img
                                        success = True
                                        consecutive_errors = 0
                                        
                                        if frame_count < 3:
                                            print(f"Live-View Frame {frame_count}: {img.size}")
                                        
                                        # Cleanup
                                        try:
                                            os.remove(test_path)
                                        except:
                                            pass
                                        
                                        break
                                        
                                    except Exception as e:
                                        print(f"Fehler beim Laden des Preview-Bildes: {e}")
                            else:
                                # Debug-Output für andere Fehler
                                if frame_count < 3 and result.stderr:
                                    print(f"Preview-Fehler: {result.stderr[:100]}")
                                        
                        except subprocess.TimeoutExpired:
                            print("Timeout bei gphoto2 preview")
                        except Exception as e:
                            print(f"Fehler bei gphoto2 Kommando {cmd}: {e}")
                    
                    if not success:
                        consecutive_errors += 1
                        print(f"Live-View Fehler #{consecutive_errors}")
                        
                        if consecutive_errors >= max_errors:
                            print("Zu viele Live-View Fehler, stoppe...")
                            break
                    
                    frame_count += 1
                    
                except Exception as e:
                    consecutive_errors += 1
                    print(f"Unerwarteter Fehler in Live-View Loop: {e}")
                    
                    if consecutive_errors >= max_errors:
                        break
                
                time.sleep(1/2)  # 2 FPS für DSLR Live-View (schont Kamera)
        
        thread = threading.Thread(target=gphoto_loop, daemon=True)
        thread.start()
    
    def get_current_image(self):
        """Gibt das aktuelle Kamerabild zurück"""
        return self.current_image
    
    def capture_photo(self, filename=None):
        """Macht ein Foto und speichert es"""
        if not self.camera_connected:
            return None
        
        if self.camera_mode == "webcam":
            return self._capture_webcam_photo(filename)
        elif self.camera_mode == "dummy":
            return self._capture_dummy_photo(filename)
        elif self.camera_mode == "gphoto2":
            return self._capture_gphoto_photo(filename)
        
        return None
    
    def _capture_webcam_photo(self, filename=None):
        """Macht ein Foto mit der Webcam"""
        if not self.webcam or not self.webcam.isOpened():
            return None
        
        try:
            ret, frame = self.webcam.read()
            if ret:
                # Frame horizontal spiegeln
                frame = cv2.flip(frame, 1)
                # Farbkonvertierung
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                
                # Dateiname generieren
                capture_path = filename or f"webcam_photo_{int(time.time())}.jpg"
                img.save(capture_path)
                return capture_path
        except Exception as e:
            print(f"Fehler beim Webcam-Foto: {e}")
        
        return None
    
    def _capture_dummy_photo(self, filename=None):
        """Dummy Foto"""
        if self.current_image:
            dummy_path = filename or f"dummy_photo_{int(time.time())}.jpg"
            self.current_image.save(dummy_path)
            return dummy_path
        return None
    
    def _capture_gphoto_photo(self, filename=None):
        """Macht ein Foto mit gphoto2"""
        try:
            capture_path = filename or f"photo_{int(time.time())}.jpg"
            
            # Erstes Versuche
            result = subprocess.run([
                'gphoto2',
                '--capture-image-and-download',
                '--filename', capture_path
            ], capture_output=True, timeout=15)
            
            # Prüfe auf USB-Konflikt
            if result.returncode != 0 and "could not claim" in result.stderr.lower():
                print("USB-Konflikt bei Foto-Aufnahme erkannt - behebe automatisch...")
                if self.diagnose_usb_issue(result.stderr):
                    print("Versuche Foto-Aufnahme erneut...")
                    # Zweiter Versuch nach USB-Fix
                    result = subprocess.run([
                        'gphoto2',
                        '--capture-image-and-download', 
                        '--filename', capture_path
                    ], capture_output=True, timeout=15)
            
            if result.returncode == 0:
                # Studio-Modus: Foto automatisch weiterleiten
                if self.studio_mode:
                    self._forward_photo_to_lightroom(capture_path)
                return capture_path
            else:
                print(f"Foto-Aufnahme fehlgeschlagen: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("Timeout bei Foto-Aufnahme")
        except Exception as e:
            print(f"Fehler beim Fotografieren: {e}")
        
        return None
    
    def _query_camera_capabilities(self):
        """Fragt verfügbare Kamera-Einstellungen ab"""
        if self.camera_mode != "gphoto2":
            return
        
        try:
            # Verfügbare Konfigurationen abfragen
            result = subprocess.run(['gphoto2', '--list-config'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("Verfügbare Kamera-Einstellungen:")
                configs = result.stdout.strip().split('\n')
                for config in configs[:10]:  # Erste 10 anzeigen
                    print(f"  - {config}")
                
                # Aktuelle Einstellungen laden
                self._load_current_settings()
                
        except Exception as e:
            print(f"Fehler beim Abfragen der Kamera-Fähigkeiten: {e}")
    
    def _load_current_settings(self):
        """Lädt aktuelle Kamera-Einstellungen"""
        settings_to_check = ['iso', 'aperture', 'shutterspeed', 'whitebalance', 'imageformat']
        
        for setting in settings_to_check:
            try:
                result = subprocess.run(['gphoto2', '--get-config', setting], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Parse gphoto2 output für aktuellen Wert
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if line.startswith('Current:'):
                            value = line.split(':', 1)[1].strip()
                            self.camera_settings[setting] = value
                            break
            except Exception as e:
                print(f"Konnte {setting} nicht abfragen: {e}")
    
    def set_camera_setting(self, setting, value):
        """Setzt eine Kamera-Einstellung via gphoto2"""
        if self.camera_mode != "gphoto2":
            print(f"Kamera-Einstellungen nur im gphoto2-Modus verfügbar")
            return False
        
        try:
            result = subprocess.run(['gphoto2', '--set-config', f'{setting}={value}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.camera_settings[setting] = value
                print(f"Einstellung {setting} auf {value} gesetzt")
                return True
            else:
                print(f"Fehler beim Setzen von {setting}: {result.stderr}")
                return False
        except Exception as e:
            print(f"Fehler beim Setzen von {setting}: {e}")
            return False
    
    def get_available_values(self, setting):
        """Gibt verfügbare Werte für eine Einstellung zurück"""
        if self.camera_mode != "gphoto2":
            return []
        
        try:
            result = subprocess.run(['gphoto2', '--get-config', setting], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                values = []
                in_choice_section = False
                
                for line in lines:
                    if line.startswith('Choice:'):
                        in_choice_section = True
                        # Parse "Choice: 0 100" -> "100"
                        parts = line.split(' ', 2)
                        if len(parts) >= 3:
                            values.append(parts[2])
                    elif in_choice_section and not line.startswith('Choice:'):
                        break
                
                return values
        except Exception as e:
            print(f"Fehler beim Abfragen verfügbarer Werte für {setting}: {e}")
        
        return []
    
    def enable_studio_mode(self, lightroom_folder=None):
        """Aktiviert Studio-Modus mit automatischer Foto-Weiterleitung"""
        self.studio_mode = True
        self.lightroom_folder = lightroom_folder
        self.auto_forward_photos = lightroom_folder is not None
        
        if self.auto_forward_photos:
            print(f"Studio-Modus aktiviert - Fotos werden an {lightroom_folder} weitergeleitet")
        else:
            print("Studio-Modus aktiviert")
    
    def _forward_photo_to_lightroom(self, photo_path):
        """Leitet Foto an Lightroom-Ordner weiter"""
        if not self.auto_forward_photos or not self.lightroom_folder:
            return
        
        try:
            import shutil
            filename = os.path.basename(photo_path)
            target_path = os.path.join(self.lightroom_folder, filename)
            
            # Kopiere Foto (nicht verschieben, für Backup)
            shutil.copy2(photo_path, target_path)
            print(f"Foto an Lightroom weitergeleitet: {filename}")
            
        except Exception as e:
            print(f"Fehler beim Weiterleiten an Lightroom: {e}")
    
    def get_camera_settings(self):
        """Gibt aktuelle Kamera-Einstellungen zurück"""
        return self.camera_settings.copy()
    
    def _check_camera_capabilities(self):
        """Prüft Kamera-Fähigkeiten und optimiert Einstellungen"""
        try:
            # Kamera-Zusammenfassung abrufen
            result = subprocess.run(['gphoto2', '--summary'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("Kamera-Zusammenfassung:")
                print(result.stdout[:500])  # Erste 500 Zeichen
                
                # Prüfe Live-View-Unterstützung
                if "liveview" in result.stdout.lower() or "preview" in result.stdout.lower():
                    print("Live-View wird unterstützt")
                    self.live_view_supported = True
                else:
                    print("Live-View-Unterstützung unbekannt, versuche trotzdem")
                    self.live_view_supported = True  # Versuche es trotzdem
            
            # Prüfe verfügbare Operationen
            result = subprocess.run(['gphoto2', '--list-operations'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                operations = result.stdout.lower()
                print(f"Verfügbare Operationen: {', '.join(operations.split()[:5])}...")
                
        except Exception as e:
            print(f"Warnung: Konnte Kamera-Fähigkeiten nicht vollständig prüfen: {e}")
            self.live_view_supported = True  # Default: versuchen
    
    def reset_camera_connection(self):
        """Setzt Kamera-Verbindung zurück (für manuelle Bedienung)"""
        try:
            print("Setze Kamera-Verbindung zurück...")
            
            # Live-View stoppen falls aktiv
            if self.live_view_active:
                self.stop_live_view()
                time.sleep(1)
            
            # Kamera "freigeben" durch exit
            result = subprocess.run(['gphoto2', '--exit'], 
                                  capture_output=True, text=True, timeout=5)
            
            time.sleep(2)  # Kurze Pause für Kamera-Reset
            
            # Erneut verbinden
            self._detect_camera()
            
            print("Kamera-Verbindung zurückgesetzt")
            
        except Exception as e:
            print(f"Fehler beim Zurücksetzen der Kamera-Verbindung: {e}")

    def enable_camera_manual_mode(self):
        """Aktiviert manuellen Kamera-Modus (deaktiviert PC-Remote)"""
        try:
            print("Aktiviere manuellen Kamera-Modus...")
            
            # Versuche Kamera in PTP-Modus zu setzen
            result = subprocess.run(['gphoto2', '--set-config', 'capture=0'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("Kamera in manuellen Modus gesetzt")
                return True
            else:
                print(f"Warnung: Konnte Kamera-Modus nicht ändern: {result.stderr}")
                
            # Alternative: Kamera-Reset
            self.reset_camera_connection()
            return True
            
        except Exception as e:
            print(f"Fehler beim Aktivieren des manuellen Modus: {e}")
            return False

    def get_camera_status(self):
        """Gibt detaillierten Kamera-Status zurück"""
        status = {
            'connected': self.camera_connected,
            'mode': self.camera_mode,
            'live_view_active': self.live_view_active,
            'studio_mode': getattr(self, 'studio_mode', False),
            'manual_control_available': False
        }
        
        if self.camera_mode == "gphoto2" and self.camera_connected:
            try:
                # Prüfe ob Kamera manuell bedienbar ist
                result = subprocess.run(['gphoto2', '--get-config', 'capture'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0 and "current: 0" in result.stdout.lower():
                    status['manual_control_available'] = True
                    
            except:
                pass
        
        return status
    
    def fix_usb_conflicts(self):
        """Behebt USB-Konflikte automatisch"""
        try:
            print("Behebe USB-Konflikte...")
            
            # Stoppe bekannte problematische Prozesse
            problematic_processes = [
                "gvfs-gphoto2-volume-monitor",
                "gvfs-mtp-volume-monitor"
            ]
            
            for process in problematic_processes:
                try:
                    # Prüfe ob Prozess läuft
                    result = subprocess.run(f"pgrep -f {process}", 
                                          capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        print(f"Stoppe {process}...")
                        
                        # Stoppe Prozess
                        subprocess.run(f"pkill -f {process}", shell=True)
                        subprocess.run(f"killall {process}", shell=True)
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"Warnung beim Stoppen von {process}: {e}")
            
            # Kurze Pause für System-Stabilisierung  
            time.sleep(2)
            
            # Teste Kamera-Zugriff erneut
            self._detect_camera()
            
            return self.camera_connected
            
        except Exception as e:
            print(f"Fehler beim Beheben der USB-Konflikte: {e}")
            return False
    
    def diagnose_usb_issue(self, error_message):
        """Diagnostiziert USB-Probleme basierend auf Fehlermeldung"""
        if "could not claim" in error_message.lower():
            print("🔍 USB-Konflikt erkannt!")
            print("Mögliche Ursachen:")
            print("• gvfs-gphoto2-volume-monitor blockiert USB")
            print("• Andere Software verwendet die Kamera")
            print("• Unzureichende USB-Berechtigungen")
            
            print("\nAutomatische Behebung wird versucht...")
            return self.fix_usb_conflicts()
        
        return False
    
    def is_connected(self):
        """Prüft ob Kamera verbunden ist"""
        return self.camera_connected
    
    def __del__(self):
        """Cleanup"""
        self.stop_live_view()
        
        # Webcam freigeben
        if self.webcam:
            self.webcam.release()
        
        # Temp-Dateien löschen
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
