# -*- coding: utf-8 -*-
"""
WI2CamtrapDP - Interfaz Gráfica de Conversión Wildlife Insights a Camtrap-DP
============================================================================

Aplicación de escritorio para convertir exportaciones de Wildlife Insights (formato ZIP)
al estándar Camtrap Data Package (Camtrap-DP v1.0.2) para publicación y análisis.

Características principales:
    - Procesamiento de exportaciones de PROYECTO (no soporta iniciativas de WI)
    - Compatibilidad con API nueva (process_zip) y antigua (process) del procesador
    - Interfaz adaptable HiDPI con tamaño inicial relativo y scroll automático
    - Seguimiento de ejecución con dos vistas: Resumen (tabla) y Detalles (log textual)
    - Generación automática de plantilla de correo para publicación en SIB Colombia
    - Validación integrada con Frictionless Framework
    - Empaquetado automático en ZIP con timestamp

Módulo: app.py
Autor: Cristian C. Acevedo
Organización: Instituto Humboldt - Red OTUS
Versión: 1.0.0
Última actualización: 23 de diciembre de 2025
Licencia: Ver LICENSE
"""

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

# Librerías de terceros
import pytz
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QLabel, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QFrame,
    QDialog, QDialogButtonBox, QTextEdit, QPushButton
)

# Módulo de procesamiento Camtrap-DP
from camtrapdp.processor import process_zip as _proc_zip


# ============================================================================
# WIDGETS PERSONALIZADOS
# ============================================================================

class AspectLabel(QLabel):
    """
    QLabel personalizado que reescala imágenes manteniendo la proporción de aspecto.
    
    Permite controlar el modo de ajuste (altura, ancho o ambos) y reescala
    automáticamente el QPixmap cuando cambia el tamaño del widget.
    
    Args:
        parent: Widget padre (opcional)
        fit: Modo de ajuste - "height", "width" o "both"
    """
    
    def __init__(self, parent=None, fit="height"):
        super().__init__(parent)
        self._orig = None  # QPixmap original sin escalar
        self._fit = fit    # Modo de ajuste: "height" | "width" | "both"
        self.setAlignment(Qt.AlignCenter)
    
    def setPixmap(self, pm: QPixmap):
        """Almacena el pixmap original y lo reescala según el tamaño actual."""
        self._orig = pm
        self._rescale()
    
    def resizeEvent(self, e):
        """Reescala la imagen cuando el widget cambia de tamaño."""
        super().resizeEvent(e)
        self._rescale()
    
    def _rescale(self):
        """Reescala el pixmap original según el modo de ajuste configurado."""
        if not isinstance(self._orig, QPixmap) or self._orig.isNull():
            super().setPixmap(QPixmap())
            return
        
        # Reescalar según el modo configurado
        if self._fit == "height":
            pm2 = self._orig.scaledToHeight(max(1, self.height()), Qt.SmoothTransformation)
        elif self._fit == "width":
            pm2 = self._orig.scaledToWidth(max(1, self.width()), Qt.SmoothTransformation)
        else:  # "both"
            pm2 = self._orig.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        super().setPixmap(pm2)


# ============================================================================
# RESOLUCIÓN DE PIPELINE (COMPATIBILIDAD API NUEVA/ANTIGUA)
# ============================================================================

def _resolve_pipeline():
    """
    Resuelve y retorna el pipeline de procesamiento compatible con la API disponible.
    
    Intenta usar primero la API nueva (process_zip) y si falla, usa la API antigua (process).
    Esto garantiza compatibilidad con diferentes versiones del módulo camtrapdp.
    
    Returns:
        callable: Función que ejecuta el pipeline con la firma:
                  (zip_path, out_dir, options, log_cb, progress_cb) → (ok, work_dir, msg)
                  
                  Donde:
                  - ok (bool): True si el procesamiento fue exitoso
                  - work_dir (str): Ruta del directorio de trabajo generado
                  - msg (str): Mensaje de resultado o error
    """

    def _check_artifacts(work_dir: Path):
        """
        Verifica la existencia de artefactos generados por el procesamiento.
        
        Comprueba que existan el directorio output, el datapackage.json y al menos
        uno de los archivos CSV con contenido (tamaño > 0).
        
        Args:
            work_dir: Directorio de trabajo del procesamiento
            
        Returns:
            tuple: (ok, out, dp, csvs) donde:
                   - ok (bool): True si los artefactos esenciales existen
                   - out (Path): Ruta del directorio output
                   - dp (Path): Ruta del datapackage.json
                   - csvs (list[Path]): Lista de rutas de archivos CSV esperados
        """
        out = Path(work_dir) / "output"
        dp  = out / "datapackage.json"
        csvs = [out / "deployments.csv", out / "media.csv", out / "observations.csv"]
        ok = out.exists() and dp.exists() and any(p.exists() and p.stat().st_size > 0 for p in csvs)
        return ok, out, dp, csvs

    try:
        # ===== INTENTO 1: API NUEVA (process_zip) =====
        # La API nueva es más robusta y moderna
        from camtrapdp.processor import process_zip as _proc_zip

        def run_pipeline(zip_path: Path, out_dir: Path, options: dict, log_cb, progress_cb):
            """
            Ejecuta el pipeline usando la API nueva (process_zip).
            
            Args:
                zip_path: Ruta del archivo ZIP de Wildlife Insights
                out_dir: Directorio de salida para los resultados
                options: Diccionario con opciones de procesamiento
                log_cb: Callback para mensajes de log
                progress_cb: Callback para actualizaciones de progreso
                
            Returns:
                tuple: (ok, work_dir, message)
            """
            try:
                # Wrapper robusto que garantiza siempre emitir (porcentaje, mensaje)
                def _safe_progress(*a, **k):
                    """Normaliza llamadas de progreso a formato (pct, msg)."""
                    try:
                        pct = int(a[0]) if len(a) >= 1 else -1
                    except Exception:
                        pct = -1
                    
                    msg = ""
                    if len(a) >= 2 and a[1] is not None:
                        msg = str(a[1])
                    elif "message" in k:
                        msg = str(k.get("message") or "")
                    
                    try:
                        progress_cb(pct, msg)
                    except Exception:
                        pass

                # Ejecutar el procesamiento con la API nueva
                work = _proc_zip(
                    zip_path, out_dir,
                    logger=log_cb,
                    report_progress=_safe_progress,
                    validate=bool(options.get("validate", True)),
                    make_zip=bool(options.get("make_zip", True)),
                    overwrite=bool(options.get("overwrite", False)),
                    timezone_hint=str(options.get("timezone_hint", "America/Bogota")),
                )

                # Verificar que se generaron los artefactos esperados
                work_dir = Path(str(work))
                ok, _, _, _ = _check_artifacts(work_dir)
                if not ok:
                    return False, str(work_dir), (
                        "No se generaron artefactos (datapackage/CSV). Revisa permisos, "
                        "espacio en disco o mensajes previos."
                    )

                return True, str(work_dir), "Proceso completado."
            except Exception as e:
                return False, "", f"{e}"

        return run_pipeline

    except Exception:
        # ===== FALLBACK: API ANTIGUA (process) =====
        # Si la API nueva no está disponible, usar la versión anterior
        from camtrapdp.processor import process as _proc_old
        try:
            from camtrapdp.config import Options as _Options
        except Exception:
            # Crear clase Options dinámicamente si no existe
            class _Options:
                def __init__(self, **kw):
                    self.__dict__.update(kw)

        def run_pipeline(zip_path: Path, out_dir: Path, options: dict, log_cb, progress_cb):
            """
            Ejecuta el pipeline usando la API antigua (process).
            
            Adaptador para mantener compatibilidad con versiones anteriores del procesador.
            
            Args:
                zip_path: Ruta del archivo ZIP de Wildlife Insights
                out_dir: Directorio de salida para los resultados
                options: Diccionario con opciones de procesamiento
                log_cb: Callback para mensajes de log
                progress_cb: Callback para actualizaciones de progreso
                
            Returns:
                tuple: (ok, work_dir, message)
            """
            try:
                # Adaptadores para los callbacks de la API antigua
                def _p(v):
                    """Callback de progreso simplificado."""
                    try:
                        progress_cb(int(v), "")
                    except Exception:
                        pass
                
                def _s(msg):
                    """Callback de estado/log."""
                    try:
                        log_cb(msg)
                    except Exception:
                        pass
                
                def _l(msg):
                    """Callback adicional de log."""
                    try:
                        log_cb(msg)
                    except Exception:
                        pass

                # Construir objeto de opciones para la API antigua
                opts = _Options(
                    timezone_hint=str(options.get("timezone_hint", "America/Bogota")),
                    validate=bool(options.get("validate", True)),
                    make_zip=bool(options.get("make_zip", True)),
                    save_log=False,
                    open_folder_after=False,
                    overwrite=bool(options.get("overwrite", False)),
                )

                # Ejecutar procesamiento con la API antigua
                res = _proc_old(str(zip_path), str(out_dir), opts,
                                progress_cb=_p, status_cb=_s, log_cb=_l)

                # La API antigua devuelve un diccionario con 'work_dir'
                # Si no existe, inferir la ruta estándar
                guess_dir = Path(out_dir) / f"WI2CamtrapDP_{Path(zip_path).stem}"
                work_dir = Path(res.get("work_dir", str(guess_dir)))

                # Verificar que se generaron los artefactos esperados
                ok, _, _, _ = _check_artifacts(work_dir)
                if not ok:
                    return False, str(work_dir), (
                        "No se generaron artefactos (datapackage/CSV). Revisa permisos, "
                        "espacio en disco o mensajes previos."
                    )

                return True, str(work_dir), "Proceso completado."
            except Exception as e:
                return False, "", f"{e}"

        return run_pipeline

