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

    root.config(menu=app.menubar)
    
    app.pack(expand=True, fill="both")

    # Verbessertes ESC-Verhalten: Vollbild beenden statt Programm schließen
    def handle_escape(event):
        if root.attributes("-fullscreen"):
            root.attributes("-fullscreen", False)
        # TODO: In Zukunft könnte hier ein Bestätigungsdialog kommen
    
    root.bind("<Escape>", handle_escape)

    root.mainloop()


if __name__ == "__main__":
    main()
