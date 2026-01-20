# -*- coding: utf-8 -*-
"""
WI2CamtrapDP - Utilidades
=========================

Funciones auxiliares para procesamiento de datos de cámaras trampa:
    - Conversión de timestamps a ISO 8601 UTC
    - Determinación de tipos MIME desde extensiones de archivo
    - Normalización Unicode y limpieza de texto
    - Corrección de mojibake (codificaciones erróneas)
    - Eliminación de diacríticos para compatibilidad ASCII

Módulo: utils.py
Autor: Cristian C. Acevedo
Organización: Instituto Humboldt - Red OTUS
Última actualización: 23 de diciembre de 2025
"""

from pathlib import Path
from datetime import datetime
from dateutil import parser as dateparser, tz


# ============================================================================
# CONVERSIÓN DE TIMESTAMPS
# ============================================================================

def to_iso_utc(value, timezone_hint: str = "America/Bogota"):
    """
    Convierte fechas/timestamps a formato ISO 8601 UTC con sufijo 'Z'.
    
    Normaliza diferentes formatos de fecha/hora a un estándar consistente.
    Timestamps sin zona horaria (naive) se asumen en la zona especificada.
    
    Args:
        value: Valor a convertir (string, datetime, o None)
        timezone_hint: Zona horaria para timestamps naive (formato IANA)
                      Por defecto: "America/Bogota" (Colombia, UTC-5)
    
    Returns:
        str: Fecha en formato ISO 8601 UTC ("YYYY-MM-DDTHH:MM:SSZ")
             o cadena vacía si el valor es None/vacío
    
    Example:
        >>> to_iso_utc("2024-01-15 14:30:00", "America/Bogota")
        '2024-01-15T19:30:00Z'
        >>> to_iso_utc(datetime(2024, 1, 15, 14, 30))
        '2024-01-15T19:30:00Z'
        
    Note:
        - Timestamps naive se localizan con timezone_hint antes de convertir a UTC
        - El sufijo 'Z' indica zona horaria UTC (Zulu time)
        - Usa dateutil.parser para parseo flexible de formatos
    """
    if value is None or value == "":
        return ""
    
    # Convertir a datetime si es string
    if isinstance(value, datetime):
        dt = value
    else:
        dt = dateparser.parse(str(value))

    # Si no tiene zona horaria, asumir timezone_hint
    if dt.tzinfo is None:
        local = tz.gettz(timezone_hint)
        dt = dt.replace(tzinfo=local)

    # Convertir a UTC y formatear con sufijo 'Z'
    return dt.astimezone(tz.UTC).replace(tzinfo=None).isoformat(timespec="seconds") + "Z"


# ============================================================================
# TIPOS MIME
# ============================================================================

def ext_to_mediatype(path_or_ext: str) -> str:
    """
    Determina el tipo MIME de un archivo desde su extensión.
    
    Mapea extensiones de archivo comunes (imágenes, videos) a sus tipos MIME
    estándar según especificaciones IANA.
    
    Args:
        path_or_ext: Ruta completa o extensión de archivo (con o sin punto)
    
    Returns:
        str: Tipo MIME correspondiente. Retorna "application/octet-stream"
             para extensiones no reconocidas (tipo genérico binario).
    
    Example:
        >>> ext_to_mediatype("photo.jpg")
        'image/jpeg'
        >>> ext_to_mediatype("/path/to/video.mp4")
        'video/mp4'
        >>> ext_to_mediatype(".png")
        'image/png'
        >>> ext_to_mediatype("archivo.xyz")
        'application/octet-stream'
    
    Supported formats:
        Imágenes: jpg, jpeg, png, gif, bmp, tif, tiff
        Videos: mp4, mov, avi
    """
    ext = Path(path_or_ext).suffix.lower()
    mapping = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
    }
    return mapping.get(ext, "application/octet-stream")

# ============================================================================
# LIMPIEZA Y NORMALIZACIÓN DE TEXTO
# ============================================================================

import re
import unicodedata

# Expresión regular para detectar caracteres de control invisibles
_CONTROL_CHARS_RE = re.compile(r"[\u0000-\u0008\u000B-\u000C\u000E-\u001F\u007F]")


