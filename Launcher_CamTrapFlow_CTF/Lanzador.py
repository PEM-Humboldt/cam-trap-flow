#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CamTrapFlow Launcher - Interfaz Gráfica Unificada de Gestión de Datos de Fototrampeo
====================================================================================

Aplicación de escritorio que centraliza el acceso a tres herramientas especializadas
para el procesamiento completo de datos de fototrampeo, desde la extracción de frames
hasta la publicación de datos estandarizados.

Características principales:
    - Lanzador unificado para tres módulos independientes:
        * Img2WI: Extracción de frames de video para Wildlife Insights
        * WI2CamtrapDP: Conversión a formato Camtrap Data Package (v1.0.2)
        * WIsualization: Generación de visualizaciones y análisis estadísticos
    - Interfaz responsive optimizada para resoluciones de laptop (1366x768+)
    - Sistema de diálogos de carga con feedback visual progresivo
    - Configuración externa vía JSON para duraciones y dimensiones de ventana
    - Logging dual (archivo + consola) para diagnóstico y troubleshooting
    - Compatible con PyInstaller one-file y modo desarrollo
    - Gestión robusta de rutas para recursos empaquetados (_MEIPASS)

Módulo: Lanzador.py
Autores: Cristian C. Acevedo & Angélica Díaz-Pulido
Organización: Instituto de Investigación de Recursos Biológicos Alexander von Humboldt - Red OTUS
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
Licencia: Ver LICENSE
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import logging
import json
from contextlib import contextmanager
from pathlib import Path

# =============================================================================================
# CONFIGURACIÓN Y LOGGING
# =============================================================================================
def setup_logging():
    """
    Configura logging dual (archivo + consola) para diagnóstico.
    
    Crea launcher.log con nivel INFO para eventos importantes.
    Para debug detallado cambiar a level=logging.DEBUG.
    """
    log_file = Path(__file__).parent / "launcher.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info("=== Iniciando CamTrapFlow Launcher ===")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Working directory: {Path.cwd()}")
    logging.info(f"Frozen: {getattr(sys, 'frozen', False)}")

# =============================================================================================
# GESTIÓN DE RECURSOS
# =============================================================================================

