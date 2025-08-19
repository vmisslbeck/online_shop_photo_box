import os
import subprocess
import threading
import time
from PIL import Image, ImageDraw, ImageFont
import tempfile
from datetime import datetime
import platform

class CameraHandler:
    def __init__(self, dummy_mode=None):
        """
        Kamera-Handler für gphoto2 mit Dummy-Modus für Entwicklung
        
        Args:
            dummy_mode: None für automatische Erkennung, True für Dummy, False für echte Kamera
        """
        self.is_dummy = dummy_mode if dummy_mode is not None else self._should_use_dummy()
        self.camera_connected = False
        self.live_view_active = False
        self.current_image = None
        self.temp_dir = tempfile.mkdtemp()
        
        if not self.is_dummy:
            self._check_gphoto2()
            self._detect_camera()
        else:
            print("Kamera-Handler im Dummy-Modus gestartet")
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
            else:
                print("Keine Kamera erkannt")
                self.camera_connected = False
        except subprocess.TimeoutExpired:
            print("Timeout bei Kamera-Erkennung")
            self.camera_connected = False
    
    def start_live_view(self):
        """Startet Live-View der Kamera"""
        if not self.camera_connected:
            return False
        
        if self.is_dummy:
            self.live_view_active = True
            self._start_dummy_live_view()
        else:
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
                time.sleep(1/30)  # 30 FPS
        
        thread = threading.Thread(target=dummy_loop, daemon=True)
        thread.start()
    
    def _start_gphoto_live_view(self):
        """Startet echte Live-View mit gphoto2"""
        def gphoto_loop():
            while self.live_view_active:
                try:
                    # Capture preview image
                    preview_path = os.path.join(self.temp_dir, "preview.jpg")
                    result = subprocess.run([
                        'gphoto2', 
                        '--capture-preview', 
                        '--filename', preview_path
                    ], capture_output=True, timeout=5)
                    
                    if result.returncode == 0 and os.path.exists(preview_path):
                        try:
                            self.current_image = Image.open(preview_path)
                            # Größe anpassen falls nötig
                            if self.current_image.size[0] > 640:
                                self.current_image = self.current_image.resize((640, 480), Image.Resampling.LANCZOS)
                        except Exception as e:
                            print(f"Fehler beim Laden des Preview-Bildes: {e}")
                    
                except subprocess.TimeoutExpired:
                    print("Timeout bei gphoto2 preview")
                except Exception as e:
                    print(f"Fehler bei gphoto2: {e}")
                
                time.sleep(1/10)  # 10 FPS für echte Kamera
        
        thread = threading.Thread(target=gphoto_loop, daemon=True)
        thread.start()
    
    def get_current_image(self):
        """Gibt das aktuelle Kamerabild zurück"""
        return self.current_image
    
    def capture_photo(self, filename=None):
        """Macht ein Foto und speichert es"""
        if not self.camera_connected:
            return None
        
        if self.is_dummy:
            # Dummy Foto
            if self.current_image:
                dummy_path = filename or f"dummy_photo_{int(time.time())}.jpg"
                self.current_image.save(dummy_path)
                return dummy_path
        else:
            try:
                capture_path = filename or f"photo_{int(time.time())}.jpg"
                result = subprocess.run([
                    'gphoto2',
                    '--capture-image-and-download',
                    '--filename', capture_path
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    return capture_path
            except Exception as e:
                print(f"Fehler beim Fotografieren: {e}")
        
        return None
    
    def is_connected(self):
        """Prüft ob Kamera verbunden ist"""
        return self.camera_connected
    
    def __del__(self):
        """Cleanup"""
        self.stop_live_view()
        # Temp-Dateien löschen
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
