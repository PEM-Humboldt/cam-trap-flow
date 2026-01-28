"""
Img2WI - Motor de Procesamiento de Videos de Cámaras Trampa
==================================================================

Módulo backend encargado de la lógica de extracción de imágenes desde archivos de video.
Implementa dos estrategias de procesamiento:
    1. Biblioteca wiutils (optimizada para archivos .MP4 de cámaras trampa)
    2. FFmpeg directo (para formatos .AVI, .MOV o como fallback)

Características principales:
    - Detección automática de FFmpeg embebido o del sistema
    - Extracción de frames con tasa configurable (fps basada en offset)
    - Preservación de metadatos temporales de los videos
    - Nomenclatura sistemática: <nombre_video>_XXXXXX.jpg
    - Detección de duración de videos con ffprobe
    - Manejo robusto de errores y fallbacks automáticos
    - Soporte para estructura de carpetas única de salida
    - Renombrado inteligente evitando colisiones de nombres

Flujo de procesamiento:
    1. Localizar binarios de FFmpeg/FFprobe
    2. Escanear videos en carpeta de entrada
    3. Por cada video:
       a. Obtener duración y timestamp
       b. Intentar extracción con wiutils (MP4)
       c. Si falla, usar FFmpeg como fallback
       d. Renombrar imágenes generadas con nomenclatura estándar
    4. Reportar progreso y estadísticas

Módulo: processor.py (Backend de procesamiento)
Autor: Cristian C. Acevedo
Organización: Instituto Humboldt - Red OTUS
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
Licencia: Ver THIRD_PARTY_NOTICES.txt
"""

import os
import sys
import time
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import wiutils


# ==============================================================================
# SECCIÓN 1: LOCALIZACIÓN DE BINARIOS FFMPEG/FFPROBE
# ==============================================================================
# Esta sección contiene funciones para localizar FFmpeg y FFprobe en diferentes
# escenarios: ejecución desde código fuente, ejecutable PyInstaller (one-file),
# o instalación del sistema.

def _find_ffmpeg() -> str:
    """
    Localiza el ejecutable de FFmpeg en múltiples ubicaciones.
    
    Estrategia de búsqueda:
        1. Si está empaquetado con PyInstaller (_MEIPASS), busca en el directorio temporal
        2. Si no, busca relativo al script actual (app/bin/ffmpeg.exe)
        3. Como último recurso, busca en el PATH del sistema
    
    Returns:
        str: Ruta completa al ejecutable de FFmpeg, o cadena vacía si no se encuentra
    """
    exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        for rel in (exe, Path("bin") / exe):
            cand = Path(meipass) / rel
            if cand.exists():
                return str(cand)
    base = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
    for rel in (Path("bin") / exe, Path(exe)):
        cand = base / rel
        if cand.exists():
            return str(cand)
    return shutil.which(exe) or ""


def _find_ffprobe() -> str:
    """
    Localiza el ejecutable de FFprobe usando la misma estrategia que _find_ffmpeg().
    
    FFprobe se utiliza para extraer metadatos de los videos (duración, codec, etc.)
    sin necesidad de procesarlos completamente.
    
    Returns:
        str: Ruta completa al ejecutable de FFprobe, o cadena vacía si no se encuentra
    """
    exe = "ffprobe.exe" if os.name == "nt" else "ffprobe"
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        for rel in (exe, Path("bin") / exe):
            cand = Path(meipass) / rel
            if cand.exists():
                return str(cand)
    base = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
    for rel in (Path("bin") / exe, Path(exe)):
        cand = base / rel
        if cand.exists():
            return str(cand)
    return shutil.which(exe) or ""


def _fps_from_offset(offset) -> float:
    """
    Convierte el offset (segundos entre imágenes) a frames por segundo (fps).
    
    Args:
        offset: Segundos entre cada imagen extraída (ej: 1 = una imagen por segundo)
    
    Returns:
        float: Frames por segundo para FFmpeg. Si offset=1, retorna 1.0 fps
        
    Ejemplos:
        offset=0.5 -> 2.0 fps (2 imágenes por segundo)
        offset=1   -> 1.0 fps (1 imagen por segundo)
        offset=2   -> 0.5 fps (1 imagen cada 2 segundos)
    """
    try:
        if offset is None:
            return 1.0
        off = float(offset)
        return 1.0 / off if off > 0 else 1.0
    except Exception:
        return 1.0


# ==============================================================================
# SECCIÓN 2: FUNCIONES DE EXTRACCIÓN DE IMÁGENES
# ==============================================================================
# Implementaciones de las dos estrategias de extracción:
# - FFmpeg: Herramienta universal de procesamiento de video
# - wiutils: Biblioteca especializada para archivos de cámaras trampa

