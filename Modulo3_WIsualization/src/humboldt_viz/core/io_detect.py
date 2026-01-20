"""
WIsualization - Módulo de Detección y Normalización de Datos
=============================================================

Funciones especializadas para lectura, detección automática y normalización de
archivos CSV exportados desde Wildlife Insights. Maneja la variabilidad en los
formatos de exportación y asegura consistencia en los datos para análisis.

Características principales:
    - Lectura robusta de CSV con detección automática de encoding y separadores
    - Identificación inteligente de DataFrames de 'images' y 'deployments'
    - Normalización de nombres científicos con múltiples estrategias de fallback
    - Manejo de múltiples formatos de exportación de Wildlife Insights
    - Conversión y validación de tipos de datos para análisis científico

Casos de uso:
    - Procesar exportaciones de proyectos de Wildlife Insights
    - Manejar CSV con diferentes encodings (UTF-8, Latin-1)
    - Unificar nomenclatura taxonómica de múltiples fuentes
    - Preparar datos para visualización y análisis estadístico

Módulo: core/io_detect.py
Autores: Cristian C. Acevedo, Angélica Díaz-Pulido
Organización: Instituto Humboldt - Red OTUS
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
Licencia: Ver LICENSE
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Dict, Tuple, Optional

import pandas as pd


# =============================================================================
# FUNCIONES DE LECTURA Y PARSING DE ARCHIVOS
# =============================================================================

def leer_csv_desde_zip(zf: zipfile.ZipFile, member: str) -> pd.DataFrame:
    """
    Lee un archivo CSV desde un ZIP probando múltiples encodings y separadores.
    
    Implementa un sistema robusto de lectura que intenta diferentes combinaciones
    de codificación de caracteres y delimitadores para maximizar la compatibilidad
    con exportaciones de diferentes regiones y configuraciones de Wildlife Insights.
    
    Estrategia de lectura:
        1. Intenta UTF-8 con coma (,) - Estándar internacional
        2. Intenta UTF-8 con punto y coma (;) - Común en Europa/Latam
        3. Intenta Latin-1 con coma - Archivos antiguos o Windows
        4. Intenta Latin-1 con punto y coma - Combinación región específica
    
    Args:
        zf (zipfile.ZipFile): Objeto ZIP abierto que contiene el CSV
        member (str): Nombre/ruta del archivo CSV dentro del ZIP
    
    Returns:
        pd.DataFrame: DataFrame con todos los datos como strings (dtype=str)
                     para evitar conversiones automáticas incorrectas
    
    Raises:
        ValueError: Si ninguna combinación de encoding/separador funciona
        
    Notas:
        - Retorna dtype=str para preservar información original
        - La conversión de tipos se hace posteriormente según necesidad
        - low_memory=False para consistencia en inferencia de tipos
    """
    with zf.open(member) as f:
        data = f.read()

    # Probar todas las combinaciones de encoding y separador
    for enc in ("utf-8", "latin-1"):
        for sep in (",", ";"):
            try:
                return pd.read_csv(
                    io.BytesIO(data),
                    encoding=enc,
                    sep=sep,
                    dtype=str,  # Mantener como strings para preservar datos
                    low_memory=False,  # Evitar warnings de tipo mixto
                )
            except Exception:
                continue  # Intentar siguiente combinación

    # Si ninguna combinación funcionó, reportar error
    raise ValueError(f"No fue posible leer el CSV: {member}. "
                    "Verificar formato, encoding o integridad del archivo.")


# =============================================================================
# FUNCIONES DE DETECCIÓN AUTOMÁTICA DE ESTRUCTURAS
# =============================================================================

def detectar_df_images(dfs_por_nombre: Dict[str, pd.DataFrame]) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
    """
    Identifica automáticamente el DataFrame de 'images' dentro de un conjunto de DataFrames.
    
    El DataFrame de images es el núcleo de los datos de Wildlife Insights, conteniendo
    información sobre cada fotografía capturada. Esta función implementa heurísticas
    flexibles para detectarlo incluso si el archivo no se llama exactamente "images.csv".
    
    Criterios de identificación:
        - OBLIGATORIO: Columnas 'timestamp' y 'deployment_id'
        - OBLIGATORIO: Al menos UNA columna de identificación taxonómica:
            * 'scientific_name' (preferido)
            * 'genus' + 'species' (combinables)
            * 'common_name' (nombre común)
            * 'wi_taxon_id' (ID taxonómico de WI)
    
    Args:
        dfs_por_nombre (Dict[str, pd.DataFrame]): Diccionario {nombre_archivo: DataFrame}
                                                   de todos los CSV cargados
    
    Returns:
        Tuple[Optional[str], Optional[pd.DataFrame]]:
            - nombre del archivo identificado como images (o None)
            - DataFrame de images (o None si no se detecta)
    
    Ejemplos:
        >>> dfs = {"images.csv": df_imgs, "deployments.csv": df_deps}
        >>> nombre, df = detectar_df_images(dfs)
        >>> print(nombre)  # "images.csv"
    
    Notas:
        - Retorna el PRIMER DataFrame que cumple los criterios
        - Es flexible con nombres de archivos no estándar
        - Útil para exportaciones con nombres personalizados
    """
    for nombre, df in dfs_por_nombre.items():
        # Validar que sea un DataFrame válido
        if not isinstance(df, pd.DataFrame):
            continue
            
        # Convertir nombres de columnas a conjunto para búsqueda eficiente
        cols = set(map(str, df.columns))
        
        # Verificar columnas base obligatorias
        base_ok = {"timestamp", "deployment_id"}.issubset(cols)
        
        # Verificar que tenga al menos UNA forma de identificación taxonómica
        tiene_nombre = (
            "scientific_name" in cols  # Caso ideal
            or {"genus", "species"}.issubset(cols)  # Nombre científico en partes
            or "common_name" in cols  # Nombre común
            or "wi_taxon_id" in cols  # ID numérico de WI
        )
        
        # Si cumple ambos criterios, es el DataFrame de images
        if base_ok and tiene_nombre:
            return nombre, df
    
    # No se encontró ningún DataFrame que cumpla los criterios
    return None, None


def detectar_df_deployments(dfs_por_nombre: Dict[str, pd.DataFrame]) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
    """
    Identifica automáticamente el DataFrame de 'deployments' dentro de un conjunto de DataFrames.
    
    El DataFrame de deployments contiene metadatos sobre cada instalación de cámara trampa,
    incluyendo ubicación, fechas de operación y configuración del equipo.
    
    Criterios de identificación:
        - OBLIGATORIO: 'deployment_id' (identificador único)
        - OBLIGATORIO: 'start_date' (inicio de operación)
        - OBLIGATORIO: 'end_date' (fin de operación)
    
    Args:
        dfs_por_nombre (Dict[str, pd.DataFrame]): Diccionario {nombre_archivo: DataFrame}
    
    Returns:
        Tuple[Optional[str], Optional[pd.DataFrame]]:
            - nombre del archivo identificado como deployments (o None)
            - DataFrame de deployments (o None si no se detecta)
    
    Ejemplos:
        >>> dfs = {"images.csv": df_imgs, "deployments.csv": df_deps}
        >>> nombre, df = detectar_df_deployments(dfs)
        >>> print(nombre)  # "deployments.csv"
    
    Notas:
        - Más estricto que detectar_df_images (requiere exactamente 3 columnas)
        - Esencial para análisis temporales y espaciales
        - Permite validar cobertura temporal del estudio
    """
    for nombre, df in dfs_por_nombre.items():
        if isinstance(df, pd.DataFrame):
            cols = set(map(str, df.columns))
            # Verificar presencia de las 3 columnas obligatorias
            if {"deployment_id", "start_date", "end_date"}.issubset(cols):
                return nombre, df
    
    return None, None


# =============================================================================
# FUNCIONES DE NORMALIZACIÓN Y LIMPIEZA DE DATOS
# =============================================================================

def normalizar_images(df_images: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza y estandariza el DataFrame de images para análisis científico.
    
    Realiza múltiples transformaciones para asegurar consistencia en los datos:
    - Conversión de timestamps a objetos datetime de pandas
    - Estandarización de deployment_id como strings
    - Unificación de nombres científicos desde múltiples fuentes
    - Limpieza de espacios en blanco y valores nulos
    
    Estrategia de nombres científicos (en orden de prioridad):
        1. 'scientific_name' existente (si válido)
        2. Concatenación 'genus' + 'species' (si ambos existen)
        3. Solo 'species' (si existe y no está vacío)
        4. 'common_name' (nombre común)
        5. 'wi_taxon_id' (ID taxonómico de WI)
        6. 'Unknown' (fallback final)
    
    Args:
        df_images (pd.DataFrame): DataFrame original de images
    
    Returns:
        pd.DataFrame: DataFrame normalizado con:
            - timestamp como datetime64[ns]
            - deployment_id como string
            - scientific_name garantizado (nunca vacío/nulo)
    
    Transformaciones realizadas:
        - Conversión de tipos de datos
        - Limpieza de espacios en blanco
        - Consolidación de nombres científicos
        - Manejo de valores nulos y vacíos
    
    Ejemplos:
        >>> df = normalizar_images(df_original)
        >>> df['timestamp'].dtype  # datetime64[ns]
        >>> df['scientific_name'].isna().sum()  # 0
    
    Notas:
        - SIEMPRE retorna un DataFrame con scientific_name válido
        - Preserva el DataFrame original (usa .copy())
        - Compatible con múltiples versiones de exportación de WI
        - Maneja casos edge como nombres parciales o IDs taxonómicos
    """
    df = df_images.copy()  # No modificar el DataFrame original

    # =========================================================================
    # PASO 1: Normalización de Timestamp
    # =========================================================================
    if "timestamp" in df.columns:
        # Convertir a datetime, marcando inválidos como NaT (Not a Time)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # =========================================================================
    # PASO 2: Normalización de Deployment ID
    # =========================================================================
    if "deployment_id" in df.columns:
        # Forzar a string para consistencia (evita problemas con IDs numéricos)
        df["deployment_id"] = df["deployment_id"].astype(str)

    # =========================================================================
    # PASO 3: Normalización de Nombres Científicos (Multi-estrategia)
    # =========================================================================
    
    # Estrategia 1: Usar 'scientific_name' existente si está disponible
    if "scientific_name" in df.columns:
        df["scientific_name"] = df["scientific_name"].astype(str).str.strip()
        # Marcar como None si está vacío (para que el fallback funcione)
        vacios = df["scientific_name"].isna() | (df["scientific_name"].str.len() == 0)
        if vacios.any():
            df.loc[vacios, "scientific_name"] = None
    else:
        # Si no existe, crear columna vacía para rellenar con fallbacks
        df["scientific_name"] = None

    # Estrategia 2: Combinar 'genus' + 'species' → "Genus species"
    if "genus" in df.columns and "species" in df.columns:
        g = df["genus"].astype(str).str.strip()
        s = df["species"].astype(str).str.strip()
        # Concatenar con espacio, limpiar espacios dobles
        combinado = (g.fillna("") + " " + s.fillna("")).str.strip()
        # Solo usar si el resultado tiene contenido
        combinado = combinado.where(combinado.str.len() > 0, None)
        # Rellenar scientific_name solo donde está None
        df["scientific_name"] = df["scientific_name"].fillna(combinado)

    # Estrategia 3: Usar solo 'species' si genus no está disponible
    if "species" in df.columns:
        s_only = df["species"].astype(str).str.strip()
        s_only = s_only.where(s_only.str.len() > 0, None)
        df["scientific_name"] = df["scientific_name"].fillna(s_only)

    # Estrategia 4: Usar 'common_name' como fallback
    if "common_name" in df.columns:
        c = df["common_name"].astype(str).str.strip()
        c = c.where(c.str.len() > 0, None)
        df["scientific_name"] = df["scientific_name"].fillna(c)

    # Estrategia 5: Usar 'wi_taxon_id' como último recurso antes de Unknown
    if "wi_taxon_id" in df.columns:
        t = df["wi_taxon_id"].astype(str).str.strip()
        t = t.where(t.str.len() > 0, None)
        df["scientific_name"] = df["scientific_name"].fillna(t)

    # Estrategia 6 (Final): Marcar como "Unknown" lo que no se pudo identificar
    df["scientific_name"] = df["scientific_name"].fillna("Unknown")
    
    return df
