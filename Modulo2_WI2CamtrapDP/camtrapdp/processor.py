# -*- coding: utf-8 -*-
"""
WI2CamtrapDP - Módulo de Procesamiento Principal
==================================================

Transforma exportaciones de Wildlife Insights (formato ZIP de proyecto) al estándar
Camtrap Data Package v1.0.2, generando los archivos CSV y metadatos requeridos.

Funcionalidades principales:
    - Extracción y normalización de datos desde ZIP de Wildlife Insights
    - Conversión de timestamps a formato ISO 8601 UTC
    - Construcción de deployments.csv con datos de despliegues de cámaras
    - Generación de media.csv con información de archivos multimedia
    - Creación de observations.csv con registros de observaciones
    - Producción de datapackage.json con metadatos del conjunto de datos
    - Validación con Frictionless Framework (opcional)
    - Empaquetado en ZIP con timestamp

Estructura de salida:
    WI2CamtrapDP_<nombre-proyecto>_<timestamp>/
    └── output/
        ├── deployments.csv
        ├── media.csv
        ├── observations.csv
        └── datapackage.json

Módulo: processor.py
Autor: Cristian C. Acevedo
Organización: Instituto Humboldt - Red OTUS
Versión: 1.0.0
Última actualización: 23 de diciembre de 2025
"""

from __future__ import annotations

import io
import os
import re
import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import numpy as np
import unicodedata

# ============================================================================
# UTILIDADES GENERALES
# ============================================================================

def _log(logger, msg: str):
    """
    Emite un mensaje de log de forma segura a través del callback proporcionado.
    
    Envuelve la llamada al logger en try-except para evitar que errores en el
    sistema de logging interrumpan el procesamiento principal.
    
    Args:
        logger: Función callback para logging (recibe un string)
        msg: Mensaje a registrar
    """
    try:
        logger(str(msg))
    except Exception:
        pass


def _progress(cb, pct: int, msg: str = ""):
    """
    Reporta progreso de forma segura a través del callback proporcionado.
    
    Emite actualizaciones de progreso con porcentaje y mensaje opcional.
    Maneja errores silenciosamente para no interrumpir el procesamiento.
    
    Args:
        cb: Función callback para progreso (recibe porcentaje y mensaje)
        pct: Porcentaje de progreso (0-100)
        msg: Mensaje descriptivo opcional
    """
    try:
        cb(int(pct), str(msg))
    except Exception:
        pass


def _slugify_name(s: str) -> str:
    """
    Convierte un nombre a formato slug válido para Camtrap-DP.
    
    Transforma cadenas a formato compatible con el estándar (minúsculas, sin acentos,
    solo caracteres permitidos: a-z, 0-9, -, ., /).
    
    Proceso de transformación:
        1. Normalización Unicode y eliminación de acentos
        2. Conversión de espacios y guiones bajos a guiones
        3. Eliminación de caracteres no permitidos
        4. Limpieza de guiones/puntos al inicio y final
    
    Args:
        s: Cadena a convertir a slug
        
    Returns:
        str: Cadena en formato slug válido. Si el resultado está vacío,
             retorna "wi-project" como valor por defecto.
             
    Example:
        >>> _slugify_name("Mi Proyecto_2024")
        'mi-proyecto-2024'
        >>> _slugify_name("Estación #1 (Bogotá)")
        'estacion-1-bogota'
    """
    # Normalización Unicode (NFD) y eliminación de acentos
    s = unicodedata.normalize("NFKD", str(s))
    s = s.encode("ascii", "ignore").decode("ascii")

    # Sustituir espacios y guiones bajos por guiones
    s = s.replace(" ", "-").replace("_", "-")

    # Convertir a minúsculas y eliminar caracteres no permitidos
    # Patrón permitido: a-z, 0-9, -, ., /
    s = s.lower()
    s = re.sub(r"[^-a-z0-9._/]+", "", s)

    # Eliminar guiones, puntos y barras al inicio o final
    s = re.sub(r"^[-./]+", "", s)
    s = re.sub(r"[-./]+$", "", s)

    return s if s else "wi-project"


def include_if_any(df: pd.DataFrame, col: str, series_like):
    """
    Agrega una columna al DataFrame solo si contiene al menos un valor no nulo/no vacío.
    
    Función auxiliar para agregar columnas opcionales de forma condicional,
    evitando agregar columnas completamente vacías al resultado final.
    
    Args:
        df: DataFrame destino donde se agregará la columna
        col: Nombre de la columna a agregar
        series_like: Datos a agregar (Series, lista, etc.)
        
    Returns:
        None: Modifica el DataFrame in-place
        
    Note:
        Si todos los valores son NaN o strings vacíos, la columna no se agrega.
        Los errores se manejan silenciosamente para no interrumpir el flujo.
    """
    try:
        s = pd.Series(series_like)
        # Verificar si todos los valores son nulos o vacíos
        if s.isna().all() or (s.astype(str).str.strip() == "").all():
            return
        df[col] = s
    except Exception:
        # Mejor no romper el flujo por columnas opcionales
        pass


def to_iso_utc(value, tz_hint: str = "America/Bogota"):
    """
    Convierte timestamps a formato ISO 8601 UTC (terminado en 'Z').
    
    Normaliza diferentes formatos de fecha/hora a un formato estándar ISO 8601
    en zona horaria UTC. Maneja timestamps naive (sin zona horaria) localizándolos
    con la zona horaria sugerida antes de convertir a UTC.
    
    Args:
        value: Valor a convertir (string, datetime, etc.)
        tz_hint: Zona horaria a usar para timestamps naive (por defecto "America/Bogota")
        
    Returns:
        str o pd.NA: String en formato ISO 8601 UTC ("YYYY-MM-DDTHH:MM:SSZ")
                     o pd.NA si el valor es inválido o vacío
                     
    Example:
        >>> to_iso_utc("2024-01-15 14:30:00", "America/Bogota")
        '2024-01-15T19:30:00Z'
        
    Note:
        - Timestamps naive se asumen en la zona horaria tz_hint
        - Strings vacíos o "nan" retornan pd.NA
        - Errores de conversión retornan pd.NA sin lanzar excepciones
    """
    if value is None:
        return pd.NA
    try:
        s = str(value).strip()
        if s == "" or s.lower() == "nan":
            return pd.NA
        
        # Intento de parseo directo
        dt = pd.to_datetime(s, utc=False, errors="coerce", dayfirst=False)
        if pd.isna(dt):
            return pd.NA
        
        # Si es 'naive' (sin zona horaria), localizar con tz_hint
        if dt.tzinfo is None or str(dt.tzinfo) == "None":
            try:
                # Localizar con zona horaria sugerida
                dt = dt.tz_localize(tz_hint, nonexistent="shift_forward", ambiguous="NaT")
            except Exception:
                # Fallback: asumir UTC si falla la localización
                dt = dt.tz_localize("UTC")
        
        # Convertir a UTC
        dt = dt.tz_convert("UTC")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return pd.NA


