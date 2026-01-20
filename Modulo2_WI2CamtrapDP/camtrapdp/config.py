# -*- coding: utf-8 -*-
"""
WI2CamtrapDP - Configuración
=============================

Clases de configuración y opciones por defecto para el procesamiento
de exportaciones de Wildlife Insights.

Módulo: config.py
Autor: Cristian C. Acevedo
Organización: Instituto Humboldt - Red OTUS
Última actualización: 23 de diciembre de 2025
"""

from dataclasses import dataclass


@dataclass
class Options:
    """
    Opciones de configuración para el procesamiento de datos Camtrap-DP.
    
    Esta clase define los parámetros configurables que controlan el comportamiento
    del procesador durante la conversión de Wildlife Insights a Camtrap-DP.
    
    Attributes:
        timezone_hint (str): Zona horaria por defecto para timestamps sin zona horaria.
                            Formato IANA (ej: "America/Bogota", "UTC", "Europe/Madrid").
                            Por defecto: "America/Bogota" (hora de Colombia, UTC-5).
                            
        validate (bool): Si True, valida el datapackage generado con Frictionless Framework.
                        La validación verifica la conformidad con el estándar Camtrap-DP
                        y reporta errores de estructura o datos.
                        Por defecto: True (recomendado).
                        
        make_zip (bool): Si True, crea un archivo ZIP con los resultados del procesamiento.
                        El ZIP incluye deployments.csv, media.csv, observations.csv y
                        datapackage.json, facilitando distribución y publicación.
                        Por defecto: True.
                        
        open_folder_after (bool): Si True, abre automáticamente la carpeta de resultados
                                 al finalizar el procesamiento (solo en interfaces gráficas).
                                 Por defecto: True.
                                 
        overwrite (bool): Si True, sobrescribe archivos y directorios existentes.
                         Si False, genera error si el directorio de salida ya existe.
                         Por defecto: True.
    
    Example:
        >>> opts = Options(
        ...     timezone_hint="America/Bogota",
        ...     validate=True,
        ...     make_zip=True
        ... )
        >>> # Usar con API antigua
        >>> from camtrapdp.processor import process
        >>> process("export.zip", "./output", opts)
    
    Note:
        Esta clase se usa principalmente con la API antigua (processor.process).
        La API nueva (processor.process_zip) acepta parámetros directamente.
    """
    
    timezone_hint: str = "America/Bogota"  # Zona horaria por defecto (Colombia, UTC-5)
    validate: bool = True                  # ✔ Validar con Frictionless Framework
    make_zip: bool = True                  # ✔ Crear ZIP final con resultados
    open_folder_after: bool = True         # ✔ Abrir carpeta al terminar (GUI)
    overwrite: bool = True                 # ✔ Sobrescribir archivos existentes
