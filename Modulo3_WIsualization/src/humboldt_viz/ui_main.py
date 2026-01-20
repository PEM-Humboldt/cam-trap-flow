"""
WIsualization - Interfaz Gráfica Principal de Visualización de Datos Wildlife Insights
=======================================================================================

Aplicación de escritorio para análisis y visualización de datos de fototrampeo exportados
desde Wildlife Insights. Proporciona herramientas científicas para generar visualizaciones
de alta calidad para estudios de biodiversidad y comportamiento animal.

Características principales:
    - Curvas de acumulación de especies con suavizado semilogarítmico y bootstrap
    - Visualización de rangos temporales de deployments por sitio
    - Análisis de patrones de actividad circadiana mediante KDE
    - Matrices espaciotemporales de presencia/ausencia de especies
    - Interfaz adaptable HiDPI con diseño responsivo
    - Carga asíncrona de datos con feedback de progreso
    - Exportación de gráficas en múltiples formatos (PNG, PDF, SVG, JPG)
    - Validación automática de calidad de datos
    - Filtros dinámicos por clase taxonómica, especie y rango temporal

Arquitectura de la aplicación:
    - Interfaz: PyQt5 con componentes reactivos y maximización automática
    - Visualización: Matplotlib embebido con FigureCanvas para gráficas interactivas
    - Datos: Pandas para procesamiento eficiente de datasets grandes
    - Threading: QThread para operaciones que consumen tiempo sin bloquear UI
    - Detección: Sistema automático de tipos de archivo y estructura de datos

Flujo de trabajo típico:
    1. Cargar archivo .zip exportado desde Wildlife Insights
    2. Detección automática de archivos images.csv y deployments.csv
    3. Seleccionar tipo de gráfica deseada
    4. Configurar filtros específicos (especies, fechas, opciones)
    5. Generar visualización científica
    6. Exportar en formato de alta resolución para publicación

Componentes principales:
    - DataLoadingThread: Carga asíncrona de archivos ZIP sin bloquear UI
    - MplCanvas: Lienzo de Matplotlib integrado en PyQt5
    - MainWindow: Ventana principal con toda la lógica de la aplicación

Módulo: ui_main.py
Autores: Cristian C. Acevedo, Angélica Díaz-Pulido
Organización: Instituto Humboldt - Programa de Evaluación y Monitoreo
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
Licencia: Ver LICENSE
"""

# =============================================================================
# IMPORTACIONES DEL SISTEMA Y UTILIDADES
# =============================================================================
import os
import sys
import zipfile
from collections import Counter
from pathlib import Path

# =============================================================================
# PROCESAMIENTO DE DATOS CIENTÍFICOS  
# =============================================================================
import pandas as pd

# =============================================================================
# INTERFAZ GRÁFICA Y COMPONENTES INTERACTIVOS
# =============================================================================
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit,
    QComboBox, QListWidget, QListWidgetItem, QSizePolicy, QFrame, QCheckBox,
    QDateEdit, QProgressBar, QStatusBar, QMenuBar, QAction
)

# =============================================================================
# VISUALIZACIÓN CIENTÍFICA INTEGRADA
# =============================================================================
# Matplotlib embebido en Qt para gráficas interactivas de alta calidad
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# =============================================================================
# MÓDULOS ESPECIALIZADOS DE LA APLICACIÓN
# =============================================================================
# Núcleo: Detección automática y normalización de datos Wildlife Insights
from humboldt_viz.core.io_detect import (
    leer_csv_desde_zip,
    detectar_df_images,
    detectar_df_deployments,
    normalizar_images,
)

# Motor de gráficas científicas con métodos estadísticos avanzados
from humboldt_viz.core.plots_mpl import (
    plot_accumulation_curve_mpl,
    plot_site_dates_mpl,
    plot_activity_hours_mpl,
    plot_presence_absence_mpl,
    _safe_tight_layout,
)


# =============================================================================
# FUNCIONES DE UTILIDAD PARA RECURSOS Y RUTAS
# =============================================================================

