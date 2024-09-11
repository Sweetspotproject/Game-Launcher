import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import json
import os
import subprocess

class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("My Game Launcher")
        self.root.geometry("854x480")

        # Colores
        self.bg_color = "#000000"  # Fondo negro
        self.fg_color = "#FFFFFF"  # Texto blanco

        # Configuración de la ventana principal
        self.root.configure(bg=self.bg_color)

        # Lista de juegos
        self.games = []

        self.load_games()

        # Interfaz de usuario
        self.create_ui()

    def create_ui(self):
        # Botón para agregar un juego nuevo
        add_button = tk.Button(
            self.root, text="Agregar nuevo juego", command=self.add_game,
            bg=self.bg_color, fg=self.fg_color
        )
        add_button.pack(pady=10)

        # Marco donde se mostrarán los juegos
        self.game_frame = tk.Frame(self.root, bg=self.bg_color)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        # Mostrar los juegos cargados
        self.display_games()

    def display_games(self):
        # Limpiar widgets antiguos antes de agregar nuevos
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        columns = 3  # Definir número de columnas
        row = 0
        col = 0

        for game in self.games:
            # Crear el marco del juego con un tamaño fijo
            game_frame = tk.Frame(self.game_frame, bd=2, relief=tk.RIDGE, bg=self.bg_color, width=200, height=300)
            game_frame.grid(row=row, column=col, padx=10, pady=10)

            # Desactivar la propagación para mantener el tamaño fijo
            game_frame.grid_propagate(False)

            # Mostrar la carátula del juego
            img = Image.open(game["cover"])
            img = img.resize((180, 180), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            cover_label = tk.Label(game_frame, image=img, bg=self.bg_color)
            cover_label.image = img  # Mantener referencia
            cover_label.pack(pady=5)

            # Información del juego
            info_frame = tk.Frame(game_frame, bg=self.bg_color)
            info_frame.pack(pady=5)

            name_label = tk.Label(info_frame, text=game["name"], font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.fg_color, wraplength=180)
            name_label.pack()

            # Botones
            button_frame = tk.Frame(game_frame, bg=self.bg_color)
            button_frame.pack(pady=5)

            play_button = tk.Button(button_frame, text="Jugar", command=lambda g=game: self.play_game(g), bg=self.bg_color, fg=self.fg_color)
            play_button.pack(side=tk.LEFT, padx=5)

            delete_button = tk.Button(button_frame, text="Eliminar", command=lambda g=game: self.delete_game(g), bg=self.bg_color, fg="red")
            delete_button.pack(side=tk.LEFT, padx=5)

            # Ajustar la cuadrícula
            col += 1
            if col == columns:
                col = 0
                row += 1

    def add_game(self):
        name = simpledialog.askstring(
            "Nombre del juego", "Introduce el nombre del juego: "
        )
        if not name:
            return

        # Seleccionar archivo ejecutable
        exe_path = filedialog.askopenfilename(
            title="Seleccionar el ejecutable del juego: ",
            filetypes=[("Archivos ejecutables", "*.exe *.msi")],
        )

        if not exe_path:
            return

        # Seleccionar carátula del juego
        cover_path = filedialog.askopenfilename(
            title="Selecciona la carátula del juego",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")],
        )

        if not cover_path:
            return

        game = {"name": name, "path": exe_path, "cover": cover_path}
        self.games.append(game)

        # Guardar en el archivo JSON
        self.save_games()

        # Actualizar la interfaz
        self.display_games()

    def play_game(self, game):
        try:
            # Ejecutar el juego con wine y gamemoderun
            subprocess.Popen(["gamemoderun", "wine", game["path"]])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar el juego: {str(e)}")

    def delete_game(self, game):
        # Confirmar antes de eliminar
        confirm = messagebox.askyesno("Eliminar juego", f"¿Estás seguro de eliminar '{game['name']}' de la biblioteca?")
        if confirm:
            self.games.remove(game)
            self.save_games()
            self.display_games()  # Actualizar la interfaz

    def save_games(self):
        with open("games.json", "w") as f:
            json.dump(self.games, f, indent=4)

    def load_games(self):
        if os.path.exists("games.json"):
            with open("games.json", "r") as f:
                self.games = json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()