def ext_to_mediatype(name: str) -> str:
    """
    Determina el tipo MIME de un archivo basándose en su extensión.
    
    Mapea extensiones de archivo comunes a sus tipos MIME correspondientes
    según estándares web.
    
    Args:
        name: Nombre del archivo con extensión
        
    Returns:
        str: Tipo MIME correspondiente. Retorna "application/octet-stream"
             para extensiones no reconocidas o entradas inválidas.
             
    Example:
        >>> ext_to_mediatype("photo.jpg")
        'image/jpeg'
        >>> ext_to_mediatype("video.mp4")
        'video/mp4'
        >>> ext_to_mediatype("archivo.xyz")
        'application/octet-stream'
        
    Supported types:
        Imágenes: jpg, jpeg, png, gif, bmp, tif, tiff
        Videos: mp4, avi
    """
    if not isinstance(name, str):
        return "application/octet-stream"
    
    # Extraer extensión (última parte después del punto)
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    
    # Mapeo de extensiones a tipos MIME
    if ext in {"jpg", "jpeg"}:
        return "image/jpeg"
    if ext in {"png"}:
        return "image/png"
    if ext in {"gif"}:
        return "image/gif"
    if ext in {"bmp"}:
        return "image/bmp"
    if ext in {"tif", "tiff"}:
        return "image/tiff"
    if ext in {"mp4"}:
        return "video/mp4"
    if ext in {"avi"}:
        return "video/x-msvideo"
    
    return "application/octet-stream"


def map_capture_method_from_text(txt: str) -> str:
    """
    Infiere el método de captura (captureMethod) desde texto libre.
    
    Analiza descripciones textuales para determinar el método de captura
    según el vocabulario controlado de Camtrap-DP.
    
    Args:
        txt: Texto descriptivo del método de captura
        
    Returns:
        str: Método de captura inferido:
             - "manual": Si contiene palabras como "manual", "bait", "lure"
             - "timeLapse": Si contiene "time" y "lapse"
             - "activityDetection": Valor por defecto (PIR/sensor de movimiento)
             
    Example:
        >>> map_capture_method_from_text("motion sensor camera")
        'activityDetection'
        >>> map_capture_method_from_text("time lapse photography")
        'timeLapse'
        
    Note:
        La heurística es básica y puede refinarse según necesidades.
    """
    if not isinstance(txt, str):
        return "activityDetection"
    
    s = txt.lower()
    
    # Detectar captura manual (cebo, señuelo)
    if "manual" in s or "bait" in s or "lure" in s:
        return "manual"
    
    # Detectar time-lapse
    if "time" in s and "lapse" in s:
        return "timeLapse"
    
    # Por defecto: detección por actividad (PIR)
    return "activityDetection"


def classify_observation_and_scientific_name(row):
    """
    Clasifica observationType y scientificName basado en common_name y otros campos taxonómicos.
    
    PRIORIDAD para scientificName:
    1. scientific_name_norm (genus + species) si están disponibles
    2. common_name si está disponible
    3. Cascada taxonómica (order → family → "Animalia")
    
    Retorna: (observationType, scientificName)
    """
    common_name = str(row.get("common_name", "")).strip()
    scientific_name_norm = str(row.get("scientific_name_norm", "")).strip()
    genus = str(row.get("genus", "")).strip()
    species = str(row.get("species", "")).strip()
    order = str(row.get("order", "")).strip()
    family = str(row.get("family", "")).strip()
    
    # Normalizar common_name para comparaciones
    common_lower = common_name.lower()
    
    # 1. Human cases
    if common_lower in {"human", "human-camera trapper"}:
        # Para humanos, priorizar scientific_name_norm si existe, sino usar "Homo sapiens"
        sci_name = scientific_name_norm if scientific_name_norm else "Homo sapiens"
        return "human", sci_name
    
    # 2. Blank case
    elif common_lower == "blank":
        return "blank", "blank"
    
    # 3. Animal generic case
    elif common_lower == "animal":
        return "animal", "Animalia"
    
    # 4. Vehicle case
    elif common_lower == "vehicle":
        return "vehicle", "blank"
    
    # 5. Unknown case
    elif common_lower == "unknown":
        return "unknown", "blank"
    
    # 6. Unclassified case
    elif common_lower == "unclassified":
        return "unclassified", "blank"
    
    # 7. Casos con datos taxonómicos (prioridad: scientific_name_norm > common_name > cascada taxonómica)
    else:
        # Determinar el scientificName según disponibilidad
        scientific_name = None
        
        # PRIORIDAD 1: scientific_name_norm (genus + species)
        if scientific_name_norm and scientific_name_norm.lower() not in {"", "nan", "none"}:
            scientific_name = scientific_name_norm
        
        # PRIORIDAD 2: common_name si existe y no está vacío
        elif common_name and common_name.lower() not in {"", "nan", "none"}:
            scientific_name = common_name
        
        # PRIORIDAD 3: Cascada taxonómica
        elif order and order.lower() not in {"", "nan", "none"}:
            scientific_name = order
        elif family and family.lower() not in {"", "nan", "none"}:
            scientific_name = family
        else:
            scientific_name = "Animalia"
        
        return "animal", scientific_name


def human_or_blank(is_blank, common_name: str | None) -> str:
    """
    [DEPRECADA] Clasifica observación como 'blank', 'human' o 'animal'.
    
    NOTA IMPORTANTE:
        Esta función se mantiene por compatibilidad con versiones anteriores
        pero YA NO SE USA en el procesamiento actual.
        
        La lógica de clasificación ahora se maneja en:
        classify_observation_and_scientific_name()
    
    Args:
        is_blank: Indicador de imagen en blanco (1/0)
        common_name: Nombre común de la especie observada
        
    Returns:
        str: Tipo de observación ("blank", "human" o "animal")
        
    Deprecated:
        Desde v1.0.0. Usar classify_observation_and_scientific_name() en su lugar.
    """
    try:
        # Wildlife Insights marca is_blank 1/0; si blank, tipo 'blank'
        if int(is_blank) == 1:
            return "blank"
    except Exception:
        pass
    
    # Si no es blank y el común dice 'human', clasificar humano
    if isinstance(common_name, str) and common_name.strip().lower() in {"human", "humano", "homo sapiens"}:
        return "human"
    
    return "animal"


