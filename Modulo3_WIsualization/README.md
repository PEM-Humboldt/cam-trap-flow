# 🐆 Humboldt Viz - Camera Trap Visualization Module

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Módulo de visualización para datos de cámaras trampa desarrollado para el Instituto Humboldt. Interfaz gráfica (PyQt5) para análisis y visualización de datos de fauna mediante matplotlib.

## 📋 Características

- 🖥️ Interfaz gráfica intuitiva basada en PyQt5
- 📊 Visualizaciones con matplotlib integradas
- 📁 Detección y lectura de archivos de datos
- 🔧 Análisis estadístico con scipy y pandas

## 🗂️ Estructura del Proyecto

```
Modulo3_WIsualization/
├── src/
│   └── humboldt_viz/
│       ├── __init__.py
│       ├── __main__.py           # Punto de entrada
│       ├── ui_main.py            # Interfaz principal PyQt5
│       ├── core/
│       │   ├── io_detect.py      # Detección y lectura de archivos
│       │   └── plots_mpl.py      # Gráficos matplotlib
│       └── resources/
│           ├── icons/            # Iconos de la aplicación
│           │   ├── app.ico
│           │   └── logo_humboldt.png
│           └── styles/           # Estilos CSS/QSS
├── build.spec                    # Configuración PyInstaller
├── pyproject.toml               # Configuración del proyecto
├── requirements.txt             # Dependencias
├── run_gui.py                   # Script de desarrollo
├── LICENSE                      # Licencia MIT
└── README.md                    # Esta documentación
```

## 🚀 Instalación y Uso

### Requisitos Previos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Ejecución en Modo Desarrollo

Opción 1 - Usando el módulo:
```bash
python -m humboldt_viz
```

Opción 2 - Usando el script de desarrollo:
```bash
python run_gui.py
```

## 📦 Generación del Ejecutable

Para crear una versión distribuible de la aplicación:

### 1. Instalar PyInstaller

```bash
pip install pyinstaller
```

### 2. Construir el Ejecutable

```bash
pyinstaller build.spec
```

El ejecutable se generará en la carpeta `dist/HumboldtViz/`:
- `HumboldtViz.exe` - Aplicación principal
- Carpetas con librerías y recursos necesarios

### Notas sobre el Build

- El archivo `build.spec` está preconfigurado con:
  - Inclusión de recursos (iconos, estilos)
  - Dependencias de matplotlib y scipy
  - Sin ventana de consola (GUI pura)
  - Compresión UPX activada (si disponible)

## 🛠️ Desarrollo

### Configuración del Entorno

1. Clonar el repositorio
2. Crear un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
3. Instalar dependencias: `pip install -r requirements.txt`

### Dependencias Principales

- **PyQt5** (≥5.15): Framework GUI
- **pandas** (≥2.0): Manipulación de datos
- **matplotlib** (≥3.8): Visualización de gráficos
- **scipy** (≥1.11): Análisis estadístico

## 🤝 Contribuciones

Este proyecto es parte del desarrollo de software para el Instituto Humboldt - Contrato 25_064.

---

# 👥 Autoría

**Desarrollo principal:**  
Cristian C. Acevedo

**Coordinación científica:**  
Angélica Diaz-Pulido

**Institución:**  
Instituto de Investigación de Recursos Biológicos Alexander von Humboldt – Red OTUS

**Proyecto:**  
Contrato 25-064 
Desarrollo de Software CamTrapFlow (CTF) y Dashboards

**Año:** 2025

---
## 📚 Cómo Citar

Si utilizas esta herramienta en tu investigación, por favor cítala como:

Acevedo, C. C., & Diaz-Pulido, A. (2025). *CamTrapFlow (CTF) - Suite integrada para el procesamiento, estandarización y análisis de datos de fototrampe (v1.0.0)* [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. https://github.com/PEM-Humboldt/cam-trap-flow


## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

**Nota**: Este es el Módulo 3 (Visualización) del proyecto CamTrapFlow (CTF).
