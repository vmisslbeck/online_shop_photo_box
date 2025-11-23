"""
MenuManager - Zentrale Verwaltung für alle Menüs der Fotobox-Anwendung
"""
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import webbrowser
import os
import sys

class MenuManager:
    def __init__(self, master, app_instance):
        self.master = master
        self.app = app_instance
        self.menubar = None
        self.is_studio_mode = hasattr(app_instance, 'studio_panel')
        
        # Menü erstellen
        self.create_menubar()
        
        # Tastaturkürzel binden
        self.bind_shortcuts()
    
    def create_menubar(self):
        """Erstellt die komplette Menüleiste"""
        self.menubar = tk.Menu(self.master)
        
        # Datei-Menü
        self.create_file_menu()
        
        # Bearbeiten-Menü
        self.create_edit_menu()
        
        # Ansicht-Menü
        self.create_view_menu()
        
        # Kamera-Menü
        self.create_camera_menu()
        
        # Studio-Menü (nur im Studio-Modus)
        if self.is_studio_mode:
            self.create_studio_menu()
        
        # Tools-Menü
        self.create_tools_menu()
        
        # Hilfe-Menü
        self.create_help_menu()
        
        return self.menubar
    
    def create_file_menu(self):
        """Datei-Menü erstellen"""
        file_menu = tk.Menu(self.menubar, tearoff=0)
        
        # Grundlegende Datei-Operationen
        file_menu.add_command(label="Neues Projekt...", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Projekt öffnen...", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_separator()
        
        file_menu.add_command(label="Foto speichern...", command=self.save_photo, accelerator="Ctrl+S")
        file_menu.add_command(label="Alle Fotos exportieren...", command=self.export_all_photos)
        file_menu.add_separator()
        
        # Einstellungen
        file_menu.add_command(label="Einstellungen...", command=self.open_settings, accelerator="Ctrl+,")
        file_menu.add_separator()
        
        # Beenden
        file_menu.add_command(label="Minimieren", command=self.minimize_app, accelerator="Ctrl+M")
        file_menu.add_command(label="Beenden", command=self.quit_app, accelerator="Ctrl+Q")
        
        self.menubar.add_cascade(label="Datei", menu=file_menu)
    
    def create_edit_menu(self):
        """Bearbeiten-Menü erstellen"""
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        
        edit_menu.add_command(label="Rückgängig", command=self.undo_action, accelerator="Ctrl+Z", state="disabled")
        edit_menu.add_command(label="Wiederholen", command=self.redo_action, accelerator="Ctrl+Y", state="disabled")
        edit_menu.add_separator()
        
        edit_menu.add_command(label="Kopieren", command=self.copy_action, accelerator="Ctrl+C", state="disabled")
        edit_menu.add_command(label="Einfügen", command=self.paste_action, accelerator="Ctrl+V", state="disabled")
        edit_menu.add_separator()
        
        edit_menu.add_command(label="Alle auswählen", command=self.select_all, accelerator="Ctrl+A", state="disabled")
        
        self.menubar.add_cascade(label="Bearbeiten", menu=edit_menu)
    
    def create_view_menu(self):
        """Ansicht-Menü erstellen"""
        view_menu = tk.Menu(self.menubar, tearoff=0)
        
        # Vollbild
        view_menu.add_command(label="Vollbild umschalten", command=self.toggle_fullscreen, accelerator="F11")
        view_menu.add_separator()
        
        # Live View
        view_menu.add_command(label="Live View umschalten", command=self.toggle_live_view, accelerator="F5")
        view_menu.add_separator()
        
        # Zoom
        zoom_menu = tk.Menu(view_menu, tearoff=0)
        zoom_menu.add_command(label="Vergrößern", command=self.zoom_in, accelerator="Ctrl++")
        zoom_menu.add_command(label="Verkleinern", command=self.zoom_out, accelerator="Ctrl+-")
        zoom_menu.add_command(label="Originalgröße", command=self.zoom_reset, accelerator="Ctrl+0")
        zoom_menu.add_command(label="An Fenster anpassen", command=self.zoom_fit, accelerator="Ctrl+F")
        view_menu.add_cascade(label="Zoom", menu=zoom_menu)
        
        view_menu.add_separator()
        
        # Interface-Elemente
        view_menu.add_command(label="Kamera-Steuerung anzeigen", command=self.toggle_camera_controls)
        view_menu.add_command(label="Statusleiste anzeigen", command=self.toggle_status_bar)
        
        self.menubar.add_cascade(label="Ansicht", menu=view_menu)
    
    def create_camera_menu(self):
        """Kamera-Menü erstellen"""
        camera_menu = tk.Menu(self.menubar, tearoff=0)
        
        # Foto-Aufnahme
        camera_menu.add_command(label="Foto aufnehmen", command=self.capture_photo, accelerator="Space")
        camera_menu.add_command(label="Serie aufnehmen...", command=self.capture_series, accelerator="Ctrl+Space")
        camera_menu.add_separator()
        
        # Live View
        camera_menu.add_command(label="Live View starten/stoppen", command=self.toggle_live_view, accelerator="F5")
        camera_menu.add_separator()
        
        # Kamera-Verbindung
        camera_menu.add_command(label="Kamera neu verbinden", command=self.reconnect_camera, accelerator="F12")
        camera_menu.add_command(label="Kamera-Status prüfen", command=self.check_camera_status)
        camera_menu.add_separator()
        
        # Schnelleinstellungen
        if hasattr(self.app.camera_handler, 'camera_mode') and self.app.camera_handler.camera_mode == "gphoto2":
            settings_menu = tk.Menu(camera_menu, tearoff=0)
            settings_menu.add_command(label="ISO einstellen...", command=lambda: self.quick_setting_dialog('iso'))
            settings_menu.add_command(label="Blende einstellen...", command=lambda: self.quick_setting_dialog('aperture'))
            settings_menu.add_command(label="Verschlusszeit einstellen...", command=lambda: self.quick_setting_dialog('shutterspeed'))
            settings_menu.add_command(label="Weißabgleich einstellen...", command=lambda: self.quick_setting_dialog('whitebalance'))
            camera_menu.add_cascade(label="Schnelleinstellungen", menu=settings_menu)
        
        self.menubar.add_cascade(label="Kamera", menu=camera_menu)
    
    def create_studio_menu(self):
        """Studio-Menü erstellen (nur im Studio-Modus)"""
        studio_menu = tk.Menu(self.menubar, tearoff=0)
        
        studio_menu.add_command(label="Studio-Kontrolle öffnen", command=self.open_studio_control, accelerator="Ctrl+K")
        studio_menu.add_separator()
        
        studio_menu.add_command(label="Lightroom-Integration...", command=self.setup_lightroom)
        studio_menu.add_command(label="Auto-Export aktivieren", command=self.toggle_auto_export)
        studio_menu.add_separator()
        
        studio_menu.add_command(label="Kamera zurücksetzen", command=self.reset_camera)
        studio_menu.add_command(label="USB-Konflikte beheben", command=self.fix_usb_conflicts)
        
        self.menubar.add_cascade(label="Studio", menu=studio_menu)
    
    def create_tools_menu(self):
        """Tools-Menü erstellen"""
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        
        tools_menu.add_command(label="Foto-Galerie...", command=self.open_photo_gallery, accelerator="Ctrl+G")
        tools_menu.add_command(label="Batch-Verarbeitung...", command=self.open_batch_processor)
        tools_menu.add_separator()
        
        tools_menu.add_command(label="System-Diagnose", command=self.run_system_diagnosis)
        tools_menu.add_command(label="Log-Dateien anzeigen", command=self.show_log_files)
        tools_menu.add_separator()
        
        tools_menu.add_command(label="IP-Adresse einstellen...", command=self.set_ip_address, accelerator="Ctrl+I")
        tools_menu.add_command(label="Netzwerk-Test", command=self.network_test)
        
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
    
    def create_help_menu(self):
        """Hilfe-Menü erstellen"""
        help_menu = tk.Menu(self.menubar, tearoff=0)
        
        help_menu.add_command(label="Benutzerhandbuch", command=self.open_user_manual, accelerator="F1")
        help_menu.add_command(label="Kamera-Setup-Anleitung", command=self.open_camera_setup_guide)
        help_menu.add_command(label="Studio-Setup-Anleitung", command=self.open_studio_setup_guide)
        help_menu.add_separator()
        
        help_menu.add_command(label="USB-Fix-Anleitung", command=self.open_usb_fix_guide)
        help_menu.add_command(label="Fehlerbehebung", command=self.open_troubleshooting)
        help_menu.add_separator()
        
        help_menu.add_command(label="Tastaturkürzel", command=self.show_keyboard_shortcuts, accelerator="Ctrl+?")
        help_menu.add_command(label="System-Info", command=self.show_system_info)
        help_menu.add_separator()
        
        help_menu.add_command(label="Über Photo Box", command=self.show_about_dialog)
        
        self.menubar.add_cascade(label="Hilfe", menu=help_menu)
    
    def bind_shortcuts(self):
        """Bindet Tastaturkürzel"""
        shortcuts = {
            '<Control-n>': self.new_project,
            '<Control-o>': self.open_project,
            '<Control-s>': self.save_photo,
            '<Control-comma>': self.open_settings,
            '<Control-m>': self.minimize_app,
            '<Control-q>': self.quit_app,
            '<F11>': self.toggle_fullscreen,
            '<F5>': self.toggle_live_view,
            '<space>': self.capture_photo,
            '<Control-space>': self.capture_series,
            '<F12>': self.reconnect_camera,
            '<Control-k>': self.open_studio_control if self.is_studio_mode else None,
            '<Control-g>': self.open_photo_gallery,
            '<Control-i>': self.set_ip_address,
            '<F1>': self.open_user_manual,
            '<Control-question>': self.show_keyboard_shortcuts,
            '<Control-plus>': self.zoom_in,
            '<Control-minus>': self.zoom_out,
            '<Control-0>': self.zoom_reset,
            '<Control-f>': self.zoom_fit
        }
        
        for key, command in shortcuts.items():
            if command:  # Nur binden wenn Funktion existiert
                self.master.bind(key, lambda e, cmd=command: cmd())
    
    # Datei-Menü Funktionen
    def new_project(self):
        """Neues Projekt erstellen"""
        # TODO: Implementiere Projekt-Management
        messagebox.showinfo("Neues Projekt", "Projekt-Management wird in einer zukünftigen Version verfügbar sein.")
    
    def open_project(self):
        """Projekt öffnen"""
        # TODO: Implementiere Projekt-Management
        messagebox.showinfo("Projekt öffnen", "Projekt-Management wird in einer zukünftigen Version verfügbar sein.")
    
    def save_photo(self):
        """Aktuelles Foto speichern"""
        if hasattr(self.app, 'capture_photo'):
            self.app.capture_photo()
        else:
            messagebox.showwarning("Foto speichern", "Keine Kamera verbunden!")
    
    def export_all_photos(self):
        """Alle Fotos exportieren"""
        folder = filedialog.askdirectory(title="Export-Ordner wählen")
        if folder:
            # TODO: Implementiere Batch-Export
            messagebox.showinfo("Export", f"Fotos werden nach {folder} exportiert...\n(Funktion in Entwicklung)")
    
    def open_settings(self):
        """Einstellungen öffnen"""
        # TODO: Implementiere Einstellungsdialog
        messagebox.showinfo("Einstellungen", "Einstellungsdialog wird in einer zukünftigen Version verfügbar sein.")
    
    def minimize_app(self):
        """Anwendung minimieren"""
        self.master.iconify()
    
    def quit_app(self):
        """Anwendung beenden"""
        if messagebox.askyesno("Beenden", "Möchten Sie die Anwendung wirklich beenden?"):
            self.master.quit()
    
    # Ansicht-Menü Funktionen
    def toggle_fullscreen(self):
        """Vollbild umschalten"""
        current_state = self.master.attributes("-fullscreen")
        self.master.attributes("-fullscreen", not current_state)
    
    def toggle_live_view(self):
        """Live View umschalten"""
        if hasattr(self.app, 'toggle_live_view'):
            self.app.toggle_live_view()
        else:
            messagebox.showwarning("Live View", "Live View nicht verfügbar!")
    
    def zoom_in(self):
        """Vergrößern"""
        # TODO: Implementiere Zoom-Funktionalität
        messagebox.showinfo("Zoom", "Zoom-Funktionalität wird implementiert...")
    
    def zoom_out(self):
        """Verkleinern"""
        # TODO: Implementiere Zoom-Funktionalität
        messagebox.showinfo("Zoom", "Zoom-Funktionalität wird implementiert...")
    
    def zoom_reset(self):
        """Zoom zurücksetzen"""
        # TODO: Implementiere Zoom-Funktionalität
        messagebox.showinfo("Zoom", "Zoom-Funktionalität wird implementiert...")
    
    def zoom_fit(self):
        """An Fenster anpassen"""
        # TODO: Implementiere Zoom-Funktionalität
        messagebox.showinfo("Zoom", "Zoom-Funktionalität wird implementiert...")
    
    def toggle_camera_controls(self):
        """Kamera-Steuerung anzeigen/verstecken"""
        # TODO: Implementiere UI-Element Toggle
        messagebox.showinfo("UI", "UI-Toggle wird implementiert...")
    
    def toggle_status_bar(self):
        """Statusleiste anzeigen/verstecken"""
        # TODO: Implementiere Statusleiste Toggle
        messagebox.showinfo("UI", "Statusleiste-Toggle wird implementiert...")
    
    # Kamera-Menü Funktionen
    def capture_photo(self):
        """Foto aufnehmen"""
        if hasattr(self.app, 'capture_photo'):
            self.app.capture_photo()
        else:
            messagebox.showwarning("Foto", "Keine Kamera verbunden!")
    
    def capture_series(self):
        """Foto-Serie aufnehmen"""
        count = simpledialog.askinteger("Foto-Serie", "Anzahl der Fotos:", initialvalue=5, minvalue=1, maxvalue=100)
        if count:
            # TODO: Implementiere Serie-Aufnahme
            messagebox.showinfo("Foto-Serie", f"Serie von {count} Fotos wird aufgenommen...\n(Funktion in Entwicklung)")
    
    def reconnect_camera(self):
        """Kamera neu verbinden"""
        if hasattr(self.app.camera_handler, 'reset_camera_connection'):
            self.app.camera_handler.reset_camera_connection()
            messagebox.showinfo("Kamera", "Kamera-Verbindung wird zurückgesetzt...")
        else:
            messagebox.showwarning("Kamera", "Kamera-Reset nicht verfügbar!")
    
    def check_camera_status(self):
        """Kamera-Status prüfen"""
        if hasattr(self.app.camera_handler, 'get_camera_status'):
            status = self.app.camera_handler.get_camera_status()
            status_text = f"Kamera-Modus: {status['mode'].upper()}\n"
            status_text += f"Verbunden: {'Ja' if status['connected'] else 'Nein'}\n"
            status_text += f"Live View: {'Aktiv' if status['live_view_active'] else 'Inaktiv'}"
            messagebox.showinfo("Kamera-Status", status_text)
        else:
            messagebox.showwarning("Kamera", "Kamera-Status nicht verfügbar!")
    
    def quick_setting_dialog(self, setting):
        """Schnelleinstellung-Dialog"""
        if hasattr(self.app.camera_handler, 'get_available_values'):
            values = self.app.camera_handler.get_available_values(setting)
            if values:
                # TODO: Implementiere Auswahl-Dialog
                messagebox.showinfo("Einstellung", f"Verfügbare {setting.upper()}-Werte:\n" + "\n".join(values[:10]))
            else:
                messagebox.showwarning("Einstellung", f"Keine {setting.upper()}-Werte verfügbar!")
        else:
            messagebox.showwarning("Einstellung", "Kamera-Einstellungen nicht verfügbar!")
    
    # Studio-Menü Funktionen (nur im Studio-Modus)
    def open_studio_control(self):
        """Studio-Kontrolle öffnen"""
        if hasattr(self.app, 'open_studio_panel'):
            self.app.open_studio_panel()
        else:
            messagebox.showwarning("Studio", "Studio-Kontrolle nicht verfügbar!")
    
    def setup_lightroom(self):
        """Lightroom-Integration einrichten"""
        folder = filedialog.askdirectory(title="Lightroom-Ordner wählen")
        if folder:
            # TODO: Lightroom-Integration konfigurieren
            messagebox.showinfo("Lightroom", f"Lightroom-Ordner gesetzt: {folder}")
    
    def toggle_auto_export(self):
        """Auto-Export umschalten"""
        # TODO: Implementiere Auto-Export Toggle
        messagebox.showinfo("Auto-Export", "Auto-Export-Funktion wird implementiert...")
    
    def reset_camera(self):
        """Kamera zurücksetzen"""
        if hasattr(self.app.camera_handler, 'reset_camera_connection'):
            self.app.camera_handler.reset_camera_connection()
            messagebox.showinfo("Kamera", "Kamera wird zurückgesetzt...")
        else:
            messagebox.showwarning("Kamera", "Kamera-Reset nicht verfügbar!")
    
    def fix_usb_conflicts(self):
        """USB-Konflikte beheben"""
        if hasattr(self.app.camera_handler, 'fix_usb_conflicts'):
            success = self.app.camera_handler.fix_usb_conflicts()
            if success:
                messagebox.showinfo("USB-Fix", "USB-Konflikte wurden behoben!")
            else:
                messagebox.showwarning("USB-Fix", "USB-Konflikte konnten nicht vollständig behoben werden.")
        else:
            messagebox.showwarning("USB-Fix", "USB-Fix nicht verfügbar!")
    
    # Tools-Menü Funktionen
    def open_photo_gallery(self):
        """Foto-Galerie öffnen"""
        # TODO: Implementiere Foto-Galerie
        messagebox.showinfo("Galerie", "Foto-Galerie wird in einer zukünftigen Version verfügbar sein.")
    
    def open_batch_processor(self):
        """Batch-Verarbeitung öffnen"""
        # TODO: Implementiere Batch-Verarbeitung
        messagebox.showinfo("Batch", "Batch-Verarbeitung wird in einer zukünftigen Version verfügbar sein.")
    
    def run_system_diagnosis(self):
        """System-Diagnose ausführen"""
        try:
            # Versuche Diagnose-Modul zu verwenden
            import diagnose
            # TODO: Führe Diagnose aus
            messagebox.showinfo("Diagnose", "System-Diagnose wird ausgeführt...")
        except ImportError:
            messagebox.showwarning("Diagnose", "Diagnose-Modul nicht verfügbar!")
    
    def show_log_files(self):
        """Log-Dateien anzeigen"""
        # TODO: Implementiere Log-Viewer
        messagebox.showinfo("Logs", "Log-Viewer wird in einer zukünftigen Version verfügbar sein.")
    
    def set_ip_address(self):
        """IP-Adresse einstellen"""
        if hasattr(self.app, 'set_ip_dialog'):
            self.app.set_ip_dialog()
        else:
            # Fallback
            ip = simpledialog.askstring("IP-Adresse", "Neue IP-Adresse eingeben:")
            if ip:
                messagebox.showinfo("IP", f"IP-Adresse gesetzt: {ip}")
    
    def network_test(self):
        """Netzwerk-Test durchführen"""
        # TODO: Implementiere Netzwerk-Test
        messagebox.showinfo("Netzwerk", "Netzwerk-Test wird durchgeführt...")
    
    # Hilfe-Menü Funktionen
    def open_user_manual(self):
        """Benutzerhandbuch öffnen"""
        # Versuche README zu öffnen
        readme_path = "README.md"
        if os.path.exists(readme_path):
            try:
                os.startfile(readme_path)  # Windows
            except:
                try:
                    os.system(f"xdg-open {readme_path}")  # Linux
                except:
                    messagebox.showinfo("Handbuch", f"Benutzerhandbuch: {readme_path}")
        else:
            messagebox.showinfo("Handbuch", "Benutzerhandbuch wird in einer zukünftigen Version verfügbar sein.")
    
    def open_camera_setup_guide(self):
        """Kamera-Setup-Anleitung öffnen"""
        guide_path = "docs/camera_setup_analysis.md"
        if os.path.exists(guide_path):
            try:
                os.startfile(guide_path)
            except:
                messagebox.showinfo("Anleitung", f"Kamera-Setup-Anleitung: {guide_path}")
        else:
            messagebox.showinfo("Anleitung", "Kamera-Setup-Anleitung wird erstellt...")
    
    def open_studio_setup_guide(self):
        """Studio-Setup-Anleitung öffnen"""
        guide_path = "docs/studio_setup_guide.md"
        if os.path.exists(guide_path):
            try:
                os.startfile(guide_path)
            except:
                messagebox.showinfo("Anleitung", f"Studio-Setup-Anleitung: {guide_path}")
        else:
            messagebox.showinfo("Anleitung", "Studio-Setup-Anleitung wird erstellt...")
    
    def open_usb_fix_guide(self):
        """USB-Fix-Anleitung öffnen"""
        guide_path = "docs/USB_FIX_GUIDE.md"
        if os.path.exists(guide_path):
            try:
                os.startfile(guide_path)
            except:
                messagebox.showinfo("Anleitung", f"USB-Fix-Anleitung: {guide_path}")
        else:
            messagebox.showinfo("Anleitung", "USB-Fix-Anleitung wird erstellt...")
    
    def open_troubleshooting(self):
        """Fehlerbehebung öffnen"""
        # TODO: Erstelle Troubleshooting-Guide
        messagebox.showinfo("Fehlerbehebung", "Fehlerbehebungs-Guide wird in einer zukünftigen Version verfügbar sein.")
    
    def show_keyboard_shortcuts(self):
        """Tastaturkürzel anzeigen"""
        shortcuts_text = """
Tastaturkürzel der Photo Box:

Datei:
  Ctrl+N    - Neues Projekt
  Ctrl+O    - Projekt öffnen
  Ctrl+S    - Foto speichern
  Ctrl+,    - Einstellungen
  Ctrl+Q    - Beenden

Ansicht:
  F11       - Vollbild umschalten
  F5        - Live View umschalten
  Ctrl++    - Vergrößern
  Ctrl+-    - Verkleinern
  Ctrl+0    - Originalgröße

Kamera:
  Space     - Foto aufnehmen
  Ctrl+Space - Serie aufnehmen
  F12       - Kamera neu verbinden

Studio:
  Ctrl+K    - Studio-Kontrolle

Tools:
  Ctrl+G    - Foto-Galerie
  Ctrl+I    - IP-Adresse einstellen

Hilfe:
  F1        - Benutzerhandbuch
  Ctrl+?    - Diese Übersicht
        """
        messagebox.showinfo("Tastaturkürzel", shortcuts_text)
    
    def show_system_info(self):
        """System-Info anzeigen"""
        import platform
        import sys
        
        info_text = f"""
System-Informationen:

Betriebssystem: {platform.system()} {platform.release()}
Architektur: {platform.machine()}
Python-Version: {sys.version.split()[0]}
Tkinter-Version: {tk.TkVersion}

Kamera-Modus: {getattr(self.app.camera_handler, 'camera_mode', 'Unbekannt').upper()}
Studio-Modus: {'Aktiviert' if self.is_studio_mode else 'Deaktiviert'}
        """
        messagebox.showinfo("System-Info", info_text)
    
    def show_about_dialog(self):
        """Über-Dialog anzeigen"""
        about_text = """
🏢 Quattrom Suite - Photo Box

📸 Professionelle Fotobox-Software für Studio und Event

✨ Features:
• Live View für DSLR-Kameras
• Studio-Integration mit Lightroom
• Automatische Foto-Verarbeitung
• GPIO-Hardware-Integration
• USB-Konflikt-Behebung

🔧 Entwickelt für professionelle Fotografie-Workflows

© 2025 Quattrom Suite
Version 1.0
        """
        messagebox.showinfo("Über Photo Box", about_text)

    # Edit-Menü Placeholder-Funktionen
    def undo_action(self):
        messagebox.showinfo("Rückgängig", "Rückgängig-Funktion wird implementiert...")
    
    def redo_action(self):
        messagebox.showinfo("Wiederholen", "Wiederholen-Funktion wird implementiert...")
    
    def copy_action(self):
        messagebox.showinfo("Kopieren", "Kopieren-Funktion wird implementiert...")
    
    def paste_action(self):
        messagebox.showinfo("Einfügen", "Einfügen-Funktion wird implementiert...")
    
    def select_all(self):
        messagebox.showinfo("Alles auswählen", "Auswahl-Funktion wird implementiert...")