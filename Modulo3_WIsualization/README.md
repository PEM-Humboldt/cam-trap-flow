# WIsualization — Module 3 of CamTrapFlow

**Statistical analysis and scientific visualization of camera-trap data**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)
![Part of](https://img.shields.io/badge/part%20of-CamTrapFlow%20v1.0-success.svg)

**English** | [Español](#wisualization--módulo-3-de-camtrapflow)

*Part of the [CamTrapFlow (CTF)](../README.md) suite · Last updated: 24 June 2026*

---

## Overview

WIsualization is the analysis and visualization stage of CamTrapFlow. It provides a graphical interface (PyQt5) to explore Wildlife Insights data and produce scientific figures with matplotlib, supporting quality control and interpretation before publication.

It reads the original Wildlife Insights export ZIP (project or initiative) — it does not process Camtrap DP packages.

### Visualizations

- Species-accumulation curves (sampling effort and richness).
- Circadian activity patterns.
- Deployment timelines (temporal coverage per site).
- Presence/absence matrices (spatial detection patterns).

Figures can be exported as PNG, PDF or SVG.

---

## Requirements

**End users**
- Windows 10/11 (64-bit). No Python required (portable executable).

**Developers**
- Python 3.12+
- Dependencies: PyQt5 (≥5.15), pandas (≥2.0), matplotlib (≥3.8), scipy (≥1.11). See [`requirements.txt`](requirements.txt).

---

## Getting started

**Run the packaged application (recommended)**
1. Download the CamTrapFlow release package: see the [main README](../README.md).
2. Launch the visualization module (directly, or through the CamTrapFlow Launcher).

**Run from source**
```bash
# from the Modulo3_WIsualization/ folder
python -m venv venv
venv\Scripts\activate            # Windows (use: source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python -m humboldt_viz           # or: python run_gui.py
```

> Note: the internal Python package is named `humboldt_viz`; the product name is **WIsualization**.

---

## Usage

1. Load the original Wildlife Insights export ZIP.
2. Choose an analysis (accumulation curve, activity pattern, deployment timeline, presence/absence).
3. Generate the figure.
4. Export it as PNG, PDF or SVG.

---

## Project structure

```
Modulo3_WIsualization/
├── src/humboldt_viz/
│   ├── __main__.py             # Entry point (python -m humboldt_viz)
│   ├── ui_main.py              # PyQt5 main interface
│   ├── core/
│   │   ├── io_detect.py        # File detection and reading
│   │   └── plots_mpl.py        # matplotlib plots
│   └── resources/icons/        # Application and institutional icons
├── run_gui.py                  # Development launch script
├── WIsualization.spec                  # PyInstaller configuration
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

## Build the executable

```bash
pyinstaller WIsualization.spec
# output: dist/WIsualization.exe (GUI, no console)
```

The `WIsualization.spec` file bundles resources (icons, styles) and the matplotlib/scipy dependencies.

---

## Third-party components

See the repository-level [`THIRD_PARTY_NOTICES.txt`](../THIRD_PARTY_NOTICES.txt).

## License

MIT — see [`LICENSE`](LICENSE).

## How to cite

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): an open, reproducible desktop workflow to mobilize camera-trap biodiversity data from Wildlife Insights to GBIF (v1.0)* [Software]. Red OTUS, Alexander von Humboldt Biological Resources Research Institute. https://github.com/PEM-Humboldt/cam-trap-flow

## Authors

**Cristian C. Acevedo** — Lead developer. Bioengineer (Universidad de Antioquia), Data Scientist. ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)
**Angélica Díaz-Pulido** — Co-author and scientific coordinator. Associate Researcher, Center for Socioecological Studies and Global Change, Knowledge Management Directorate, Alexander von Humboldt Biological Resources Research Institute. ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

---

<br>

# WIsualization — Módulo 3 de CamTrapFlow

**Análisis estadístico y visualización científica de datos de cámaras trampa**

[English](#wisualization--module-3-of-camtrapflow) | **Español**

*Parte de la suite [CamTrapFlow (CTF)](../README.md) · Última actualización: 24 de junio de 2026*

---

## Descripción

WIsualization es la etapa de análisis y visualización de CamTrapFlow. Ofrece una interfaz gráfica (PyQt5) para explorar datos de Wildlife Insights y producir figuras científicas con matplotlib, apoyando el control de calidad y la interpretación antes de publicar.

Lee el archivo ZIP original exportado desde Wildlife Insights (proyecto o iniciativa) — no procesa paquetes Camtrap DP.

### Visualizaciones

- Curvas de acumulación de especies (esfuerzo de muestreo y riqueza).
- Patrones de actividad circadiana.
- Líneas de tiempo de despliegues (cobertura temporal por sitio).
- Matrices de presencia/ausencia (patrones espaciales de detección).

Las figuras se pueden exportar como PNG, PDF o SVG.

---

## Requisitos

**Usuarios finales**
- Windows 10/11 (64 bits). No requiere Python (ejecutable portable).

**Desarrolladores**
- Python 3.12+
- Dependencias: PyQt5 (≥5.15), pandas (≥2.0), matplotlib (≥3.8), scipy (≥1.11). Ver [`requirements.txt`](requirements.txt).

---

## Inicio rápido

**Ejecutar la aplicación empaquetada (recomendado)**
1. Descarga el paquete de la versión de CamTrapFlow: ver el [README principal](../README.md).
2. Ejecuta el módulo de visualización (directamente o desde el CamTrapFlow Launcher).

**Ejecutar desde el código fuente**
```bash
# desde la carpeta Modulo3_WIsualization/
python -m venv venv
venv\Scripts\activate            # Windows (en macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python -m humboldt_viz           # o: python run_gui.py
```

> Nota: el paquete interno de Python se llama `humboldt_viz`; el nombre del producto es **WIsualization**.

---

## Uso

1. Carga el ZIP original exportado desde Wildlife Insights.
2. Elige un análisis (curva de acumulación, patrón de actividad, línea de tiempo de despliegues, presencia/ausencia).
3. Genera la figura.
4. Expórtala como PNG, PDF o SVG.

---

## Estructura del proyecto

```
Modulo3_WIsualization/
├── src/humboldt_viz/
│   ├── __main__.py             # Punto de entrada (python -m humboldt_viz)
│   ├── ui_main.py              # Interfaz principal PyQt5
│   ├── core/
│   │   ├── io_detect.py        # Detección y lectura de archivos
│   │   └── plots_mpl.py        # Gráficos matplotlib
│   └── resources/icons/        # Iconos de la aplicación e institucionales
├── run_gui.py                  # Script de ejecución para desarrollo
├── WIsualization.spec                  # Configuración PyInstaller
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

## Compilar el ejecutable

```bash
pyinstaller WIsualization.spec
# salida: dist/WIsualization.exe (GUI, sin consola)
```

El archivo `WIsualization.spec` incluye los recursos (iconos, estilos) y las dependencias de matplotlib/scipy.

---

## Componentes de terceros

Ver el aviso a nivel de repositorio [`THIRD_PARTY_NOTICES.txt`](../THIRD_PARTY_NOTICES.txt).

## Licencia

MIT — ver [`LICENSE`](LICENSE).

## Cómo citar

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): flujo de trabajo de escritorio, abierto y reproducible, para movilizar datos de biodiversidad de fototrampeo desde Wildlife Insights hacia GBIF (v1.0)* [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. https://github.com/PEM-Humboldt/cam-trap-flow

## Autoría

**Cristian C. Acevedo** — Desarrollador principal. Bioingeniero (Universidad de Antioquia), Data Scientist. ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)
**Angélica Díaz-Pulido** — Coautora y coordinadora científica. Investigadora Adjunta, Centro de Estudios Socioecológicos y Cambio Global, Dirección de Conocimiento, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

---

*Módulo 3 de la suite CamTrapFlow (CTF) — Instituto de Investigación de Recursos Biológicos Alexander von Humboldt.*
