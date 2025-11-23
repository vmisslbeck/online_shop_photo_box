import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from ui import App
from menu_manager import MenuManager

class StudioControlPanel(tk.Toplevel):
    def __init__(self, parent, camera_handler):
        super().__init__(parent)
        self.camera_handler = camera_handler
        self.title("Studio Kamera-Kontrolle")
        self.geometry("400x600")
        
        # Haupt-Container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Studio-Modus Sektion
        studio_frame = ttk.LabelFrame(main_frame, text="Studio-Modus", padding=10)
        studio_frame.pack(fill="x", pady=5)
        
        self.studio_enabled = tk.BooleanVar()
        studio_check = ttk.Checkbutton(studio_frame, text="Studio-Modus aktivieren", 
                                     variable=self.studio_enabled,
                                     command=self.toggle_studio_mode)
        studio_check.pack(anchor="w")
        
        # Lightroom-Ordner
        lightroom_frame = ttk.Frame(studio_frame)
        lightroom_frame.pack(fill="x", pady=5)
        
        ttk.Label(lightroom_frame, text="Lightroom-Ordner:").pack(anchor="w")
        
        folder_frame = ttk.Frame(lightroom_frame)
        folder_frame.pack(fill="x", pady=2)
        
        self.lightroom_path = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.lightroom_path, state="disabled")
        self.folder_entry.pack(side="left", fill="x", expand=True)
        
        self.folder_button = ttk.Button(folder_frame, text="...", width=3, 
                                      command=self.select_lightroom_folder, state="disabled")
        self.folder_button.pack(side="right", padx=(5,0))
        
        # Kamera-Einstellungen (nur bei gphoto2)
        if camera_handler.camera_mode == "gphoto2":
            self.create_camera_controls(main_frame)
        
        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Kamera-Status", padding=10)
        status_frame.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Bereit")
        self.status_label.pack()
        
        # Kamera-Modus Kontrollen (nur für gphoto2)
        if camera_handler.camera_mode == "gphoto2":
            control_frame = ttk.LabelFrame(status_frame, text="Kamera-Kontrolle", padding=5)
            control_frame.pack(fill="x", pady=5)
            
            # Buttons für Kamera-Modus
            button_frame = ttk.Frame(control_frame)
            button_frame.pack(fill="x", pady=2)
            
            self.manual_mode_button = ttk.Button(button_frame, text="Manuelle Bedienung aktivieren", 
                                               command=self.enable_manual_mode)
            self.manual_mode_button.pack(side="left", padx=2)
            
            self.reset_camera_button = ttk.Button(button_frame, text="Kamera zurücksetzen", 
                                                command=self.reset_camera)
            self.reset_camera_button.pack(side="left", padx=2)
            
            self.refresh_status_button = ttk.Button(button_frame, text="Status aktualisieren", 
                                                  command=self.refresh_status)
            self.refresh_status_button.pack(side="left", padx=2)
            
            # USB-Fix Button
            usb_frame = ttk.Frame(control_frame)
            usb_frame.pack(fill="x", pady=5)
            
            self.usb_fix_button = ttk.Button(usb_frame, text="USB-Konflikte beheben", 
                                           command=self.fix_usb_conflicts)
            self.usb_fix_button.pack(side="left", padx=2)
            
            self.external_fix_button = ttk.Button(usb_frame, text="Externes USB-Fix", 
                                                command=self.run_external_fix)
            self.external_fix_button.pack(side="left", padx=2)
        
        # Aktualisiere Status
        self.update_status()
        
        # Kontinuierliche Status-Updates
        self.start_status_updates()
    
    def create_camera_controls(self, parent):
        """Erstellt Kamera-Einstellungs-Kontrollen"""
        camera_frame = ttk.LabelFrame(parent, text="Kamera-Einstellungen", padding=10)
        camera_frame.pack(fill="both", expand=True, pady=5)
        
        # Scroll-Container für viele Einstellungen
        canvas = tk.Canvas(camera_frame, height=200)
        scrollbar = ttk.Scrollbar(camera_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Wichtige Kamera-Parameter
        self.settings_vars = {}
        settings = ['iso', 'aperture', 'shutterspeed', 'whitebalance', 'imageformat']
        
        for i, setting in enumerate(settings):
            # Label
            ttk.Label(scrollable_frame, text=f"{setting.upper()}:").grid(row=i, column=0, sticky="w", pady=2)
            
            # Combobox für Werte
            self.settings_vars[setting] = tk.StringVar()
            combo = ttk.Combobox(scrollable_frame, textvariable=self.settings_vars[setting], 
                               width=20, state="readonly")
            combo.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            combo.bind('<<ComboboxSelected>>', lambda e, s=setting: self.on_setting_changed(s))
            
            # Verfügbare Werte laden
            values = self.camera_handler.get_available_values(setting)
            combo['values'] = values
            
            # Aktuellen Wert setzen
            current = self.camera_handler.camera_settings.get(setting, '')
            if current in values:
                combo.set(current)
        
        scrollable_frame.columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh Button
        refresh_btn = ttk.Button(camera_frame, text="Einstellungen aktualisieren", 
                               command=self.refresh_camera_settings)
        refresh_btn.pack(pady=5)
    
    def toggle_studio_mode(self):
        """Aktiviert/Deaktiviert Studio-Modus"""
        enabled = self.studio_enabled.get()
        
        # Kontrollen aktivieren/deaktivieren
        state = "normal" if enabled else "disabled"
        self.folder_entry.config(state=state)
        self.folder_button.config(state=state)
        
        if enabled:
            # Studio-Modus aktivieren
            lightroom_folder = self.lightroom_path.get() if self.lightroom_path.get() else None
            self.camera_handler.enable_studio_mode(lightroom_folder)
        else:
            # Studio-Modus deaktivieren
            self.camera_handler.studio_mode = False
            self.camera_handler.auto_forward_photos = False
        
        self.update_status()
    
    def select_lightroom_folder(self):
        """Wählt Lightroom-Ordner aus"""
        folder = filedialog.askdirectory(title="Lightroom-Ordner wählen")
        if folder:
            self.lightroom_path.set(folder)
            # Studio-Modus mit neuem Ordner aktualisieren
            if self.studio_enabled.get():
                self.camera_handler.enable_studio_mode(folder)
            self.update_status()
    
    def on_setting_changed(self, setting):
        """Reagiert auf Änderung einer Kamera-Einstellung"""
        new_value = self.settings_vars[setting].get()
        if new_value:
            success = self.camera_handler.set_camera_setting(setting, new_value)
            if success:
                self.status_label.config(text=f"{setting.upper()} auf {new_value} gesetzt")
            else:
                self.status_label.config(text=f"Fehler beim Setzen von {setting.upper()}")
            
            # Status nach 3 Sekunden zurücksetzen
            self.after(3000, self.update_status)
    
    def refresh_camera_settings(self):
        """Aktualisiert Kamera-Einstellungen"""
        self.camera_handler._load_current_settings()
        
        # UI-Werte aktualisieren
        for setting, var in self.settings_vars.items():
            current = self.camera_handler.camera_settings.get(setting, '')
            if current:
                var.set(current)
        
        self.status_label.config(text="Einstellungen aktualisiert")
        self.after(2000, self.update_status)
    
    def update_status(self):
        """Aktualisiert Status-Anzeige"""
        status = self.camera_handler.get_camera_status()
        
        status_text = f"Kamera: {status['mode'].upper()}"
        if status['connected']:
            status_text += " (Verbunden)"
            if status.get('manual_control_available', False):
                status_text += " - Manuell bedienbar ✅"
            else:
                status_text += " - PC-Remote Modus ⚠️"
        else:
            status_text += " (Nicht verbunden)"
        
        if status['live_view_active']:
            status_text += "\nLive-View: Aktiv"
        
        if self.camera_handler.studio_mode:
            if self.camera_handler.auto_forward_photos:
                folder = self.camera_handler.lightroom_folder
                status_text += f"\nStudio-Modus: Aktiv → {os.path.basename(folder) if folder else 'Unbekannt'}"
            else:
                status_text += "\nStudio-Modus: Aktiv (ohne Auto-Weiterleitung)"
        else:
            status_text += "\nStudio-Modus: Inaktiv"
            
        self.status_label.config(text=status_text)
    
    def enable_manual_mode(self):
        """Aktiviert manuellen Kamera-Modus"""
        success = self.camera_handler.enable_camera_manual_mode()
        if success:
            self.status_label.config(text="Manueller Modus aktiviert - Kamera kann wieder direkt bedient werden")
        else:
            self.status_label.config(text="Fehler beim Aktivieren des manuellen Modus")
        
        # Status nach 3 Sekunden aktualisieren
        self.after(3000, self.refresh_status)
    
    def reset_camera(self):
        """Setzt Kamera-Verbindung zurück"""
        self.status_label.config(text="Setze Kamera zurück...")
        self.camera_handler.reset_camera_connection()
        self.after(2000, self.refresh_status)
    
    def refresh_status(self):
        """Aktualisiert alle Status-Informationen"""
        self.camera_handler._load_current_settings()
        self.update_status()
        
        # UI-Werte aktualisieren falls vorhanden
        if hasattr(self, 'settings_vars'):
            for setting, var in self.settings_vars.items():
                current = self.camera_handler.camera_settings.get(setting, '')
                if current:
                    var.set(current)
    
    def start_status_updates(self):
        """Startet kontinuierliche Status-Updates"""
        self.update_status()
        self.after(5000, self.start_status_updates)  # Alle 5 Sekunden
        
    def fix_usb_conflicts(self):
        """Behebt USB-Konflikte über CameraHandler"""
        self.status_label.config(text="Behebe USB-Konflikte...")
        
        try:
            success = self.camera_handler.fix_usb_conflicts()
            if success:
                self.status_label.config(text="✅ USB-Konflikte behoben - Kamera wieder verfügbar")
                messagebox.showinfo("Erfolg", "USB-Konflikte wurden behoben!\n\nDie Kamera sollte jetzt wieder funktionieren.")
            else:
                self.status_label.config(text="⚠️ USB-Konflikte konnten nicht vollständig behoben werden")
                messagebox.showwarning("Teilweise erfolgreich", 
                    "Einige USB-Konflikte wurden behoben,\naber Probleme könnten bestehen bleiben.\n\n"
                    "Versuchen Sie 'Externes USB-Fix' oder\nstarten Sie die Kamera neu.")
        except Exception as e:
            self.status_label.config(text=f"❌ Fehler beim USB-Fix: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Beheben der USB-Konflikte:\n{str(e)}")
        
        # Status nach 3 Sekunden aktualisieren
        self.after(3000, self.refresh_status)
    
    def run_external_fix(self):
        """Führt externes USB-Fix-Script aus"""
        import subprocess
        import threading
        
        def run_fix():
            try:
                self.status_label.config(text="Führe externes USB-Fix aus...")
                
                # Führe fix_usb.py aus
                result = subprocess.run([
                    "python", "src/fix_usb.py"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.after(100, lambda: self.status_label.config(text="✅ Externes USB-Fix erfolgreich"))
                    self.after(100, lambda: messagebox.showinfo("Erfolg", 
                        "Externes USB-Fix wurde erfolgreich ausgeführt!\n\n"
                        "Ausgabe:\n" + result.stdout[:300]))
                else:
                    self.after(100, lambda: self.status_label.config(text="⚠️ Externes USB-Fix mit Warnung beendet"))
                    self.after(100, lambda: messagebox.showwarning("Warnung", 
                        f"USB-Fix mit Problemen:\n\nFehler:\n{result.stderr[:300]}"))
                        
            except subprocess.TimeoutExpired:
                self.after(100, lambda: self.status_label.config(text="⏰ Externes USB-Fix Timeout"))
                self.after(100, lambda: messagebox.showerror("Timeout", 
                    "Das externe USB-Fix-Script hat zu lange gedauert.\n"
                    "Führen Sie es manuell in einem Terminal aus:\n"
                    "python src/fix_usb.py"))
            except Exception as e:
                self.after(100, lambda: self.status_label.config(text=f"❌ USB-Fix Fehler: {str(e)}"))
                self.after(100, lambda: messagebox.showerror("Fehler", f"Fehler beim externen USB-Fix:\n{str(e)}"))
            
            # Status aktualisieren
            self.after(2000, self.refresh_status)
        
        # In separatem Thread ausführen um UI nicht zu blockieren
        thread = threading.Thread(target=run_fix, daemon=True)
        thread.start()

# Erweiterte App-Klasse
class StudioApp(App):
    def __init__(self, master=None):
        super().__init__(master)
        self.studio_panel = None
        
        # Studio-spezifisches Menü erstellen (überschreibt das Standard-Menü)
        self.menu_manager = MenuManager(master, self)
        self.menubar = self.menu_manager.menubar
    
    def create_widgets(self):
        # Originale Widgets erstellen
        super().create_widgets()
        
        # Studio-Button hinzufügen
        if self.camera_handler.camera_mode == "gphoto2":
            self.studio_button = ttk.Button(self.camera_buttons_frame,
                                          text="Studio-Kontrolle",
                                          command=self.open_studio_panel)
            self.studio_button.pack(side="left", padx=5)
    
    def open_studio_panel(self):
        """Öffnet Studio-Kontrollpanel"""
        if self.studio_panel is None or not self.studio_panel.winfo_exists():
            self.studio_panel = StudioControlPanel(self.master, self.camera_handler)
        else:
            self.studio_panel.lift()  # Bringe Fenster nach vorne
