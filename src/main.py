from ui import App
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Fotobox UI")

    # Vollbild aktivieren
    root.attributes("-fullscreen", True)

    app = App(root)
    app.pack(expand=True, fill="both")

    # Optional: ESC zum Beenden
    root.bind("<Escape>", lambda e: root.destroy()) # TODO program should not be termined by esc

    root.mainloop()


if __name__ == "__main__":
    main()