def _resource_path(*parts: str) -> str:
    """
    Construye rutas absolutas hacia archivos de recursos (iconos, imágenes, etc.).
    
    FUNCIONALIDAD:
    - Funciona tanto en desarrollo como en ejecutables compilados (.exe)
    - Resuelve automáticamente la ubicación de recursos según el contexto
    - Compatible con PyInstaller y ejecución directa desde código
    
    Args:
        *parts: Componentes de la ruta (ej: "icons", "logo.png")
        
    Returns:
        str: Ruta absoluta hacia el recurso solicitado
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    if base.name == "humboldt_viz":
        base = base.parent
    return str(base / "humboldt_viz" / "resources" / Path(*parts))


# =============================================================================
# CLASES PARA PROCESAMIENTO ASÍNCRONO Y VISUALIZACIÓN
# =============================================================================

class DataLoadingThread(QThread):
    """
    Hilo de procesamiento para carga asíncrona de datos desde archivos ZIP.
    
    PROPÓSITO:
    Evita que la interfaz se congele durante la carga de archivos grandes
    proporcionando feedback visual del progreso y manejo de errores robusto.
    
    SEÑALES:
    - progress: Emite porcentaje de progreso (0-100)
    - finished_loading: Emite datos cargados y mensaje de éxito
    - error_occurred: Emite mensaje de error si algo falla
    
    PROCESO:
    1. Abre el archivo ZIP de forma segura
    2. Identifica todos los archivos CSV dentro del ZIP
    3. Carga cada CSV progresivamente con feedback visual
    4. Maneja errores individuales sin detener el proceso completo
    5. Emite resultados finales o errores para que la UI responda
    """
    progress = pyqtSignal(int)              # Progreso de carga (0-100%)
    finished_loading = pyqtSignal(dict, str)  # (datos_cargados, mensaje_éxito)
    error_occurred = pyqtSignal(str)         # Mensaje de error
    
    def __init__(self, zip_path):
        super().__init__()
        self.zip_path = zip_path
    
    def run(self):
        """
        Método principal que ejecuta la carga de datos en hilo separado.
        
        ALGORITMO:
        1. Validar que el ZIP contiene archivos CSV
        2. Procesar cada CSV individualmente con manejo de errores
        3. Actualizar progreso para feedback visual en tiempo real
        4. Recopilar todos los resultados (exitosos y fallidos)
        5. Emitir señal de finalización con datos o error crítico
        """
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zf:
                # Filtrar solo archivos CSV (case-insensitive)
                miembros = [m for m in zf.namelist() if m.lower().endswith(".csv")]
                
                if not miembros:
                    self.error_occurred.emit("El .zip no contiene archivos .csv")
                    return
                    
                dfs_por_nombre = {}
                
                # Procesar cada CSV con actualización de progreso
                for i, m in enumerate(miembros):
                    self.progress.emit(int((i + 1) / len(miembros) * 100))
                    try:
                        df = leer_csv_desde_zip(zf, m)
                        dfs_por_nombre[m] = df
                    except Exception as e:
                        # Registrar error pero continuar con otros archivos
                        dfs_por_nombre[m] = f"ERROR: {e}"
                
                self.finished_loading.emit(dfs_por_nombre, "Datos cargados exitosamente")
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class MplCanvas(FigureCanvas):
    """
    Lienzo de Matplotlib integrado en PyQt5 para visualizaciones científicas.
    
    FUNCIONALIDAD:
    - Contenedor para todas las gráficas generadas por la aplicación
    - Se redimensiona automáticamente con la ventana
    - Proporciona placeholder informativo cuando no hay gráficas
    - Maneja la limpieza y actualización de contenido visual
    
    CARACTERÍSTICAS:
    - Resolución optimizada para pantallas modernas (100 DPI)
    - Tamaño inicial apropiado que se adapta al layout
    - Integración completa con el sistema de eventos de Qt
    """
    
    def __init__(self):
        """
        Inicializa el lienzo con configuración optimizada para gráficas científicas.
        """
        # Crear figura de Matplotlib con dimensiones y resolución apropiadas
        self.fig = Figure(figsize=(6, 4), dpi=100)
        super().__init__(self.fig)
        
        # Configurar política de redimensionamiento automático
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        
        # Mostrar mensaje de bienvenida hasta que se genere primera gráfica
        self.show_placeholder()

    def show_placeholder(self):
        """
        Muestra mensaje instructivo cuando no hay gráficas para mostrar.
        
        PROPÓSITO:
        Guía al usuario sobre los pasos necesarios para generar visualizaciones,
        evitando confusión con áreas en blanco.
        """
        self.fig.clf()  # Limpiar figura anterior
        ax = self.fig.add_subplot(111)
        ax.axis("off")  # Sin ejes para mensaje limpio
        ax.text(
            0.5, 0.5,
            "Aquí verás tu gráfica.\n\nCargar un .zip → elegir gráfica → ajustar filtros → «Graficar».",
            ha="center", va="center", fontsize=11, color="#666", 
            transform=ax.transAxes,
        )
        self.draw()

    def clear(self):
        """Limpia completamente el lienzo y fuerza redibujado."""
        self.fig.clf()
        self.draw()


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación WIsualization.
    
    RESPONSABILIDADES PRINCIPALES:
    1. Gestión de la interfaz de usuario completa
    2. Coordinación entre carga de datos y visualización
    3. Manejo de filtros dinámicos y configuraciones de gráficas
    4. Control de flujo de trabajo desde carga hasta exportación
    
    ARQUITECTURA DE LA UI:
    - Diseño responsivo que se adapta a diferentes resoluciones
    - Componentes dinámicos que aparecen según el tipo de gráfica
    - Sistema de caché para optimizar performance con datasets grandes
    - Threading para operaciones que consumen tiempo
    
    ESTADO DE LA APLICACIÓN:
    - Mantiene datos cargados en memoria para análisis múltiples
    - Cache inteligente de especies filtradas por clase taxonómica
    - Configuraciones persistentes de filtros y preferencias de usuario
    """
    
    def __init__(self):
        """
        Inicializa la ventana principal y todos sus componentes.
        
        PROCESO DE INICIALIZACIÓN:
        1. Configuración básica de ventana (título, icono, tamaño)
        2. Inicialización de variables de estado de la aplicación
        3. Construcción del layout completo de la interfaz
        4. Configuración de conexiones entre componentes
        5. Aplicación de estilos y temas visuales
        """
        super().__init__()

        # =============================================================================
        # CONFIGURACIÓN BÁSICA DE LA VENTANA PRINCIPAL
        # =============================================================================
        self.setWindowTitle("WIsualization (Visualización de datos de WI)")
        app_icon_path = _resource_path("icons", "app.ico")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        
        # Configuración responsiva para diferentes resoluciones de pantalla
        self.setMinimumSize(1200, 700)  # Mínimo funcional en pantallas pequeñas
        self.resize(1350, 750)          # Tamaño inicial optimizado para laptops 15"
        
        # Maximizar ventana para aprovechar espacio en monitores grandes
        self.showMaximized()

        # =============================================================================
        # VARIABLES DE ESTADO DE LA APLICACIÓN
        # =============================================================================
        # Datos principales cargados desde archivos ZIP
        self.dfs_por_nombre = {}        # Diccionario con todos los DataFrames cargados
        self.images_df = None           # DataFrame principal de registros de especies
        self.deployments_df = None      # DataFrame de información de deployments
        
        # Metadatos extraídos automáticamente durante la carga
        self._class_col = None          # Nombre real de columna de clase taxonómica
        self._images_min_date = None    # Fecha más temprana en los datos
        self._images_max_date = None    # Fecha más tardía en los datos
        
        # Sistema de caché para optimización de rendimiento
        self._especies_cache = {}       # Cache de especies filtradas por clase
        self._last_class_filter = None # Último filtro aplicado (para detectar cambios)

        # ---------- Encabezado centrado y compacto ----------
        self.header_title = QLabel("📊 WIsualization — Visualización de datos de WI")
        self.header_title.setAlignment(Qt.AlignCenter)
        self.header_title.setStyleSheet("font-size:16px; font-weight:700; color:#000;")

        self.header_desc = QLabel(
            "Explora datos de fototrampeo de <b>proyectos e iniciativas</b> a partir de un ZIP de Wildlife Insights. "
            "Genera curvas de acumulación, rangos por sitio, horarios de actividad y matrices de presencia/ausencia."
        )
        self.header_desc.setAlignment(Qt.AlignCenter)
        self.header_desc.setWordWrap(True)
        self.header_desc.setStyleSheet("color:#000;")

        self.header_guide = QLabel("<b>🧭 Guía rápida:</b> 1) Cargar .zip  →  2) Elegir gráfica  →  3) Ajustar filtros  →  4) Graficar")
        self.header_guide.setAlignment(Qt.AlignCenter)
        self.header_guide.setStyleSheet("color:#000;")

        header_box = QVBoxLayout()
        header_box.setContentsMargins(6, 4, 6, 4)  # Márgenes más compactos
        header_box.setSpacing(2)  # Espaciado más compacto
        header_box.addWidget(self.header_title)
        header_box.addWidget(self.header_desc)
        header_box.addWidget(self.header_guide)

        header_frame = QFrame()
        header_frame.setLayout(header_box)
        header_frame.setFrameShape(QFrame.NoFrame)
        header_frame.setStyleSheet(
            "QFrame { background:#f7f9fb; border:1px solid #e6e9ef; border-radius:8px; }"
        )
        header_frame.setMaximumHeight(90)  # Más compacto

        # ---------- Barra de progreso (oculta por defecto) ----------
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)

        # ---------- Barra superior de controles (compacta) ----------
        self.btn_cargar = QPushButton("Cargar .zip")
        self.btn_cargar.clicked.connect(self.cargar_zip)
        self.btn_cargar.setStyleSheet("font-weight:600;")

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setToolTip("Limpiar selección y reiniciar el lienzo")
        self.btn_limpiar.clicked.connect(self._accion_limpiar)
        self.btn_limpiar.setStyleSheet("font-weight:600;")

        self.btn_reiniciar = QPushButton("Reiniciar")
        self.btn_reiniciar.setToolTip("Cambiar insumo de datos (volver a cargar otro .zip)")
        self.btn_reiniciar.clicked.connect(self._accion_reiniciar)
        self.btn_reiniciar.setStyleSheet("font-weight:600;")

        self.lbl_grafica = QLabel("<b>Gráfica:</b>")
        self.cmb_grafica = QComboBox()
        self.cmb_grafica.addItem("Seleccione una gráfica…")
        self.cmb_grafica.addItem("Curva de acumulación (richness vs fecha)")
        self.cmb_grafica.addItem("Rangos de fechas por sitio (start/end)")
        self.cmb_grafica.addItem("Densidad de horas de actividad por especie")
        self.cmb_grafica.addItem("Presencia/Ausencia por día y deployment")
        self.cmb_grafica.setEnabled(False)
        self.cmb_grafica.currentIndexChanged.connect(self._on_cambio_grafica)

        self.lbl_year = QLabel("<b>Año:</b>")
        self.cmb_year = QComboBox()
        self.lbl_year.setVisible(False)
        self.cmb_year.setVisible(False)
        self.cmb_year.currentIndexChanged.connect(self._replot_if_ranges)

        # Controles de especie (según gráfica)
        self.lbl_especie = QLabel("<b>Especie:</b>")
        self.cmb_especie = QComboBox()
        self.lbl_especie.setVisible(False)
        self.cmb_especie.setVisible(False)

        self.lbl_especies_multi = QLabel("<b>Especies</b> (Ctrl/Shift):")
        self.list_especies = QListWidget()
        self.list_especies.setSelectionMode(QListWidget.MultiSelection)
        # Aplicar fuente cursiva para nombres científicos
        font = self.list_especies.font()
        font.setItalic(True)
        self.list_especies.setFont(font)
        self.lbl_especies_multi.setVisible(False)
        self.list_especies.setVisible(False)
        self.list_especies.setMaximumHeight(110)

        # Filtro por Clase y checkbox de “seleccionar todas”
        self.lbl_clase = QLabel("<b>Clase:</b>")
        self.cmb_clase = QComboBox()
        self.chk_todas = QCheckBox("Seleccionar todas")
        self.lbl_clase.setVisible(False)
        self.cmb_clase.setVisible(False)
        self.chk_todas.setVisible(False)
        self.cmb_clase.currentIndexChanged.connect(self._refrescar_listado_especies)
        self.chk_todas.toggled.connect(self._toggle_select_all_species)

        # NUEVO: Filtro de fechas para Presencia/Ausencia
        self.lbl_fecha = QLabel("<b>Fecha:</b>")
        self.dt_desde = QDateEdit(calendarPopup=True)
        self.dt_hasta = QDateEdit(calendarPopup=True)
        for dt in (self.dt_desde, self.dt_hasta):
            dt.setDisplayFormat("yyyy-MM-dd")
            dt.setMinimumWidth(110)
        # Ocultos por defecto; se muestran solo en Presencia/Ausencia
        self.lbl_fecha.setVisible(False)
        self.dt_desde.setVisible(False)
        self.dt_hasta.setVisible(False)

        # NUEVO: Opciones de suavizado para curva de acumulación
        self.chk_smooth_curve = QCheckBox("Curva suavizada")
        self.chk_smooth_curve.setToolTip("Aplicar suavizado semilogarítmico según Ugland et al. (2003)")
        self.chk_smooth_curve.setChecked(True)  # Activado por defecto
        self.chk_smooth_curve.setVisible(False)

        self.chk_confidence = QCheckBox("Intervalos de confianza")
        self.chk_confidence.setToolTip("Mostrar intervalos de confianza del 95% (bootstrap)")
        self.chk_confidence.setChecked(False)  # Desactivado por defecto para mejor performance
        self.chk_confidence.setVisible(False)

        self.btn_graficar = QPushButton("Graficar")
        self.btn_graficar.setEnabled(False)
        self.btn_graficar.clicked.connect(self._graficar)
        self.btn_graficar.setStyleSheet("font-weight:600;")

        top_bar_left = QHBoxLayout()
        top_bar_left.setSpacing(6)
        top_bar_left.addWidget(self.btn_cargar)
        top_bar_left.addWidget(self.btn_limpiar)
        top_bar_left.addWidget(self.btn_reiniciar)

        top_bar_right = QHBoxLayout()
        top_bar_right.setSpacing(6)
        top_bar_right.addWidget(self.lbl_grafica)
        top_bar_right.addWidget(self.cmb_grafica)
        top_bar_right.addWidget(self.lbl_year)
        top_bar_right.addWidget(self.cmb_year)
        top_bar_right.addWidget(self.btn_graficar)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(6, 0, 6, 0)
        top_bar.addLayout(top_bar_left, stretch=1)
        top_bar.addStretch(1)
        top_bar.addLayout(top_bar_right, stretch=3)

        top_frame = QFrame()
        top_frame.setLayout(top_bar)
        top_frame.setFrameShape(QFrame.NoFrame)
        top_frame.setStyleSheet("QFrame { background:#f2f3f6; border:1px solid #e6e9ef; border-radius:8px; }")

        # ---------- Panel de filtros dinámico (se muestra cuando es necesario) ----------
        self.filters_frame = QFrame()
        self.filters_frame.setVisible(False)
        self.filters_frame.setFrameShape(QFrame.NoFrame)
        self.filters_frame.setStyleSheet("QFrame { background:#f8f9fa; border:1px solid #e6e9ef; border-radius:6px; }")
        self.filters_frame.setMaximumHeight(120)
        
        filters_layout = QHBoxLayout()
        filters_layout.setContentsMargins(8, 6, 8, 6)
        filters_layout.setSpacing(6)
        
        # Filtros de clase
        filters_layout.addWidget(self.lbl_clase)
        filters_layout.addWidget(self.cmb_clase)
        
        # Filtros de especies
        filters_layout.addWidget(self.lbl_especie)
        filters_layout.addWidget(self.cmb_especie)
        filters_layout.addWidget(self.lbl_especies_multi)
        filters_layout.addWidget(self.list_especies)
        filters_layout.addWidget(self.chk_todas)
        
        # Filtros de fecha
        filters_layout.addWidget(self.lbl_fecha)
        filters_layout.addWidget(self.dt_desde)
        filters_layout.addWidget(self.dt_hasta)
        
        # Opciones de curva de acumulación
        filters_layout.addWidget(self.chk_smooth_curve)
        filters_layout.addWidget(self.chk_confidence)
        
        filters_layout.addStretch()  # Para empujar todo hacia la izquierda
        self.filters_frame.setLayout(filters_layout)

        # ---------- Panel de información (QTextEdit para negritas) ----------
        self.txt_resumen = QTextEdit()
        self.txt_resumen.setReadOnly(True)
        self.txt_resumen.setPlaceholderText("📁 Aquí verás el resumen del proyecto, la carpeta principal y los archivos cargados.")
        self.txt_resumen.setMaximumHeight(100)  # Reducido para dar más espacio a gráficas

        # ---------- Área de graficación ----------
        self.lbl_plot_area = QLabel("🖼️ <b>Área de graficación</b>")
        self.lbl_plot_area.setAlignment(Qt.AlignCenter)
        self.canvas = MplCanvas()

        # ---------- Pie: logo izquierda + cita ----------
        self.footer_logo = QLabel()
        logo_path = _resource_path("icons", "logo_humboldt.png")
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path)
            if not pm.isNull():
                self.footer_logo.setPixmap(pm.scaledToHeight(24, Qt.SmoothTransformation))
        self.footer_logo.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        cita_txt = (
            "<b>Citar como:</b> Acevedo, C. C., & Diaz-Pulido, A. (2025). Gestión de datos de fototrampeo (v1.0.0) [Software]. "
                "Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. Publicado el 7 de septiembre de 2025."
        )
        self.footer_text = QLabel(cita_txt)
        self.footer_text.setWordWrap(True)
        self.footer_text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.footer_text.setStyleSheet("color:#555;")

        # Botón de exportar (inicialmente deshabilitado)
        self.btn_export_plot = QPushButton("📤 Exportar gráfica")
        self.btn_export_plot.setEnabled(False)
        self.btn_export_plot.clicked.connect(self._export_plot)
        self.btn_export_plot.setStyleSheet(
            "QPushButton { font-weight:600; padding:6px 12px; }"
            "QPushButton:disabled { color: #999; }"
        )
        
        footer_bar = QHBoxLayout()
        footer_bar.setContentsMargins(6, 2, 6, 2)
        footer_bar.setSpacing(10)
        footer_bar.addWidget(self.footer_logo)
        footer_bar.addWidget(self.footer_text, stretch=1)
        footer_bar.addWidget(self.btn_export_plot)

        footer_frame = QFrame()
        footer_frame.setLayout(footer_bar)
        footer_frame.setFrameShape(QFrame.NoFrame)

        # ---------- Layout principal ----------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(6, 4, 6, 4)  # Márgenes más compactos
        main_layout.setSpacing(4)  # Espaciado más compacto
        main_layout.addWidget(header_frame)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(top_frame)
        main_layout.addWidget(self.filters_frame)  # Panel de filtros dinámico
        main_layout.addWidget(self.txt_resumen)
        main_layout.addWidget(self.lbl_plot_area)
        main_layout.addWidget(self.canvas, stretch=1)  # El canvas toma todo el espacio disponible
        main_layout.addWidget(footer_frame)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # ---------- Barra de estado ----------
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para cargar datos")

    # -------------------------------------------------
    # Utilidades
    # -------------------------------------------------
    @staticmethod
    def _find_col_case_insensitive(df: pd.DataFrame, target: str):
        lower = {c.lower(): c for c in df.columns}
        return lower.get(target.lower())

    def _poblar_combo_anios_deployments(self):
        years = set()
        if self.deployments_df is not None and "start_date" in self.deployments_df.columns:
            sd = pd.to_datetime(self.deployments_df["start_date"], errors="coerce")
            years.update(int(y) for y in sd.dropna().dt.year.unique())

        years = sorted(years)
        self.cmb_year.blockSignals(True)
        self.cmb_year.clear()
        self.cmb_year.addItem("Todos")
        for y in years:
            self.cmb_year.addItem(str(y))
        self.cmb_year.blockSignals(False)

    def _filtrar_deployments_por_anio(self, df: pd.DataFrame, year_sel: str) -> pd.DataFrame:
        if year_sel in (None, "", "Todos"):
            return df
        year = int(year_sel)
        d = df.copy()
        d["start_date"] = pd.to_datetime(d["start_date"], errors="coerce")
        mask = d["start_date"].notna() & (d["start_date"].dt.year == year)
        return d.loc[mask]

    def _refrescar_listado_especies(self):
        """Rellena list_especies y cmb_especie según filtro de Clase (si existe)."""
        if self.images_df is None:
            return
        
        # Usar cache para evitar recalcular si no hay cambios
        if not hasattr(self, '_especies_cache'):
            self._especies_cache = {}
        
        clase_sel = self.cmb_clase.currentText() if self.cmb_clase.isVisible() else "Todos"
        
        # Check cache
        if clase_sel in self._especies_cache:
            especies = self._especies_cache[clase_sel]
        else:
            df = self.images_df
            
            # Filtro por Clase si existe
            if self._class_col and clase_sel not in ("", "Todos"):
                clase_sel_norm = "Mammalia" if clase_sel.lower().startswith("mamal") else clase_sel
                mask = df[self._class_col].fillna("").astype(str).str.strip()
                mask = mask.str.lower()
                df = df[mask == clase_sel_norm.lower()]
            
            especies = sorted(df["scientific_name"].dropna().unique().astype(str))
            self._especies_cache[clase_sel] = especies
        
        # Multi (para densidad) - aplicar cursiva a nombres científicos
        self.list_especies.clear()
        for sp in especies:
            item = QListWidgetItem(sp)
            # Almacenar el nombre original como dato para uso posterior
            item.setData(Qt.UserRole, sp)
            self.list_especies.addItem(item)
        # Single (para presencia/ausencia) - aplicar estilo cursiva al ComboBox
        self.cmb_especie.clear()
        self.cmb_especie.addItems(especies)
        # Aplicar estilo cursiva al ComboBox para nombres científicos
        self.cmb_especie.setStyleSheet("""
            QComboBox {
                font-style: italic;
            }
            QComboBox QAbstractItemView {
                font-style: italic;
            }
        """)

        # Si el check "todas" está activo, seleccionar todo
        if self.chk_todas.isChecked():
            for i in range(self.list_especies.count()):
                self.list_especies.item(i).setSelected(True)

    def _toggle_select_all_species(self, checked: bool):
        for i in range(self.list_especies.count()):
            self.list_especies.item(i).setSelected(checked)

    def _reset_estado_ui(self):
        """Deshabilita/limpia controles y restablece el lienzo."""
        self.cmb_grafica.setEnabled(False)
        self.btn_graficar.setEnabled(False)
        self.cmb_grafica.setCurrentIndex(0)
        self.cmb_year.clear()
        self.cmb_year.addItem("Todos")
        self.lbl_year.setVisible(False)
        self.cmb_year.setVisible(False)

        self.lbl_especie.setVisible(False)
        self.cmb_especie.setVisible(False)
        self.cmb_especie.clear()

        self.lbl_especies_multi.setVisible(False)
        self.list_especies.setVisible(False)
        self.list_especies.clear()

        self.lbl_clase.setVisible(False)
        self.cmb_clase.setVisible(False)
        self.cmb_clase.clear()
        self.chk_todas.setVisible(False)
        self.chk_todas.setChecked(False)

        # Fecha
        self.lbl_fecha.setVisible(False)
        self.dt_desde.setVisible(False)
        self.dt_hasta.setVisible(False)

        # Opciones de curva de acumulación
        self.chk_smooth_curve.setVisible(False)
        self.chk_confidence.setVisible(False)

        # Ocultar panel de filtros y deshabilitar exportar
        self.filters_frame.setVisible(False)
        self.btn_export_plot.setEnabled(False)
        self.canvas.show_placeholder()



    def _export_plot(self):
        """Exportar gráfica actual en diferentes formatos"""
        if hasattr(self, 'canvas') and self.canvas.fig.get_axes():
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar gráfica", "grafica.png", 
                "PNG (*.png);;PDF (*.pdf);;SVG (*.svg);;JPG (*.jpg)"
            )
            if filename:
                try:
                    dpi = 300  # Alta resolución
                    self.canvas.fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                                          facecolor='white', edgecolor='none')
                    self.status_bar.showMessage(f"Gráfica exportada: {filename}", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")
        else:
            QMessageBox.information(self, "Sin gráfica", "No hay gráfica para exportar")



    def _validate_data_quality(self):
        """Valida la calidad de los datos y muestra advertencias"""
        issues = []
        
        if self.images_df is not None:
            # Verificar timestamps
            invalid_timestamps = pd.to_datetime(self.images_df["timestamp"], errors="coerce").isna().sum()
            if invalid_timestamps > 0:
                issues.append(f"⚠️ {invalid_timestamps} registros con timestamps inválidos")
            
            # Verificar nombres científicos vacíos
            empty_names = self.images_df["scientific_name"].isna().sum()
            if empty_names > 0:
                issues.append(f"⚠️ {empty_names} registros sin nombre científico")
            
            # Verificar duplicados
            duplicates = self.images_df.duplicated().sum()
            if duplicates > 0:
                issues.append(f"⚠️ {duplicates} registros duplicados detectados")
        
        if issues:
            warning_text = "Se detectaron los siguientes problemas en los datos:\n\n" + "\n".join(issues)
            warning_text += "\n\nLas gráficas pueden verse afectadas."
            QMessageBox.warning(self, "Problemas en los datos", warning_text)

    # -------------------------------------------------
    # Acciones
    # -------------------------------------------------
    def cargar_zip(self):
        path_zip, _ = QFileDialog.getOpenFileName(
            self, "Selecciona el archivo .zip", ".", "Zip files (*.zip)"
        )
        if not path_zip:
            return
        
        # Reset estado
        self.dfs_por_nombre.clear()
        self.images_df = None
        self.deployments_df = None
        self._class_col = None
        self._images_min_date = None
        self._images_max_date = None
        self._especies_cache.clear()
        self.txt_resumen.clear()
        self._reset_estado_ui()
        
        # Mostrar progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_cargar.setEnabled(False)
        self.status_bar.showMessage("Cargando datos...")
        
        # Usar thread para no bloquear UI
        self.loading_thread = DataLoadingThread(path_zip)
        self.loading_thread.progress.connect(self.progress_bar.setValue)
        self.loading_thread.finished_loading.connect(self._on_data_loaded)
        self.loading_thread.error_occurred.connect(self._on_loading_error)
        self.loading_thread.start()

    def _on_data_loaded(self, dfs_por_nombre, message):
        """Callback cuando se completa la carga de datos"""
        try:
            self.dfs_por_nombre = dfs_por_nombre

            # Detección flexible
            nom_img, images = detectar_df_images(self.dfs_por_nombre)
            nom_dep, deployments = detectar_df_deployments(self.dfs_por_nombre)

            if images is None:
                raise ValueError(
                    "No se encontró un CSV válido para 'images'. "
                    "Debe incluir columnas: 'timestamp' y 'deployment_id' y algún nombre taxonómico."
                )
            if deployments is None:
                raise ValueError(
                    "No se encontró un CSV con columnas requeridas para 'deployments': "
                    "deployment_id, start_date, end_date."
                )

            # Normalizar imágenes
            self.images_df = normalizar_images(images)
            self.deployments_df = deployments.copy()

            # Rango de fechas de IMAGES (para filtros/plots)
            ts = pd.to_datetime(self.images_df["timestamp"], errors="coerce")
            ts = ts.dropna()
            if not ts.empty:
                self._images_min_date = ts.min().normalize()
                self._images_max_date = ts.max().normalize()

            # Buscar projects.csv → project_name
            project_name = "—"
            df_projects = None
            for k, v in self.dfs_por_nombre.items():
                if isinstance(v, pd.DataFrame) and ("projects" in k.lower() or Path(k).name.lower() == "projects.csv"):
                    df_projects = v
                    break
            if df_projects is not None and "project_name" in df_projects.columns and not df_projects["project_name"].empty:
                project_name = str(df_projects["project_name"].dropna().iloc[0])

            # Carpeta raíz dentro del zip o nombre del zip
            miembros_csv = [k for k in self.dfs_por_nombre.keys() if k.lower().endswith('.csv')]
            parts = [m.split("/")[0] for m in miembros_csv if "/" in m]
            top_folder = Counter(parts).most_common(1)[0][0] if parts else "Datos cargados"

            # Resumen (HTML, con negritas)
            html_lines = [
                f"<b>📛 Nombre del proyecto:</b> {project_name}",
                f"<b>🗂️ Nombre general de la carpeta:</b> {top_folder}",
                "<b>📄 Archivos cargados:</b>",
                "<ul style='margin-top:4px;'>",
            ]
            for nombre, df in self.dfs_por_nombre.items():
                base = Path(nombre).name
                if isinstance(df, pd.DataFrame):
                    html_lines.append(f"<li>{base}  →  filas={len(df)}, columnas={len(df.columns)}</li>")
                else:
                    html_lines.append(f"<li>{base}  →  {df}</li>")
            html_lines.append("</ul>")
            self.txt_resumen.setHtml("\n".join(html_lines))

            # Columna CLASS si existe
            for cand in ("class", "taxon_class", "class_name"):
                col = self._find_col_case_insensitive(self.images_df, cand)
                if col:
                    self._class_col = col
                    break

            # Poblar clase (si existe) y especies
            self.cmb_clase.clear()
            self.cmb_clase.addItem("Todos")
            if self._class_col:
                classes = (
                    self.images_df[self._class_col]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .str.capitalize()
                    .replace({"Mamalia": "Mammalia"})
                    .unique()
                )
                prefer = ["Aves", "Mammalia"]
                resto = sorted([c for c in classes if c not in prefer])
                for c in prefer:
                    if c in classes:
                        self.cmb_clase.addItem(c)
                for c in resto:
                    self.cmb_clase.addItem(c)

            self._refrescar_listado_especies()

            # Configurar filtros de FECHA (Presencia/Ausencia)
            if self._images_min_date is not None and self._images_max_date is not None:
                self.dt_desde.setDate(QDate(self._images_min_date.year, self._images_min_date.month, self._images_min_date.day))
                self.dt_hasta.setDate(QDate(self._images_max_date.year, self._images_max_date.month, self._images_max_date.day))
                self.dt_desde.setMinimumDate(self.dt_desde.date())
                self.dt_desde.setMaximumDate(self.dt_hasta.date())
                self.dt_hasta.setMinimumDate(self.dt_desde.date())

            # Habilitar UI
            self.cmb_grafica.setEnabled(True)
            self.btn_graficar.setEnabled(True)
            self.btn_cargar.setEnabled(True)

            # Poblamos años solo de deployments (para la gráfica de rangos)
            self._poblar_combo_anios_deployments()

            # Validar calidad de datos
            self._validate_data_quality()

            # Ocultar progreso
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("¡Zip cargado y datos listos para graficar!", 3000)

            QMessageBox.information(self, "Listo", "¡Zip cargado y datos listos para graficar!")

        except Exception as e:
            self._on_loading_error(str(e))
            
    def _on_loading_error(self, error_message):
        """Callback cuando hay error en la carga"""
        self.progress_bar.setVisible(False)
        self.btn_cargar.setEnabled(True)
        self.status_bar.showMessage("Error al cargar datos", 3000)
        QMessageBox.critical(self, "Error al cargar .zip", error_message)

    def _on_cambio_grafica(self, _idx: int):
        texto = self.cmb_grafica.currentText()
        
        # Año para Rangos
        show_year = "Rangos de fechas" in texto
        self.lbl_year.setVisible(show_year)
        self.cmb_year.setVisible(show_year)

        # Determinar si necesitamos mostrar el panel de filtros
        needs_filters = ("Densidad de horas" in texto or 
                        "Presencia/Ausencia" in texto or 
                        "Curva de acumulación" in texto)
        self.filters_frame.setVisible(needs_filters)

        if "Curva de acumulación" in texto:
            # Mostrar opciones de suavizado solo para curva de acumulación
            self.chk_smooth_curve.setVisible(True)
            self.chk_confidence.setVisible(True)
            # Ocultar otros filtros
            self.lbl_especies_multi.setVisible(False)
            self.list_especies.setVisible(False)
            self.lbl_especie.setVisible(False)
            self.cmb_especie.setVisible(False)
            self.lbl_clase.setVisible(False)
            self.cmb_clase.setVisible(False)
            self.chk_todas.setVisible(False)
            self.lbl_fecha.setVisible(False)
            self.dt_desde.setVisible(False)
            self.dt_hasta.setVisible(False)

        elif "Densidad de horas" in texto:
            # Mostrar controles para múltiples especies
            self.lbl_especies_multi.setVisible(True)
            self.list_especies.setVisible(True)
            self.lbl_especie.setVisible(False)
            self.cmb_especie.setVisible(False)
            self.lbl_clase.setVisible(True)
            self.cmb_clase.setVisible(True)
            self.chk_todas.setVisible(True)
            # Ocultar filtros de fecha y opciones de curva
            self.lbl_fecha.setVisible(False)
            self.dt_desde.setVisible(False)
            self.dt_hasta.setVisible(False)
            self.chk_smooth_curve.setVisible(False)
            self.chk_confidence.setVisible(False)

        elif "Presencia/Ausencia" in texto:
            # Mostrar controles para especie individual y fechas
            self.lbl_especies_multi.setVisible(False)
            self.list_especies.setVisible(False)
            self.lbl_especie.setVisible(True)
            self.cmb_especie.setVisible(True)
            self.lbl_clase.setVisible(True)
            self.cmb_clase.setVisible(True)
            self.chk_todas.setVisible(False)
            self._refrescar_listado_especies()
            # Mostrar filtros de fecha
            self.lbl_fecha.setVisible(True)
            self.dt_desde.setVisible(True)
            self.dt_hasta.setVisible(True)
            # Ocultar opciones de curva
            self.chk_smooth_curve.setVisible(False)
            self.chk_confidence.setVisible(False)

        else:
            # Ocultar todos los filtros específicos
            self.lbl_especies_multi.setVisible(False)
            self.list_especies.setVisible(False)
            self.lbl_especie.setVisible(False)
            self.cmb_especie.setVisible(False)
            self.lbl_clase.setVisible(False)
            self.cmb_clase.setVisible(False)
            self.chk_todas.setVisible(False)
            self.lbl_fecha.setVisible(False)
            self.dt_desde.setVisible(False)
            self.dt_hasta.setVisible(False)
            self.chk_smooth_curve.setVisible(False)
            self.chk_confidence.setVisible(False)

    def _replot_if_ranges(self, *_):
        if "Rangos de fechas" in self.cmb_grafica.currentText():
            self._graficar()

    def _accion_limpiar(self):
        """Limpia selección de filtros, gráfica y muestra placeholder."""
        self.cmb_grafica.setCurrentIndex(0)
        if self.cmb_year.count() > 0:
            self.cmb_year.setCurrentIndex(0)
        self.cmb_especie.clear()
        self.list_especies.clearSelection()
        self.chk_todas.setChecked(False)
        self.filters_frame.setVisible(False)
        self.btn_export_plot.setEnabled(False)
        self.canvas.show_placeholder()

    def _accion_reiniciar(self):
        """Permite cambiar de insumo: resetea estado y vuelve a abrir el diálogo."""
        resp = QMessageBox.question(
            self, "Reiniciar",
            "Esto limpiará la selección actual y te permitirá cargar un nuevo .zip.\n\n¿Deseas continuar?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.txt_resumen.clear()
            self._reset_estado_ui()
            self.cargar_zip()

    def _graficar(self):
        if self.images_df is None or self.deployments_df is None:
            QMessageBox.warning(self, "Faltan datos", "Carga primero el .zip con los CSV.")
            return

        opcion = self.cmb_grafica.currentText()
        try:
            self.canvas.fig.clf()

            if "Curva de acumulación" in opcion:
                ax = self.canvas.fig.add_subplot(111)
                # Obtener configuraciones de suavizado del usuario
                use_confidence = (self.chk_confidence.isChecked() and 
                                self.chk_confidence.isVisible() and 
                                len(self.images_df) > 100)
                use_smooth = (self.chk_smooth_curve.isChecked() and 
                             self.chk_smooth_curve.isVisible())
                
                plot_accumulation_curve_mpl(self.images_df, self.deployments_df, ax, 
                                          confidence_interval=use_confidence,
                                          smooth_curve=use_smooth)

            elif "Rangos de fechas" in opcion:
                year_sel = self.cmb_year.currentText() if self.cmb_year.isVisible() else "Todos"
                deps = self._filtrar_deployments_por_anio(self.deployments_df, year_sel)
                ax = self.canvas.fig.add_subplot(111)
                plot_site_dates_mpl(deps, ax)

            elif "Densidad de horas" in opcion:
                # Obtener nombres científicos reales usando UserRole data
                seleccion = [i.data(Qt.UserRole) for i in self.list_especies.selectedItems()]
                if not seleccion:
                    seleccion = [sp for sp, _ in Counter(self.images_df["scientific_name"]).most_common(3)]
                ax = self.canvas.fig.add_subplot(111)
                plot_activity_hours_mpl(
                    self.images_df, seleccion, ax,
                    class_col=self._class_col,
                    class_filter=self.cmb_clase.currentText() if self.cmb_clase.isVisible() else "Todos"
                )

            elif "Presencia/Ausencia" in opcion:
                especie = self.cmb_especie.currentText().strip()
                if not especie:
                    QMessageBox.warning(self, "Selecciona especie", "Elige una especie para la matriz de presencia/ausencia.")
                    return
                # rango de fechas desde los QDateEdit
                date_start = None
                date_end = None
                if self.dt_desde.isVisible() and self.dt_hasta.isVisible():
                    d1 = self.dt_desde.date()
                    d2 = self.dt_hasta.date()
                    date_start = pd.Timestamp(year=d1.year(), month=d1.month(), day=d1.day())
                    date_end   = pd.Timestamp(year=d2.year(), month=d2.month(), day=d2.day())
                ax = self.canvas.fig.add_subplot(111)
                plot_presence_absence_mpl(
                    self.images_df, self.deployments_df, especie, ax,
                    class_col=self._class_col,
                    class_filter=self.cmb_clase.currentText() if self.cmb_clase.isVisible() else "Todos",
                    date_start=date_start, date_end=date_end
                )

            else:
                self.canvas.show_placeholder()
                return

            # Aplicar layout mejorado con manejo de errores
            _safe_tight_layout(self.canvas.fig)
            self.canvas.draw()
            
            # Habilitar botón de exportar cuando hay una gráfica
            self.btn_export_plot.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error al graficar", str(e))
            self.btn_export_plot.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    # La ventana ya se maximiza en __init__(), pero aseguramos que se muestre
    win.show()
    sys.exit(app.exec_())


# Permitir ejecutar este archivo directo desde VS Code
if __name__ == "__main__" and __package__ is None:
    main()