# Pipeline resuelto según la API disponible
RUN_PIPELINE = _resolve_pipeline()


# ============================================================================
# WORKER: PROCESAMIENTO EN HILO SEPARADO
# ============================================================================
class Worker(QObject):
    """
    Worker para ejecutar el pipeline de procesamiento en un hilo separado.
    
    Ejecuta el procesamiento de forma asíncrona para evitar bloquear la interfaz gráfica.
    Emite señales para reportar progreso y resultado final.
    
    Signals:
        progress (int, str): Emitido durante el procesamiento con (porcentaje, mensaje)
                             El porcentaje puede ser -1 para indicar progreso indeterminado
        finished (bool, str, str): Emitido al terminar con (ok, work_dir, mensaje)
                                   - ok: True si fue exitoso
                                   - work_dir: Directorio de trabajo generado
                                   - mensaje: Descripción del resultado o error
    
    Attributes:
        zip_path (Path): Ruta del archivo ZIP a procesar
        out_dir (Path): Directorio de salida
        options (dict): Opciones de procesamiento
    """
    
    # Señales Qt
    progress = pyqtSignal(int, str)        # (porcentaje, mensaje)
    finished = pyqtSignal(bool, str, str)  # (ok, work_dir, mensaje)
    
    def __init__(self, zip_path: Path, out_dir: Path, options: dict):
        super().__init__()
        self.zip_path = Path(zip_path)
        self.out_dir = Path(out_dir)
        self.options = options
    
    def _log(self, msg: str):
        """Emite un mensaje de log sin porcentaje de progreso."""
        self.progress.emit(-1, str(msg))
    
    def _progress(self, pct: int, msg: str = ""):
        """Emite una actualización de progreso con porcentaje."""
        self.progress.emit(int(pct), str(msg))
    
    def run(self):
        """
        Ejecuta el pipeline de procesamiento.
        
        Este método es llamado automáticamente cuando el QThread inicia.
        Al terminar, emite la señal finished con los resultados.
        """
        ok, work_dir, err_or_ok = RUN_PIPELINE(
            self.zip_path, self.out_dir, self.options,
            log_cb=self._log, progress_cb=self._progress
        )
        self.finished.emit(ok, work_dir, err_or_ok)


# ============================================================================
# FUNCIONES UTILITARIAS
# ============================================================================

