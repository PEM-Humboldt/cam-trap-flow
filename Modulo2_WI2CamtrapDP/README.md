# WI2CamtrapDP — Module 2 of CamTrapFlow

**Convert Wildlife Insights project exports into Camtrap DP (v1.0) packages, ready for GBIF and SiB Colombia**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Camtrap DP](https://img.shields.io/badge/Camtrap%20DP-1.0-success.svg)
![Part of](https://img.shields.io/badge/part%20of-CamTrapFlow%20v1.0-success.svg)

**English** | [Español](#wi2camtrapdp--módulo-2-de-camtrapflow)

*Part of the [CamTrapFlow (CTF)](../README.md) suite · Last updated: 24 June 2026*

---

## Overview

WI2CamtrapDP is a desktop application that converts [Wildlife Insights](https://www.wildlifeinsights.org/) project exports into the [Camtrap Data Package (Camtrap DP)](https://camtrap-dp.tdwg.org/) standard, version 1.0, for scientific publication and standardized analysis of camera-trap data. It is the standardization stage of the CamTrapFlow workflow.

### Features

- Automated conversion of Wildlife Insights projects to Camtrap DP.
- Integrated validation with the Frictionless framework (v5.x).
- Intuitive graphical interface (PyQt5).
- Robust taxonomy handling (incomplete data detection, multiple identifications).
- Automatic time-zone conversion to ISO-8601 UTC.
- Automatic packaging into a ZIP with `datapackage.json` + CSVs.
- Built-in email template to request publication from SiB Colombia.
- Distributed as a portable executable (.exe), no Python required.

---

## Requirements

**End users**
- Windows 10/11 (64-bit). No Python or dependencies required.

**Developers**
- Python 3.10+
- Dependencies: see [`requirements.txt`](requirements.txt)

---

## Getting started

**Run the packaged application (recommended)**
1. Download the CamTrapFlow release package: see the [main README](../README.md).
2. Launch `WI2CamtrapDP.exe` (directly, or through the CamTrapFlow Launcher).

**Run from source**
```bash
# from the Modulo2_WI2CamtrapDP/ folder
python -m venv venv
venv\Scripts\activate            # Windows (use: source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python app.py
```

---

## Workflow

1. **Export from Wildlife Insights:** sign in, select your **project** (not an initiative) and download the full export (ZIP with the CSV tables).
2. **Open WI2CamtrapDP** and select the Wildlife Insights ZIP.
3. **Configure options:** Frictionless validation, ZIP packaging, open folder when finished, and time zone (default `America/Bogota`).
4. **Process** and monitor progress in the log.
5. **Results:**
   ```
   WI2CamtrapDP_{project_name}/
   ├── output/
   │   ├── deployments.csv
   │   ├── media.csv
   │   ├── observations.csv
   │   └── datapackage.json
   └── WI2CamtrapDP_{project_name}.zip
   ```
6. **Publish (optional):** use the email template to contact SiB Colombia.

---

## Input and output

**Input — Wildlife Insights export** (ZIP, PROJECT export):

| File | Description |
| --- | --- |
| `projects.csv` | Project metadata (name, coordinator, licenses, objectives) |
| `cameras.csv` | Equipment information (make, model, serial) |
| `deployments.csv` | Spatio-temporal deployments (coordinates, dates, locations) |
| `images_{id}.csv` | Image records + taxonomic identifications |

> Only **PROJECT** exports are supported (a single `images_*.csv`). INITIATIVE exports (multiple `images_*.csv`) are not supported.

**Output — Camtrap DP v1.0** (3 CSV tables + JSON metadata):

| File | Description |
| --- | --- |
| `deployments.csv` | Camera deployments (deploymentID, locationName, latitude, longitude, start/end, cameraModel) |
| `media.csv` | Media files (mediaID, deploymentID, captureMethod, timestamp, filePath, fileMediatype) |
| `observations.csv` | Taxonomic observations (observationID, mediaID, scientificName, vernacularName, count, observationType) |
| `datapackage.json` | Package metadata (title, description, licenses, contributors, validation schemas) |

---

## Key validations

**Stops the process:** `No CV Result` values in taxonomic fields; INITIATIVE export instead of PROJECT; required fields empty in `deployments.csv`.

**Warnings (process continues):** empty optional fields (e.g., `cameraModel`, `age`, `sex`); out-of-range coordinates (replaced by NA); malformed timestamps (corrected or discarded).

**Optional Frictionless validation:** verifies the full Data Package structure, data types and constraints, producing a detailed per-resource/field/row report.

---

## Main transformations

- **Taxonomy (Wildlife Insights → Darwin Core):** `genus` + `species` → `scientificName`; `common_name` → `vernacularName`.
- **Dates (local → ISO-8601 UTC):** e.g., `2023-05-15 14:23:11` (America/Bogota, GMT-5) → `2023-05-15T19:23:11Z`.
- **Multiple observations:** one photo with two identified species → one row in `media.csv` and two rows in `observations.csv`.
- **Observation classification:** Blank → `blank`; Human → `human` (Homo sapiens); Vehicle → `vehicle`; Unknown → `unknown`; species name → `animal` (Genus species).

---

## Project structure

```
Modulo2_WI2CamtrapDP/
├── app.py                      # Main application (GUI) — entry point
├── camtrapdp/                  # Core package
│   ├── config.py               # Default configuration
│   ├── processor.py            # WI → Camtrap DP transformation engine
│   ├── utils.py                # Utilities (dates, MIME, text cleanup)
│   ├── validator.py            # Frictionless validation
│   └── schemas/                # Camtrap DP v1.0 JSON schemas (TDWG)
├── ui/camtrapdp.ui             # Qt Designer interface
├── assets/                     # Icons and institutional logo
├── camtrapdp.spec              # PyInstaller configuration
├── requirements.txt
├── GUIA_DESARROLLO.md          # Detailed development guide
├── CONTRIBUTING.md
├── THIRD_PARTY_NOTICES.txt
├── LICENSE
└── README.md
```

## Build the executable

```bash
python -m PyInstaller camtrapdp.spec --clean
# output: dist/Camtrap DP.exe (standalone, ~95-110 MB)
```

The `.spec` file already includes the icon, resources and hidden dependencies. The `build/` and `dist/` folders are temporary and excluded from Git.

---

## Third-party components

This module bundles the Camtrap DP 1.0 JSON schemas (TDWG). See
[`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt) and the repository-level
[`THIRD_PARTY_NOTICES.txt`](../THIRD_PARTY_NOTICES.txt).

## License

MIT — see [`LICENSE`](LICENSE).

## How to cite

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): an open, reproducible desktop workflow to mobilize camera-trap biodiversity data from Wildlife Insights to GBIF (v1.0)* [Software]. Red OTUS, Alexander von Humboldt Biological Resources Research Institute. https://github.com/PEM-Humboldt/cam-trap-flow

## Authors

**Cristian C. Acevedo** — Lead developer. Bioengineer (Universidad de Antioquia), Data Scientist. ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)
**Angélica Díaz-Pulido** — Co-author and scientific coordinator. Associate Researcher, Center for Socioecological Studies and Global Change, Knowledge Management Directorate, Alexander von Humboldt Biological Resources Research Institute. ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

## References

[Camtrap DP](https://camtrap-dp.tdwg.org/) · [Wildlife Insights](https://www.wildlifeinsights.org/) · [Frictionless](https://framework.frictionlessdata.io/) · [SiB Colombia](https://biodiversidad.co/) · [GBIF](https://www.gbif.org/)

---

<br>

# WI2CamtrapDP — Módulo 2 de CamTrapFlow

**Convierte exportaciones de proyecto de Wildlife Insights en paquetes Camtrap DP (v1.0), listos para GBIF y SiB Colombia**

[English](#wi2camtrapdp--module-2-of-camtrapflow) | **Español**

*Parte de la suite [CamTrapFlow (CTF)](../README.md) · Última actualización: 24 de junio de 2026*

---

## Descripción

WI2CamtrapDP es una aplicación de escritorio que convierte las exportaciones de proyecto de [Wildlife Insights](https://www.wildlifeinsights.org/) al estándar [Camtrap Data Package (Camtrap DP)](https://camtrap-dp.tdwg.org/), versión 1.0, para publicación científica y análisis estandarizado de datos de fototrampeo. Es la etapa de estandarización del flujo de CamTrapFlow.

### Características

- Conversión automatizada de proyectos de Wildlife Insights a Camtrap DP.
- Validación integrada con el framework Frictionless (v5.x).
- Interfaz gráfica intuitiva (PyQt5).
- Gestión robusta de taxonomía (detección de datos incompletos, identificaciones múltiples).
- Conversión automática de zonas horarias a ISO-8601 UTC.
- Empaquetado automático en ZIP con `datapackage.json` + CSVs.
- Plantilla de correo integrada para solicitar publicación al SiB Colombia.
- Se distribuye como ejecutable portable (.exe), sin requerir Python.

---

## Requisitos

**Usuarios finales**
- Windows 10/11 (64 bits). No requiere Python ni dependencias.

**Desarrolladores**
- Python 3.10+
- Dependencias: ver [`requirements.txt`](requirements.txt)

---

## Inicio rápido

**Ejecutar la aplicación empaquetada (recomendado)**
1. Descarga el paquete de la versión de CamTrapFlow: ver el [README principal](../README.md).
2. Ejecuta `WI2CamtrapDP.exe` (directamente o desde el CamTrapFlow Launcher).

**Ejecutar desde el código fuente**
```bash
# desde la carpeta Modulo2_WI2CamtrapDP/
python -m venv venv
venv\Scripts\activate            # Windows (en macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

---

## Flujo de trabajo

1. **Exportar desde Wildlife Insights:** inicia sesión, selecciona tu **proyecto** (no una iniciativa) y descarga la exportación completa (ZIP con las tablas CSV).
2. **Abrir WI2CamtrapDP** y seleccionar el ZIP de Wildlife Insights.
3. **Configurar opciones:** validación Frictionless, empaquetado ZIP, abrir carpeta al terminar y zona horaria (predeterminada `America/Bogota`).
4. **Procesar** y monitorear el progreso en el log.
5. **Resultados:**
   ```
   WI2CamtrapDP_{nombre_proyecto}/
   ├── output/
   │   ├── deployments.csv
   │   ├── media.csv
   │   ├── observations.csv
   │   └── datapackage.json
   └── WI2CamtrapDP_{nombre_proyecto}.zip
   ```
6. **Publicar (opcional):** usa la plantilla de correo para contactar al SiB Colombia.

---

## Entrada y salida

**Entrada — Exportación de Wildlife Insights** (ZIP, exportación de PROYECTO):

| Archivo | Descripción |
| --- | --- |
| `projects.csv` | Metadatos del proyecto (nombre, coordinador, licencias, objetivos) |
| `cameras.csv` | Información de equipos (fabricante, modelo, serial) |
| `deployments.csv` | Despliegues espaciotemporales (coordenadas, fechas, ubicaciones) |
| `images_{id}.csv` | Registros fotográficos + identificaciones taxonómicas |

> Solo se admiten exportaciones de **PROYECTO** (un único `images_*.csv`). Las de INICIATIVA (múltiples `images_*.csv`) no son soportadas.

**Salida — Camtrap DP v1.0** (3 tablas CSV + metadatos JSON):

| Archivo | Descripción |
| --- | --- |
| `deployments.csv` | Despliegues de cámaras (deploymentID, locationName, latitude, longitude, inicio/fin, cameraModel) |
| `media.csv` | Archivos multimedia (mediaID, deploymentID, captureMethod, timestamp, filePath, fileMediatype) |
| `observations.csv` | Observaciones taxonómicas (observationID, mediaID, scientificName, vernacularName, count, observationType) |
| `datapackage.json` | Metadatos del paquete (título, descripción, licencias, contribuidores, esquemas de validación) |

---

## Validaciones clave

**Detiene el proceso:** valores `No CV Result` en campos taxonómicos; exportación de INICIATIVA en lugar de PROYECTO; campos requeridos vacíos en `deployments.csv`.

**Advertencias (el proceso continúa):** campos opcionales vacíos (p. ej. `cameraModel`, `age`, `sex`); coordenadas fuera de rango (se reemplazan por NA); timestamps malformados (se corrigen o descartan).

**Validación opcional Frictionless:** verifica la estructura completa del Data Package, tipos de datos y restricciones, generando un reporte detallado por recurso/campo/fila.

---

## Transformaciones principales

- **Taxonomía (Wildlife Insights → Darwin Core):** `genus` + `species` → `scientificName`; `common_name` → `vernacularName`.
- **Fechas (local → ISO-8601 UTC):** p. ej. `2023-05-15 14:23:11` (America/Bogota, GMT-5) → `2023-05-15T19:23:11Z`.
- **Observaciones múltiples:** una foto con dos especies identificadas → una fila en `media.csv` y dos en `observations.csv`.
- **Clasificación de observaciones:** Blank → `blank`; Human → `human` (Homo sapiens); Vehicle → `vehicle`; Unknown → `unknown`; nombre de especie → `animal` (Genus species).

---

## Estructura del proyecto

```
Modulo2_WI2CamtrapDP/
├── app.py                      # Aplicación principal (GUI) — punto de entrada
├── camtrapdp/                  # Paquete principal
│   ├── config.py               # Configuración por defecto
│   ├── processor.py            # Motor de transformación WI → Camtrap DP
│   ├── utils.py                # Utilidades (fechas, MIME, limpieza de texto)
│   ├── validator.py            # Validación con Frictionless
│   └── schemas/                # Esquemas JSON Camtrap DP v1.0 (TDWG)
├── ui/camtrapdp.ui             # Interfaz Qt Designer
├── assets/                     # Iconos y logo institucional
├── camtrapdp.spec              # Configuración PyInstaller
├── requirements.txt
├── GUIA_DESARROLLO.md          # Guía detallada de desarrollo
├── CONTRIBUTING.md
├── THIRD_PARTY_NOTICES.txt
├── LICENSE
└── README.md
```

## Compilar el ejecutable

```bash
python -m PyInstaller camtrapdp.spec --clean
# salida: dist/Camtrap DP.exe (standalone, ~95-110 MB)
```

El archivo `.spec` ya incluye el icono, los recursos y las dependencias ocultas. Las carpetas `build/` y `dist/` son temporales y están excluidas de Git.

---

## Componentes de terceros

Este módulo incluye empaquetados los esquemas JSON de Camtrap DP 1.0 (TDWG). Ver
[`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt) y el aviso a nivel de
repositorio [`THIRD_PARTY_NOTICES.txt`](../THIRD_PARTY_NOTICES.txt).

## Licencia

MIT — ver [`LICENSE`](LICENSE).

## Cómo citar

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): flujo de trabajo de escritorio, abierto y reproducible, para movilizar datos de biodiversidad de fototrampeo desde Wildlife Insights hacia GBIF (v1.0)* [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. https://github.com/PEM-Humboldt/cam-trap-flow

## Autoría

**Cristian C. Acevedo** — Desarrollador principal. Bioingeniero (Universidad de Antioquia), Data Scientist. ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)
**Angélica Díaz-Pulido** — Coautora y coordinadora científica. Investigadora Adjunta, Centro de Estudios Socioecológicos y Cambio Global, Dirección de Conocimiento, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

## Referencias

[Camtrap DP](https://camtrap-dp.tdwg.org/) · [Wildlife Insights](https://www.wildlifeinsights.org/) · [Frictionless](https://framework.frictionlessdata.io/) · [SiB Colombia](https://biodiversidad.co/) · [GBIF](https://www.gbif.org/)

---

*Módulo 2 de la suite CamTrapFlow (CTF) — Instituto de Investigación de Recursos Biológicos Alexander von Humboldt.*
