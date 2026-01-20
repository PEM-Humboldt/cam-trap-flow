"""
Img2WI - Extractor de Imágenes desde Videos de Cámaras Trampa
==================================================================

Aplicación de escritorio para convertir automáticamente videos capturados con cámaras trampa
en secuencias de imágenes individuales, facilitando su análisis posterior o carga en plataformas
como Wildlife Insights.

Características principales:
    - Procesamiento de videos en formatos .MP4, .MOV y .AVI
    - Extracción de frames con offset configurable (segundos por imagen)
    - Interfaz gráfica intuitiva desarrollada con PyQt5
    - Integración de FFmpeg para procesamiento de video
    - Nomenclatura automática y organizada de imágenes extraídas
    - Generación de carpeta única de salida con timestamp
    - Seguimiento en tiempo real del procesamiento con logs estructurados
    - Soporte para múltiples videos en estructura de carpetas

Módulo: main.py (Punto de entrada)
Autor: Cristian C. Acevedo
Organización: Instituto Humboldt - Red OTUS
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
Licencia: Ver THIRD_PARTY_NOTICES.txt
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Añadir la carpeta raíz del proyecto al sys.path para imports relativos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ui_main import VideoProcessorWindow

if __name__ == "__main__":
    # Inicializar la aplicación PyQt5
    app = QApplication(sys.argv)
    
    # Crear y mostrar la ventana principal
    ventana = VideoProcessorWindow()
    ventana.show()
    
    # Iniciar el loop de eventos de la aplicación
    sys.exit(app.exec_())