def _extract_with_ffmpeg(ffmpeg_bin: str, video_path: Path, out_dir: Path,
                         fps: float, update_status=None) -> bool:
    """
    Extrae frames de un video usando FFmpeg con filtro de tasa de frames variable.
    
    Comando FFmpeg utilizado:
        -vsync vfr: Variable frame rate (extrae solo frames únicos)
        -vf fps=X: Filtro para especificar la tasa de extracción
    
    Args:
        ffmpeg_bin: Ruta al ejecutable de FFmpeg
        video_path: Ruta del archivo de video a procesar
        out_dir: Directorio donde se guardarán las imágenes
        fps: Frames por segundo a extraer
        update_status: Función callback opcional para reportar el progreso
    
    Returns:
        bool: True si la extracción fue exitosa, False en caso contrario
    """
    try:
        if not ffmpeg_bin or not Path(ffmpeg_bin).exists():
            update_status and update_status(f"⚠️ FFmpeg no encontrado. Ruta: '{ffmpeg_bin}'")
            return False

        out_dir.mkdir(parents=True, exist_ok=True)
        before = {p.name for p in out_dir.glob("*")
                  if p.suffix.lower() in (".jpg", ".jpeg", ".png")}

        video_stem = Path(video_path).stem
        pattern = out_dir / f"{video_stem}_%06d.jpg"

        cmd = [
            ffmpeg_bin, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-fflags", "+genpts", "-i", str(video_path),
            "-vsync", "vfr", "-vf", f"fps={fps}", str(pattern),
        ]
        creationflags = 0x08000000 if os.name == "nt" else 0
        subprocess.run(cmd, check=True, capture_output=True, creationflags=creationflags)

        produced = [p for p in out_dir.glob("*")
                    if p.name not in before and p.suffix.lower() in (".jpg", ".jpeg", ".png")]
        if not produced:
            update_status and update_status("⚠️ FFmpeg se ejecutó pero no produjo imágenes.")
            return False
        return True

    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
        update_status and update_status(f"❌ FFmpeg falló con '{video_path.name}'. Código: {e.returncode}. {msg[:400]}")
        return False
    except Exception as e:
        update_status and update_status(f"❌ Error inesperado con FFmpeg: {e}")
        return False


def _extract_with_wiutils(video_path: Path, out_dir: Path, timestamp: str, offset) -> bool:
    """
    Extrae frames usando la biblioteca wiutils, especializada para cámaras trampa.
    
    wiutils está optimizado para archivos .MP4 de cámaras trampa y preserva
    mejor los metadatos temporales originales del video.
    
    Args:
        video_path: Ruta del archivo de video a procesar
        out_dir: Directorio de salida para las imágenes
        timestamp: Timestamp base del video (formato: MM-DD-YYYY HH:MM:SS)
        offset: Segundos entre cada imagen extraída
    
    Returns:
        bool: True si se generaron imágenes, False si falló o no produjo output
    """
    try:
        wiutils.convert_video_to_images(str(video_path), str(out_dir), timestamp, offset=offset)
        return any(p.suffix.lower() in (".jpg", ".jpeg", ".png") for p in out_dir.glob("*"))
    except Exception as e:
        print(f"[wiutils] Falla con {video_path.name}: {e}")
        return False


# ==============================================================================
# SECCIÓN 3: SISTEMA DE RENOMBRADO Y NOMENCLATURA
# ==============================================================================
# Funciones para gestionar la nomenclatura uniforme de las imágenes extraídas.
# Formato estándar: <nombre_video>_XXXXXX.jpg (índice de 6 dígitos)

def _parse_index_from_name(p: Path, video_stem: str) -> int:
    """
    Extrae el índice numérico del nombre de un archivo de imagen.
    
    Esperado: <video_stem>_XXXXXX.ext donde XXXXXX es un número de 6 dígitos.
    
    Args:
        p: Path del archivo a analizar
        video_stem: Nombre base del video (sin extensión)
    
    Returns:
        int: Índice extraído, o -1 si no se puede parsear
    """
    try:
        base = p.stem
        if not base.startswith(f"{video_stem}_"):
            return -1
        part = base.split("_")[-1]
        return int(part) if part.isdigit() else -1
    except Exception:
        return -1


def _next_index_for_prefix(out_dir: Path, video_stem: str) -> int:
    """
    Encuentra el siguiente índice disponible para un prefijo de video dado.
    
    Escanea la carpeta de salida buscando archivos con el formato
    <video_stem>_XXXXXX.ext y retorna el siguiente índice libre.
    
    Args:
        out_dir: Directorio donde buscar archivos existentes
        video_stem: Nombre base del video
    
    Returns:
        int: Siguiente índice disponible (max_actual + 1)
    """
    max_idx = 0
    for p in out_dir.glob(f"{video_stem}_*.*"):
        if p.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        idx = _parse_index_from_name(p, video_stem)
        if idx > max_idx:
            max_idx = idx
    return max_idx + 1


