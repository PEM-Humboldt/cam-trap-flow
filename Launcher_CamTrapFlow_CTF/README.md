# CamTrapFlow Launcher

**Unified graphical interface to run the three CamTrapFlow modules from a single entry point**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Part of](https://img.shields.io/badge/part%20of-CamTrapFlow%20v1.0-success.svg)

**English** | [Español](#camtrapflow-launcher-1)

*Part of the [CamTrapFlow (CTF)](../README.md) suite · Last updated: 24 June 2026*

---

## Overview

The CamTrapFlow Launcher is a desktop application that centralizes access to the three tools of the suite, providing a single entry point for the complete camera-trap data workflow:

- **Img2WI** — extract frames from video for Wildlife Insights.
- **WI2CamtrapDP** — convert Wildlife Insights exports to Camtrap DP (v1.0).
- **WIsualization** — analysis and visualization (accumulation curves, activity, presence/absence).

### Features

- Centralized access to all tools from one application.
- Each module launches as an independent process.
- External configuration via `config.json` (load times and window size).
- Full logging in `launcher.log` for diagnostics.
- PyInstaller-compatible (one-file and development modes).
- Robust resource-path handling for packaged executables.

---

## Requirements

**End users**
- Windows 10/11 (optimized for Windows)
- Minimum resolution 1000×600 (1366×768+ recommended)
- 4 GB RAM minimum (8 GB recommended)

**Developers**
- Python 3.10+ (uses the standard library, including `tkinter`)

The launcher expects the module executables to be available in a `bin/` folder: `Img2WI.exe`, `WI2CamtrapDP.exe`, `WIsualization.exe`.

---

## Getting started

**Run the packaged application (recommended)**
1. Download the CamTrapFlow release package: see the [main README](../README.md).
2. Keep `CamTrapFlow.exe` next to the `assets/` and `bin/` folders (and optional `config.json`).
3. Double-click `CamTrapFlow.exe`.

**Run from source**
```bash
# from the Launcher_CamTrapFlow_CTF/ folder
python Lanzador.py
```

---

## Configuration (`config.json`)

Optional file to customize load times and window dimensions:

```json
{
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
```

- `durations_ms`: how long the loading dialog stays visible per module (adjust to each module's real startup time).
- `window`: initial and minimum window dimensions.

---

## Project structure

```
Launcher_CamTrapFlow_CTF/
├── Lanzador.py               # Main launcher script (entry point)
├── config.json              # Optional configuration
├── assets/                  # Icons and institutional logo
├── CamTrapFlow.spec         # PyInstaller configuration
└── README.md
```

## Build the executable

```bash
pyinstaller CamTrapFlow.spec
# output: dist/CamTrapFlow.exe
```

---

## Troubleshooting

- **The launcher does not start:** ensure `assets/` and `bin/` are in the same folder; check `launcher.log`; run from a terminal to see console errors.
- **Module not found:** confirm the executables exist in `bin/` and have execution permissions.
- **Loading dialog stays too long:** some modules take time to load; adjust the times in `config.json`.
- **Icons not shown:** verify the files in `assets/`; icons are optional and do not affect functionality.

---

## License

MIT — see [`LICENSE`](../LICENSE).

## How to cite

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): an open, reproducible desktop workflow to mobilize camera-trap biodiversity data from Wildlife Insights to GBIF (v1.0)* [Software]. Red OTUS, Alexander von Humboldt Biological Resources Research Institute. https://github.com/PEM-Humboldt/cam-trap-flow

## Authors

**Cristian C. Acevedo** — Lead developer. Bioengineer (Universidad de Antioquia), Data Scientist. ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)
**Angélica Díaz-Pulido** — Co-author and scientific coordinator. Associate Researcher, Center for Socioecological Studies and Global Change, Knowledge Management Directorate, Alexander von Humboldt Biological Resources Research Institute. ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

---

<br>

# CamTrapFlow Launcher

**Interfaz gráfica unificada para ejecutar los tres módulos de CamTrapFlow desde un único punto de acceso**

[English](#camtrapflow-launcher) | **Español**

*Parte de la suite [CamTrapFlow (CTF)](../README.md) · Última actualización: 24 de junio de 2026*

---

## Descripción

El CamTrapFlow Launcher es una aplicación de escritorio que centraliza el acceso a las tres herramientas de la suite, ofreciendo un único punto de entrada para el flujo completo de datos de fototrampeo:

- **Img2WI** — extracción de fotogramas de video para Wildlife Insights.
- **WI2CamtrapDP** — conversión de exportaciones de Wildlife Insights a Camtrap DP (v1.0).
- **WIsualization** — análisis y visualización (curvas de acumulación, actividad, presencia/ausencia).

### Características

- Acceso centralizado a todas las herramientas desde una sola aplicación.
- Cada módulo se ejecuta como un proceso independiente.
- Configuración externa mediante `config.json` (tiempos de carga y tamaño de ventana).
- Registro completo en `launcher.log` para diagnóstico.
- Compatible con PyInstaller (modo one-file y desarrollo).
- Gestión robusta de rutas de recursos para ejecutables empaquetados.

---

## Requisitos

**Usuarios finales**
- Windows 10/11 (optimizado para Windows)
- Resolución mínima 1000×600 (recomendado 1366×768+)
- 4 GB de RAM mínimo (8 GB recomendado)

**Desarrolladores**
- Python 3.10+ (usa la biblioteca estándar, incluido `tkinter`)

El launcher espera que los ejecutables de los módulos estén disponibles en una carpeta `bin/`: `Img2WI.exe`, `WI2CamtrapDP.exe`, `WIsualization.exe`.

---

## Inicio rápido

**Ejecutar la aplicación empaquetada (recomendado)**
1. Descarga el paquete de la versión de CamTrapFlow: ver el [README principal](../README.md).
2. Mantén `CamTrapFlow.exe` junto a las carpetas `assets/` y `bin/` (y el `config.json` opcional).
3. Haz doble clic en `CamTrapFlow.exe`.

**Ejecutar desde el código fuente**
```bash
# desde la carpeta Launcher_CamTrapFlow_CTF/
python Lanzador.py
```

---

## Configuración (`config.json`)

Archivo opcional para personalizar tiempos de carga y dimensiones de ventana:

```json
{
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
```

- `durations_ms`: cuánto permanece visible el diálogo de carga por módulo (ajustar al tiempo real de arranque de cada uno).
- `window`: dimensiones inicial y mínima de la ventana.

---

## Estructura del proyecto

```
Launcher_CamTrapFlow_CTF/
├── Lanzador.py               # Script principal del launcher (punto de entrada)
├── config.json              # Configuración opcional
├── assets/                  # Iconos y logo institucional
├── CamTrapFlow.spec         # Configuración PyInstaller
└── README.md
```

## Compilar el ejecutable

```bash
pyinstaller CamTrapFlow.spec
# salida: dist/CamTrapFlow.exe
```

---

## Solución de problemas

- **El launcher no inicia:** verifica que `assets/` y `bin/` estén en la misma carpeta; revisa `launcher.log`; ejecútalo desde una terminal para ver errores en consola.
- **Módulo no encontrado:** confirma que los ejecutables existen en `bin/` y tienen permisos de ejecución.
- **El diálogo de carga permanece mucho tiempo:** algunos módulos tardan en cargar; ajusta los tiempos en `config.json`.
- **No se muestran los iconos:** verifica los archivos en `assets/`; los iconos son opcionales y no afectan la funcionalidad.

---

## Licencia

MIT — ver [`LICENSE`](../LICENSE).

## Cómo citar

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): flujo de trabajo de escritorio, abierto y reproducible, para movilizar datos de biodiversidad de fototrampeo desde Wildlife Insights hacia GBIF (v1.0)* [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. https://github.com/PEM-Humboldt/cam-trap-flow

## Autoría

**Cristian C. Acevedo** — Desarrollador principal. Bioingeniero (Universidad de Antioquia), Data Scientist. ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)
**Angélica Díaz-Pulido** — Coautora y coordinadora científica. Investigadora Adjunta, Centro de Estudios Socioecológicos y Cambio Global, Dirección de Conocimiento, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

---

*Lanzador de la suite CamTrapFlow (CTF) — Instituto de Investigación de Recursos Biológicos Alexander von Humboldt.*
