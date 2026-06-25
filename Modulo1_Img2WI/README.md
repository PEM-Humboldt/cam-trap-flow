# Img2WI — Module 1 of CamTrapFlow

**Convert camera-trap videos into standardized image sequences for Wildlife Insights**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Part of](https://img.shields.io/badge/part%20of-CamTrapFlow%20v1.0-success.svg)

**English** | [Español](#img2wi--módulo-1-de-camtrapflow)

*Part of the [CamTrapFlow (CTF)](../README.md) suite · Last updated: 24 June 2026*

---

## Overview

Img2WI is a desktop application that automatically converts camera-trap videos (`.MP4`, `.MOV`, `.AVI`) into individual, organized images, ready for analysis or upload to Wildlife Insights. It is the first stage of the CamTrapFlow workflow.

### Features

- Intuitive graphical interface (PyQt5); no technical knowledge required.
- Dual processing engine: `wiutils` (optimized for MP4) and FFmpeg (AVI/MOV).
- Configurable interval: extract one image every X seconds (0.5, 1, 2, 3, 4, 5).
- Automatic organization: all images in a single timestamped output folder.
- Systematic naming: `<video_name>_000001.jpg`, `<video_name>_000002.jpg`, …
- Real-time monitoring: structured logs, progress bar and timer.
- Asynchronous processing: the interface stays responsive.
- Portable executable (.exe), no installation required.

---

## Requirements

**End users**
- Windows 10/11 (64-bit). No additional dependencies.

**Developers**
- Python 3.10+
- Python dependencies: see [`requirements.txt`](requirements.txt)
- FFmpeg (static x64 build) — [download](https://www.gyan.dev/ffmpeg/builds/), placed at `app/bin/ffmpeg.exe` (or available on the system PATH).

---

## Getting started

**Run the packaged application (recommended)**
1. Download the CamTrapFlow release package: see the [main README](../README.md).
2. Launch `Img2WI.exe` (directly, or through the CamTrapFlow Launcher). No installation required.

**Run from source**
```bash
# from the Modulo1_Img2WI/ folder
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
# place FFmpeg at app/bin/ffmpeg.exe (see Requirements)
python app/main.py
```

---

## Usage

1. Select the folder containing your videos.
2. Set the extraction interval (seconds between frames; 1 s is a common choice).
3. Start processing.
4. Images are written to a timestamped folder: `Img2WI_<folder_name>_HH-MM_DD_MM_YYYY/`.

**Supported formats:** `.MP4` (wiutils, FFmpeg fallback), `.MOV` and `.AVI` (FFmpeg).

---

## Project structure

```
Modulo1_Img2WI/
├── app/
│   ├── bin/ffmpeg.exe        # FFmpeg binary (see Requirements / THIRD_PARTY_NOTICES)
│   ├── main.py               # Entry point
│   ├── ui_main.py            # Graphical interface
│   └── processor.py          # Processing logic
├── resources/icons/          # Application and institutional icons
├── ExtractorCamtrap.spec     # PyInstaller configuration
├── requirements.txt
├── THIRD_PARTY_NOTICES.txt
└── README.md
```

## Build the executable

```bash
python -m PyInstaller ExtractorCamtrap.spec --clean
# output: dist/Img2WI.exe (portable; bundles Python, PyQt5 and FFmpeg)
```

PyInstaller generates temporary `build/` and `dist/` folders (excluded from Git). Antivirus software may flag PyInstaller executables as false positives.

---

## Troubleshooting

- **"FFmpeg not found":** ensure `ffmpeg.exe` is at `app/bin/`, or install FFmpeg on the system PATH.
- **"No videos found":** confirm files are `.MP4/.MOV/.AVI` and not in hidden folders.
- **The executable does not open:** run as administrator, check that antivirus is not blocking it, or re-download if corrupted.
- **Disk space / time:** smaller intervals produce more images and take longer; process large batches in groups.

---

## Third-party components

This module redistributes the FFmpeg binary under its own license. See
[`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt) and the repository-level
[`THIRD_PARTY_NOTICES.txt`](../THIRD_PARTY_NOTICES.txt).

## License

MIT — see [`LICENSE`](../LICENSE).

## How to cite

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): an open, reproducible desktop workflow to mobilize camera-trap biodiversity data from Wildlife Insights to GBIF (v1.0)* [Software]. Red OTUS, Alexander von Humboldt Biological Resources Research Institute. https://github.com/PEM-Humboldt/cam-trap-flow

## Authors

**Cristian C. Acevedo** — Lead developer. Bioengineer (Universidad de Antioquia), Data Scientist. ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)
**Angélica Díaz-Pulido** — Co-author and scientific coordinator. Associate Researcher, Center for Socioecological Studies and Global Change, Knowledge Management Directorate, Alexander von Humboldt Biological Resources Research Institute. ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

---

<br>

# Img2WI — Módulo 1 de CamTrapFlow

**Convierte videos de cámaras trampa en secuencias de imágenes estandarizadas para Wildlife Insights**

[English](#img2wi--module-1-of-camtrapflow) | **Español**

*Parte de la suite [CamTrapFlow (CTF)](../README.md) · Última actualización: 24 de junio de 2026*

---

## Descripción

Img2WI es una aplicación de escritorio que convierte automáticamente videos de cámaras trampa (`.MP4`, `.MOV`, `.AVI`) en imágenes individuales y organizadas, listas para análisis o carga en Wildlife Insights. Es la primera etapa del flujo de CamTrapFlow.

### Características

- Interfaz gráfica intuitiva (PyQt5); no requiere conocimientos técnicos.
- Motor de procesamiento dual: `wiutils` (optimizado para MP4) y FFmpeg (AVI/MOV).
- Intervalo configurable: extrae una imagen cada X segundos (0.5, 1, 2, 3, 4, 5).
- Organización automática: todas las imágenes en una sola carpeta con marca temporal.
- Nomenclatura sistemática: `<nombre_video>_000001.jpg`, `<nombre_video>_000002.jpg`, …
- Monitoreo en tiempo real: logs estructurados, barra de progreso y cronómetro.
- Procesamiento asíncrono: la interfaz no se congela.
- Ejecutable portable (.exe), sin instalación.

---

## Requisitos

**Usuarios finales**
- Windows 10/11 (64 bits). Sin dependencias adicionales.

**Desarrolladores**
- Python 3.10+
- Dependencias Python: ver [`requirements.txt`](requirements.txt)
- FFmpeg (build static x64) — [descargar](https://www.gyan.dev/ffmpeg/builds/), ubicado en `app/bin/ffmpeg.exe` (o disponible en el PATH del sistema).

---

## Inicio rápido

**Ejecutar la aplicación empaquetada (recomendado)**
1. Descarga el paquete de la versión de CamTrapFlow: ver el [README principal](../README.md).
2. Ejecuta `Img2WI.exe` (directamente o desde el CamTrapFlow Launcher). Sin instalación.

**Ejecutar desde el código fuente**
```bash
# desde la carpeta Modulo1_Img2WI/
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
# coloca FFmpeg en app/bin/ffmpeg.exe (ver Requisitos)
python app/main.py
```

---

## Uso

1. Selecciona la carpeta que contiene tus videos.
2. Define el intervalo de extracción (segundos entre fotogramas; 1 s es una elección común).
3. Inicia el procesamiento.
4. Las imágenes se guardan en una carpeta con marca temporal: `Img2WI_<nombre_carpeta>_HH-MM_DD_MM_AAAA/`.

**Formatos soportados:** `.MP4` (wiutils, con FFmpeg de respaldo), `.MOV` y `.AVI` (FFmpeg).

---

## Estructura del proyecto

```
Modulo1_Img2WI/
├── app/
│   ├── bin/ffmpeg.exe        # Binario FFmpeg (ver Requisitos / THIRD_PARTY_NOTICES)
│   ├── main.py               # Punto de entrada
│   ├── ui_main.py            # Interfaz gráfica
│   └── processor.py          # Lógica de procesamiento
├── resources/icons/          # Iconos de la aplicación e institucionales
├── ExtractorCamtrap.spec     # Configuración PyInstaller
├── requirements.txt
├── THIRD_PARTY_NOTICES.txt
└── README.md
```

## Compilar el ejecutable

```bash
python -m PyInstaller ExtractorCamtrap.spec --clean
# salida: dist/Img2WI.exe (portable; incluye Python, PyQt5 y FFmpeg)
```

PyInstaller genera carpetas temporales `build/` y `dist/` (excluidas de Git). El antivirus puede marcar falsos positivos con ejecutables de PyInstaller.

---

## Solución de problemas

- **"FFmpeg no encontrado":** verifica que `ffmpeg.exe` esté en `app/bin/`, o instala FFmpeg en el PATH del sistema.
- **"No se encontraron videos":** confirma que los archivos sean `.MP4/.MOV/.AVI` y no estén en carpetas ocultas.
- **El ejecutable no abre:** ejecútalo como administrador, revisa que el antivirus no lo bloquee, o descárgalo de nuevo si está corrupto.
- **Espacio en disco / tiempo:** intervalos menores producen más imágenes y tardan más; procesa lotes grandes por grupos.

---

## Componentes de terceros

Este módulo redistribuye el binario FFmpeg bajo su propia licencia. Ver
[`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt) y el aviso a nivel de
repositorio [`THIRD_PARTY_NOTICES.txt`](../THIRD_PARTY_NOTICES.txt).

## Licencia

MIT — ver [`LICENSE`](../LICENSE).

## Cómo citar

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): flujo de trabajo de escritorio, abierto y reproducible, para movilizar datos de biodiversidad de fototrampeo desde Wildlife Insights hacia GBIF (v1.0)* [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. https://github.com/PEM-Humboldt/cam-trap-flow

## Autoría

**Cristian C. Acevedo** — Desarrollador principal. Bioingeniero (Universidad de Antioquia), Data Scientist. ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)
**Angélica Díaz-Pulido** — Coautora y coordinadora científica. Investigadora Adjunta, Centro de Estudios Socioecológicos y Cambio Global, Dirección de Conocimiento, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

---

*Módulo 1 de la suite CamTrapFlow (CTF) — Instituto de Investigación de Recursos Biológicos Alexander von Humboldt.*
