import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import socket
from gpio_helper import GPIOHandler
from PIL import Image, ImageTk
from camera_handler import CameraHandler
from menu_manager import MenuManager
#from data_provider import DataProvider

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="#1e1e1e")

        # Logo laden
        image = Image.open("src/resources/img/quattrom-logo.png")  # Pfad zu deinem Logo
        image = image.resize((180, 54))  # optional verkleinern
        self.logo = ImageTk.PhotoImage(image)

        # Label mit Logo
        self.logo_label = tk.Label(self, image=self.logo, bg="#1e1e1e")
        self.logo_label.pack(pady=10)
        # Datenquelle (Platzhalter)
        #self.data_provider = DataProvider()

        # GPIO Handler (Buttons, etc.)
        self.gpio_handler = GPIOHandler(callback=self.on_gpio_event)

        # Kamera Handler
        self.camera_handler = CameraHandler(camera_mode="auto")  # Automatische Erkennung
        
        # Kamera-Display Variablen
        self.camera_display = None
        self.camera_photo = None

        # MenuManager erstellen (nach camera_handler Initialisierung)
        self.menu_manager = MenuManager(master, self)
        self.menubar = self.menu_manager.menubar


        # Aktuelle IP merken
        self.current_ip = self.get_local_ip()

        # UI-Elemente
        self.create_widgets()

        # Update Loop für Daten
        self.update_data()
        
        # Separater schneller Update für Kamera
        self.update_camera_fast()


    def create_widgets(self):
        # Überschrift
        self.label_title = ttk.Label(self, text="Photo Box UI", font=("Arial", 16))
        self.label_title.pack(pady=10)

        # Kamera-Frame (links)
        self.camera_frame = tk.Frame(self, bg="#1e1e1e")
        self.camera_frame.pack(side="left", padx=20, pady=10, fill="both", expand=True)
        
        # Kamera-Status
        camera_mode = self.camera_handler.camera_mode.upper()
        camera_status = f"Verbunden ({camera_mode})" if self.camera_handler.is_connected() else "Nicht verbunden"
        self.camera_status_label = ttk.Label(self.camera_frame, text=f"Kamera: {camera_status}", font=("Arial", 10))
        self.camera_status_label.pack(pady=5)
        
        # Kamera-Display Container für bessere Kontrolle
        self.camera_display_frame = tk.Frame(self.camera_frame, bg="#1e1e1e")
        self.camera_display_frame.pack(pady=10, expand=True, fill="both")
        
        # Kamera-Display
        self.camera_display = tk.Label(self.camera_display_frame, 
                                     text="Kamera-Vorschau\n(Live View starten)", 
                                     bg="#2d2d2d", fg="white",
                                     font=("Arial", 12))
        self.camera_display.pack(expand=True)
        
        # Kamera-Buttons Frame
        self.camera_buttons_frame = tk.Frame(self.camera_frame, bg="#1e1e1e")
        self.camera_buttons_frame.pack(pady=10)
        
        # Live View Button
        self.live_view_button = ttk.Button(self.camera_buttons_frame, 
                                         text="Live View starten",
                                         command=self.toggle_live_view)
        self.live_view_button.pack(side="left", padx=5)
        
        # Foto Button
        self.capture_button = ttk.Button(self.camera_buttons_frame,
                                       text="Foto aufnehmen",
                                       command=self.capture_photo)
        self.capture_button.pack(side="left", padx=5)

        # Rechte Seite - Kontrollen (rechts)
        self.controls_frame = tk.Frame(self, bg="#1e1e1e")
        self.controls_frame.pack(side="right", padx=20, pady=10, fill="y")

        # Drehwinkel Block
        self.angle_label = ttk.Label(self.controls_frame, text="Drehwinkel:", font=("Arial", 12))
        self.angle_label.pack(pady=5)

        self.angle_value = ttk.Label(self.controls_frame, text="---", font=("Arial", 14))
        self.angle_value.pack(pady=5)

        # Button als Beispiel
        self.quit_button = ttk.Button(self.controls_frame, text="Beenden", command=self.quit)
        self.quit_button.pack(pady=10)

        # Button zum Setzen der IP (nur einmal erstellen!)
        self.ip_button = ttk.Button(self.controls_frame, text="IP einstellen",
                                    command=self.set_ip_dialog)
        self.ip_button.pack(side="bottom", anchor="se", padx=10, pady=12)

        # Label unten rechts für IP-Adresse (nur einmal erstellen!)
        self.ip_label = tk.Label(self.controls_frame, text=f"IP: {self.current_ip}",
                                 font=("Arial", 12),
                                 fg="white", bg="#1e1e1e", anchor="se")
        self.ip_label.pack(side="bottom", anchor="se", padx=10, pady=10)


    def update_data(self):
        # Hole Daten vom Provider
        angle = 0  # self.data_provider.get_angle()
        self.angle_value.config(text=f"{angle} °")

        # IP-Label ggf. aktualisieren (aber nicht neu erzeugen!)
        self.ip_label.config(text=f"IP: {self.current_ip}")

        # Langsamere Updates alle 500ms (nur für Status-Daten)
        self.after(500, self.update_data)
        
    def update_camera_fast(self):
        """Schnelle Kamera-Updates für flüssige Darstellung"""
        # Kamera-Display aktualisieren
        self.update_camera_display()

        # Schnelle Updates alle 16ms (60 FPS)
        self.after(16, self.update_camera_fast)


    def set_ip_dialog(self):
        # Eingabedialog für IPv4
        ip = simpledialog.askstring("IPv4-Adresse eingeben",
                                    "Bitte IPv4-Adresse eingeben:",
                                    parent=self)
        if ip:
            if self.validate_ip(ip):
                self.current_ip = ip
                self.ip_label.config(text=f"IP: {self.current_ip}")
            else:
                messagebox.showerror("Fehler", "Ungültige IPv4-Adresse!")

    def validate_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def get_local_ip(self):
        """Liest die lokale IP des Geräts (z. B. eth0 oder wlan0)."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "0.0.0.0"


    def on_gpio_event(self, channel):
        print(f"GPIO Event erkannt an Pin {channel}")
        #  UI-reactions
        
    def toggle_live_view(self):
        """Startet oder stoppt Live View"""
        if not self.camera_handler.is_connected():
            messagebox.showerror("Fehler", "Keine Kamera verbunden!")
            return
            
        if not self.camera_handler.live_view_active:
            # Live-View starten
            print("Starte Live-View...")
            self.live_view_button.config(text="Live View wird gestartet...", state="disabled")
            
            # Kurze Verzögerung für UI-Update
            self.after(100, self._start_live_view_delayed)
        else:
            # Live-View stoppen
            print("Stoppe Live-View...")
            self.camera_handler.stop_live_view()
            self.live_view_button.config(text="Live View starten", state="normal")
            
            # Display zurücksetzen
            self.camera_display.config(image="", text="Kamera-Vorschau\n(Live View starten)")
            self._debug_printed = False  # Reset debug flag
    
    def _start_live_view_delayed(self):
        """Startet Live-View mit Verzögerung (für UI-Responsivität)"""
        try:
            if self.camera_handler.start_live_view():
                self.live_view_button.config(text="Live View stoppen", state="normal")
                
                # Gib Feedback je nach Kamera-Modus
                if self.camera_handler.camera_mode == "gphoto2":
                    messagebox.showinfo("Info", 
                        "Live View gestartet\n\n"
                        "Hinweis: Bei Canon DSLRs kann es 2-3 Sekunden dauern bis das erste Bild erscheint.\n"
                        "Falls kein Bild erscheint, prüfen Sie:\n"
                        "• Kamera-Modus (M/Av/Tv statt Auto)\n" 
                        "• Live-View-Einstellung an der Kamera\n"
                        "• USB-Verbindung")
                else:
                    messagebox.showinfo("Info", "Live View gestartet")
            else:
                self.live_view_button.config(text="Live View starten", state="normal")
                messagebox.showerror("Fehler", 
                    "Live View konnte nicht gestartet werden!\n\n"
                    "Mögliche Lösungen:\n"
                    "• Kamera in M/Av/Tv-Modus stellen (nicht Auto)\n"
                    "• Live-View an der Kamera aktivieren\n"
                    "• Kamera-Verbindung zurücksetzen (Studio-Kontrolle)")
        except Exception as e:
            self.live_view_button.config(text="Live View starten", state="normal")
            messagebox.showerror("Fehler", f"Live View Fehler: {str(e)}")
            print(f"Live View Fehler: {e}")
            
    def update_camera_display(self):
        """Aktualisiert das Kamera-Display mit dem aktuellen Bild"""
        if self.camera_handler.live_view_active:
            current_image = self.camera_handler.get_current_image()
            if current_image:
                try:
                    # Debug-Info
                    original_size = current_image.size
                    
                    # Bild für Display vorbereiten
                    display_image = current_image.copy()
                    
                    # Berechne die optimale Größe für das Display
                    # Maximal 640x480, aber mit korrektem Aspektverhältnis
                    max_width, max_height = 640, 480
                    img_width, img_height = display_image.size
                    
                    # Berechne Skalierungsfaktor unter Beibehaltung des Aspektverhältnisses
                    scale_w = max_width / img_width
                    scale_h = max_height / img_height
                    scale = min(scale_w, scale_h)
                    
                    # Neue Größe berechnen
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    
                    # Debug-Info nur beim ersten mal
                    if not hasattr(self, '_debug_printed'):
                        print(f"Bildgrößen - Original: {original_size}, Skaliert: {new_width}x{new_height}, Scale: {scale:.2f}")
                        self._debug_printed = True
                    
                    # Bild skalieren
                    display_image = display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # In PhotoImage umwandeln
                    self.camera_photo = ImageTk.PhotoImage(display_image)
                    self.camera_display.config(image=self.camera_photo, text="")
                    
                except Exception as e:
                    print(f"Fehler beim Aktualisieren des Kamera-Displays: {e}")
                    print(f"Originalgröße: {current_image.size if current_image else 'None'}")
                    
    def capture_photo(self):
        """Nimmt ein Foto auf"""
        if not self.camera_handler.is_connected():
            messagebox.showerror("Fehler", "Keine Kamera verbunden!")
            return
            
        try:
            filename = self.camera_handler.capture_photo()
            if filename:
                messagebox.showinfo("Erfolg", f"Foto gespeichert als: {filename}")
            else:
                messagebox.showerror("Fehler", "Foto konnte nicht aufgenommen werden!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Fotografieren: {str(e)}")