def resource_path(*parts: str) -> Path:
    """
    Construye rutas absolutas compatibles con PyInstaller y desarrollo.
    
    Args:
        *parts: Componentes de ruta (ej: "assets", "icon.ico")
    
    Returns:
        Path: Ruta absoluta al recurso
    
    Usa _MEIPASS en executables PyInstaller, __file__ en desarrollo.
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base.joinpath(*parts)

def setup_ttk_styles():
    """
    Configura estilos TTK personalizados para la interfaz.
    
    Returns:
        dict: Paleta de colores corporativa
    
    Define estilos para tarjetas de módulos, botones, encabezados y texto.
    Optimizado para resoluciones 1366x768+.
    """
    style = ttk.Style()
    
    # Seleccionar tema: Vista (Windows) > Clam (multiplataforma) > Default
    try:
        style.theme_use('vista')
    except:
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
    
    # Paleta corporativa inspirada en Material Design
    colors = {
        # Colores primarios (azul)
        'primary': '#2E5BBA',
        'primary_light': '#4A7BC8',
        'primary_dark': '#1A4480',
        'button_bg': '#1E4B8B',
        
        # Fondos
        'background': '#F8F9FA',
        'surface': '#FFFFFF',
        
        # Textos
        'text_primary': '#1A1A1A',
        'text_secondary': '#6C757D',
        
        # Bordes y estados
        'border': '#DEE2E6',
        'success': '#28A745',
        'warning': '#FFC107',
        'error': '#DC3545'
    }
    
    # Estilos para tarjetas de módulos
    style.configure("ModuleCard.TLabelframe",
                   background=colors['surface'],
                   borderwidth=2,
                   relief="ridge",
                   padding=15)
    
    style.configure("ModuleCard.TLabelframe.Label",
                   background=colors['surface'],
                   foreground=colors['primary'],
                   font=("Segoe UI", 11, "bold"))
    
    style.configure("Card.TFrame",
                   background=colors['surface'])
    
    style.configure("ModuleDesc.TLabel",
                   background=colors['surface'],
                   foreground=colors['text_secondary'],
                   font=("Segoe UI", 10))
    
    # Estilo principal de botones con efectos hover
    style.configure("Professional.TButton",
                   font=("Segoe UI", 10, "bold"),
                   padding=(15, 8),
                   relief="raised",
                   borderwidth=2,
                   focuscolor='none',
                   anchor='center',
                   width=15,
                   background=colors['primary'],
                   foreground='white')
    
    style.map("Professional.TButton",
             background=[('active', colors['primary_light']),
                        ('pressed', colors['primary_dark']),
                        ('disabled', colors['border']),
                        ('!disabled', colors['primary'])],
             foreground=[('active', 'white'),
                        ('pressed', 'white'),
                        ('disabled', colors['text_secondary']),
                        ('!disabled', 'white')],
             relief=[('pressed', 'sunken'),
                    ('!pressed', 'raised')],
             bordercolor=[('active', colors['primary_dark']),
                         ('!active', colors['primary_dark'])])
    
    # Estilo alternativo con mayor contraste
    style.configure("HighContrast.TButton",
                   font=("Segoe UI", 10, "bold"),
                   padding=(15, 8),
                   relief="solid",
                   borderwidth=2,
                   focuscolor='none',
                   anchor='center',
                   width=15,
                   background=colors['button_bg'],
                   foreground='white')
    
    style.map("HighContrast.TButton",
             background=[('active', colors['primary_light']),
                        ('pressed', colors['primary_dark']),
                        ('disabled', colors['border']),
                        ('!disabled', colors['button_bg'])],
             foreground=[('active', 'white'),
                        ('pressed', 'white'),
                        ('disabled', colors['text_secondary']),
                        ('!disabled', 'white')],
             relief=[('pressed', 'sunken'),
                    ('!pressed', 'solid')],
             bordercolor=[('active', colors['primary_light']),
                         ('!active', colors['button_bg'])])
    
    style.configure("Main.TFrame",
                   background=colors['background'])
    
    style.configure("Header.TLabel",
                   background=colors['background'],
                   foreground=colors['primary'],
                   font=("Segoe UI", 20, "bold"))
    
    style.configure("SubHeader.TLabel",
                   background=colors['background'],
                   foreground=colors['text_secondary'],
                   font=("Segoe UI", 11))
    
    style.configure("Version.TLabel",
                   background=colors['background'],
                   foreground=colors['primary_light'],
                   font=("Segoe UI", 10, "italic"))
    
    style.configure("SectionHeader.TLabel",
                   background=colors['background'],
                   foreground=colors['primary'],
                   font=("Segoe UI", 12, "bold"))  # Reducido de 16 a 14
    
    style.configure("Note.TLabel",
                   background=colors['background'],
                   foreground=colors['text_secondary'],
                   font=("Segoe UI", 9))  # Fuente más pequeña para la nota
    
    return colors

def exe_path(exe_name: str) -> Path:
    """
    Localiza ejecutable del módulo en _MEIPASS/bin, bin/ o directorio base.
    
    Returns:
        Path: Ruta al ejecutable (existe o último candidato para error)
    """
    logging.debug(f"Buscando ejecutable: {exe_name}")
    
    # Buscar en _MEIPASS/bin (PyInstaller one-file)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p = Path(meipass) / "bin" / exe_name
        logging.debug(f"Verificando ruta PyInstaller: {p}")
        if p.exists():
            logging.info(f"Ejecutable encontrado (PyInstaller): {p}")
            return p
    
    # Buscar en bin/ (desarrollo)
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    cand = base / "bin" / exe_name
    logging.debug(f"Verificando ruta dev: {cand}")
    if cand.exists():
        logging.info(f"Ejecutable encontrado (dev): {cand}")
        return cand
    
    # Buscar en directorio base
    cand2 = base / exe_name
    logging.debug(f"Verificando ruta plana: {cand2}")
    if cand2.exists():
        logging.info(f"Ejecutable encontrado (plano): {cand2}")
        return cand2
    
    logging.warning(f"Ejecutable no encontrado: {exe_name}")
    return cand

def validate_resources() -> tuple[bool, list[str]]:
    """
    Valida existencia de recursos necesarios (iconos, imágenes).
    
    Returns:
        tuple: (todos_existen, lista_faltantes)
    """
    required_assets = [
        "assets/icon.ico",
        "assets/logo_humboldt.png"
    ]
    
    missing = []
    for asset in required_assets:
        asset_path = resource_path(asset)
        if not asset_path.exists():
            missing.append(asset)
            logging.warning(f"Recurso faltante: {asset_path}")
        else:
            logging.debug(f"Recurso encontrado: {asset_path}")
    
    if missing:
        logging.error(f"Recursos faltantes: {missing}")
        return False, missing
    
    logging.info("Todos los recursos validados correctamente")
    return True, []

def load_config() -> dict:
    """
    Carga configuración desde config.json o retorna valores por defecto.
    
    Returns:
        dict: Configuración con duraciones de carga y dimensiones de ventana
    """
    config_file = resource_path("config.json")
    default_config = {
        "durations_ms": {
            "Img2WI.exe": 18000,
            "WI2CamtrapDP.exe": 7000,
            "WIsualization.exe": 30000
        },
        "window": {
            "default_width": 1200,
            "default_height": 680,
            "min_width": 1000,
            "min_height": 600
        }
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logging.info(f"Configuración cargada desde: {config_file}")
                return {**default_config, **config}
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error al cargar configuración: {e}")
            logging.info("Usando configuración por defecto")
    else:
        logging.info("Archivo de configuración no encontrado, usando valores por defecto")
    
    return default_config

# =============================================================================================
# CONTENIDO DE LA APLICACIÓN
# =============================================================================================

# Metadatos
APP_TITLE = "CTF - CamTrapFlow"
VERSION = "1.0.0"
DATE = "2025"

APP_DESC = (
    "**CTF - CamTrapFlow** reúne tres herramientas para llevar tus datos de fototrampeo desde el video hasta la publicación. "
    "**Img2WI** convierte videos en imágenes listas para **Wildlife Insights**; **WIsualization** permite explorar y validar rápidamente; "
    "y **WI2CamtrapDP** normaliza los resultados al estándar **Camtrap Data Package** para compartir (por ejemplo, en **GBIF/SIB Colombia**). "
    "Todo desde un único ejecutable, **portátil** y **sin dependencias**."
)


NOTE_TEXT = (
    "⏳ **Nota**: la ventana de cada módulo suele abrirse en **menos de un minuto**. "
    "El tiempo exacto depende del **rendimiento del equipo** (CPU, memoria, disco) "
    "y de otras tareas en ejecución."
)

# Configuración de módulos - cada entrada define una herramienta
MODULES = [
    {
        "title": "🎬  Módulo 1 — Img2WI",
        "desc":  "Extrae **imágenes (frames)** de lotes de videos a **intervalos definidos** para preparar insumos de carga a **Wildlife Insights**.",
        "exe":   "Img2WI.exe",
        "btn":   "Abrir Img2WI",
        "loading_info": {
            "icon": "🎬",
            "desc": "Herramienta de extracción de frames de video",
            "name": "Img2WI"
        }
    },
    {
        "title": "🧩  Módulo 2 — WI2CamtrapDP",
        "desc":  "Convierte exportaciones de **Wildlife Insights** al estándar **Camtrap Data Package** (datapackage.json, deployments.csv, media.csv, observations.csv…).",
        "exe":   "WI2CamtrapDP.exe",
        "btn":   "Abrir WI2CamtrapDP",
        "loading_info": {
            "icon": "🧩",
            "desc": "Convertidor a formato Camtrap Data Package",
            "name": "WI2CamtrapDP"
        }
    },
    {
        "title": "📊  Módulo 3 — WIsualization",
        "desc":  "Genera **visualizaciones** listas para análisis (**curva de acumulación**, **calendario/fechas de muestreo**, **actividad horaria**, **presencia/ausencia**) desde **WI** o **Camtrap-DP**.",
        "exe":   "WIsualization.exe",
        "btn":   "Abrir WIsualization",
        "loading_info": {
            "icon": "📊",
            "desc": "Generador de visualizaciones y análisis",
            "name": "WIsualization"
        }
    },
]

CITATION = (
    "**Citar como**: Acevedo C.C. & A. Díaz-Pulido. 2025. **Gestión de datos de fototrampeo** (v1.0.0) [Software]. "
    "07/09/2025. **Red OTUS**. **Instituto de Investigación de Recursos Biológicos Alexander von Humboldt**."
)

# =============================================================================================
# COMPONENTES DE INTERFAZ
# =============================================================================================

def scaled_photo(path: Path, target_h: int) -> tk.PhotoImage | None:
    """
    Escala imagen PNG a altura objetivo usando subsample nativo de Tkinter.
    
    Args:
        path: Ruta a imagen PNG
        target_h: Altura objetivo en píxeles
    
    Returns:
        tk.PhotoImage escalada o None si hay error
    """
    if not path.exists():
        logging.warning(f"Imagen no encontrada: {path}")
        return None
    try:
        img = tk.PhotoImage(file=str(path))
        h = img.height()
        if h > target_h:
            factor = max(1, round(h / target_h))
            img = img.subsample(factor, factor)
            logging.debug(f"Imagen escalada: {path} (factor: {factor})")
        else:
            logging.debug(f"Imagen cargada sin escalar: {path}")
        return img
    except tk.TclError as e:
        logging.error(f"Error al cargar imagen {path}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado al cargar imagen {path}: {e}")
        return None

def create_rich_text_label(parent, text, style_name, wraplength=None, justify="left"):
    """
    Crea label TTK removiendo formato **negrita** para evitar problemas de layout.
    
    Args:
        parent: Widget padre
        text: Texto con formato Markdown (**bold**)
        style_name: Nombre del estilo TTK
        wraplength: Longitud máxima de línea
        justify: Justificación del texto
    
    Returns:
        ttk.Label con texto sin formato
    """
    import re
    
    clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    label = ttk.Label(parent,
                     text=clean_text,
                     style=style_name,
                     wraplength=wraplength if wraplength else 800,
                     justify=justify)
    
    return label

def create_styled_button(parent, text, command, colors):
    """
    Crea botón con estilos garantizados y efectos hover.
    
    Args:
        parent: Widget padre
        text: Texto del botón
        command: Función a ejecutar al hacer clic
        colors: Diccionario de paleta de colores
    
    Returns:
        tk.Button con efectos hover configurados
    """
    btn = tk.Button(parent,
                   text=text,
                   font=("Segoe UI", 10, "bold"),
                   bg='#1E4B8B',
                   fg='white',
                   activebackground='#4A7BC8',
                   activeforeground='white',
                   disabledforeground='#6C757D',
                   relief="raised",
                   borderwidth=2,
                   width=18,
                   height=1,
                   cursor="hand2",
                   command=command)
    
    # Efectos hover
    def on_enter(e):
        if btn['state'] != 'disabled':
            btn.configure(bg='#4A7BC8', relief="raised")
    
    def on_leave(e):
        if btn['state'] != 'disabled':
            btn.configure(bg='#1E4B8B', relief="raised")
    
    def on_press(e):
        if btn['state'] != 'disabled':
            btn.configure(relief="sunken")
    
    def on_release(e):
        if btn['state'] != 'disabled':
            btn.configure(relief="raised")
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.bind("<Button-1>", on_press)
    btn.bind("<ButtonRelease-1>", on_release)
    
    return btn

def make_simple_card(parent, module_data, colors, on_click):
    """
    Crea tarjeta de módulo con descripción y botón de acción.
    
    Args:
        parent: Widget padre
        module_data: Dict con info del módulo (title, desc, btn)
        colors: Paleta de colores
        on_click: Función al hacer clic en botón
    
    Returns:
        tuple: (card_frame, desc_label, button)
    """
    card = ttk.LabelFrame(parent, 
                         text=module_data["title"], 
                         padding=10,
                         style="ModuleCard.TLabelframe")
    
    content_frame = ttk.Frame(card, style="Card.TFrame")
    content_frame.pack(fill="both", expand=True, padx=2, pady=2)
    
    # Layout horizontal: descripción | botón
    left_frame = ttk.Frame(content_frame, style="Card.TFrame")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    right_frame = ttk.Frame(content_frame, style="Card.TFrame")
    right_frame.pack(side="right", padx=(10, 0))
    
    desc_label = create_rich_text_label(left_frame, module_data["desc"], "ModuleDesc.TLabel", 800, "left")
    desc_label.pack(fill="both", expand=True, anchor="w")
    
    btn = create_styled_button(right_frame, module_data["btn"], on_click, colors)
    btn.pack(anchor="e", padx=5, pady=5)
    
    return card, desc_label, btn

# =============================================================================================
# DIÁLOGO DE CARGA
# =============================================================================================

class LoadingDialog(tk.Toplevel):
    """
    Diálogo modal con feedback visual durante el lanzamiento de módulos.
    
    Características:
    - Progress bar animado
    - Mensajes de estado actualizados cada 1.5s
    - Centrado sobre ventana principal
    - Modal (bloquea interacción con ventana padre)
    """
    
    def __init__(self, parent, message="Abriendo módulo…", module_info=None):
        """
        Inicializa diálogo de carga.
        
        Args:
            parent: Ventana padre
            message: Mensaje inicial
            module_info: Dict con icon, desc, name del módulo
        """
        super().__init__(parent)
        self.title("Cargando CamTrapFlow")
        self.message = message
        self.module_info = module_info or {}
        
        # Heredar iconos del padre
        try:
            ico = resource_path("assets", "icon.ico")
            if ico.exists():
                self.iconbitmap(default=str(ico))
            png = resource_path("assets", "logo_humboldt.png")
            if png.exists():
                icon_img = tk.PhotoImage(file=str(png))
                self.iconphoto(True, icon_img)
                self._icon_img_ref = icon_img
        except tk.TclError as e:
            logging.warning(f"Error al establecer iconos del diálogo: {e}")
        except Exception as e:
            logging.error(f"Error inesperado con iconos del diálogo: {e}")

        self.resizable(False, False)
        self.configure(bg="#f8f9fa")
        self.transient(parent)
        self.grab_set()

        # Frame principal
        main_frame = tk.Frame(self, bg="#f8f9fa", padx=24, pady=24)
        main_frame.pack(fill="both", expand=True)

        # Icono del módulo
        if self.module_info.get("icon"):
            icon_label = tk.Label(
                main_frame, 
                text=self.module_info["icon"], 
                font=("Segoe UI", 32),
                bg="#f8f9fa",
                fg="#2c3e50"
            )
            icon_label.pack(pady=(0, 12))

        # Mensaje principal
        self.main_label = tk.Label(
            main_frame, 
            text=message, 
            font=("Segoe UI", 12, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        self.main_label.pack(pady=(0, 8))

        # Descripción del módulo
        if self.module_info.get("desc"):
            desc_label = tk.Label(
                main_frame,
                text=self.module_info["desc"],
                font=("Segoe UI", 9),
                bg="#f8f9fa",
                fg="#7f8c8d",
                wraplength=300,
                justify="center"
            )
            desc_label.pack(pady=(0, 16))

        # Progress bar
        self.pb = ttk.Progressbar(
            main_frame, 
            mode="indeterminate", 
            length=320
        )
        self.pb.pack(pady=(0, 12), padx=20, fill="x")
        
        # Mensaje de estado
        self.status_label = tk.Label(
            main_frame,
            text="Iniciando módulo, por favor espere...",
            font=("Segoe UI", 8),
            bg="#f8f9fa",
            fg="#95a5a6"
        )
        self.status_label.pack()

        # Centrar sobre la ventana principal
        self.update_idletasks()
        w, h = 400, 200 if self.module_info.get("desc") else 160
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        self.pb.start(8)
        
        # Mensajes progresivos
        self.status_messages = [
            "Iniciando módulo...",
            "Cargando componentes...",
            "Preparando interfaz...",
            "Finalizando carga..."
        ]
        self.status_index = 0
        self.after(1000, self.update_status)

    def update_status(self):
        """Actualiza mensaje de estado cíclicamente cada 1.5s."""
        try:
            if hasattr(self, 'status_label'):
                try:
                    if self.status_label.winfo_exists():
                        message = self.status_messages[self.status_index % len(self.status_messages)]
                        self.status_label.configure(text=message)
                        self.status_index = (self.status_index + 1) % len(self.status_messages)
                        self.after(1500, self.update_status)
                except tk.TclError:
                    pass
        except Exception as e:
            logging.debug(f"Error en update_status: {e}")
    
    def update_message(self, new_message: str):
        """Actualiza mensaje principal del diálogo."""
        try:
            if hasattr(self, 'main_label'):
                try:
                    if self.main_label.winfo_exists():
                        self.main_label.configure(text=new_message)
                        logging.debug(f"Mensaje del diálogo actualizado: {new_message}")
                        self.update_idletasks()
                except tk.TclError:
                    logging.debug("Intento de actualizar mensaje en ventana cerrada")
        except Exception as e:
            logging.warning(f"Error al actualizar mensaje del diálogo: {e}")

    def close(self):
        """Cierra el diálogo y libera recursos."""
        try:
            self.pb.stop()
        except tk.TclError as e:
            logging.warning(f"Error al detener progress bar: {e}")
        except Exception as e:
            logging.error(f"Error inesperado al cerrar diálogo: {e}")
        
        try:
            self.grab_release()
            self.destroy()
        except tk.TclError as e:
            logging.warning(f"Error al cerrar ventana de diálogo: {e}")

@contextmanager
def loading_context(parent, message: str, module_info: dict = None):
    """Context manager para diálogo de carga con gestión de botones."""
    dlg = LoadingDialog(parent, message, module_info)
    set_module_buttons_enabled(False)
    logging.info(f"Mostrando diálogo de carga: {message}")
    
    try:
        yield dlg
    finally:
        try:
            dlg.close()
        finally:
            set_module_buttons_enabled(True)
            logging.debug("Diálogo de carga cerrado")

# =============================================================================================
# LÓGICA DE LANZAMIENTO
# =============================================================================================

# Variables globales para gestión de estado
module_buttons: list[ttk.Button] = []
module_text_labels: list[ttk.Label] = []
root: tk.Tk | None = None
desc_label: ttk.Label | None = None
cite_label: ttk.Label | None = None

def set_module_buttons_enabled(enabled: bool):
    """Habilita o deshabilita todos los botones de módulos."""
    state = "normal" if enabled else "disabled"
    action = "habilitando" if enabled else "deshabilitando"
    logging.debug(f"Botones de módulos: {action}")
    
    for b in module_buttons:
        try:
            b.configure(state=state)
        except tk.TclError as e:
            logging.warning(f"Error al cambiar estado del botón: {e}")
        except Exception as e:
            logging.error(f"Error inesperado al cambiar estado del botón: {e}")

def lanzar(exe_name: str, human_name: str = "módulo", module_info: dict = None):
    """
    Lanza ejecutable de módulo con diálogo de carga.
    
    Args:
        exe_name: Nombre del ejecutable (ej: "Img2WI.exe")
        human_name: Nombre amigable para mensajes
        module_info: Dict con información del módulo (icon, desc, name)
    
    Proceso:
    1. Valida existencia del ejecutable
    2. Muestra diálogo de carga
    3. Lanza proceso con subprocess.Popen
    4. Actualiza mensajes progresivamente
    5. Cierra diálogo después del tiempo configurado
    """
    config = load_config()
    durations = config.get("durations_ms", {})
    
    logging.info(f"Iniciando lanzamiento de: {exe_name}")
    
    p = exe_path(exe_name)
    if not p.exists():
        error_msg = f"No se encontró {exe_name}.\nBuscado en: {p.parent}"
        logging.error(error_msg)
        messagebox.showerror("Archivo no encontrado", error_msg)
        return

    # Preparar diálogo de carga
    module_name = module_info.get("name", human_name) if module_info else human_name
    loading_message = f"Cargando {module_name}..."
    
    dlg = LoadingDialog(root, loading_message, module_info)
    set_module_buttons_enabled(False)
    logging.info(f"Mostrando diálogo de carga: {loading_message}")
    
    def _do_launch():
        """Ejecuta el lanzamiento del proceso."""
        try:
            dlg.update_message(f"Iniciando {module_name}...")
            
            # Lanzar proceso
            process = subprocess.Popen(
                [str(p)], 
                cwd=str(p.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logging.info(f"Proceso lanzado exitosamente: PID {process.pid}")
            
            root.after(800, lambda: dlg.update_message(f"{module_name} iniciado correctamente"))
            
            # Duración configurada por módulo (mínimo 3s)
            duration = max(3000, durations.get(exe_name, 7000))
            logging.debug(f"Esperando {duration}ms antes de cerrar diálogo")
            
            # Mensajes progresivos
            root.after(1500, lambda: dlg.update_message(f"Cargando componentes de {module_name}..."))
            root.after(duration - 1000, lambda: dlg.update_message(f"Abriendo ventana de {module_name}..."))
            root.after(duration, _close_ok)
            
        except FileNotFoundError:
            error_msg = f"Ejecutable no encontrado: {exe_name}"
            logging.error(error_msg)
            _close_err(error_msg)
        except PermissionError:
            error_msg = f"Sin permisos para ejecutar: {exe_name}"
            logging.error(error_msg)
            _close_err(error_msg)
        except subprocess.SubprocessError as e:
            error_msg = f"Error al lanzar proceso: {e}"
            logging.error(error_msg)
            _close_err(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado: {e}"
            logging.error(error_msg)
            _close_err(error_msg)

    def _close_ok():
        """Cierra diálogo tras lanzamiento exitoso."""
        logging.info(f"Lanzamiento completado: {exe_name}")
        try:
            dlg.close()
        finally:
            set_module_buttons_enabled(True)
            logging.debug("Diálogo de carga cerrado")

    def _close_err(error_msg: str):
        """Cierra diálogo y muestra error."""
        try:
            dlg.close()
        finally:
            set_module_buttons_enabled(True)
            logging.debug("Diálogo de carga cerrado")
            messagebox.showerror("Error al lanzar", f"No se pudo iniciar {exe_name}.\n{error_msg}")

    root.after(50, _do_launch)

# =============================================================================================
# VENTANA PRINCIPAL
# =============================================================================================

def main():
    """
    Función principal - inicializa y ejecuta la aplicación.
    
    Secuencia:
    1. Setup logging y validación de recursos
    2. Carga de configuración
    3. Creación de ventana principal con estilos TTK
    4. Construcción de interfaz (header, módulos, footer)
    5. Configuración de dimensiones y posición
    6. Inicio del bucle principal
    """
    # Inicialización
    setup_logging()
    
    resources_ok, missing = validate_resources()
    if not resources_ok:
        logging.warning(f"Algunos recursos no están disponibles: {missing}")
    
    config = load_config()
    window_config = config.get("window", {})
    
    # Inicialización de estado global
    global root, module_buttons, module_text_labels
    module_buttons = []
    module_text_labels = []
    
    # Crear ventana principal
    root = tk.Tk()
    root.title(APP_TITLE)
    
    colors = setup_ttk_styles()
    root.configure(bg=colors['background'])

    # Icono de la ventana
    try:
        ico = resource_path("assets", "icon.ico")
        if ico.exists():
            root.iconbitmap(default=str(ico))
            logging.debug("Icono .ico establecido")
    except Exception as e:
        logging.warning(f"Error al establecer icono: {e}")

    # Frame principal
    main_frame = ttk.Frame(root, style="Main.TFrame", padding=15)
    main_frame.pack(fill="both", expand=True)
    
    # === HEADER ===
    header_frame = ttk.Frame(main_frame, style="Main.TFrame")
    header_frame.pack(fill="x", pady=(0, 12))
    
    title_label = ttk.Label(header_frame,
                           text=APP_TITLE,
                           style="Header.TLabel")
    title_label.pack(pady=(0, 3))
    
    version_info = f"Versión {VERSION} • {DATE}"
    version_label = ttk.Label(header_frame,
                             text=version_info,
                             style="Version.TLabel")
    version_label.pack(pady=(0, 8))
    
    desc_label = create_rich_text_label(header_frame, APP_DESC, "SubHeader.TLabel", 1000, "center")
    desc_label.pack(pady=(0, 8))
    
    note_label = create_rich_text_label(header_frame, NOTE_TEXT, "Note.TLabel", 900, "center")
    note_label.pack(pady=(0, 10))
    
    separator = ttk.Separator(header_frame, orient='horizontal')
    separator.pack(fill="x", pady=(8, 15), padx=40)
    
    # === MÓDULOS ===
    modules_frame = ttk.Frame(main_frame, style="Main.TFrame")
    modules_frame.pack(fill="both", expand=True)
    
    section_title = ttk.Label(modules_frame,
                             text="Herramientas Disponibles",
                             style="SectionHeader.TLabel")
    section_title.pack(pady=(0, 10))
    
    # Generar tarjetas de módulos
    for i, m in enumerate(MODULES):
        card, txt_lbl, btn = make_simple_card(
            modules_frame,
            m,
            colors,
            on_click=lambda e=m["exe"], t=m["title"], info=m.get("loading_info", {}): lanzar(e, t, info)
        )
        card.pack(fill="x", pady=8, padx=12)
        module_buttons.append(btn)
        module_text_labels.append(txt_lbl)
    
    # === FOOTER ===
    footer_frame = ttk.Frame(main_frame, style="Main.TFrame")
    footer_frame.pack(fill="x", pady=(15, 0))
    
    separator2 = ttk.Separator(footer_frame, orient='horizontal')
    separator2.pack(fill="x", pady=(0, 12), padx=40)
    
    cite_text = f"✍️ {CITATION}"
    cite_label = create_rich_text_label(footer_frame, cite_text, "SubHeader.TLabel", 1200, "center")
    cite_label.pack(pady=(0, 3))

    # Configuración de ventana
    w = window_config.get("default_width", 980)
    h = window_config.get("default_height", 640)
    min_w = window_config.get("min_width", 860)
    min_h = window_config.get("min_height", 580)
    
    root.geometry(f"{w}x{h}")
    root.minsize(min_w, min_h)
    
    # Centrar en pantalla
    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    x = int((sw - w) / 2)
    y = int((sh - h) / 2.4)
    root.geometry(f"+{x}+{y}")
    
    logging.info(f"Ventana configurada: {w}x{h} en posición ({x}, {y})")
    logging.info("Iniciando bucle principal de la aplicación")
    
    # Bucle principal
    root.mainloop()
    
    logging.info("Aplicación cerrada")

# =============================================================================================
# PUNTO DE ENTRADA
# =============================================================================================

if __name__ == "__main__":
    main()
