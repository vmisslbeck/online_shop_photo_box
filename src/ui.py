import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import socket
from gpio_helper import GPIOHandler
from PIL import Image, ImageTk
#from data_provider import DataProvider

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="#1e1e1e")

        # Logo laden
        image = Image.open("logo.png")  # Pfad zu deinem Logo
        image = image.resize((120, 120))  # optional verkleinern
        self.logo = ImageTk.PhotoImage(image)

        # Label mit Logo
        self.logo_label = tk.Label(self, image=self.logo, bg="#1e1e1e")
        self.logo_label.pack(pady=10)
        # Datenquelle (Platzhalter)
        #self.data_provider = DataProvider()

        # GPIO Handler (Buttons, etc.)
        self.gpio_handler = GPIOHandler(callback=self.on_gpio_event)


        # Aktuelle IP merken
        self.current_ip = self.get_local_ip()

        # UI-Elemente
        self.create_widgets()

        # Update Loop für Daten
        self.update_data()


    def create_widgets(self):
        # Überschrift
        self.label_title = ttk.Label(self, text="Motor UI", font=("Arial", 16))
        self.label_title.pack(pady=10)

        # Drehwinkel Block
        self.angle_label = ttk.Label(self, text="Drehwinkel:", font=("Arial", 12))
        self.angle_label.pack(pady=5)

        self.angle_value = ttk.Label(self, text="---", font=("Arial", 14))
        self.angle_value.pack(pady=5)

        # Button als Beispiel
        self.quit_button = ttk.Button(self, text="Beenden", command=self.quit)
        self.quit_button.pack(pady=10)

    def update_data(self):
        # Hole Daten vom Provider
        angle = 0#self.data_provider.get_angle()
        self.angle_value.config(text=f"{angle} °")

        # alle 500ms neu abfragen
        self.after(500, self.update_data)

        # Button zum Setzen der IP
        self.ip_button = ttk.Button(self, text="IP einstellen",
                                    command=self.set_ip_dialog)
        self.ip_button.pack(pady=10)

        # Label unten rechts für IP-Adresse
        self.ip_label = tk.Label(self, text=f"IP: {self.current_ip}",
                                 font=("Arial", 10),
                                 fg="white", bg="#1e1e1e", anchor="se")
        self.ip_label.pack(side="bottom", anchor="se", padx=10, pady=10)

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
        # hier könntest du direkt UI-Reaktionen einbauen
