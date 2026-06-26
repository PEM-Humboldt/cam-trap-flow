# CamTrapFlow (CTF)

**An open, reproducible desktop workflow to mobilize camera-trap biodiversity data from Wildlife Insights to GBIF**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Camtrap DP](https://img.shields.io/badge/Camtrap%20DP-1.0-success.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)

**English** | [Español](#camtrapflow-ctf-1)

*Last updated: 24 June 2026 · Version 1.0*

---

## Overview

CamTrapFlow (CTF) is an open, reproducible, offline desktop suite that covers the complete camera-trap data lifecycle: from generating images out of video, to scientific standardization and validation, to ecological analysis and visualization, managed through a single graphical launcher.

It was developed for the **Alexander von Humboldt Biological Resources Research Institute** within **Red OTUS**, a Colombian network that promotes biodiversity recognition by connecting practitioners, institutions, and monitoring programs that use camera traps to support conservation action across the country.

Camera-trap monitoring is one of the most widespread methods for biodiversity assessment, yet a persistent bottleneck separates field observation from global biodiversity knowledge: turning raw records into standardized, publication-ready datasets is time-consuming and error-prone. CamTrapFlow addresses this by automating and accelerating standardization, reducing the errors of manual handling, and ensuring that it is always the original data producer who decides when and how their dataset reaches GBIF.

The suite runs locally on Windows as a portable application, requiring **no installation and no administrator privileges**, making it usable in field stations, protected-area offices, and academic institutions where technical resources and connectivity are limited.

### Key features

- Automated conversion of camera-trap videos into standardized, timestamped images.
- Conversion to the **Camtrap Data Package (Camtrap DP) standard, version 1.0**, ready for publication.
- Automated **Frictionless** validation and time-zone standardization.
- Ecological analysis and scientific visualization.
- Unified graphical launcher for centralized operation.
- Interoperability with **Wildlife Insights**, **GBIF**, and **SiB Colombia**.

---

## Modules

| Module | Name | Description | Docs |
| --- | --- | --- | --- |
| Module 1 | **Img2WI** | Converts camera-trap videos into organized, timestamped image sequences ready for upload and AI-assisted identification in Wildlife Insights. | [README](Modulo1_Img2WI/README.md) |
| Module 2 | **WI2CamtrapDP** | Converts Wildlife Insights project exports into a fully compliant Camtrap DP (v1.0) package — deployments, media, observations and datapackage metadata — with automated Frictionless validation. | [README](Modulo2_WI2CamtrapDP/README.md) |
| Module 3 | **WIsualization** | Statistical analysis and visualization: species-accumulation curves, activity patterns, deployment timelines, and presence/absence matrices. | [README](Modulo3_WIsualization/README.md) |
| Launcher | **CamTrapFlow Launcher** | Centralized graphical interface to run the three modules from a single entry point. | [README](Launcher_CamTrapFlow_CTF/README.md) |

---

## Workflow

1. **Img2WI** — convert camera-trap videos into individual, standardized images.
2. **Upload to Wildlife Insights** for AI-assisted taxonomic identification, then export the project as a ZIP.
3. **WI2CamtrapDP** — convert the Wildlife Insights export into a validated Camtrap DP package, ready for GBIF / SiB Colombia; a built-in email template helps request publication from the national node.
4. **WIsualization** — explore and communicate results (accumulation curves, activity, timelines, presence/absence).
5. **CamTrapFlow Launcher** — run the entire workflow from one graphical application.

Together, these modules take a monitoring team from raw camera-trap records to a validated, globally interoperable dataset without requiring a single line of code.

---

## Requirements

**End users**
- Windows 10/11 (64-bit)
- 4 GB RAM minimum (8 GB recommended)
- ~4 GB free disk space
- No Python required (portable executable)

**Developers**
- Python 3.10+ (Img2WI, WI2CamtrapDP) / 3.12+ (WIsualization)
- See `requirements.txt` in each module.

---

## Getting started

**Run the packaged application (recommended)**
1. Go to the [v1.0 release](https://github.com/PEM-Humboldt/cam-trap-flow/releases/tag/v1.0) and download `CamTrapFlow.exe` (full suite) or any individual module (`Img2WI.exe`, `WI2CamtrapDP.exe`, `WIsualization.exe`).
2. Save it to a local folder (avoid cloud-synced folders and paths with spaces or special characters). The executables are portable — no installation or extraction needed.
3. Double-click `CamTrapFlow.exe`. If Windows SmartScreen appears, choose *More info → Run anyway*.

**Run from source**
1. Clone this repository.
2. Install the dependencies of each module: `pip install -r requirements.txt`.
3. Run each entry point (`Lanzador.py` for the launcher; see each module's README). FFmpeg is required for Img2WI (see `Modulo1_Img2WI/requirements.txt`).

No cost or account is required to review or operate CamTrapFlow.

---

## Documentation
- User manual (ES): [CamTrapFlow User Manual v1.0 (PDF)](https://github.com/PEM-Humboldt/cam-trap-flow/releases/download/v1.0/CamTrapFlow_User_Manual_v1.0_ES.pdf)
- Module documentation: see the table above.

Related standards and platforms: [Camtrap DP](https://camtrap-dp.tdwg.org/) · [Wildlife Insights](https://www.wildlifeinsights.org/) · [GBIF](https://www.gbif.org/) · [SiB Colombia](https://biodiversidad.co/)

---

## Open source and licensing

All source code and documentation are released under the **MIT License** (see [`LICENSE`](LICENSE)). The packaged application redistributes third-party components (FFmpeg, PyQt, and others) under their respective licenses; see [`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt).

---

## How to cite

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): an open, reproducible desktop workflow to mobilize camera-trap biodiversity data from Wildlife Insights to GBIF (v1.0)* [Software]. Red OTUS, Alexander von Humboldt Biological Resources Research Institute. https://github.com/PEM-Humboldt/cam-trap-flow

See also [`CITATION.cff`](CITATION.cff).

---

## Authors

**Cristian C. Acevedo** — Lead developer.
Bioengineer (Universidad de Antioquia), Data Scientist.
ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)

**Angélica Díaz-Pulido** — Co-author and scientific coordinator.
Associate Researcher, Center for Socioecological Studies and Global Change, Knowledge Management Directorate, Alexander von Humboldt Biological Resources Research Institute.
ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

**Institution:** Alexander von Humboldt Biological Resources Research Institute — Red OTUS, Colombia.

---

## Data policy

This repository does not version sensitive data, real field datasets, intermediate outputs of production projects, or large result files. Each module's README indicates where input data should be located, which folders are used for local outputs, and what must not be committed to Git.

---

<br>

# CamTrapFlow (CTF)

**Flujo de trabajo de escritorio, abierto y reproducible, para movilizar datos de biodiversidad de fototrampeo desde Wildlife Insights hacia GBIF**

[English](#camtrapflow-ctf) | **Español**

*Última actualización: 24 de junio de 2026 · Versión 1.0*

---

## Descripción

CamTrapFlow (CTF) es una suite de escritorio abierta, reproducible y de uso local que cubre el ciclo completo de los datos de fototrampeo: desde la generación de imágenes a partir de video, hasta la estandarización y validación científica, el análisis ecológico y la visualización, todo gestionado mediante un único lanzador gráfico.

Fue desarrollada para el **Instituto de Investigación de Recursos Biológicos Alexander von Humboldt** en el marco de la **Red OTUS**, una red colombiana que promueve el reconocimiento de la biodiversidad conectando a investigadores, instituciones y programas de monitoreo que usan cámaras trampa para apoyar la acción de conservación en todo el país.

El fototrampeo es uno de los métodos más extendidos para evaluar la biodiversidad, pero persiste un cuello de botella entre la observación en campo y el conocimiento global: convertir los registros crudos en conjuntos de datos estandarizados y listos para publicación consume mucho tiempo y es propenso a errores. CamTrapFlow lo resuelve automatizando y acelerando la estandarización, reduciendo los errores del manejo manual y garantizando que sea siempre el productor original de los datos quien decide cuándo y cómo su conjunto de datos llega a GBIF.

La suite se ejecuta localmente en Windows como una aplicación portable, **sin instalación ni privilegios de administrador**, lo que la hace utilizable en estaciones de campo, oficinas de áreas protegidas e instituciones académicas donde los recursos técnicos y la conectividad son limitados.

### Características principales

- Conversión automatizada de videos de cámaras trampa en imágenes estandarizadas y con marca temporal.
- Conversión al estándar **Camtrap Data Package (Camtrap DP), versión 1.0**, listo para publicación.
- Validación automática con **Frictionless** y estandarización de zona horaria.
- Análisis ecológico y visualización científica.
- Lanzador gráfico unificado para operación centralizada.
- Interoperabilidad con **Wildlife Insights**, **GBIF** y **SiB Colombia**.

---

## Módulos

| Módulo | Nombre | Descripción | Docs |
| --- | --- | --- | --- |
| Módulo 1 | **Img2WI** | Convierte videos de cámaras trampa en secuencias de imágenes organizadas y con marca temporal, listas para cargar e identificar con apoyo de IA en Wildlife Insights. | [README](Modulo1_Img2WI/README.md) |
| Módulo 2 | **WI2CamtrapDP** | Convierte las exportaciones de proyecto de Wildlife Insights en un paquete Camtrap DP (v1.0) conforme al estándar —deployments, media, observations y metadatos datapackage— con validación automática Frictionless. | [README](Modulo2_WI2CamtrapDP/README.md) |
| Módulo 3 | **WIsualization** | Análisis estadístico y visualización: curvas de acumulación de especies, patrones de actividad, líneas de tiempo de despliegues y matrices de presencia/ausencia. | [README](Modulo3_WIsualization/README.md) |
| Launcher | **CamTrapFlow Launcher** | Interfaz gráfica centralizada para ejecutar los tres módulos desde un único punto de acceso. | [README](Launcher_CamTrapFlow_CTF/README.md) |

---

## Flujo de trabajo

1. **Img2WI** — convierte los videos de cámaras trampa en imágenes individuales y estandarizadas.
2. **Carga en Wildlife Insights** para identificación taxonómica asistida por IA; luego se exporta el proyecto como ZIP.
3. **WI2CamtrapDP** — convierte la exportación de Wildlife Insights en un paquete Camtrap DP validado, listo para GBIF / SiB Colombia; una plantilla de correo integrada facilita solicitar la publicación al nodo nacional.
4. **WIsualization** — explora y comunica resultados (curvas de acumulación, actividad, líneas de tiempo, presencia/ausencia).
5. **CamTrapFlow Launcher** — ejecuta todo el flujo desde una sola aplicación gráfica.

En conjunto, estos módulos llevan a un equipo de monitoreo desde los registros crudos de cámaras trampa hasta un conjunto de datos validado e interoperable a nivel global, sin requerir una sola línea de código.

---

## Requisitos

**Usuarios finales**
- Windows 10/11 (64 bits)
- 4 GB de RAM mínimo (8 GB recomendado)
- ~4 GB de espacio libre en disco
- No requiere Python (ejecutable portable)

**Desarrolladores**
- Python 3.10+ (Img2WI, WI2CamtrapDP) / 3.12+ (WIsualization)
- Ver `requirements.txt` en cada módulo.

---

## Inicio rápido

**Ejecutar la aplicación empaquetada (recomendado)**
1. Entra al [release v1.0](https://github.com/PEM-Humboldt/cam-trap-flow/releases/tag/v1.0) y descarga `CamTrapFlow.exe` (suite completa) o cualquier módulo individual (`Img2WI.exe`, `WI2CamtrapDP.exe`, `WIsualization.exe`).
2. Guárdalo en una carpeta local (evita carpetas sincronizadas con la nube y rutas con espacios o caracteres especiales). Los ejecutables son portables: no requieren instalación ni descompresión.
3. Haz doble clic en `CamTrapFlow.exe`. Si aparece Windows SmartScreen, elige *Más información → Ejecutar de todos modos*.

**Ejecutar desde el código fuente**
1. Clona este repositorio.
2. Instala las dependencias de cada módulo: `pip install -r requirements.txt`.
3. Ejecuta cada punto de entrada (`Lanzador.py` para el launcher; ver el README de cada módulo). Img2WI requiere FFmpeg (ver `Modulo1_Img2WI/requirements.txt`).

No se requiere costo ni cuenta para revisar u operar CamTrapFlow.

---

## Documentación
## Documentación
- Manual de usuario (ES): [Manual de usuario CamTrapFlow v1.0 (PDF)](https://github.com/PEM-Humboldt/cam-trap-flow/releases/download/v1.0/CamTrapFlow_User_Manual_v1.0_ES.pdf)
- Documentación de los módulos: ver la tabla anterior.

Estándares y plataformas relacionados: [Camtrap DP](https://camtrap-dp.tdwg.org/) · [Wildlife Insights](https://www.wildlifeinsights.org/) · [GBIF](https://www.gbif.org/) · [SiB Colombia](https://biodiversidad.co/)

---

## Código abierto y licenciamiento

Todo el código fuente y la documentación se publican bajo la **Licencia MIT** (ver [`LICENSE`](LICENSE)). La aplicación empaquetada redistribuye componentes de terceros (FFmpeg, PyQt, entre otros) bajo sus respectivas licencias; ver [`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt).

---

## Cómo citar

Acevedo, C. C., & Díaz-Pulido, A. (2026). *CamTrapFlow (CTF): flujo de trabajo de escritorio, abierto y reproducible, para movilizar datos de biodiversidad de fototrampeo desde Wildlife Insights hacia GBIF (v1.0)* [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. https://github.com/PEM-Humboldt/cam-trap-flow

Ver también [`CITATION.cff`](CITATION.cff).

---

## Autoría

**Cristian C. Acevedo** — Desarrollador principal.
Bioingeniero (Universidad de Antioquia), Data Scientist.
ORCID: [0000-0002-7864-0775](https://orcid.org/0000-0002-7864-0775)

**Angélica Díaz-Pulido** — Coautora y coordinadora científica.
Investigadora Adjunta, Centro de Estudios Socioecológicos y Cambio Global, Dirección de Conocimiento, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt.
ORCID: [0000-0003-4166-4084](https://orcid.org/0000-0003-4166-4084)

**Institución:** Instituto de Investigación de Recursos Biológicos Alexander von Humboldt — Red OTUS, Colombia.

---

## Política de datos

Este repositorio no versiona datos sensibles, conjuntos de datos reales de campo, salidas intermedias de proyectos productivos ni archivos de resultados pesados. El README de cada módulo indica dónde ubicar los datos de entrada, qué carpetas se usan para salidas locales y qué no debe subirse a Git.

---

*Instituto de Investigación de Recursos Biológicos Alexander von Humboldt — comprometidos con la conservación y el conocimiento de la biodiversidad colombiana.*