def _schemas_dir() -> Path | None:
    """
    Localiza el directorio que contiene los schemas JSON de Camtrap-DP.
    
    Busca la carpeta 'schemas' que contiene los archivos de definición de esquemas
    (deployments-table-schema.json, media-table-schema.json, observations-table-schema.json)
    en varias ubicaciones posibles relativas al módulo actual.
    
    Ubicaciones de búsqueda (en orden):
        1. <directorio_actual>/schemas/
        2. <directorio_padre>/schemas/
        3. <directorio_actual>/camtrapdp/schemas/
    
    Returns:
        Path o None: Ruta al directorio de schemas si existe, None si no se encuentra
        
    Example:
        >>> schemas = _schemas_dir()
        >>> if schemas:
        ...     dep_schema = schemas / "deployments-table-schema.json"
    """
    here = Path(__file__).resolve().parent
    candidates = [
        here / "schemas",
        here.parent / "schemas",
        here / "camtrapdp" / "schemas",
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    return None


def _align_df_to_local_schema(df: pd.DataFrame, schema_path: Path) -> pd.DataFrame:
    """
    Alinea las columnas de un DataFrame con un schema JSON de Camtrap-DP.
    
    Lee el schema JSON y reorganiza el DataFrame para que:
        1. Todas las columnas del schema estén presentes (crea faltantes como vacías)
        2. Las columnas estén en el orden especificado por el schema
    
    Args:
        df: DataFrame a alinear
        schema_path: Ruta al archivo JSON con el schema (formato Table Schema)
        
    Returns:
        pd.DataFrame: DataFrame alineado con columnas del schema.
                      Si falla la lectura del schema, retorna el DataFrame original.
                      
    Note:
        No realiza casting de tipos estricto, solo organización de columnas.
        Columnas en el DataFrame que no estén en el schema se descartan.
        
    Example:
        >>> schema = Path("deployments-table-schema.json")
        >>> df_aligned = _align_df_to_local_schema(df, schema)
    """
    try:
        # Leer schema JSON
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        fields = [f["name"] for f in schema.get("fields", []) if "name" in f]
        
        if fields:
            # Agregar columnas faltantes como vacías
            for col in fields:
                if col not in df.columns:
                    df[col] = pd.NA
            
            # Reordenar columnas según schema
            df = df[fields]
    except Exception:
        # Si falla la lectura del schema, devolver DataFrame sin cambios
        pass
    
    return df


# ============================================================================
# FUNCIONES CORE: LECTURA Y CONSTRUCCIÓN
# ============================================================================

def _load_csv_from_zip(zf: zipfile.ZipFile, name_contains: str) -> pd.DataFrame:
    """
    Extrae y carga un archivo CSV desde un archivo ZIP.
    
    Busca el primer archivo CSV dentro del ZIP cuyo nombre contenga la cadena
    especificada (búsqueda case-insensitive) y lo carga como DataFrame.
    
    Args:
        zf: Objeto ZipFile abierto para lectura
        name_contains: Subcadena a buscar en nombres de archivos (ej: "images", "deploy")
        
    Returns:
        pd.DataFrame: DataFrame con los datos del CSV encontrado.
                      Si no se encuentra ningún archivo coincidente,
                      retorna un DataFrame vacío.
                      
    Example:
        >>> with zipfile.ZipFile("export.zip") as zf:
        ...     images = _load_csv_from_zip(zf, "images")
        ...     deploys = _load_csv_from_zip(zf, "deploy")
        
    Note:
        La búsqueda es case-insensitive para mayor flexibilidad.
    """
    name_contains = name_contains.lower()
    for info in zf.infolist():
        if info.filename.lower().endswith(".csv") and name_contains in info.filename.lower():
            with zf.open(info) as fp:
                data = fp.read()
                return pd.read_csv(io.BytesIO(data), low_memory=False)
    return pd.DataFrame()


def _ensure_work_dir(zip_path: Path, out_dir: Path, overwrite: bool) -> Path:
    """
    Crea el directorio de trabajo para almacenar resultados del procesamiento.
    
    Genera una estructura de directorios con timestamp para organizar los archivos
    de salida. Si overwrite=True, limpia el contenido existente.
    
    Estructura creada:
        <out_dir>/
        └── WI2CamtrapDP_<nombre-zip>_<YYYYMMDD_HHMMSS>/
            └── output/
                ├── deployments.csv
                ├── media.csv
                ├── observations.csv
                └── datapackage.json
    
    Args:
        zip_path: Ruta del archivo ZIP de entrada (se usa su nombre)
        out_dir: Directorio base donde crear la estructura
        overwrite: Si True, limpia contenido existente del directorio output
        
    Returns:
        Path: Ruta al directorio de trabajo creado (sin incluir /output/)
        
    Example:
        >>> work_dir = _ensure_work_dir(
        ...     Path("project.zip"),
        ...     Path("/output"),
        ...     overwrite=True
        ... )
        >>> print(work_dir)
        /output/WI2CamtrapDP_project_20250123_143022
    """
    from datetime import datetime
    
    # Generar timestamp para nombre único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"WI2CamtrapDP_{Path(zip_path).stem}_{timestamp}"
    work_dir = Path(out_dir) / name
    output = work_dir / "output"
    
    # Limpiar si existe y overwrite=True
    if output.exists() and overwrite:
        for p in output.glob("*"):
            try:
                p.unlink()
            except IsADirectoryError:
                for q in p.glob("*"):
                    q.unlink(missing_ok=True)
                p.rmdir()
    
    # Crear estructura de directorios
    output.mkdir(parents=True, exist_ok=True)
    return work_dir


def _infer_field_type(series: pd.Series) -> str:
    """
    Infiere el tipo de dato de una columna para el schema JSON.
    
    Determina el tipo apropiado según el vocabulario de Table Schema
    (integer, number, boolean, string).
    
    Args:
        series: Serie de pandas a analizar
        
    Returns:
        str: Tipo inferido ("integer", "number", "boolean", "string")
        
    Note:
        Si falla la inferencia, retorna "string" como tipo por defecto.
    """
    try:
        if pd.api.types.is_integer_dtype(series):
            return "integer"
        if pd.api.types.is_float_dtype(series):
            return "number"
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        return "string"
    except Exception:
        return "string"


def _schema_from_df(df: pd.DataFrame):
    """
    Genera un schema básico JSON a partir de un DataFrame.
    
    Crea un diccionario con formato Table Schema que describe
    los campos del DataFrame (nombre y tipo de cada columna).
    
    Args:
        df: DataFrame del cual generar el schema
        
    Returns:
        dict: Schema en formato Table Schema con estructura:
              {"fields": [{"name": str, "type": str}, ...]}
              
    Example:
        >>> df = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})
        >>> schema = _schema_from_df(df)
        >>> schema
        {'fields': [{'name': 'id', 'type': 'integer'},
                    {'name': 'name', 'type': 'string'}]}
    """
    return {"fields": [{"name": str(c), "type": _infer_field_type(df[c])} for c in df.columns]}


def _build_datapackage_min(work_dir: Path,
                           dep_df: pd.DataFrame,
                           med_df: pd.DataFrame,
                           obs_df: pd.DataFrame,
                           projects: pd.DataFrame,
                           timezone_hint="America/Bogota",
                           schema_paths: dict | None = None):
    """
    Genera datapackage.json mínimo pero válido. Usa table-schemas locales si existen,
    si no, infiere con _schema_from_df.
    """
    # Función auxiliar para construir el array de licencias
    def _build_licenses_array(data_license: str, media_license: str) -> list:
        """
        Construye el array de licencias según el estándar Camtrap-DP
        """
        licenses = []
        
        # Normalizar licencias vacías o no válidas
        def normalize_license(lic_str: str) -> str:
            if not lic_str or str(lic_str).strip() == "" or str(lic_str).lower() in ["nan", "none"]:
                return "CC-BY-4.0"  # Valor por defecto
            lic_clean = str(lic_str).strip()
            
            # Mapeo de formatos comunes a estándar SPDX
            license_mapping = {
                "CC-BY": "CC-BY-4.0",
                "CC-BY-NC": "CC-BY-NC-4.0", 
                "CC-BY-SA": "CC-BY-SA-4.0",
                "CC-BY-NC-SA": "CC-BY-NC-SA-4.0",
                "CC0": "CC0-1.0",
                "Public Domain": "CC0-1.0"
            }
            
            return license_mapping.get(lic_clean, lic_clean)
        
        # Normalizar licencias
        data_lic_norm = normalize_license(data_license)
        media_lic_norm = normalize_license(media_license)
        
        # Agregar licencia de datos
        licenses.append({
            "name": data_lic_norm,
            "scope": "data"
        })
        
        # Agregar licencia de media
        licenses.append({
            "name": media_lic_norm,
            "scope": "media"
        })
        
        return licenses

    # Metadata del proyecto
    pkg_created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not projects.empty:
        name = projects.get("project_name", pd.Series(["wi-project"])).iloc[0]
        title = projects.get("project_name", pd.Series(["WI Project"])).iloc[0]
        desc = projects.get("project_objectives", pd.Series([""])).iloc[0]
        pid  = str(projects.get("project_id", pd.Series([""])).iloc[0])
        admin = projects.get("project_admin", pd.Series([""])).iloc[0]
        admin_email = projects.get("project_admin_email", pd.Series([""])).iloc[0]
        org = projects.get("project_admin_organization", pd.Series([""])).iloc[0]
        data_lic = projects.get("metadata_license", pd.Series([""])).iloc[0]
        img_lic  = projects.get("image_license", pd.Series([""])).iloc[0]
        capt_m   = projects.get("project_sensor_method", pd.Series([""])).iloc[0]
        capt_layout = projects.get("project_sensor_layout", pd.Series([""])).iloc[0]
        proj_type= projects.get("project_type", pd.Series([""])).iloc[0]
    else:
        name = "wi-project"
        title = "WI Project"
        desc = ""
        pid  = ""
        admin = ""
        admin_email = ""
        org = ""
        data_lic = ""
        img_lic  = ""
        capt_m   = ""
        capt_layout = ""
        proj_type= ""

    # schemas
    if schema_paths and all(Path(p).exists() for p in schema_paths.values()):
        with open(schema_paths["deployments"], "r", encoding="utf-8") as f:
            dep_schema = json.load(f)
        with open(schema_paths["media"], "r", encoding="utf-8") as f:
            med_schema = json.load(f)
        with open(schema_paths["observations"], "r", encoding="utf-8") as f:
            obs_schema = json.load(f)
    else:
        dep_schema = _schema_from_df(dep_df)
        med_schema = _schema_from_df(med_df)
        obs_schema = _schema_from_df(obs_df)

    pkg_name  = projects.get("project_name", pd.Series(["wi-project"])).iloc[0] if not projects.empty else "wi-project"
    pkg_title = projects.get("project_name", pd.Series(["WI Project"])).iloc[0] if not projects.empty else "WI Project"

    # Construir lista de captureMethod desde project_sensor_method y project_sensor_layout
    capture_methods = []
    if str(capt_m).strip():
        capture_methods.append(str(capt_m).strip())
    if str(capt_layout).strip() and str(capt_layout).strip() not in capture_methods:
        capture_methods.append(str(capt_layout).strip())
    if not capture_methods:
        capture_methods = ["activityDetection"]

    datapackage  = {
        "profile": "tabular-data-package",
        "name": _slugify_name(str(pkg_name)),   # ← SLUG (minúsculas, sin espacios/acentos)
        "title": str(pkg_title),
        "id": str(pid),
        "description": str(desc),
        "created": pkg_created,
        "mainContributorName": str(admin),
        "mainContributorEmail": str(admin_email),
        "organization": str(org),
        "licenses": _build_licenses_array(data_lic, img_lic),
        "captureMethod": capture_methods,
        "observationLevel": str(proj_type),
        "extras": {"timezone_hint": timezone_hint},
        # Recursos
        "resources": [
            {
                "name": "deployments",
                "profile": "tabular-data-resource",
                "path": "deployments.csv",
                "schema": dep_schema,
            },
            {
                "name": "media",
                "profile": "tabular-data-resource",
                "path": "media.csv",
                "schema": med_schema,
            },
            {
                "name": "observations",
                "profile": "tabular-data-resource",
                "path": "observations.csv",
                "schema": obs_schema,
            },
        ],
    }
    return datapackage 


def _make_result_zip(work_dir: Path, overwrite: bool = False) -> str:
    """
    Crea un archivo ZIP con los resultados del procesamiento Camtrap-DP.
    
    Empaqueta los archivos generados (CSVs y datapackage.json) en un ZIP
    para facilitar distribución y publicación.
    
    Args:
        work_dir: Directorio de trabajo que contiene la carpeta output/
        overwrite: Si True, sobrescribe el ZIP si ya existe
        
    Returns:
        str: Ruta completa del archivo ZIP creado
        
    Example:
        >>> zip_path = _make_result_zip(Path("/output/WI2CamtrapDP_project_20250123"))
        >>> print(zip_path)
        /output/WI2CamtrapDP_project_20250123/WI2CamtrapDP_project_20250123.zip
        
    Note:
        El ZIP contendrá la carpeta output/ con todos los archivos generados.
        Usa compresión DEFLATE para reducir tamaño.
    """
    zip_path = work_dir / f"{work_dir.name}.zip"
    
    # Eliminar ZIP existente si overwrite=True
    if zip_path.exists() and overwrite:
        zip_path.unlink()
    
    # Crear ZIP con compresión
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fn in ["deployments.csv", "media.csv", "observations.csv", "datapackage.json"]:
            p = work_dir / "output" / fn
            if p.exists() and p.is_file():
                zf.write(p, arcname=f"output/{fn}")
    
    return str(zip_path)


# ============================================================================
# API PRINCIPAL: PROCESO DE CONVERSIÓN
# ============================================================================

def process_zip(
    zip_path: Path,
    out_dir: Path,
    logger=print,
    report_progress=_progress,
    validate: bool = True,
    make_zip: bool = True,
    overwrite: bool = False,
    timezone_hint: str = "America/Bogota",
):
    """
    Procesa una exportación de Wildlife Insights y la convierte a Camtrap-DP v1.0.2.
    
    Función principal que orquesta todo el flujo de conversión: extracción de datos,
    normalización, construcción de tablas Camtrap-DP, validación y empaquetado.
    
    Flujo de procesamiento:
        1. Validación de entrada y extracción de CSVs del ZIP
        2. Validación temprana de completitud de datos ("No CV Result", etc.)
        3. Normalización de timestamps y campos taxonómicos
        4. Construcción de deployments.csv (despliegues de cámaras)
        5. Construcción de media.csv (archivos multimedia)
        6. Construcción de observations.csv (registros de observaciones)
        7. Generación de datapackage.json con metadatos
        8. Validación con Frictionless Framework (opcional)
        9. Creación de ZIP final (opcional)
    
    Args:
        zip_path: Ruta al archivo ZIP de exportación de Wildlife Insights (proyecto)
        out_dir: Directorio base donde se creará la carpeta de resultados
        logger: Función callback para mensajes de log (recibe str)
        report_progress: Función callback para progreso (recibe int, str)
        validate: Si True, valida el datapackage con Frictionless Framework
        make_zip: Si True, crea un ZIP final con todos los archivos generados
        overwrite: Si True, sobrescribe directorios/archivos existentes
        timezone_hint: Zona horaria por defecto para timestamps naive
        
    Returns:
        str: Ruta del directorio de trabajo creado (WI2CamtrapDP_<nombre>_<timestamp>)
        
    Raises:
        FileNotFoundError: Si el archivo ZIP no existe
        RuntimeError: Si hay errores de validación de datos o campos requeridos vacíos
        
    Example:
        >>> work_dir = process_zip(
        ...     zip_path=Path("export.zip"),
        ...     out_dir=Path("/output"),
        ...     validate=True,
        ...     make_zip=True,
        ...     timezone_hint="America/Bogota"
        ... )
        >>> print(f"Resultados en: {work_dir}/output/")
        
    Note:
        - Solo procesa exportaciones de PROYECTO (no iniciativas de Wildlife Insights)
        - Requiere que los datos tengan identificaciones taxonómicas completas
        - Los timestamps se convierten automáticamente a ISO 8601 UTC
        - La validación con Frictionless es opcional pero recomendada
    """
    zip_path = Path(zip_path)
    out_dir = Path(out_dir)

    _log(logger, "[INFO] Iniciando procesamiento…")
    _progress(report_progress, 1, "Leyendo ZIP…")

    if not zip_path.exists():
        raise FileNotFoundError(f"No se encuentra el ZIP: {zip_path}")

    # ========================================================================
    # EXTRACCIÓN DE DATOS DESDE ZIP
    # ========================================================================
    # Cargar los 4 archivos CSV principales de Wildlife Insights:
    # - projects.csv: Metadatos del proyecto
    # - cameras.csv: Información de cámaras trampa
    # - deployments.csv: Despliegues de cámaras en el campo
    # - images_*.csv: Registros de imágenes y observaciones
    with zipfile.ZipFile(zip_path, "r") as zf:
        projects   = _load_csv_from_zip(zf, "projects")
        cameras    = _load_csv_from_zip(zf, "cameras")
        deploys    = _load_csv_from_zip(zf, "deploy")    # deployments.csv
        images     = _load_csv_from_zip(zf, "images")
    
    # ========================================================================
    # VALIDACIÓN TEMPRANA: COMPLETITUD DE IDENTIFICACIONES TAXONÓMICAS
    # ========================================================================
    # Verificar que no haya registros con "No CV Result" en campos taxonómicos.
    # Este valor indica que las identificaciones están incompletas en Wildlife Insights.
    _progress(report_progress, 5, "Validando integridad de datos...")
    
    # Encontrar el nombre del archivo images_*.csv en el ZIP
    images_filename = "images_*.csv"  # valor por defecto
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                base_name = info.filename.lower()
                if base_name.endswith(".csv") and "images_" in base_name:
                    images_filename = info.filename
                    break
    except Exception:
        pass
    
    # Verificar "No CV Result" en multiple campos del archivo images
    no_cv_issues = []
    if not images.empty:
        # Campos a verificar para "No CV Result"
        fields_to_check = ["common_name", "genus", "species", "family", "order"]
        
        for field in fields_to_check:
            if field in images.columns:
                # Buscar registros con "No CV Result" (case-insensitive)
                mask = images[field].astype(str).str.lower().str.strip() == "no cv result"
                if mask.any():
                    problematic_rows = images[mask]
                    for _, row in problematic_rows.iterrows():
                        filename_value = row.get("filename", "N/A")
                        no_cv_issues.append({
                            "field": field,
                            "filename": filename_value,
                            "row_index": row.name + 1  # +1 para mostrar número de fila (1-indexed)
                        })
    
    # Si hay problemas, detener el procesamiento y mostrar error detallado
    if no_cv_issues:
        # Agrupar por campo para mejor legibilidad
        issues_by_field = {}
        for issue in no_cv_issues:
            field = issue["field"]
            if field not in issues_by_field:
                issues_by_field[field] = []
            issues_by_field[field].append(issue)
        
        # Construir mensaje de error detallado (más conciso)
        error_message = f"⚠️ VALIDACIÓN DE TAXONOMÍA FALLIDA\n\n"
        error_message += f"Se encontraron {len(no_cv_issues)} registros con valor 'No CV Result' en '{images_filename}'.\n\n"
        error_message += "CAUSA:\n"
        error_message += "Este valor indica que las identificaciones taxonómicas están incompletas en Wildlife Insights.\n\n"
        error_message += "REGISTROS AFECTADOS:\n"
        error_message += "=" * 50 + "\n"
        
        for field, field_issues in issues_by_field.items():
            error_message += f"\nCampo '{field}' ({len(field_issues)} registros):\n"
            for i, issue in enumerate(field_issues[:8]):  # Mostrar máximo 8 por campo
                error_message += f"  • Fila {issue['row_index']}: {issue['filename']}\n"
            if len(field_issues) > 8:
                error_message += f"  ... y {len(field_issues) - 8} más\n"
        
        error_message += "\n" + "=" * 50
        error_message += f"\nTOTAL: {len(no_cv_issues)} registros requieren identificación\n"
        error_message += "\nACCIÓN REQUERIDA:\n"
        error_message += "1. Ingresar a Wildlife Insights y completar las identificaciones taxonómicas\n"
        error_message += "2. Asegurarse de que todos los campos (common_name, genus, species, etc.) estén completos\n"
        error_message += "3. Exportar nuevamente el proyecto\n"
        error_message += "4. Reintentar el procesamiento con el archivo actualizado"
        
        # Log resumido para evitar duplicación
        _log(logger, f"[ERROR] Validación de taxonomía fallida: {len(no_cv_issues)} registros con 'No CV Result'")
        raise RuntimeError(error_message)

    # ========================================================================
    # NORMALIZACIÓN DE DATOS
    # ========================================================================
    # Preparar datos para conversión a formato Camtrap-DP
    _progress(report_progress, 8, "Normalizando timestamps y campos…")

    # ------------------------------------------------------------------------
    # 1. Zona horaria por deployment
    # ------------------------------------------------------------------------
    # Asegurar que cada deployment tenga una zona horaria definida
    if "timezone" not in deploys.columns:
        deploys["timezone"] = timezone_hint

    # ------------------------------------------------------------------------
    # 2. Conversión de timestamps de deployment a ISO UTC
    # ------------------------------------------------------------------------
    # Normalizar fechas de inicio/fin de despliegues a formato estándar ISO 8601 UTC
    deploys["deploymentStart"] = [
        to_iso_utc(a, tz_hint=b) for a, b in zip(deploys.get("start_date", ""), deploys["timezone"])
    ]
    deploys["deploymentEnd"] = [
        to_iso_utc(a, tz_hint=b) for a, b in zip(deploys.get("end_date", ""), deploys["timezone"])
    ]

    # ------------------------------------------------------------------------
    # 3. Timestamps ISO por imagen según zona horaria del deployment
    # ------------------------------------------------------------------------
    # Crear mapeo deployment_id → timezone para procesar imágenes
    dep_tz = {}
    if "deployment_id" in deploys.columns:
        dep_tz = deploys.set_index("deployment_id")["timezone"].to_dict()
    
    # Convertir timestamp de cada imagen usando la zona horaria de su deployment
    images["timestamp_iso"] = images.apply(
        lambda r: to_iso_utc(r.get("timestamp"),
                             tz_hint=dep_tz.get(r.get("deployment_id"), timezone_hint)),
        axis=1
    )

    # ------------------------------------------------------------------------
    # 4. Normalización de nombres científicos
    # ------------------------------------------------------------------------
    # Formatear genus (capitalizado) y species (minúsculas)
    if "genus" in images.columns:
        images["genus"] = images["genus"].fillna("").str.strip().str.capitalize()
    if "species" in images.columns:
        images["species"] = images["species"].fillna("").str.strip().str.lower()
    
    # Construir nombre científico completo: "Genus species"
    images["scientific_name_norm"] = (
        images.get("genus", "").fillna("") + " " + images.get("species", "").fillna("")
    ).str.strip()

    # ========================================================================
    # CONSTRUCCIÓN DE DEPLOYMENTS.CSV
    # ========================================================================
    _progress(report_progress, 20, "Construyendo deployments.csv…")

    dep_out = pd.DataFrame()
    dep_out["deploymentID"] = deploys.get("deployment_id", pd.Series(dtype=object))
    dep_out["latitude"] = pd.to_numeric(deploys.get("latitude"), errors="coerce")
    dep_out["longitude"] = pd.to_numeric(deploys.get("longitude"), errors="coerce")
    dep_out["deploymentStart"] = deploys["deploymentStart"]
    dep_out["deploymentEnd"] = deploys["deploymentEnd"]

    # Limpiar rangos inválidos
    dep_out.loc[(dep_out["latitude"] < -90) | (dep_out["latitude"] > 90), "latitude"] = np.nan
    dep_out.loc[(dep_out["longitude"] < -180) | (dep_out["longitude"] > 180), "longitude"] = np.nan

    include_if_any(dep_out, "locationName", deploys.get("placename"))

    def _to_location_id(val):
        if pd.isna(val) or str(val).strip() == "":
            return pd.NA
        slug = re.sub(r"[^a-z0-9]+", "-", str(val).strip().lower()).strip("-")
        return f"loc-{slug}"[:64]

    if "placename" in deploys.columns:
        include_if_any(dep_out, "locationID", deploys["placename"].apply(_to_location_id))

    include_if_any(dep_out, "cameraID", deploys.get("camera_id"))

    # cameraModel desde cameras
    cam = cameras.copy()
    if "manufacturer" not in cam.columns and "make" in cam.columns:
        cam["manufacturer"] = cam["make"]

    if {"camera_id", "model"}.issubset(cam.columns) and "camera_id" in deploys.columns:
        tmp = cam[["camera_id", "manufacturer", "model"]].copy()
        merged = deploys[["deployment_id", "camera_id"]].merge(tmp, on="camera_id", how="left")
        cam_model = (
            merged.get("manufacturer", "").fillna("") + "-" + merged.get("model", "").fillna("")
        ).str.strip("-")
        cam_model = cam_model.replace({"-": ""}, regex=False)
        include_if_any(dep_out, "cameraModel", cam_model)

    # Mapeo de cameraHeight desde sensor_height y height_other (Wildlife Insights → Camtrap-DP)
    def _map_camera_height(row):
        """
        Mapea sensor_height (categorías) a valores numéricos en centímetros para cameraHeight.
        Si sensor_height es "Other", intenta extraer valor numérico de height_other.
        
        Mapeo (entrada → salida en cm):
        - "Chest height" → 100 cm
        - "Knee height" → 50 cm
        - "Other" → extraer número de height_other (ej: "120 cm" → 120)
        - "Unknown" → vacío (pd.NA)
        - Vacío/NaN → vacío (pd.NA)
        """
        sensor_height = row.get("sensor_height")
        height_other = row.get("height_other")
        
        # Manejar valores vacíos o NaN en sensor_height
        if pd.isna(sensor_height):
            return pd.NA
        
        # Normalizar el valor de entrada (eliminar espacios y convertir a minúsculas)
        val_normalized = str(sensor_height).strip().lower()
        
        # Mapeo de categorías a valores en centímetros
        if val_normalized == "chest height":
            return 100
        elif val_normalized == "knee height":
            return 50
        elif val_normalized == "other":
            # Intentar extraer valor numérico de height_other
            if pd.isna(height_other):
                return pd.NA
            
            height_other_str = str(height_other).strip()
            if not height_other_str:
                return pd.NA
            
            # Buscar primer número en el texto usando regex
            import re
            match = re.search(r'\d+', height_other_str)
            if match:
                try:
                    return int(match.group())
                except (ValueError, TypeError):
                    return pd.NA
            else:
                # Solo contiene texto/palabras, no números → vacío
                return pd.NA
        elif val_normalized in ["unknown", ""]:
            return pd.NA
        else:
            # Valor no reconocido → vacío
            return pd.NA
    
    if "sensor_height" in deploys.columns:
        camera_heights = deploys.apply(_map_camera_height, axis=1)
        include_if_any(dep_out, "cameraHeight", camera_heights)

    # Verificación requerida
    for col in ["deploymentID", "latitude", "longitude", "deploymentStart", "deploymentEnd"]:
        if dep_out[col].isna().sum() > 0:
            num_missing = dep_out[col].isna().sum()
            total_rows = len(dep_out)
            
            # Mensajes específicos según el campo
            if col == "deploymentStart":
                error_detail = (
                    f"⚠️ DATOS INCOMPLETOS EN DESPLIEGUES\n\n"
                    f"Se detectaron {num_missing} de {total_rows} despliegues sin fecha de inicio (deploymentStart).\n\n"
                    f"CAUSA PROBABLE:\n"
                    f"• El campo 'start_date' en deployments.csv contiene valores vacíos o fechas inválidas\n"
                    f"• Formato de fecha incorrecto en Wildlife Insights\n\n"
                    f"ACCIÓN REQUERIDA:\n"
                    f"1. Revisar el archivo deployments.csv en Wildlife Insights\n"
                    f"2. Completar las fechas de inicio (start_date) para todos los despliegues\n"
                    f"3. Verificar que las fechas tengan formato válido (YYYY-MM-DD HH:MM:SS)\n"
                    f"4. Exportar nuevamente el proyecto y reintentar el procesamiento"
                )
            elif col == "deploymentEnd":
                error_detail = (
                    f"⚠️ DATOS INCOMPLETOS EN DESPLIEGUES\n\n"
                    f"Se detectaron {num_missing} de {total_rows} despliegues sin fecha de fin (deploymentEnd).\n\n"
                    f"CAUSA PROBABLE:\n"
                    f"• El campo 'end_date' en deployments.csv contiene valores vacíos o fechas inválidas\n"
                    f"• Despliegues aún activos en Wildlife Insights\n\n"
                    f"ACCIÓN REQUERIDA:\n"
                    f"1. Revisar el archivo deployments.csv en Wildlife Insights\n"
                    f"2. Completar las fechas de fin (end_date) para los despliegues finalizados\n"
                    f"3. Si el despliegue está activo, asignar una fecha estimada de fin\n"
                    f"4. Exportar nuevamente el proyecto y reintentar el procesamiento"
                )
            elif col in ["latitude", "longitude"]:
                coord_type = "latitud" if col == "latitude" else "longitud"
                error_detail = (
                    f"⚠️ DATOS INCOMPLETOS EN COORDENADAS\n\n"
                    f"Se detectaron {num_missing} de {total_rows} despliegues sin {coord_type} válida.\n\n"
                    f"CAUSA PROBABLE:\n"
                    f"• El campo '{col}' en deployments.csv contiene valores vacíos\n"
                    f"• Coordenadas fuera del rango válido ({'-90 a 90' if col == 'latitude' else '-180 a 180'} grados)\n\n"
                    f"ACCIÓN REQUERIDA:\n"
                    f"1. Revisar las coordenadas de los despliegues en Wildlife Insights\n"
                    f"2. Completar las coordenadas faltantes con valores GPS válidos\n"
                    f"3. Verificar que las coordenadas estén en formato decimal (no grados/minutos/segundos)\n"
                    f"4. Exportar nuevamente el proyecto y reintentar el procesamiento"
                )
            else:  # deploymentID
                error_detail = (
                    f"⚠️ DATOS INCOMPLETOS EN IDENTIFICADORES\n\n"
                    f"Se detectaron {num_missing} de {total_rows} despliegues sin identificador (deploymentID).\n\n"
                    f"CAUSA PROBABLE:\n"
                    f"• El campo 'deployment_id' en deployments.csv contiene valores vacíos\n\n"
                    f"ACCIÓN REQUERIDA:\n"
                    f"1. Revisar el archivo deployments.csv en Wildlife Insights\n"
                    f"2. Asignar identificadores únicos a todos los despliegues\n"
                    f"3. Exportar nuevamente el proyecto y reintentar el procesamiento"
                )
            
            raise RuntimeError(error_detail)

    # ===================== MEDIA =====================
    _progress(report_progress, 40, "Construyendo media.csv…")

    sort_cols = [c for c in ["image_id", "timestamp_iso", "filename", "deployment_id"] if c in images.columns]
    img_sorted = images.sort_values(sort_cols).copy() if sort_cols else images.copy()

    counts = img_sorted.get("image_id", pd.Series(dtype=object)).value_counts(dropna=False)
    dup_ids = set(counts[counts > 1].index.tolist())
    within, media_ids = {}, []
    if "image_id" in img_sorted.columns:
        for _, row in img_sorted.iterrows():
            iid = row["image_id"]
            if iid in dup_ids:
                within[iid] = within.get(iid, 0) + 1
                media_ids.append(f"{iid}_{within[iid]:02d}")
            else:
                media_ids.append(iid)
        img_sorted["mediaID"] = media_ids
    else:
        img_sorted["mediaID"] = [f"m{i:06d}" for i in range(1, len(img_sorted) + 1)]

    med_out = pd.DataFrame()
    med_out["mediaID"] = img_sorted["mediaID"]
    med_out["deploymentID"] = img_sorted.get("deployment_id", pd.Series([pd.NA] * len(img_sorted)))
    med_out["timestamp"] = img_sorted.get("timestamp_iso", pd.Series([pd.NA] * len(img_sorted)))
    med_out["filePath"] = img_sorted.get("location", pd.Series([pd.NA] * len(img_sorted)))
    if "filename" in img_sorted.columns:
        med_out["fileMediatype"] = img_sorted["filename"].astype(str).apply(ext_to_mediatype)
        include_if_any(med_out, "fileName", img_sorted["filename"])
    else:
        med_out["fileMediatype"] = "application/octet-stream"
    med_out["filePublic"] = False
    
    # Mapear favorite desde highlighted
    if "highlighted" in img_sorted.columns:
        include_if_any(med_out, "favorite", img_sorted["highlighted"])

    cap_value = pd.NA
    if "project_sensor_method" in projects.columns:
        raw = projects["project_sensor_method"].dropna().astype(str).str.strip()
        if not raw.empty:
            cap_value = map_capture_method_from_text(raw.iloc[0])
    if pd.isna(cap_value):
        cap_value = "activityDetection"
    med_out["captureMethod"] = pd.Series(cap_value, index=med_out.index)

    # Verificaciones
    for col in ["mediaID", "deploymentID", "timestamp", "filePath", "fileMediatype", "filePublic"]:
        if med_out[col].isna().sum() > 0:
            num_missing = med_out[col].isna().sum()
            total_rows = len(med_out)
            
            # Mensajes específicos según el campo
            if col == "timestamp":
                error_detail = (
                    f"⚠️ DATOS INCOMPLETOS EN ARCHIVOS MULTIMEDIA\n\n"
                    f"Se detectaron {num_missing} de {total_rows} registros sin marca de tiempo (timestamp).\n\n"
                    f"CAUSA PROBABLE:\n"
                    f"• El campo 'timestamp' en images_*.csv contiene valores vacíos o fechas inválidas\n"
                    f"• Metadatos EXIF de las imágenes incompletos o corruptos\n"
                    f"• Formato de fecha/hora incorrecto en Wildlife Insights\n\n"
                    f"ACCIÓN REQUERIDA:\n"
                    f"1. Revisar el archivo images_*.csv en Wildlife Insights\n"
                    f"2. Verificar que todas las imágenes tengan timestamps válidos\n"
                    f"3. Confirmar que el formato sea correcto (YYYY-MM-DD HH:MM:SS)\n"
                    f"4. Exportar nuevamente el proyecto y reintentar el procesamiento"
                )
            elif col == "deploymentID":
                error_detail = (
                    f"⚠️ DATOS INCOMPLETOS EN ARCHIVOS MULTIMEDIA\n\n"
                    f"Se detectaron {num_missing} de {total_rows} registros sin identificador de despliegue.\n\n"
                    f"CAUSA PROBABLE:\n"
                    f"• El campo 'deployment_id' en images_*.csv contiene valores vacíos\n"
                    f"• Imágenes no asociadas a ningún despliegue en Wildlife Insights\n\n"
                    f"ACCIÓN REQUERIDA:\n"
                    f"1. Revisar el archivo images_*.csv en Wildlife Insights\n"
                    f"2. Asociar todas las imágenes a sus despliegues correspondientes\n"
                    f"3. Exportar nuevamente el proyecto y reintentar el procesamiento"
                )
            elif col == "filePath":
                error_detail = (
                    f"⚠️ DATOS INCOMPLETOS EN ARCHIVOS MULTIMEDIA\n\n"
                    f"Se detectaron {num_missing} de {total_rows} registros sin ruta de archivo.\n\n"
                    f"CAUSA PROBABLE:\n"
                    f"• El campo 'location' en images_*.csv contiene valores vacíos\n"
                    f"• URLs de almacenamiento no generadas en Wildlife Insights\n\n"
                    f"ACCIÓN REQUERIDA:\n"
                    f"1. Verificar que todas las imágenes estén correctamente cargadas en Wildlife Insights\n"
                    f"2. Exportar nuevamente el proyecto después de validar las rutas\n"
                    f"3. Reintentar el procesamiento"
                )
            else:
                error_detail = (
                    f"⚠️ DATOS INCOMPLETOS EN ARCHIVOS MULTIMEDIA\n\n"
                    f"Se detectaron {num_missing} de {total_rows} registros con el campo '{col}' vacío o inválido.\n\n"
                    f"ACCIÓN REQUERIDA:\n"
                    f"1. Revisar el archivo images_*.csv en Wildlife Insights\n"
                    f"2. Completar los datos faltantes\n"
                    f"3. Exportar nuevamente el proyecto y reintentar el procesamiento"
                )
            
            raise RuntimeError(error_detail)
    if not med_out["mediaID"].is_unique:
        dups = med_out.loc[med_out["mediaID"].duplicated(), "mediaID"].unique()[:10]
        raise RuntimeError(f"MEDIA: mediaID duplicados: {list(dups)}")

    # ===================== OBSERVATIONS =====================
    _progress(report_progress, 70, "Construyendo observations.csv…")

    dep_tz_map = dep_tz  # ya calculado arriba
    img_for_obs = img_sorted.copy()

    obs_out = pd.DataFrame()
    obs_out["observationID"] = "obs_" + img_for_obs["mediaID"].astype(str)
    obs_out["deploymentID"] = img_for_obs.get("deployment_id", pd.Series([pd.NA] * len(img_for_obs)))
    obs_out["mediaID"] = img_for_obs["mediaID"]

    has_start = "start_time" in img_for_obs.columns
    has_end = "end_time" in img_for_obs.columns

    def _to_evt_iso(row):
        tz_hint = dep_tz_map.get(row.get("deployment_id"), timezone_hint)
        if has_start:
            start_raw = row.get("start_time")
            start_iso = to_iso_utc(start_raw, tz_hint=tz_hint) if (start_raw not in [None, ""] and str(start_raw).strip() != "") else row.get("timestamp_iso")
        else:
            start_iso = row.get("timestamp_iso")
        if has_end:
            end_raw = row.get("end_time")
            end_iso = to_iso_utc(end_raw, tz_hint=tz_hint) if (end_raw not in [None, ""] and str(end_raw).strip() != "") else row.get("timestamp_iso")
        else:
            end_iso = row.get("timestamp_iso")
        return start_iso, end_iso

    _evt = img_for_obs.apply(lambda r: _to_evt_iso(r), axis=1, result_type="expand")
    obs_out["eventStart"] = _evt[0]
    obs_out["eventEnd"] = _evt[1]

    obs_out["observationLevel"] = "media"
    
    # Nueva lógica para observationType y scientificName
    classification_results = img_for_obs.apply(classify_observation_and_scientific_name, axis=1, result_type="expand")
    obs_out["observationType"] = classification_results[0]
    obs_out["scientificName"] = classification_results[1]

    include_if_any(obs_out, "vernacularName", img_for_obs.get("common_name"))

    # Requeridos
    for col in ["observationID", "deploymentID", "eventStart", "eventEnd", "observationLevel", "observationType"]:
        if obs_out[col].isna().sum() > 0:
            raise RuntimeError(f"OBSERVATIONS: el campo requerido '{col}' tiene vacíos.")

    # ===================== Escritura + datapackage =====================
    _progress(report_progress, 85, "Escribiendo archivos (CSV y datapackage.json)…")

    work_dir = _ensure_work_dir(zip_path, out_dir, overwrite=overwrite)
    output_dir = work_dir / "output"

    # Alinear a schemas locales si existen
    schema_dir = _schemas_dir()
    schema_paths = None
    if schema_dir:
        dep_schema_path = schema_dir / "deployments-table-schema.json"
        med_schema_path = schema_dir / "media-table-schema.json"
        obs_schema_path = schema_dir / "observations-table-schema.json"
        if dep_schema_path.exists() and med_schema_path.exists() and obs_schema_path.exists():
            dep_out = _align_df_to_local_schema(dep_out, dep_schema_path)
            med_out = _align_df_to_local_schema(med_out, med_schema_path)
            obs_out = _align_df_to_local_schema(obs_out, obs_schema_path)
            schema_paths = {
                "deployments": str(dep_schema_path),
                "media": str(med_schema_path),
                "observations": str(obs_schema_path),
            }

    dep_path = output_dir / "deployments.csv"
    med_path = output_dir / "media.csv"
    obs_path = output_dir / "observations.csv"

    dep_out.to_csv(dep_path, index=False, encoding="utf-8")
    med_out.to_csv(med_path, index=False, encoding="utf-8")
    obs_out.to_csv(obs_path, index=False, encoding="utf-8")
    _log(logger, f"[INFO] Escrito: {dep_path}")
    _log(logger, f"[INFO] Escrito: {med_path}")
    _log(logger, f"[INFO] Escrito: {obs_path}")

    # datapackage.json
    dp_obj = _build_datapackage_min(
        work_dir=work_dir,
        dep_df=dep_out,
        med_df=med_out,
        obs_df=obs_out,
        projects=projects,
        timezone_hint=timezone_hint,
        schema_paths=schema_paths,
    )
    dp_path = output_dir / "datapackage.json"
    with open(dp_path, "w", encoding="utf-8") as f:
        json.dump(dp_obj, f, ensure_ascii=False, indent=2)
    _log(logger, f"[INFO] Escrito: {dp_path}")

    # ===================== Validación (opcional) — Frictionless 5.x =====================
    if validate:
        try:
            import frictionless as fr  # v5.18.1
            _progress(report_progress, 92, "Validando con Frictionless…")

            # Opción A (sencilla): detecta automáticamente que es un Package por el datapackage.json
            report = fr.validate(str(dp_path))

            # # Opción B (equivalente):
            # pkg = fr.Package(str(dp_path))
            # report = pkg.validate()

            if report.valid:
                _log(logger, "[INFO] Datapackage válido (Frictionless).")
            else:
                # Construir un resumen legible de los errores
                msgs = []
                for task in getattr(report, "tasks", []):
                    res_name = getattr(task.resource, "name", getattr(task.resource, "path", "resource"))
                    for err in getattr(task, "errors", []):
                        etype = getattr(err, "type", "error")
                        note  = getattr(err, "note", "")
                        fld   = getattr(err, "fieldName", None)
                        rowp  = getattr(err, "rowPosition", None)
                        where = []
                        if fld:  where.append(f"field={fld}")
                        if rowp: where.append(f"row={rowp}")
                        where_s = f" ({', '.join(where)})" if where else ""
                        msgs.append(f"{res_name}: {etype}{where_s} — {note}")
                if not msgs:
                    msgs = [str(report)]
                _log(logger, "[WARN] Validación con Frictionless reporta issues: " + "; ".join(msgs[:10]))

        except Exception as ex:
            _log(logger, f"[WARN] Validación saltada: {ex!r}")


    # ZIP final (opcional)
    if make_zip:
        _progress(report_progress, 95, "Creando ZIP final…")
        zip_final = _make_result_zip(work_dir, overwrite=overwrite)
        _log(logger, f"[INFO] ZIP final: {zip_final}")

    _progress(report_progress, 100, "Proceso completado.")

    # Verificación final de artefactos
    missing = [p.name for p in [dep_path, med_path, obs_path, dp_path] if (not p.exists()) or p.stat().st_size == 0]
    if missing:
        raise RuntimeError(f"Artefactos no creados o vacíos: {missing}")

    _log(logger, "[OK] Proceso completado.")
    return str(work_dir)
