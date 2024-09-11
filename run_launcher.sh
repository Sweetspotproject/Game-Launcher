#!/bin/bash
# Activar el entorno virtual

source ~/myenv/bin/activate

# Ejecutar el script del lanzador
exec python /home/sweetspot/.local/bin/Sweet-Launcher/app.py

# Desactivar el entorno virtual al salir
deactivate
