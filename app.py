import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog, Menu
from PIL import Image, ImageTk
import json
import os
import subprocess

# Constantes para colores y configuración
BG_COLOR = "#1E1E1E"  # Fondo oscuro
FG_COLOR = "#FFFFFF"  # Texto blanco
BORDER_COLOR = "#3A3A3A"  # Color del borde
COLUMN_COUNT = 4  # Número de columnas para los juegos
IMAGE_SIZE = (200, 200)  # Tamaño de la carátula del juego (cuadrado)
BORDER_THICKNESS = 5  # Grosor del borde
GAP = 10  # Espacio entre los cuadros de juegos
MENU_BUTTON_SIZE = 20  # Tamaño del botón de menú


class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("My Game Launcher")
        self.root.geometry("950x650")
        self.root.maxsize(1024, 680)
        self.root.configure(fg_color=BG_COLOR)
        self.games = []
        self.image_references = {}
        self.current_menu = None
        self.current_menu_button = None

        # Directorio de instalación
        self.install_dir = os.path.dirname(os.path.abspath(__file__))

        self.load_games()
        self.create_ui()
        self.root.resizable(False, False)

        # Manejar clics fuera del menú
        self.root.bind("<Button-1>", self.close_menu)

    def create_ui(self):
        ctk.CTkButton(
            self.root,
            text="Agregar nuevo juego",
            command=self.add_game,
            fg_color=BG_COLOR,
            text_color=FG_COLOR,
            border_width=2,
            corner_radius=10,
        ).pack(pady=10)

        # Frame para el canvas de desplazamiento
        self.canvas_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR)
        self.canvas_frame.pack(fill=ctk.BOTH, expand=True, padx=GAP, pady=GAP)

        # Canvas y scrollbar
        self.canvas = ctk.CTkCanvas(
            self.canvas_frame, bg=BG_COLOR, highlightthickness=0
        )
        self.scrollbar = ctk.CTkScrollbar(
            self.canvas_frame, orientation="vertical", command=self.canvas.yview
        )

        self.scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        # Frame para los juegos dentro del canvas
        self.game_frame = ctk.CTkFrame(self.canvas, fg_color=BG_COLOR)
        self.canvas.create_window((0, 0), window=self.game_frame, anchor="nw")

        # Configurar el tamaño del canvas y la región de desplazamiento
        self.game_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        # Manejar el desplazamiento del mouse
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.display_games()

    def on_frame_configure(self, event):
        # Actualizar el tamaño del canvas para que se ajuste al contenido
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        # Manejar el desplazamiento del mouse
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def display_games(self):
        self.clear_frame(self.game_frame)
        for index, game in enumerate(self.games):
            game_frame = self.create_game_frame(game)
            row, col = divmod(index, COLUMN_COUNT)
            game_frame.grid(row=row, column=col, padx=GAP, pady=GAP)

        self.on_frame_configure(None)

    def create_game_frame(self, game):
        border_frame = ctk.CTkFrame(
            self.game_frame,
            fg_color=BORDER_COLOR,
            width=IMAGE_SIZE[0] + BORDER_THICKNESS * 2,
            height=IMAGE_SIZE[1] + BORDER_THICKNESS * 2,
            corner_radius=15,
        )
        border_frame.grid_propagate(False)

        game_frame = ctk.CTkFrame(
            border_frame,
            fg_color=BG_COLOR,
            width=IMAGE_SIZE[0],
            height=IMAGE_SIZE[1],
            corner_radius=15,
        )
        game_frame.grid_propagate(False)

        # Cargar la imagen solo cuando sea necesario
        img = self.lazy_load_image(game["cover"])
        ctk.CTkLabel(game_frame, image=img, fg_color=BG_COLOR, text="").pack(
            pady=5, fill=ctk.BOTH, expand=True
        )

        # Botón de menú en la parte superior derecha del cuadrado
        menu_button = ctk.CTkButton(
            border_frame,
            text="⋮",
            command=lambda: self.toggle_menu(game, menu_button),
            width=MENU_BUTTON_SIZE,
            height=MENU_BUTTON_SIZE,
            fg_color=BG_COLOR,
            text_color=FG_COLOR,
            border_width=2,
            corner_radius=10,
        )
        menu_button.place(relx=1.0, rely=0.0, anchor="ne")

        game_frame.pack(
            padx=BORDER_THICKNESS, pady=BORDER_THICKNESS, fill=ctk.BOTH, expand=True
        )

        return border_frame

    def toggle_menu(self, game, menu_button):
        # Cerrar el menú actual si hay uno abierto
        if self.current_menu:
            if self.current_menu_button == menu_button:
                self.close_menu(
                    None
                )  # Cierra el menú si se vuelve a hacer clic en el botón
                return
            else:
                self.current_menu.destroy()

        self.current_menu = Menu(self.root, tearoff=0, bg=BG_COLOR, fg=FG_COLOR)
        self.current_menu.add_command(
            label="Jugar", command=lambda: self.play_game(game)
        )
        self.current_menu.add_command(
            label="Editar", command=lambda: self.edit_game(game)
        )
        self.current_menu.add_command(
            label="Eliminar", command=lambda: self.delete_game(game)
        )

        # Obtener la posición del botón en el monitor
        x = menu_button.winfo_rootx()
        y = menu_button.winfo_rooty() + menu_button.winfo_height()

        self.current_menu.post(x, y)
        self.current_menu_button = menu_button

    def close_menu(self, event):
        # Cerrar el menú si el clic está fuera del área del menú actual
        if self.current_menu:
            if event is None or not self.current_menu.winfo_containing(
                event.x_root, event.y_root
            ):
                self.current_menu.destroy()
                self.current_menu = None
                self.current_menu_button = None

    def lazy_load_image(self, path):
        if path in self.image_references:
            return self.image_references[path]
        img = Image.open(path).resize(IMAGE_SIZE, Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.image_references[path] = img
        return img

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def add_game(self):
        name = simpledialog.askstring(
            "Nombre del juego", "Introduce el nombre del juego: "
        )
        if not name:
            return

        exe_path = filedialog.askopenfilename(
            title="Seleccionar el ejecutable del juego: ",
            filetypes=[("Archivos ejecutables", "*.exe *.msi")],
        )
        if not exe_path:
            return

        cover_path = filedialog.askopenfilename(
            title="Selecciona la carátula del juego",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")],
        )
        if not cover_path:
            return

        self.games.append({"name": name, "path": exe_path, "cover": cover_path})
        self.save_games()
        self.display_games()

    def play_game(self, game):
        try:
            subprocess.Popen(["gamemoderun", "wine", game["path"]])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar el juego: {str(e)}")

    def edit_game(self, game):
        new_name = simpledialog.askstring(
            "Editar nombre",
            "Introduce el nuevo nombre del juego:",
            initialvalue=game["name"],
        )
        if new_name is None:
            return

        new_exe_path = filedialog.askopenfilename(
            title="Seleccionar el nuevo ejecutable del juego: ",
            filetypes=[("Archivos ejecutables", "*.exe *.msi")],
        )
        if new_exe_path == "":
            new_exe_path = game["path"]

        new_cover_path = filedialog.askopenfilename(
            title="Selecciona la nueva carátula del juego",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")],
        )
        if new_cover_path == "":
            new_cover_path = game["cover"]

        game["name"] = new_name
        game["path"] = new_exe_path
        game["cover"] = new_cover_path
        self.save_games()
        self.display_games()

    def delete_game(self, game):
        if messagebox.askyesno(
            "Confirmar", f"¿Estás seguro de que quieres eliminar este juego?"
        ):
            self.games.remove(game)
            self.save_games()
            self.display_games()

    def load_games(self):
        if os.path.exists("games.json"):
            with open("games.json", "r") as f:
                self.games = json.load(f)

    def save_games(self):
        with open("games.json", "w") as f:
            json.dump(self.games, f, indent=4)


if __name__ == "__main__":
    root = ctk.CTk()
    app = GameLauncher(root)
    root.mainloop()
