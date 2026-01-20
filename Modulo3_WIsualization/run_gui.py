"""
WIsualization - Script de Desarrollo y Depuración
==================================================

Script auxiliar para ejecutar la aplicación WIsualization durante el desarrollo.
Facilita la ejecución directa desde editores como VS Code sin necesidad de
instalación del paquete.

Funcionalidad:
    - Configura el path de Python para importar el módulo humboldt_viz desde src/
    - Permite ejecutar con F5 en VS Code o "Run Python File"
    - Útil durante el desarrollo para pruebas rápidas de cambios
    - Simula el entorno de ejecución del paquete instalado

Uso desde VS Code:
    1. Abrir este archivo en el editor
    2. Presionar F5 o hacer clic en "Run Python File"
    3. La aplicación se lanzará directamente

Uso desde terminal:
    python run_gui.py

Nota: Para uso en producción, preferir:
    - python -m humboldt_viz (después de pip install .)
    - O ejecutar el .exe generado con PyInstaller

Módulo: run_gui.py
Autores: Cristian C. Acevedo, Angélica Díaz-Pulido
Organización: Instituto Humboldt
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
"""

import os
import sys

# =============================================================================
# CONFIGURACIÓN DEL PATH PARA DESARROLLO
# =============================================================================
# Añade "<raiz>/src" al sys.path para que 'humboldt_viz' sea importable
# sin necesidad de instalar el paquete completo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# =============================================================================
# IMPORTACIÓN Y EJECUCIÓN
# =============================================================================
from humboldt_viz.ui_main import main

if __name__ == "__main__":
    main()
