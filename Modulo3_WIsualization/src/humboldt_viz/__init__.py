"""
WIsualization - Módulo de Visualización de Datos de Wildlife Insights
======================================================================

Paquete Python para análisis y visualización de datos de fototrampeo exportados
desde Wildlife Insights (WI). Proporciona herramientas para generar visualizaciones
científicas de alta calidad para estudios de biodiversidad y comportamiento animal.

Características principales:
    - Curvas de acumulación de especies con suavizado semilogarítmico y bootstrap
    - Visualización de rangos temporales de deployments por sitio
    - Análisis de patrones de actividad circadiana mediante KDE
    - Matrices espaciotemporales de presencia/ausencia de especies
    - Interfaz gráfica intuitiva basada en PyQt5
    - Detección automática de estructura de archivos CSV
    - Normalización inteligente de datos Wildlife Insights

Módulo: __init__.py
Autores: Cristian C. Acevedo, Angélica Díaz-Pulido
Organización: Instituto de Investigación de Recursos Biológicos Alexander von Humboldt
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
Licencia: Ver LICENSE
"""

__app_name__ = "WIsualization"
__version__ = "1.0.0"
__authors__ = ["C.C. Acevedo", "A. Díaz-Pulido"]
__org__ = "Instituto de Investigación de Recursos Biológicos Alexander von Humboldt"

# Exportar función principal para uso como módulo ejecutable
# Uso: python -m humboldt_viz
from .ui_main import main  # noqa: F401