def _rename_new_flat(out_dir: Path, video_stem: str, before_names: set) -> int:
    """
    Renombra las imágenes recién extraídas a la nomenclatura estándar.
    
    Solo procesa archivos nuevos (no presentes en before_names) que no tengan
    ya el formato correcto. Evita colisiones de nombres y normaliza extensiones.
    
    Args:
        out_dir: Directorio con las imágenes a renombrar
        video_stem: Nombre base del video (prefijo para las imágenes)
        before_names: Set de nombres de archivos que ya existían antes
    
    Returns:
        int: Total de imágenes nuevas encontradas (renombradas o no)
    """  
    new_imgs = [p for p in out_dir.glob("*")
                if p.name not in before_names and p.suffix.lower() in (".jpg", ".jpeg", ".png")]
    to_rename = [p for p in new_imgs if not p.name.startswith(f"{video_stem}_")]
    if not to_rename:
        return len(new_imgs)

    next_idx = _next_index_for_prefix(out_dir, video_stem)
    for p in sorted(to_rename, key=lambda x: x.name.lower()):
        ext = p.suffix.lower()
        if ext == ".jpeg":  # normaliza
            ext = ".jpg"
        target = out_dir / f"{video_stem}_{next_idx:06d}{ext}"
        while target.exists():
            next_idx += 1
            target = out_dir / f"{video_stem}_{next_idx:06d}{ext}"
        try:
            p.rename(target)
            next_idx += 1
        except Exception as e:
            print(f"[rename] No se pudo renombrar {p.name} -> {target.name}: {e}")
    return len(new_imgs)


# ==============================================================================
# SECCIÓN 4: EXTRACCIÓN DE METADATOS DE VIDEO
# ==============================================================================
# Funciones para obtener información técnica de los videos sin procesarlos.