def resource_path(*parts) -> Path:
    """
    Resuelve la ruta de recursos empaquetados (PyInstaller) o del código fuente.
    
    Cuando la aplicación está empaquetada con PyInstaller, los recursos se extraen
    a una carpeta temporal (_MEIPASS). Esta función maneja ambos casos.
    
    Args:
        *parts: Componentes de la ruta (ej: "assets", "icon.png")
        
    Returns:
        Path: Ruta completa al recurso
        
    Example:
        >>> icon = resource_path("assets", "app_icon.png")
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


def _now() -> str:
    """
    Retorna la hora actual en formato HH:MM:SS.
    
    Returns:
        str: Hora actual formateada (ej: "14:35:22")
    """
    return datetime.now().strftime("%H:%M:%S")


def _tz_items_with_gmt(ids):
    """
    Genera lista de tuplas (texto_display, timezone_id) con offset GMT.
    
    Formatea cada zona horaria con su offset GMT para mejor visualización
    en el combobox de zonas horarias.
    
    Args:
        ids (list): Lista de IDs de zonas horarias (ej: ["America/Bogota", ...])
        
    Returns:
        list[tuple]: Lista de tuplas ("(GMT+/-HH:MM) Timezone", "timezone_id")
        
    Example:
        >>> _tz_items_with_gmt(["America/Bogota"])
        [("(GMT-05:00) America/Bogota", "America/Bogota")]
    """
    items = []
    for tzid in ids:
        try:
            tz = pytz.timezone(tzid)
            offset = datetime.now(tz).utcoffset()
            total_min = 0 if offset is None else int(offset.total_seconds() // 60)
            sign = "-" if total_min < 0 else "+"
            hh, mm = divmod(abs(total_min), 60)
            items.append((f"(GMT{sign}{hh:02d}:{mm:02d}) {tzid}", tzid))
        except Exception:
            # Si falla el parsing, agregar sin formato
            items.append((tzid, tzid))
    return items


def _emoji_for(level: str) -> str:
    """
    Retorna el emoji correspondiente a un nivel de log.
    
    Args:
        level: Nivel del mensaje ("ERROR", "WARN", "OK", "INFO")
        
    Returns:
        str: Emoji representativo del nivel
    """
    return {"ERROR": "🔴", "WARN": "🟡", "OK": "🟢", "INFO": "🔵"}.get(level, "🔵")


def _level_from_msg(msg: str) -> str:
    """
    Infiere el nivel de log desde el contenido del mensaje.
    
    Analiza el texto del mensaje para determinar si es un error, advertencia,
    mensaje exitoso o informativo.
    
    Args:
        msg: Mensaje de log
        
    Returns:
        str: Nivel inferido ("ERROR", "WARN", "OK", "INFO")
    """
    s = msg.strip().lower()
    if s.startswith("error") or "traceback" in s:
        return "ERROR"
    if s.startswith("warn") or "warning" in s or "advertencia" in s:
        return "WARN"
    if s.startswith("validación: ok") or s.startswith("listo") or "proceso completado" in s:
        return "OK"
    return "INFO"


def _detect_initiative_zip(zip_path: Path) -> int:
    """
    Detecta si un ZIP es de iniciativa (no soportado) contando archivos images_*.csv.
    
    Las exportaciones de INICIATIVA contienen múltiples archivos images_*.csv
    (uno por proyecto), mientras que las exportaciones de PROYECTO tienen solo uno.
    
    Args:
        zip_path: Ruta del archivo ZIP a analizar
        
    Returns:
        int: Número de archivos images_*.csv encontrados.
             Si > 1, es una iniciativa (no soportada).
             
    Raises:
        zipfile.BadZipFile: Si el archivo no es un ZIP válido
    """
    count = 0
    with zipfile.ZipFile(str(zip_path), "r") as z:
        for n in z.namelist():
            base = os.path.basename(n).lower()
            if base.startswith("images_") and base.endswith(".csv"):
                count += 1
    return count


# ============================================================================
# FUNCIÓN PRINCIPAL DE APLICACIÓN
# ============================================================================

def main():
    """
    Función principal de la aplicación WI2CamtrapDP.
    
    Inicializa la aplicación Qt, configura la interfaz gráfica, establece los
    manejadores de eventos y ejecuta el loop principal de la aplicación.
    
    La aplicación permite convertir exportaciones de Wildlife Insights (formato ZIP)
    al estándar Camtrap Data Package v1.0.2, con opciones de validación y empaquetado.
    
    Componentes principales:
        - Configuración HiDPI para pantallas de alta resolución
        - Carga de interfaz desde archivo .ui
        - Configuración de widgets personalizados (logo, tabs, tablas)
        - Manejadores de eventos para procesamiento asíncrono
        - Sistema de seguimiento con vista resumida y detallada
        
    Returns:
        int: Código de salida de la aplicación (0 si es exitoso)
    """
    # ========================================================================
    # CONFIGURACIÓN HIDPI PARA PANTALLAS DE ALTA RESOLUCIÓN
    # ========================================================================
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "1"
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    # ========================================================================
    # CARGA DE INTERFAZ Y RECURSOS
    # ========================================================================
    # Cargar iconos de la aplicación
    icon_png = resource_path("assets", "app_icon.png")
    icon_ico = resource_path("assets", "app_icon.ico")
    app_icon = QIcon(str(icon_png)) if icon_png.exists() else (QIcon(str(icon_ico)) if icon_ico.exists() else None)
    
    # Cargar diseño de interfaz desde archivo .ui
    ui_file = resource_path("ui", "camtrapdp.ui")
    w = uic.loadUi(str(ui_file))
    w.setWindowTitle("WI2CamtrapDP")
    
    # Aplicar icono a ventana y aplicación
    if app_icon is not None:
        app.setWindowIcon(app_icon)
        w.setWindowIcon(app_icon)

    # Ocultar “Guardar log de ejecución” si existe
    if hasattr(w, "chkSaveLog"):
        w.chkSaveLog.setChecked(False); w.chkSaveLog.setVisible(False); w.chkSaveLog.setEnabled(False)

    # Tamaño inicial
    screen = w.screen() or app.primaryScreen()
    geo = screen.availableGeometry()
    w.resize(int(geo.width()*0.85), int(geo.height()*0.85))
    w.setMinimumSize(1000, 700)

    # Encabezado
    title_html = "<div style='font-size:18px; font-weight:700; text-align:center;'>📦 De Wildlife Insights a Camtrap-DP </div>"
    obs_html = ("<div style='text-align:center;'>Convierte una exportación de Wildlife Insights (ZIP) al estándar "
                "<i>Camtrap Data Package</i> (Camtrap-DP) para publicación y análisis.<br>"
                "<b>Observación:</b> esta utilidad procesa únicamente exportaciones de <b>proyecto</b> (no iniciativas de WI).</div>")
    central = w.centralWidget() if hasattr(w, "centralWidget") else w
    root_layout = central.layout()
    header = QWidget(); hv = QVBoxLayout(header); hv.setContentsMargins(0,0,6,6)
    hv.addWidget(QLabel(title_html))
    lbl_obs = QLabel(obs_html); lbl_obs.setWordWrap(True); lbl_obs.setAlignment(Qt.AlignCenter)
    hv.addWidget(lbl_obs)
    if root_layout is not None:
        root_layout.insertWidget(0, header)

    # ========================================================================
    # SECCIÓN DE GUÍA: INSTRUCCIONES DE USO
    # ========================================================================
    # Crear widget con guía paso a paso para el usuario
    guide_box = QGroupBox("📘 Guía rápida de uso")
    gv = QVBoxLayout(guide_box)
    gv.setContentsMargins(10, 6, 10, 10)
    
    # Contenido HTML con pasos numerados
    guide_html = (
        "<ol style='margin:4px 0 4px 18px;'>"
        "<li>Seleccione el archivo <i>ZIP</i> del proyecto (botón <b>Seleccionar…</b>).</li>"
        "<li>Elija las <b>opciones</b> de validación y empaquetado según su necesidad.</li>"
        "<li>Pulse <b>Procesar</b>; la barra mostrará el avance y el seguimiento detallará cada paso.</li>"
        "<li>Al finalizar, abra la <b>carpeta de salida</b> o el <code>datapackage.json</code> con los botones inferiores.</li>"
        "</ol>"
        "Los resultados se guardan en la misma carpeta del ZIP, dentro de <code>WI2CamtrapDP_[nombre]_[fecha-hora]</code>."
    )
    gv.addWidget(QLabel(guide_html))

    if root_layout is not None:
        root_layout.insertWidget(1, guide_box)

    # ========================================================================
    # SISTEMA DE SEGUIMIENTO: TABS CON VISTA RESUMIDA Y DETALLADA
    # ========================================================================
    gl = getattr(w, "groupLog", None)
    if gl and hasattr(w, "logConsole"):
        # Cambiar título del groupBox para reflejar funcionalidad de seguimiento
        if hasattr(gl, "setTitle"):
            gl.setTitle("📋 Seguimiento de ejecución")
        
        # Crear sistema de tabs con dos vistas
        w.logTabs = QTabWidget()
        w.logTabs.setObjectName("logTabs")
        
        # ====================================================================
        # TAB 1: VISTA RESUMIDA (TABLA)
        # ====================================================================
        # Crear tabla para mostrar resumen de eventos importantes
        w.logTable = QTableWidget(0, 3)
        w.logTable.setObjectName("logTable")
        w.logTable.setHorizontalHeaderLabels(["Hora", "Nivel", "Mensaje"])
        w.logTable.horizontalHeader().setStretchLastSection(True)
        w.logTable.verticalHeader().setVisible(False)
        w.logTable.setEditTriggers(QTableWidget.NoEditTriggers)
        w.logTable.setSelectionBehavior(QTableWidget.SelectRows)
        w.logTable.setAlternatingRowColors(True)
        
        # ====================================================================
        # TAB 2: VISTA DETALLADA (TEXTO)
        # ====================================================================
        # Reutilizar widget logConsole existente para vista de texto completo
        gl.layout().removeWidget(w.logConsole)
        
        # Agregar ambas vistas como tabs
        w.logTabs.addTab(w.logTable, "📊 Resumen")
        w.logTabs.addTab(w.logConsole, "📝 Detalles")
        gl.layout().addWidget(w.logTabs)

    # ========================================================================
    # FOOTER: LOGO Y CITACIÓN
    # ========================================================================
    footer = QFrame()
    fb = QHBoxLayout(footer)
    fb.setContentsMargins(0, 6, 0, 0)
    
    # Logo del Instituto Humboldt
    logo_lbl = AspectLabel(fit="height")
    logo_lbl.setFixedHeight(18)
    logo_path = resource_path("assets", "logo_humboldt.png")
    if logo_path.exists():
        pm = QPixmap(str(logo_path))
        if not pm.isNull():
            logo_lbl.setPixmap(pm)
    
    fb.addWidget(logo_lbl, 0, Qt.AlignLeft | Qt.AlignVCenter)
    fb.addSpacing(8)
    
    # Texto de citación
    citation = ("<b>Citar como:</b> Acevedo, C. C., & Diaz-Pulido, A. (2025). Gestión de datos de fototrampeo (v1.0.0) [Software]. "
                "Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. Publicado el 7 de septiembre de 2025.")
    footer_txt = QLabel(citation)
    footer_txt.setStyleSheet("color:#666; font-size:11px;")
    footer_txt.setWordWrap(True)
    footer_txt.setAlignment(Qt.AlignCenter)
    footer_txt.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    fb.addWidget(footer_txt); fb.addSpacing(8); fb.setStretchFactor(logo_lbl, 0); fb.setStretch(fb.indexOf(footer_txt), 1)
    if root_layout is not None: root_layout.addWidget(footer)

    # Zonas horarias
    if hasattr(w, "cbTimezone"):
        w.cbTimezone.clear()
        for txt, tzid in _tz_items_with_gmt(sorted(pytz.all_timezones)):
            w.cbTimezone.addItem(txt, tzid)
        idx = max(0, w.cbTimezone.findData("America/Bogota"))
        w.cbTimezone.setCurrentIndex(idx)

    # Checks por defecto
    try:
        import frictionless as _fr
        ver = getattr(_fr, "__version__", None)
    except Exception:
        ver = None
    if hasattr(w, "chkValidate"):   w.chkValidate.setChecked(True);   w.chkValidate.setText(f"🔍 Validar con Frictionless{f' (v{ver})' if ver else ''}")
    if hasattr(w, "chkMakeZip"):    w.chkMakeZip.setChecked(True);    w.chkMakeZip.setText("📦 Crear ZIP final (incluye fecha-hora)")
    if hasattr(w, "chkOpenFolder"): w.chkOpenFolder.setChecked(True); w.chkOpenFolder.setText("📂 Abrir carpeta al terminar")
    if hasattr(w, "chkOverwrite"):  w.chkOverwrite.setChecked(True);  w.chkOverwrite.setText("♻️ Sobrescribir si existe")

    # Salida fija a carpeta del ZIP
    if hasattr(w, "btnOut"): w.btnOut.setVisible(False); w.btnOut.setEnabled(False)
    if hasattr(w, "leOut"):
        w.leOut.setReadOnly(True)
        w.leOut.setPlaceholderText("Se usará la misma carpeta del ZIP")
        w.leOut.clear()

    # ========================================================================
    # CONFIGURACIÓN DE BOTONES DE RESULTADOS
    # ========================================================================
    # Ocultar botón de log (funcionalidad no utilizada)
    if hasattr(w, "btnOpenLog"):
        w.btnOpenLog.setVisible(False)
        w.btnOpenLog.setEnabled(False)
    
    # Deshabilitar botón de limpiar inicialmente
    if hasattr(w, "btnClear"):
        w.btnClear.setEnabled(False)
    
    # Ocultar botones de apertura de resultados (se habilitan después del procesamiento)
    for bn in ["btnOpenOut", "btnOpenDatapackage"]:
        if hasattr(w, bn):
            getattr(w, bn).setEnabled(False)
            getattr(w, bn).setVisible(False)

    # ========================================================================
    # REORGANIZACIÓN DE LAYOUT: OPCIONES EN FILA HORIZONTAL
    # ========================================================================
    def _remove_from_layout(widget):
        """
        Remueve un widget del layout y lo destruye.
        
        Args:
            widget: Widget a remover
        """
        if not widget:
            return
        parent = widget.parentWidget()
        lay = parent.layout() if parent else None
        if lay:
            lay.removeWidget(widget)
        widget.setParent(None)
        widget.deleteLater()

    # Reorganizar checkboxes de opciones en una sola fila
    if hasattr(w, "groupOptions") and w.groupOptions.layout():
        grid = w.groupOptions.layout()
        
        # Remover checkbox de log si existe (funcionalidad legacy)
        if hasattr(w, "chkSaveLog"):
            _remove_from_layout(w.chkSaveLog)
            delattr(w, "chkSaveLog")
        
        # Remover spacers existentes
        for i in reversed(range(grid.count())):
            if grid.itemAt(i) and grid.itemAt(i).spacerItem() is not None:
                grid.takeAt(i)
        
        # Agregar checkboxes en fila horizontal
        col = 0
        for name in ("chkValidate", "chkMakeZip", "chkOpenFolder", "chkOverwrite"):
            if hasattr(w, name):
                grid.addWidget(getattr(w, name), 0, col, 1, 1)
                grid.setColumnStretch(col, 1)
                col += 1
        
        # Ajustar espaciado y márgenes
        grid.setHorizontalSpacing(12)
        grid.setContentsMargins(8, 8, 8, 8)

    # ========================================================================
    # CONFIGURACIÓN DE BOTONES DE EJECUCIÓN
    # ========================================================================
    # Agregar botón de plantilla de correo en sección de ejecución
    if hasattr(w, "groupRun") and w.groupRun.layout():
        run_grid = w.groupRun.layout()
        
        # Crear botón de plantilla si no existe
        if not hasattr(w, "btnEmailTemplate"):
            w.btnEmailTemplate = QPushButton("Plantilla de correo", w.groupRun)
            w.btnEmailTemplate.setObjectName("btnEmailTemplate")
        w.btnEmailTemplate.setEnabled(False)  # Deshabilitado inicialmente
        
        # Reorganizar botones en fila horizontal
        if hasattr(w, "btnProcess"):
            run_grid.addWidget(w.btnProcess, 0, 0, 1, 1)
        run_grid.addWidget(w.btnEmailTemplate, 0, 1, 1, 1)
        if hasattr(w, "btnClear"):
            run_grid.addWidget(w.btnClear, 0, 2, 1, 1)
        
        # Configurar stretch factors para distribución uniforme
        for c in range(3):
            run_grid.setColumnStretch(c, 1)
        
        # Ajustar espaciado y márgenes
        run_grid.setHorizontalSpacing(12)
        run_grid.setContentsMargins(8, 8, 8, 8)
        
        # Asegurar que la barra de progreso ocupe todo el ancho
        if hasattr(w, "progressBar"):
            run_grid.addWidget(w.progressBar, 1, 0, 1, 3)
            w.progressBar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    # ========================================================================
    # INICIALIZACIÓN DE ESTADO INTERNO
    # ========================================================================
    # Variables para manejo de hilo de procesamiento y resultados
    w._thread = None              # QThread para procesamiento asíncrono
    w._worker = None              # Worker que ejecuta el pipeline
    w._last_work_dir = ""         # Último directorio de salida generado
    w._last_validation = ""       # Estado de validación: "OK" | "Con errores" | ""

    # ========================================================================
    # FUNCIONES HELPER: LOGGING Y GESTIÓN DE ESTADO
    # ========================================================================
    def append_log(level: str, message: str):
        """
        Agrega un mensaje al sistema de seguimiento (tabla y consola).
        
        Args:
            level: Nivel del mensaje ("ERROR", "WARN", "OK", "INFO")
            message: Contenido del mensaje
        """
        ts = _now()
        emoji = _emoji_for(level)
        
        # Agregar fila a la tabla de resumen
        if hasattr(w, "logTable"):
            row = w.logTable.rowCount(); w.logTable.insertRow(row)
            for col, val in enumerate([ts, f"{emoji} {level}", message]):
                it = QTableWidgetItem(val)
                if col == 1:
                    if level == "ERROR": it.setForeground(Qt.red)
                    elif level == "WARN": it.setForeground(Qt.darkYellow)
                    elif level == "OK": it.setForeground(Qt.darkGreen)
                it.setToolTip(val); w.logTable.setItem(row, col, it)
            w.logTable.scrollToBottom()
        if hasattr(w, "logConsole"): w.logConsole.appendPlainText(f"{ts} | {emoji} {level} | {message}")

    def set_busy(busy: bool):
        if hasattr(w, "progressBar"): w.progressBar.setRange(0, 0 if busy else 100)

    def set_progress_bar_error_state():
        """Configura la barra de progreso en estado de error (roja, 100%)."""
        if hasattr(w, "progressBar"):
            w.progressBar.setValue(100)
            w.progressBar.setRange(0, 100)
            w.progressBar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #c0392b;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #fadbd8;
                }
                QProgressBar::chunk {
                    background-color: #e74c3c;
                    width: 1px;
                }
            """)

    def set_progress_bar_success_state():
        """Configura la barra de progreso en estado exitoso (verde, 100%)."""
        if hasattr(w, "progressBar"):
            w.progressBar.setValue(100)
            w.progressBar.setRange(0, 100)
            w.progressBar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #27ae60;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #d5f4e6;
                }
                QProgressBar::chunk {
                    background-color: #2ecc71;
                    width: 1px;
                }
            """)

    def reset_progress_bar_style():
        """Restaura el estilo por defecto de la barra de progreso."""
        if hasattr(w, "progressBar"):
            w.progressBar.setStyleSheet("")

    def enable_result_buttons(enabled: bool, has_dp: bool, out_dir: Path | None):
        if hasattr(w, "btnOpenOut"):        w.btnOpenOut.setEnabled(bool(enabled and out_dir and out_dir.exists()))
        if hasattr(w, "btnOpenDatapackage"): w.btnOpenDatapackage.setEnabled(enabled and has_dp)

    def update_email_button_state(work_dir: Path | None = None):
        """Habilita el botón si existe datapackage.json (desde label, work_dir o _last_work_dir)."""
        has_dp = False
        if hasattr(w, "lblDatapackagePath"):
            ptxt = (w.lblDatapackagePath.text() or "").strip()
            if ptxt and Path(ptxt).exists():
                has_dp = True
        if not has_dp and work_dir:
            cand = Path(work_dir) / "output" / "datapackage.json"
            has_dp = cand.exists()
        if not has_dp and getattr(w, "_last_work_dir", ""):
            cand = Path(w._last_work_dir) / "output" / "datapackage.json"
            has_dp = cand.exists()
        if hasattr(w, "btnEmailTemplate"):
            w.btnEmailTemplate.setEnabled(bool(has_dp))

    # ===== Acciones UI =====
    def choose_zip():
        path, _ = QFileDialog.getOpenFileName(
            w, "Seleccionar ZIP exportado de Wildlife Insights",
            str(Path.home()), "Archivos ZIP (*.zip)"
        )
        if path:
            w.leZip.setText(path)
            out_dir = str(Path(path).resolve().parent)
            if hasattr(w, "leOut"): w.leOut.setText(out_dir)
            append_log("INFO", f"Seleccionado: {path}")
            if hasattr(w, "btnProcess"): w.btnProcess.setEnabled(True)
            enable_result_buttons(False, False, None)
            update_email_button_state(None)

    def _set_path_label(lbl_name: str, path_obj):
        """Escribe una ruta candidata en el label (o vacío si no aplica), sin 'None\\...'.
        Acepta Path o str; ignora None."""
        if hasattr(w, lbl_name):
            txt = ""
            if path_obj is not None:
                try:
                    txt = str(Path(path_obj))
                except Exception:
                    txt = ""
            getattr(w, lbl_name).setText(txt)

    def _open_email_template_dialog(parent):
        """Diálogo de plantilla de correo (rellena desde datapackage.json)."""
        dp_path = ""
        
        # Estrategia 1: desde lblDatapackagePath
        if hasattr(parent, "lblDatapackagePath") and parent.lblDatapackagePath.text().strip():
            dp_path = parent.lblDatapackagePath.text().strip()
            print(f"DEBUG: Intentando desde lblDatapackagePath: {dp_path}")
        
        # Estrategia 2: desde _last_work_dir
        if not dp_path and getattr(parent, "_last_work_dir", ""):
            cand = Path(parent._last_work_dir) / "output" / "datapackage.json"
            if cand.exists(): 
                dp_path = str(cand)
                print(f"DEBUG: Encontrado en _last_work_dir: {dp_path}")
            else:
                print(f"DEBUG: No existe en _last_work_dir: {cand}")
        
        # Estrategia 3: buscar en directorio actual/reciente (fallback adicional)
        if not dp_path:
            # Buscar en el directorio de salida configurado
            if hasattr(parent, "leOut") and parent.leOut.text().strip():
                out_dir = Path(parent.leOut.text().strip())
                # Buscar directorios que empiecen con "WI2CamtrapDP_"
                potential_dirs = list(out_dir.glob("WI2CamtrapDP_*"))
                if potential_dirs:
                    # Tomar el más reciente
                    latest_dir = max(potential_dirs, key=lambda x: x.stat().st_mtime)
                    cand = latest_dir / "output" / "datapackage.json"
                    if cand.exists():
                        dp_path = str(cand)
                        print(f"DEBUG: Encontrado por búsqueda en output dir: {dp_path}")
        
        # Verificación final
        if not dp_path or not Path(dp_path).exists():
            error_msg = f"No se encontró el archivo datapackage.json."
            if dp_path:
                error_msg += f"\nRuta buscada: {dp_path}"
            if getattr(parent, "_last_work_dir", ""):
                error_msg += f"\nDirectorio de trabajo: {parent._last_work_dir}"
            QMessageBox.information(parent, "No disponible", error_msg)
            return
            
        try:
            with open(dp_path, "r", encoding="utf-8") as f:
                dp = json.load(f)
        except Exception as e:
            QMessageBox.warning(parent, "Error", f"No se pudo leer datapackage.json:\n{e}")
            return

        def g(key, default=""):
            v = dp.get(key, default)
            return "" if v is None else str(v).strip()

        org   = g("organization", g("title", "")) or "(organización)"
        name  = g("mainContributorName", "")
        email = g("mainContributorEmail", "")
        desc  = g("description", g("title", "")) or "(descripción breve del conjunto de datos)"

        asunto = f"Publicación datos Cámaras Trampa – {org}"
        cuerpo = (
            "Para: sib@humboldt.org.co\n\n"
            f"Asunto: {asunto}\n\n"
            "Apreciado equipo SIB Colombia,\n\n"
            f"Mi nombre es {name or '(tu nombre)'}, de {org}. "
            "Solicito apoyo para publicar un conjunto de datos de cámaras trampa que preparé y validé con WI2CamtrapDP (formato Camtrap-DP).\n\n"
            f"Descripción del conjunto de datos: {desc}\n\n"
            "Adjunto el paquete Camtrap-DP (ZIP) que incluye:\n"
            "• deployments.csv\n"
            "• media.csv\n"
            "• observations.csv\n"
            "• datapackage.json\n\n"
            "Quedo atento(a) a comentarios o ajustes necesarios para continuar con la publicación.\n\n"
            "Cordial saludo,\n"
            f"{name or ''}\n{org}\n{('Correo: ' + email) if email else ''}\n"
        )

        dlg = QDialog(parent); dlg.setWindowTitle("Modelo de correo electrónico recomendado"); dlg.setModal(True)
        lay = QVBoxLayout(dlg); lay.addWidget(QLabel("<b>Modelo de correo electrónico recomendado:</b>"))
        txt = QTextEdit(dlg); txt.setReadOnly(True); txt.setPlainText(cuerpo); txt.setMinimumSize(600, 380); lay.addWidget(txt)
        btns = QDialogButtonBox(dlg); btnCopiar = btns.addButton("Copiar al portapapeles", QDialogButtonBox.ActionRole)
        btnCerrar = btns.addButton(QDialogButtonBox.Close); lay.addWidget(btns)
        btnCopiar.clicked.connect(lambda: (QtWidgets.QApplication.clipboard().setText(txt.toPlainText()),
                                           QMessageBox.information(dlg, "Copiado", "La plantilla se copió al portapapeles.")))
        btnCerrar.clicked.connect(dlg.accept)
        dlg.exec_()

    # Conexiones
    if hasattr(w, "btnZip"): w.btnZip.clicked.connect(choose_zip)
    if hasattr(w, "btnEmailTemplate"): w.btnEmailTemplate.clicked.connect(lambda: _open_email_template_dialog(w))

    # Limpiar
    def clear_ui():
        running = False
        if w._thread:
            try: running = w._thread.isRunning()
            except RuntimeError: running = False
        if running:
            QMessageBox.information(w, "En ejecución", "Espera a que termine para limpiar."); return
        for name in ["leZip","leOut","lblStatus","lblDeploymentsPath","lblMediaPath",
                     "lblObservationsPath","lblDatapackagePath","lblZipPath","lblLogPath","lblValidateResult"]:
            if hasattr(w, name):
                obj = getattr(w, name); (obj.clear() if hasattr(obj,"clear") else obj.setText(""))
        if hasattr(w,"logConsole"): w.logConsole.clear()
        if hasattr(w,"logTable"):   w.logTable.setRowCount(0)
        if hasattr(w,"progressBar"): 
            w.progressBar.setValue(0)
            w.progressBar.setRange(0,100)
            reset_progress_bar_style()
        if hasattr(w,"lblStatus"): 
            w.lblStatus.setStyleSheet("")  # Restaurar estilo por defecto
        if hasattr(w,"btnProcess"): w.btnProcess.setEnabled(bool(getattr(w,"leZip",None) and w.leZip.text().strip()))
        if hasattr(w,"btnClear"):   w.btnClear.setEnabled(False)
        update_email_button_state(None)
        enable_result_buttons(False, False, None)
        w._last_work_dir = ""
        w._last_validation = ""

    if hasattr(w, "btnClear"): w.btnClear.clicked.connect(clear_ui)

    # Procesar
    def on_process():
        zip_txt = w.leZip.text().strip() if hasattr(w, "leZip") else ""
        if not zip_txt or not Path(zip_txt).exists():
            QMessageBox.warning(w, "Falta ZIP", "Selecciona un archivo .zip válido."); return
        try: images_files = _detect_initiative_zip(Path(zip_txt))
        except Exception as e:
            QMessageBox.warning(w, "ZIP inválido", f"No se pudo inspeccionar el ZIP:\n{e}"); return
        if images_files > 1:
            msg = (f"Se detectaron {images_files} archivos 'images_*.csv'. Parece una exportación de una INICIATIVA. "
                   "Esta utilidad solo procesa PROYECTOS.")
            append_log("WARN", msg); QMessageBox.warning(w, "No soportado (Iniciativa)", msg)
            if hasattr(w,"lblStatus"): w.lblStatus.setText("Cancelado")
            set_busy(False); enable_result_buttons(False, False, None); update_email_button_state(None); return

        out_dir = str(Path(zip_txt).resolve().parent)
        if hasattr(w, "leOut"): w.leOut.setText(out_dir)

        options = {
            "timezone_hint": (w.cbTimezone.currentData() if hasattr(w, "cbTimezone") else "America/Bogota"),
            "validate": (w.chkValidate.isChecked() if hasattr(w, "chkValidate") else True),
            "make_zip": (w.chkMakeZip.isChecked() if hasattr(w, "chkMakeZip") else True),
            "open_folder": (w.chkOpenFolder.isChecked() if hasattr(w, "chkOpenFolder") else False),
            "overwrite": (w.chkOverwrite.isChecked() if hasattr(w, "chkOverwrite") else False),
        }

        if hasattr(w, "lblStatus"): 
            w.lblStatus.setText("🔄 Procesando…")
            w.lblStatus.setStyleSheet("")  # Restaurar estilo por defecto
        reset_progress_bar_style()
        set_busy(True)
        if hasattr(w,"btnProcess"): w.btnProcess.setEnabled(False)
        if hasattr(w,"btnClear"):   w.btnClear.setEnabled(False)
        update_email_button_state(None)
        if hasattr(w,"logConsole"): w.logConsole.clear()
        if hasattr(w,"logTable"):   w.logTable.setRowCount(0)
        if hasattr(w, "lblValidateResult"): w.lblValidateResult.setText("")
        append_log("INFO", "→ Procesando…")
        enable_result_buttons(False, False, None)

        th = QThread(); worker = Worker(Path(zip_txt), Path(out_dir), options); worker.moveToThread(th)
        w._thread, w._worker = th, worker
        th.started.connect(worker.run)

        def on_progress(pct: int, msg: str):
            if msg:
                append_log(_level_from_msg(msg), msg)
                low = msg.lower()
                low_norm = low.replace("ó","o").replace("á","a")
                if ("validación:" in low) or ("validacion:" in low_norm):
                    w._last_validation = "OK" if (" ok" in low or " ok" in low_norm) else "Con errores"
                    if hasattr(w, "lblValidateResult"):
                        w.lblValidateResult.setText(w._last_validation)

            if hasattr(w,"progressBar") and pct >= 0:
                if w.progressBar.minimum() == 0 and w.progressBar.maximum() == 0: w.progressBar.setRange(0,100)
                w.progressBar.setValue(min(100, pct))

        from typing import Optional

        def _find_best_workdir(base_dir: Path, job_name: str) -> Optional[Path]:
            """
            Busca la carpeta más reciente tipo WI2CamtrapDP_<job_name>[_N]
            dentro de base_dir. Devuelve None si no hay coincidencias.
            """
            patt = f"WI2CamtrapDP_{job_name}"
            cands = []
            try:
                for p in base_dir.glob(patt + "*"):
                    if p.is_dir():
                        cands.append((p.stat().st_mtime, p))
                cands.sort(reverse=True)
                return cands[0][1] if cands else None
            except Exception:
                return None


        def on_finished(ok: bool, work_dir: str, message: str):
            # 0) Estado visual mejorado
            set_busy(False)
            
            if ok:
                # Proceso exitoso: barra verde y mensaje claro
                append_log("OK", message)
                append_log("INFO", "✅ Revise la sección 'Resultados' para acceder a los archivos generados.")
                if hasattr(w, "lblStatus"): 
                    w.lblStatus.setText("✅ Proceso completado con éxito")
                    w.lblStatus.setStyleSheet("")
                set_progress_bar_success_state()
            else:
                # Proceso con errores: barra roja y mensaje con instrucciones
                append_log("ERROR", message)
                if hasattr(w, "lblStatus"): 
                    w.lblStatus.setText("❌ Ejecución detenida por errores - Requiere revisión")
                    w.lblStatus.setStyleSheet("color: #c0392b; font-weight: bold;")
                set_progress_bar_error_state()
                append_log("INFO", "🔄 Para volver a procesar: revise los errores en el seguimiento (pestaña '📝 Detalles'), corrija los datos de entrada y haga clic en 'Limpiar' para reiniciar.")

            # 1) Normaliza/detecta el work_dir real
            base_out_dir = Path(w.leOut.text().strip()) if hasattr(w, "leOut") and w.leOut.text().strip() else None
            job_name = Path(zip_txt).stem
            wd = None

            # preferir el que retorna el processor
            if work_dir and str(work_dir).strip().lower() != "none":
                wd = Path(work_dir)

            # si no existe, intentar descubrir el más reciente (maneja sufijos _2, _3, ...)
            if not wd or not wd.exists():
                if base_out_dir:
                    best = _find_best_workdir(base_out_dir, job_name)
                    if best and best.exists():
                        wd = best

            # si aún no hay, no seguimos (evitamos rutas fantasma tipo "None\output\...")
            if not wd or not wd.exists():
                w._last_work_dir = ""
                # limpiar labels de resultado
                for nm in ("lblDeploymentsPath","lblMediaPath","lblObservationsPath","lblDatapackagePath","lblZipPath"):
                    if hasattr(w, nm): getattr(w, nm).setText("")
                # desactivar plantilla y botones
                enable_result_buttons(False, False, None)
                update_email_button_state(None)
                if hasattr(w,"btnProcess"): w.btnProcess.setEnabled(True)
                if hasattr(w,"btnClear"):   w.btnClear.setEnabled(True)
                
                # Solo mostrar mensaje genérico si NO es un error de datos conocido
                msg_lower = message.lower()
                is_known_error = any([
                    "no cv result" in msg_lower,
                    "validación fallida" in msg_lower or "validacion fallida" in msg_lower,
                    "validación de taxonomía" in msg_lower or "validacion de taxonomia" in msg_lower,
                    "datos incompletos" in msg_lower,
                    "campo requerido" in msg_lower,
                    "acción requerida" in msg_lower or "accion requerida" in msg_lower,
                    "registros afectados" in msg_lower
                ])
                
                if not is_known_error:
                    append_log("WARN", "⚠️ No se generaron archivos de salida. Revisa los errores anteriores para más detalles.")
                return

            # guardar para próximas acciones
            w._last_work_dir = str(wd)

            # 2) Construye rutas esperadas y **escríbelas SIEMPRE** (sin prefijo None)
            out = wd / "output"
            zip_name = f"WI2CamtrapDP_{job_name}.zip"
            def _set_path_label(lbl_name: str, p: Path | None):
                if hasattr(w, lbl_name):
                    getattr(w, lbl_name).setText(str(p) if p else "")

            _set_path_label("lblDeploymentsPath",  out / "deployments.csv"   if out else None)
            _set_path_label("lblMediaPath",        out / "media.csv"         if out else None)
            _set_path_label("lblObservationsPath", out / "observations.csv"  if out else None)
            _set_path_label("lblDatapackagePath",  out / "datapackage.json"  if out else None)
            if hasattr(w, "chkMakeZip") and w.chkMakeZip.isChecked():
                _set_path_label("lblZipPath", wd / zip_name)
            else:
                _set_path_label("lblZipPath", None)

            # oculta la fila "Log:" del panel de resultados (si existe)
            for nm in ("labelLog", "lblLogPath"):
                if hasattr(w, nm):
                    getattr(w, nm).hide()

            # 3) Verificación real en disco + habilitar botones/plantilla
            dp_file = out / "datapackage.json"
            has_dp  = dp_file.exists()
            enable_result_buttons(True, has_dp, out)
            update_email_button_state(wd)  # 1ª pasada
            # 2ª pasada por si el FS tarda un instante
            QtCore.QTimer.singleShot(150, lambda: update_email_button_state(wd))

            # 4) Mostrar resultado de validación si no vino por log (mejora UX)
            if hasattr(w, "lblValidateResult") and not (w.lblValidateResult.text() or "").strip():
                # si existe dp.json damos por buena la ejecución; el processor ya validó si estaba marcado
                w.lblValidateResult.setText("OK" if has_dp else "")

            if ok and hasattr(w,"chkOpenFolder") and w.chkOpenFolder.isChecked() and out.exists():
                os.startfile(str(out))
            if hasattr(w,"btnProcess"): w.btnProcess.setEnabled(True)
            if hasattr(w,"btnClear"):   w.btnClear.setEnabled(True)


        worker.progress.connect(on_progress)
        worker.finished.connect(on_finished)
        worker.finished.connect(th.quit)
        worker.finished.connect(worker.deleteLater)
        th.finished.connect(th.deleteLater)
        th.start(); set_busy(True)

    if hasattr(w, "btnProcess"): w.btnProcess.clicked.connect(on_process)
    if hasattr(w, "btnEmailTemplate"): w.btnEmailTemplate.clicked.connect(lambda: _open_email_template_dialog(w))

    # Scroll wrapper + promoción de atributos
    def _make_scrollable_and_flexible(window: QtWidgets.QWidget):
        root = window.centralWidget() if hasattr(window, "centralWidget") else window
        for wid in root.findChildren((QGroupBox, QFrame, QWidget)):
            sp = wid.sizePolicy(); sp.setHorizontalPolicy(QtWidgets.QSizePolicy.Preferred)
            sp.setVerticalPolicy(QtWidgets.QSizePolicy.Preferred); wid.setSizePolicy(sp)
        for lbl in root.findChildren(QLabel): lbl.setWordWrap(True)
        if hasattr(window, "centralWidget"):
            scroll = QtWidgets.QScrollArea(window); scroll.setWidget(root); scroll.setWidgetResizable(True)
            window.setCentralWidget(scroll); return window
        mw = QtWidgets.QMainWindow(); mw.setWindowTitle(window.windowTitle())
        try: mw.setWindowIcon(window.windowIcon())
        except Exception: pass
        scroll = QtWidgets.QScrollArea(mw); scroll.setWidget(window); scroll.setWidgetResizable(True)
        mw.setCentralWidget(scroll); mw.resize(window.size())
        mw.setMinimumSize(max(window.minimumWidth(),1000), max(window.minimumHeight(),700))
        mw._inner = window; return mw

    def _promote_children_to_attrs(window: QtWidgets.QWidget):
        root = getattr(window, "_inner", window)
        for child in root.findChildren(QtWidgets.QWidget):
            name = child.objectName()
            if name and not hasattr(window, name):
                try: setattr(window, name, child)
                except Exception: pass

    wrapper = _make_scrollable_and_flexible(w)
    w = wrapper
    _promote_children_to_attrs(w)

    # Asegura que el botón “promocionado” tenga el slot conectado
    if hasattr(w, "btnEmailTemplate"):
        try:
            w.btnEmailTemplate.clicked.disconnect()
        except Exception:
            pass
        w.btnEmailTemplate.clicked.connect(lambda: _open_email_template_dialog(w))

    # Mostrar ventana
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
