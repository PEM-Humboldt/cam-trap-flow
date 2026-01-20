"""
WI2CamtrapDP - Conversor de Wildlife Insights a Camtrap Data Package
====================================================================

Paquete Python para transformar exportaciones de Wildlife Insights al estándar
internacional Camtrap-DP (Camera Trap Data Package) v1.0.2.

Características:
    - Conversión automática de formatos Wildlife Insights a Camtrap-DP
    - Normalización de timestamps a ISO 8601 UTC
    - Validación con Frictionless Framework
    - Mapeo completo de campos taxonómicos y metadatos
    - Generación de datapackage.json compatible con estándares
    - Empaquetado en ZIP para distribución y publicación

Módulos principales:
    config: Configuración y opciones de procesamiento
    processor: Motor de transformación WI → Camtrap-DP
    utils: Utilidades (fechas, tipos MIME, limpieza de texto)
    validator: Validación de Data Packages con Frictionless

Uso básico:
    >>> from camtrapdp import process_zip
    >>> work_dir = process_zip(
    ...     zip_path="export.zip",
    ...     out_dir="./output",
    ...     validate=True,
    ...     timezone_hint="America/Bogota"
    ... )

Autor: Cristian C. Acevedo, Angélica Diaz-Pulido
Organización: Instituto de Investigación de Recursos Biológicos Alexander von Humboldt
Proyecto: Red OTUS - Gestión de Datos de Fototrampeo
Versión: 1.0.0
Última actualización: 23 de diciembre de 2025
"""

__version__ = "1.0.0"
__author__ = "Cristian C. Acevedo, Angélica Diaz-Pulido"
__organization__ = "Instituto Humboldt"
__email__ = "adiaz@humboldt.org.co"

# Importar componentes principales para acceso directo
from .config import Options
from .processor import process_zip
from .validator import validate_datapackage

__all__ = [
    "Options",
    "process_zip",
    "validate_datapackage",
]
