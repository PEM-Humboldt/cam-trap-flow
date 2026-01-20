"""
Img2WI - Interfaz Gráfica de Extracción de Imágenes desde Videos
==================================================================

Interfaz de usuario desarrollada con PyQt5 para la conversión de videos de cámaras trampa
en secuencias de imágenes individuales para análisis o carga en Wildlife Insights.

Características principales:
    - Diseño intuitivo y responsivo con PyQt5
    - Selección de carpeta de proyecto con validación automática
    - Configuración de offset (segundos por imagen) mediante selector
    - Procesamiento asíncrono con QThread (UI no se bloquea)
    - Sistema de logs estructurado con tabla de tres columnas (Hora, Tipo, Mensaje)
    - Barra de progreso en tiempo real
    - Cronómetro de duración del procesamiento
    - Acceso directo a carpeta de resultados
    - Validación de formatos soportados (.MP4, .MOV, .AVI)
    - Generación automática de carpeta de salida con timestamp

Arquitectura:
    - VideoProcessorWindow: Ventana principal con todos los controles
    - Worker: Objeto QObject que ejecuta el procesamiento en hilo separado
    - Sistema de señales PyQt para comunicación segura entre hilos

Módulo: ui_main.py (Interfaz de usuario)
Autor: Cristian C. Acevedo
Organización: Instituto Humboldt - Red OTUS
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
Licencia: Ver THIRD_PARTY_NOTICES.txt
"""

import os
import sys
import time
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QTime, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QTextOption, QPixmap, QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QComboBox, QGroupBox, QSizePolicy,
    QFrame, QTableWidget, QTableWidgetItem, QProgressBar
)

# ==============================================================================
# UTILIDADES DE RECURSOS
# ==============================================================================
# Funciones auxiliares para manejo de recursos (iconos, imágenes) en diferentes
# entornos: desarrollo (código fuente) y producción (ejecutable PyInstaller).

