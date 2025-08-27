from ui import App
from studio_ui import StudioApp
import tkinter as tk
import sys

def main():
    root = tk.Tk()
    root.title("Fotobox UI")
    
    # Mindestgröße setzen
    root.minsize(1000, 700)
    
    # Vollbild aktivieren
    root.attributes("-fullscreen", True)

    # Verwende Studio-App wenn --studio Parameter gegeben
    if "--studio" in sys.argv:
        app = StudioApp(root)
        print("Studio-Modus aktiviert")
    else:
        app = App(root)
    
    app.pack(expand=True, fill="both")

    # Optional: ESC zum Beenden
    root.bind("<Escape>", lambda e: root.destroy()) # TODO program should not be termined by esc

    root.mainloop()


if __name__ == "__main__":
    main()
