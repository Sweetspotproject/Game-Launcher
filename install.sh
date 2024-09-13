#!/bin/bash

# Variables
REPO_DIR="$(pwd)"
INSTALL_DIR="$HOME/.local/bin/Sweet-Launcher"
VENV_DIR="$INSTALL_DIR/.venv"
LAUNCHER_SCRIPT="$INSTALL_DIR/run.sh"
ICON_PATH="$INSTALL_DIR/icon.png"
DESKTOP_FILE="$HOME/.local/share/applications/Sweet-Launcher.desktop"

# Verifica si python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python3 no está instalado. Instálalo y vuelve a intentarlo."
    exit 1
fi

# Verifica si el directorio de instalación existe
if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
fi

# Copia los archivos necesarios al directorio de instalación
cp app.py "$INSTALL_DIR/"
cp icon.png "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

# Crea el entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "Creando el entorno virtual..."
    python3 -m venv "$VENV_DIR"
fi

# Activa el entorno virtual y instala dependencias
echo "Instalando dependencias..."
source "$VENV_DIR/bin/activate"
pip install -r "$INSTALL_DIR/requirements.txt"
deactivate

# Crea el script de lanzamiento
echo "Creando el script de lanzamiento..."
cat <<EOL > "$LAUNCHER_SCRIPT"
#!/bin/bash
source "$VENV_DIR/bin/activate"
python "$INSTALL_DIR/app.py"
deactivate
EOL

# Hacer el script ejecutable
chmod +x "$LAUNCHER_SCRIPT"

# Crea el archivo .desktop
echo "Creando el archivo .desktop..."
cat <<EOL > "$DESKTOP_FILE"
[Desktop Entry]
Name=Sweet Launcher
Comment=Launch and manage your games
Exec=bash "$LAUNCHER_SCRIPT"
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Games;
EOL

# Hacer el archivo .desktop ejecutable
chmod +x "$DESKTOP_FILE"

# Elimina la carpeta del repositorio
echo "Eliminando la carpeta del repositorio..."
rm -rf "$REPO_DIR"

echo "Instalación completada. El lanzador se ha instalado en $INSTALL_DIR y el acceso directo se encuentra en $DESKTOP_FILE."