def resource_path(relative: str) -> str:
    """
    Localiza recursos (iconos, imágenes) tanto en desarrollo como en ejecutable.
    
    Cuando PyInstaller genera un ejecutable one-file, descomprime los recursos
    en un directorio temporal (sys._MEIPASS). Esta función maneja ambos casos.
    
    Args:
        relative: Ruta relativa al recurso (ej: "../resources/icons/app_icon.png")
    
    Returns:
        str: Ruta absoluta al recurso, ajustada según el entorno de ejecución
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    p1 = (base / relative).resolve()
    if p1.exists():
        return str(p1)
    rel2 = relative.replace("../", "")
    p2 = (base / rel2).resolve()
    return str(p2)


# ==============================================================================
# VENTANA PRINCIPAL DE LA APLICACIÓN
# ==============================================================================

class VideoProcessorWindow(QWidget):
    """
    Ventana principal de la aplicación Img2WI.
    
    Proporciona una interfaz completa para:
        - Selección de carpeta de proyecto con videos
        - Configuración de parámetros de extracción (offset)
        - Monitoreo de procesamiento con logs estructurados
        - Visualización de progreso y tiempo transcurrido
        - Acceso rápido a resultados
    
    Atributos:
        input_path (Path): Carpeta seleccionada con los videos a procesar
        output_path (Path): Carpeta de salida donde se guardan las imágenes
        thread (QThread): Hilo para procesamiento asíncrono
        worker (Worker): Objeto que ejecuta el procesamiento en el hilo
        timer (QTimer): Cronómetro para medir duración del proceso
    """
    def __init__(self):
        super().__init__()

        # Variables de estado de la aplicación
        self.input_path: Path = None   # carpeta con videos seleccionada por el usuario
        self.output_path: Path = None  # carpeta única de salida generada automáticamente

        # Configuración de la ventana principal
        self.setWindowTitle("Extractor de Imágenes - Cámaras Trampa")
        self.setMinimumSize(900, 600)
        self.resize(1100, 720)
        self.setWindowIcon(QIcon(resource_path("../resources/icons/app_icon.png")))

        root = QVBoxLayout(self)
        root.setSpacing(10)

        # -------- Encabezado ---------------------------------------------------
        title = QLabel("🖼️ Extractor de Imágenes desde Videos de Cámaras Trampa")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E4053;")
        root.addWidget(title)

        description = QLabel(
            "Esta herramienta convierte automáticamente videos capturados con cámaras trampa "
            "en imágenes individuales para su análisis o carga en Wildlife Insights.<br><br>"
            "<b>Formatos soportados:</b> <code>.MP4</code>, <code>.MOV</code> y <code>.AVI</code>.<br>"
            "Todas las imágenes se guardan en <b>una sola carpeta</b> con el nombre "
            "<code>Img2WI_<i>&lt;nombre_de_su_carpeta_de_proyecto&gt;</i>_<i>HH-MM_DD_MM_AAAA</i></code>."
        )
        description.setTextFormat(Qt.RichText)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        root.addWidget(description)

        # -------- Guía rápida --------------------------------------------------
        guide_group = QGroupBox("🧭 Guía rápida de uso")
        guide_v = QVBoxLayout(guide_group)
        guide = QLabel(
            "<div style='text-align:center;'>"
            "<ol style='display:inline-block; text-align:left; margin:0; padding-left:22px;'>"
            "<li>Haga clic en <b>“Seleccionar carpeta del proyecto (con videos)”</b> y elija su carpeta.</li>"
            "<li>En <b>Configuración</b>, seleccione cada cuántos <b>segundos por imagen (offset)</b> desea extraer (sugerido: <b>1</b>).</li>"
            "<li>Presione <b>“Iniciar procesamiento”</b>. El avance y los mensajes aparecen en el panel inferior.</li>"
            "<li>Las imágenes quedan en una <b>carpeta única</b> junto a su proyecto, llamada "
            "<code>Img2WI_<i>&lt;nombre_de_su_carpeta_de_proyecto&gt;</i>_<i>HH-MM_DD_MM_AAAA</i></code>.</li>"
            "</ol>"
            "</div>"
        )
        guide.setTextFormat(Qt.RichText)
        guide.setAlignment(Qt.AlignCenter)
        guide.setWordWrap(True)
        guide_v.addWidget(guide)
        root.addWidget(guide_group)

        # -------- Control + Configuración -------------------------------------
        ctrl_group = QGroupBox("📦 Control y configuración")
        ctrl_v = QVBoxLayout(ctrl_group)

        # (1) Seleccionar carpeta
        self.btn_select = QPushButton("📁 Seleccionar carpeta del proyecto (con videos)")
        self.btn_select.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_select.clicked.connect(self.select_folder)
        ctrl_v.addWidget(self.btn_select)

        # (2) Offset
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Seleccione cada cuántos segundos desea extraer una imagen del video:"))
        self.offset_selector = QComboBox()
        self.offset_selector.addItems(["0.5", "1", "2", "3", "4", "5"])
        self.offset_selector.setCurrentText("1")
        self.offset_selector.setFixedWidth(120)
        row2.addWidget(self.offset_selector)
        row2.addStretch(1)
        ctrl_v.addLayout(row2)

        # (3) Iniciar + progreso
        row3 = QHBoxLayout()
        self.btn_start = QPushButton("▶️ Iniciar procesamiento")
        self.btn_start.setEnabled(False)  # Deshabilitado hasta que haya carpeta
        self.btn_start.clicked.connect(self.start_processing)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        row3.addWidget(self.btn_start)
        row3.addWidget(self.progress, 1)
        ctrl_v.addLayout(row3)

        # (4) Acciones post-proceso
        row4 = QHBoxLayout()
        self.btn_open_out = QPushButton("🗂 Abrir carpeta de imágenes")
        self.btn_open_out.setEnabled(False)
        self.btn_open_out.clicked.connect(self.open_output_folder)

        self.btn_clear = QPushButton("🧹 Limpiar")
        self.btn_clear.setEnabled(False)
        self.btn_clear.clicked.connect(self.reset_ui)

        row4.addStretch(1)
        row4.addWidget(self.btn_open_out)
        row4.addWidget(self.btn_clear)
        ctrl_v.addLayout(row4)

        root.addWidget(ctrl_group)

        # -------- Tabla de logs (estructurada) --------------------------------
        self.log_table = QTableWidget(0, 3)
        self.log_table.setHorizontalHeaderLabels(["Hora", "Tipo", "Mensaje"])
        self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setEditTriggers(self.log_table.NoEditTriggers)
        self.log_table.setSelectionBehavior(self.log_table.SelectRows)
        self.log_table.setSelectionMode(self.log_table.SingleSelection)
        self.log_table.setMinimumHeight(260)
        root.addWidget(self.log_table, 1)

        # Mensaje inicial
        self._add_log("ok", "Esperando acción del usuario…")

        # -------- Separador + cronómetro --------------------------------------
        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setFrameShadow(QFrame.Sunken)
        root.addWidget(sep)

        self.timer_label = QLabel("⏱️ Tiempo: 00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self.timer_label)

        # Cronómetro
        self.timer = QTimer(self)
        self.time_elapsed = QTime(0, 0)
        self.timer.timeout.connect(self.update_timer)

        # -------- Pie (logo + citación) ---------------------------------------
        footer_sep = QFrame(); footer_sep.setFrameShape(QFrame.HLine); footer_sep.setFrameShadow(QFrame.Sunken)
        root.addWidget(footer_sep)

        footer_row = QHBoxLayout()
        logo_lbl = QLabel()
        logo_path = resource_path("../resources/icons/logo_humboldt.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            logo_lbl.setPixmap(pix.scaledToHeight(28, Qt.SmoothTransformation))
        logo_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        footer_row.addWidget(logo_lbl)

        cite_lbl = QLabel(
            "<b>Citar como</b>: Acevedo, C. C., & Diaz-Pulido, A. (2025). Gestión de datos de fototrampeo (v1.0.0) [Software]. "
            "Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. Publicado el 7 de septiembre de 2025."
        )
        cite_lbl.setWordWrap(True)
        cite_lbl.setAlignment(Qt.AlignCenter)
        cite_lbl.setStyleSheet("color:#555;")
        footer_row.addWidget(cite_lbl, 1)
        root.addLayout(footer_row)

        # Estilos base
        self.setStyleSheet("""
            QLabel { font-size: 10pt; }
            QPushButton {
                background-color: #f2f2f2; border: 1px solid #ccc; padding: 6px;
            }
            QPushButton:hover { background-color: #e6e6e6; }
            QGroupBox {
                font-weight: bold; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 5px 10px; }
        """)

        # Referencias de hilo/worker para procesamiento asíncrono
        self.thread: QThread = None
        self.worker: "Worker" = None

    # ==========================================================================
    # MÉTODOS AUXILIARES DE INTERFAZ
    # ==========================================================================
    
    def _add_log(self, level: str, message: str):
        """
        Añade una entrada a la tabla de logs con formato y color según el nivel.
        
        Args:
            level: Nivel del mensaje ("info", "warn", "ok", "error")
            message: Texto del mensaje a mostrar
        
        Colores por nivel:
            - info: Azul (#1f77b4) - Información general
            - warn: Amarillo (#e6a700) - Advertencias
            - ok: Verde (#2ca02c) - Éxito
            - error: Rojo (#d62728) - Errores
        """
        colors = {
            "info": QColor("#1f77b4"),  # azul
            "warn": QColor("#e6a700"),  # amarillo
            "ok":   QColor("#2ca02c"),  # verde
            "error":QColor("#d62728"),  # rojo
        }
        from datetime import datetime
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        titem = QTableWidgetItem(datetime.now().strftime("%H:%M:%S"))
        litem = QTableWidgetItem(level.upper())
        mitem = QTableWidgetItem(message)

        col = colors.get(level, QColor("#1f77b4"))
        litem.setForeground(col); mitem.setForeground(col)

        self.log_table.setItem(row, 0, titem)
        self.log_table.setItem(row, 1, litem)
        self.log_table.setItem(row, 2, mitem)
        self.log_table.scrollToBottom()

    def _log_from_backend(self, text: str):
        """
        Procesa mensajes del backend y los añade a los logs con el nivel correcto.
        
        Detecta prefijos emoji del backend y los mapea a niveles de log:
            ✅ -> ok (operación exitosa)
            ⚠️ -> warn (advertencia)
            ❌ -> error (error)
            🔵 -> info (información general)
        
        Args:
            text: Mensaje del backend (puede incluir emoji como prefijo)
        """
        msg = (text or "").strip()
        lvl = "info"
        if msg.startswith("✅"):
            lvl = "ok";   msg = msg.lstrip("✅ ").strip()
        elif msg.startswith("⚠️"):
            lvl = "warn"; msg = msg.lstrip("⚠️ ").strip()
        elif msg.startswith("❌"):
            lvl = "error";msg = msg.lstrip("❌ ").strip()
        elif msg.startswith("🔵"):
            lvl = "info"; msg = msg.lstrip("🔵 ").strip()
        self._add_log(lvl, msg)

    def reset_ui(self):
        """
        Reinicia la interfaz al estado inicial (sin proyecto seleccionado).
        
        Limpia:
            - Rutas de entrada/salida
            - Tabla de logs
            - Barra de progreso
            - Cronómetro
        
        Restablece el estado de botones:
            - Habilitado: Selector de carpeta y offset
            - Deshabilitado: Inicio, abrir carpeta, limpiar
        """
        self.input_path = None
        self.output_path = None
        self.log_table.setRowCount(0)
        self._add_log("ok", "Esperando acción del usuario…")

        self.progress.setValue(0)
        self.time_elapsed = QTime(0, 0)
        self.timer_label.setText("⏱️ Tiempo: 00:00")

        # Estado inicial: sólo se puede seleccionar carpeta
        self.btn_select.setEnabled(True)
        self.offset_selector.setEnabled(True)
        self.btn_start.setEnabled(False)       # <- permanece deshabilitado hasta seleccionar
        self.btn_open_out.setEnabled(False)
        self.btn_clear.setEnabled(False)

    def open_output_folder(self):
        """
        Abre el explorador de archivos en la carpeta de salida con las imágenes.
        
        Usa os.startfile (Windows) para abrir la carpeta en el Explorador.
        Muestra mensaje informativo si la carpeta aún no existe.
        """
        try:
            if self.output_path and self.output_path.exists():
                os.startfile(str(self.output_path))
            else:
                QMessageBox.information(self, "Abrir carpeta", "La carpeta de salida no existe todavía.")
        except Exception as e:
            QMessageBox.warning(self, "Abrir carpeta", f"No se pudo abrir la carpeta: {e}")

    # ==========================================================================
    # MÉTODOS DE ACCIÓN DEL USUARIO
    # ==========================================================================
    
    def _scan_videos(self, base: Path):
        """
        Escanea recursivamente la carpeta seleccionada buscando archivos de video.
        
        Clasifica los archivos en:
            - Soportados: .MP4, .MOV, .AVI (pueden procesarse)
            - No soportados: Otros formatos de video comunes (feedback al usuario)
        
        Args:
            base: Carpeta raíz donde buscar videos
        
        Returns:
            tuple: (videos_válidos, videos_no_soportados, todos_los_archivos)
        """
        valid_exts = {".mp4", ".mov", ".avi"}
        common_video_exts = {".mov", ".mkv", ".wmv", ".flv", ".mpg", ".mpeg", ".m4v",
                             ".3gp", ".webm", ".ts", ".vob", ".asf", ".avi", ".mp4"}
        all_files = list(base.rglob("*"))
        vids_ok   = [p for p in all_files if p.suffix.lower() in valid_exts]
        vids_skip = [p for p in all_files if p.suffix.lower() in common_video_exts
                     and p.suffix.lower() not in valid_exts]
        return vids_ok, vids_skip, all_files

    def select_folder(self):
        """
        Permite al usuario seleccionar la carpeta del proyecto con videos.
        
        Proceso:
            1. Abre diálogo de selección de carpeta
            2. Genera nombre de carpeta de salida con timestamp
            3. Valida contenido (busca videos soportados)
            4. Muestra advertencias si no hay archivos o formatos no soportados
            5. Habilita botón de inicio si hay videos válidos
        
        Formato de carpeta de salida:
            Img2WI_<nombre_proyecto>_HH-MM_DD_MM_AAAA
        """
        folder = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta del proyecto con los videos")
        if not folder:
            self._add_log("warn", "No se seleccionó ningún proyecto.")
            self.btn_start.setEnabled(False)
            return

        # Carpeta elegida
        self.input_path = Path(folder)

        # TIMESTAMP seguro para Windows: HH-MM_DD_MM_AAAA
        ts = time.strftime("%H-%M_%d_%m_%Y")
        self.output_path = self.input_path.parent / f"Img2WI_{self.input_path.name}_{ts}"

        # Validaciones tempranas
        vids_ok, vids_skip, all_files = self._scan_videos(self.input_path)
        if not all_files:
            QMessageBox.information(self, "Carpeta vacía", "La carpeta seleccionada está vacía.")
            self._add_log("warn", "Carpeta vacía.")
            self.btn_start.setEnabled(False)
            return
        if not vids_ok and vids_skip:
            # Tiene videos pero ninguno soportado
            sample = "\n".join(f"• {p.name}" for p in vids_skip[:10])
            QMessageBox.information(
                self, "Formatos no soportados",
                "Se encontraron videos con formatos no soportados.\n"
                "Soportados: .MP4, .MOV, .AVI\n\nEjemplos:\n" + sample +
                ("\n…" if len(vids_skip) > 10 else "")
            )
            self._add_log("warn", "Se encontraron videos con formatos no soportados.")
            self.btn_start.setEnabled(False)
            return

        # Feedback en logs
        self._add_log("ok",   f"Proyecto: {self.input_path}")
        self._add_log("info", f"Salida: {self.output_path}")

        # Habilitar inicio
        self.btn_start.setEnabled(bool(vids_ok))

    def start_processing(self):
        """
        Inicia el procesamiento de videos en un hilo separado.
        
        Flujo:
            1. Valida que haya carpeta seleccionada
            2. Obtiene configuración de offset del usuario
            3. Deshabilita controles durante el procesamiento
            4. Inicia cronómetro
            5. Crea Worker y QThread
            6. Conecta señales para comunicación segura entre hilos
            7. Inicia el hilo de procesamiento
        
        Señales conectadas:
            - worker.status -> Actualización de logs
            - worker.progress -> Actualización de barra de progreso
            - worker.finished -> Finalización y limpieza
        """
        if not self.input_path:
            QMessageBox.warning(self, "Proyecto no seleccionado", "Primero debes seleccionar una carpeta con videos.")
            return

        # Offset
        txt = self.offset_selector.currentText()
        offset = None if txt == "None" else float(txt)

        # Preparación UI
        self.progress.setValue(0)
        self.btn_select.setEnabled(False)
        self.offset_selector.setEnabled(False)
        self.btn_start.setEnabled(False)    # <- deshabilitado al iniciar
        self.btn_open_out.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self._add_log("info", "Iniciando procesamiento…")

        # Cronómetro
        self.time_elapsed = QTime(0, 0)
        self.timer_label.setText("⏱️ Tiempo: 00:00")
        self.timer.start(1000)

        # Hilo/worker
        self.worker = Worker(self.input_path, self.output_path, offset)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Conexiones
        self.thread.started.connect(self.worker.run)
        self.worker.status.connect(self._log_from_backend)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.finish_processing)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def update_timer(self):
        """
        Actualiza el cronómetro cada segundo durante el procesamiento.
        
        Llamado automáticamente por QTimer.timeout cada 1000ms.
        """
        self.time_elapsed = self.time_elapsed.addSecs(1)
        self.timer_label.setText(f"⏱️ Tiempo: {self.time_elapsed.toString('mm:ss')}")

    def finish_processing(self, total_videos: int, total_images: int):
        """
        Finaliza el procesamiento y actualiza la UI con los resultados.
        
        Args:
            total_videos: Número total de videos procesados
            total_images: Número total de imágenes generadas
        
        Acciones:
            - Detiene el cronómetro
            - Muestra estadísticas finales en logs
            - Habilita botones de post-procesamiento (abrir carpeta, limpiar)
            - Mantiene botón de inicio deshabilitado hasta limpiar
        """
        self.timer.stop()
        tiempo = self.time_elapsed.toString("mm:ss")
        self._add_log("ok", f"Proceso completado. Videos: {total_videos} · Imágenes: {total_images}")
        self.timer_label.setText(f"⏱️ Duración del procesamiento: {tiempo}")

        # Activar post-proceso
        self.btn_open_out.setEnabled(True)
        self.btn_clear.setEnabled(True)
        # Mantener Start deshabilitado hasta que el usuario limpie o seleccione otra carpeta
        self.btn_start.setEnabled(False)


# ==============================================================================
# WORKER PARA PROCESAMIENTO ASÍNCRONO
# ==============================================================================

class Worker(QObject):
    """
    Worker que ejecuta el procesamiento de videos en un hilo separado.
    
    Implementa el patrón Worker/QThread de PyQt5 para mantener la UI responsiva
    durante operaciones largas. Se comunica con la UI principal mediante señales.
    
    Señales:
        finished: Se emite al terminar con (total_videos, total_imagenes)
        status: Se emite para cada mensaje de log del backend
        progress: Se emite para actualizar la barra de progreso (0-100)
    
    Atributos:
        input_path (Path): Carpeta con los videos a procesar
        output_path (Path): Carpeta donde se guardarán las imágenes
        offset: Segundos entre imágenes (configurado por el usuario)
    """
    finished = pyqtSignal(int, int)   # total_videos, total_imagenes
    status   = pyqtSignal(str)        # logs del backend
    progress = pyqtSignal(int)        # 0..100

    def __init__(self, input_path: Path, output_path: Path, offset):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.offset = offset

    def _status_cb(self, msg: str):
        """Callback para emitir mensajes de estado al hilo principal."""
        self.status.emit(msg)

    def _progress_cb(self, val: int):
        """Callback para emitir progreso (0-100) al hilo principal."""
        self.progress.emit(int(val))

    def _count_images(self, root: Path) -> int:
        """
        Cuenta el total de imágenes generadas en la carpeta de salida.
        
        Args:
            root: Carpeta raíz donde buscar imágenes
        
        Returns:
            int: Número total de archivos .jpg, .jpeg y .png encontrados
        """
        exts = {".jpg", ".jpeg", ".png"}
        return sum(1 for p in root.glob("**/*") if p.is_file() and p.suffix.lower() in exts)

    def run(self):
        """
        Método principal ejecutado en el hilo separado.
        
        Proceso:
            1. Importa el módulo processor (evita importación circular)
            2. Llama a process_videos con callbacks para comunicación
            3. Cuenta imágenes generadas
            4. Emite señal finished con resultados
        
        Este método se ejecuta automáticamente cuando el QThread arranca.
        """
        from app.processor import process_videos
        total, _ = process_videos(
            self.input_path,
            self.output_path,
            update_status=self._status_cb,
            update_progress=self._progress_cb,
            offset=self.offset
        )
        total_images = self._count_images(self.output_path)
        self.finished.emit(total, total_images)


# ==============================================================================
# PUNTO DE ENTRADA ALTERNATIVO (PARA PRUEBAS)
# ==============================================================================

if __name__ == "__main__":
    # Este bloque permite ejecutar ui_main.py directamente para pruebas
    # En producción, la aplicación se inicia desde app/main.py
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = VideoProcessorWindow()
    w.show()
    sys.exit(app.exec_())