def _probe_duration_str(ffprobe_bin: str, ffmpeg_bin: str, video: Path) -> str:
    """
    Obtiene la duración de un video en formato legible (HH:MM:SS o MM:SS).
    
    Estrategia de detección (por prioridad):
        1. FFprobe con opción -show_entries format=duration (más preciso)
        2. FFmpeg -i parseando la salida stderr (fallback)
        3. "desconocida" si ambos métodos fallan
    
    Args:
        ffprobe_bin: Ruta al ejecutable de FFprobe
        ffmpeg_bin: Ruta al ejecutable de FFmpeg (usado como fallback)
        video: Path del archivo de video a analizar
    
    Returns:
        str: Duración en formato "HH:MM:SS" o "desconocida" si falla
    """
    # 1) ffprobe (si existe)
    if ffprobe_bin and Path(ffprobe_bin).exists():
        try:
            creationflags = 0x08000000 if os.name == "nt" else 0
            pr = subprocess.run(
                [ffprobe_bin, "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
                capture_output=True, check=True, creationflags=creationflags
            )
            txt = (pr.stdout or b"").decode("utf-8", errors="ignore").strip()
            secs = float(txt)
            return _secs_to_hms(secs)
        except Exception:
            pass

    # 2) ffmpeg -i (parsea "Duration: 00:00:00.xx")
    if ffmpeg_bin and Path(ffmpeg_bin).exists():
        try:
            creationflags = 0x08000000 if os.name == "nt" else 0
            pr = subprocess.run(
                [ffmpeg_bin, "-hide_banner", "-i", str(video)],
                capture_output=True, check=False, creationflags=creationflags
            )
            err = (pr.stderr or b"").decode("utf-8", errors="ignore")
            for line in err.splitlines():
                if "Duration:" in line:
                    # Ejemplo: "  Duration: 00:00:12.34, start: 0.000000, bitrate: ..."
                    part = line.split("Duration:", 1)[1].split(",", 1)[0].strip()
                    # toma HH:MM:SS.xx y trunca a HH:MM:SS
                    hms = part.split(".")[0]
                    return hms
        except Exception:
            pass

    return "desconocida"


def _secs_to_hms(secs: float) -> str:
    """
    Convierte segundos a formato HH:MM:SS.
    
    Args:
        secs: Duración en segundos (float)
    
    Returns:
        str: Duración formateada como "HH:MM:SS" con ceros a la izquierda
    """
    secs = max(0, int(round(secs)))
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# ==============================================================================
# SECCIÓN 5: FLUJO PRINCIPAL DE PROCESAMIENTO
# ==============================================================================
# Función principal que coordina todo el proceso de extracción de imágenes.

def process_videos(input_path: Path, output_path: Path, update_status, update_progress, offset=None):
    """
    Función principal: procesa todos los videos encontrados en input_path.
    
    Flujo de ejecución:
        1. Localiza FFmpeg y FFprobe
        2. Escanea recursivamente buscando videos (.mp4, .mov, .avi)
        3. Por cada video:
           - Detecta duración
           - Extrae frames (wiutils para MP4, FFmpeg para otros o fallback)
           - Renombra imágenes con nomenclatura estándar
        4. Reporta progreso mediante callbacks
    
    Args:
        input_path: Carpeta raíz donde buscar videos recursivamente
        output_path: Carpeta única donde se guardarán todas las imágenes
        update_status: Callback para mensajes de log (función que recibe str)
        update_progress: Callback para progreso (función que recibe int 0-100)
        offset: Segundos entre imágenes (None = 1 segundo por defecto)
    
    Returns:
        tuple: (total_videos_procesados, tiempo_transcurrido_segundos)
    """
    exts = {".mp4", ".avi", ".mov"}
    video_paths = sorted((p for p in input_path.rglob("*") if p.suffix.lower() in exts),
                         key=lambda x: str(x).lower())
    total_videos = len(video_paths)

    # ffmpeg/ffprobe y fps
    ffmpeg_bin = _find_ffmpeg()
    ffprobe_bin = _find_ffprobe()
    update_status and update_status(f"🔵 FFmpeg: {ffmpeg_bin or 'NO ENCONTRADO'}")
    update_status and update_status(f"🔵 FFprobe: {ffprobe_bin or 'NO ENCONTRADO'}")
    if ffmpeg_bin:
        update_status and update_status(f"🔵 {_ffmpeg_self_test(ffmpeg_bin)}")
    else:
        update_status and update_status("⚠️ ffmpeg ausente")

    fps = _fps_from_offset(offset)
    output_path.mkdir(parents=True, exist_ok=True)
    start = time.time()

    for i, video_path in enumerate(video_paths, start=1):
        try:
            dur = _probe_duration_str(ffprobe_bin, ffmpeg_bin, video_path)
            update_status and update_status(
                f"🔵 Procesando {i}/{total_videos}: {video_path.name} (duración {dur})"
            )

            # Timestamp para wiutils
            mod_time = os.path.getmtime(video_path)
            fecha_dt = datetime.fromtimestamp(mod_time) - timedelta(seconds=29)
            timestamp = fecha_dt.strftime("%m-%d-%Y %H:%M:%S")

            video_stem = video_path.stem
            out_dir = output_path

            before = {p.name for p in out_dir.glob("*")
                      if p.suffix.lower() in (".jpg", ".jpeg", ".png")}

            # MP4 -> wiutils, si falla -> FFmpeg ; AVI/MOV -> FFmpeg
            suffix = video_path.suffix.lower()
            if suffix in {".avi", ".mov"}:
                ok = _extract_with_ffmpeg(ffmpeg_bin, video_path, out_dir, fps, update_status)
            else:
                ok = _extract_with_wiutils(video_path, out_dir, timestamp, offset)
                if not ok:
                    update_status and update_status("⚠️ wiutils falló; probando FFmpeg…")
                    ok = _extract_with_ffmpeg(ffmpeg_bin, video_path, out_dir, fps, update_status)

            if not ok:
                continue

            # Renombrado (sólo nuevas sin prefijo)
            new_count = _rename_new_flat(out_dir, video_stem, before)
            update_status and update_status(f"✅ {new_count} imágenes generadas desde '{video_path.name}'")

            # progreso simple por video
            try:
                update_progress and update_progress(int(i / max(total_videos, 1) * 100))
            except Exception:
                pass

        except Exception as e:
            update_status and update_status(f"❌ Error procesando {video_path.name}: {e}")

    duration = round(time.time() - start, 2)
    return total_videos, duration


def _ffmpeg_self_test(ffmpeg_bin: str) -> str:
    """
    Verifica que FFmpeg esté funcionando correctamente ejecutando -version.
    
    Args:
        ffmpeg_bin: Ruta al ejecutable de FFmpeg
    
    Returns:
        str: Primera línea de la versión de FFmpeg o mensaje de error
    """
    try:
        pr = subprocess.run(
            [ffmpeg_bin, "-hide_banner", "-loglevel", "error", "-version"],
            capture_output=True, check=True,
            creationflags=(0x08000000 if os.name == "nt" else 0)
        )
        out = (pr.stdout or pr.stderr or b"").decode("utf-8", errors="ignore").splitlines()
        return out[0] if out else "ffmpeg ok (sin salida)"
    except Exception as e:
        return f"no se pudo ejecutar ffmpeg: {e}"