def _normalize_unicode(text: str) -> str:
    """
    Normaliza una cadena a Unicode NFC y elimina caracteres de control.
    
    La normalización NFC (Canonical Composition) asegura que caracteres con acentos
    se representen de forma consistente, facilitando comparaciones y búsquedas.
    
    Args:
        text: Cadena a normalizar
    
    Returns:
        str: Cadena normalizada sin caracteres de control
    
    Example:
        >>> _normalize_unicode("caf\u00e9")  # e + acento combinado
        'café'  # é precompuesto
        
    Note:
        Elimina caracteres de control Unicode (\u0000-\u001F, \u007F) que
        pueden causar problemas en procesamiento de texto.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    
    # Normalización NFC (Canonical Composition)
    text = unicodedata.normalize("NFC", text)
    
    # Eliminar caracteres de control invisibles
    text = _CONTROL_CHARS_RE.sub("", text)
    
    return text


def _fix_mojibake(text: str) -> str:
    """
    Corrige errores de codificación (mojibake) en cadenas de texto.
    
    Intenta reparar texto dañado por problemas de codificación UTF-8/Latin-1,
    común en sistemas con configuraciones mixtas.
    
    Estrategia de corrección:
        1. Intenta usar ftfy (fix text for you) si está disponible
        2. Si no, intenta roundtrip latin-1 → utf-8
        3. Si falla, retorna texto normalizado sin corrección
    
    Args:
        text: Cadena potencialmente dañada
    
    Returns:
        str: Cadena corregida
    
    Example:
        >>> _fix_mojibake("Ang\u00c3\u00a9lica")  # AngÃ©lica mal codificada
        'Angélica'  # Corregido
        >>> _fix_mojibake("CÃ¡ceres")
        'Cáceres'
    
    Note:
        - Requiere ftfy para mejor corrección: pip install ftfy
        - Sin ftfy, usa estrategia básica latin-1/utf-8 roundtrip
    """
    t = _normalize_unicode(text)
    
    # Estrategia 1: Usar ftfy si está disponible (más robusto)
    try:
        import ftfy
        return _normalize_unicode(ftfy.fix_text(t))
    except Exception:
        pass
    
    # Estrategia 2: Roundtrip latin-1 → utf-8 (casos comunes)
    try:
        b = t.encode("latin-1", errors="strict")
        t2 = b.decode("utf-8", errors="strict")
        return _normalize_unicode(t2)
    except Exception:
        return t


def _strip_accents_keep_ascii(text: str) -> str:
    """
    Elimina diacríticos (tildes, acentos) para generar ASCII puro.
    
    Convierte caracteres acentuados a sus equivalentes sin acento,
    útil para compatibilidad con sistemas que solo aceptan ASCII.
    
    Args:
        text: Cadena con posibles acentos
    
    Returns:
        str: Cadena sin acentos (solo ASCII)
    
    Example:
        >>> _strip_accents_keep_ascii("Angélica Díaz-Pulido")
        'Angelica Diaz-Pulido'
        >>> _strip_accents_keep_ascii("Cáceres, Colombia")
        'Caceres, Colombia'
        >>> _strip_accents_keep_ascii("Ñandú")
        'Nandu'
    
    Note:
        Usa descomposición NFKD (Compatibility Decomposition) para separar
        caracteres base de marcas diacríticas, luego elimina las marcas.
    """
    t = _normalize_unicode(text)
    
    # Descomposición NFKD: separa caracteres base de marcas diacríticas
    # Luego filtra solo caracteres no combinatorios (elimina acentos)
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", t)
        if not unicodedata.combining(ch)
    )


def clean_text_general(text: str) -> str:
    """
    Limpieza completa de texto para metadatos compatibles con SIB Colombia.
    
    Pipeline de limpieza:
        1. Corrección de mojibake ('AngÃ©lica' → 'Angélica')
        2. Normalización y compactación de espacios
        3. Eliminación de tildes/diacríticos para ASCII ('Angélica' → 'Angelica')
    
    Args:
        text: Cadena a limpiar
    
    Returns:
        str: Cadena limpia en ASCII sin acentos
    
    Example:
        >>> clean_text_general("Ang\u00c3\u00a9lica   D\u00edaz")
        'Angelica Diaz'
        >>> clean_text_general("  Cáceres,  Colombia  ")
        'Caceres, Colombia'
    
    Note:
        Esta función está diseñada para cumplir con requisitos del SIB Colombia
        que requiere metadatos sin acentos para compatibilidad de sistemas.
    """
    # Paso 1: Corregir mojibake
    t = _fix_mojibake(text)
    
    # Paso 2: Normalizar y compactar espacios
    t = " ".join(t.split())
    
    # Paso 3: Eliminar tildes/diacríticos para ASCII
    t = _strip_accents_keep_ascii(t)
    
    return t
