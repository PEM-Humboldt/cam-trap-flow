# CamTrapFlow (CTF)

**Suite integrada para el procesamiento, estandarización y análisis de datos de fototrampeo**

[![License](https://img.shields.io/badge/license-Check%20LICENSE-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

---

## 📋 Tabla de contenidos

- [Descripción](#-descripción)
- [Módulos incluidos](#-módulos-incluidos)
- [Arquitectura](#-arquitectura-general)
- [Flujo de trabajo](#-flujo-de-trabajo-típico)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso rápido](#-uso-rápido)
- [Documentación](#-documentación)
- [Política de datos](#-política-de-datos)
- [Alcance institucional](#-alcance-institucional)
- [Contribución](#-contribución)
- [Autoría](#-autoría)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## 🔬 Descripción

CamTrapFlow es un ecosistema de herramientas desarrollado para el **Instituto de Investigación de Recursos Biológicos Alexander von Humboldt – Red OTUS**, que cubre el flujo completo de trabajo de datos de cámaras trampa, desde la generación de imágenes a partir de video, la estandarización científica de la información, el análisis estadístico y la visualización, hasta la gestión unificada mediante una interfaz gráfica central.

### ✨ Características principales

- 🎬 Conversión automatizada de videos a imágenes estandarizadas
- 📦 Conversión a estándar **Camtrap Data Package (v1.0.2)**
- 📊 Análisis estadístico y visualización ecológica avanzada
- 🖥️ Interfaz gráfica unificada para gestión centralizada
- 🔄 Interoperabilidad con **Wildlife Insights**, **GBIF** y **SIB Colombia**
- ✅ Cumplimiento de estándares científicos internacionales

---

## 📦 Módulos incluidos

| Módulo | Nombre | Descripción | Documentación |
|--------|--------|-------------|---------------|
| **Módulo 1** | **Img2WI** | Convierte videos de cámaras trampa en secuencias de imágenes organizadas y estandarizadas, listas para análisis o carga en Wildlife Insights. | [📖 Ver docs](Modulo1_Img2WI/README.md) |
| **Módulo 2** | **WI2CamtrapDP** | Convierte exportaciones de Wildlife Insights al estándar científico **Camtrap Data Package (v1.0.2)**, listo para publicación en plataformas como GBIF y SIB Colombia. | [📖 Ver docs](Modulo2_WI2CamtrapDP/README.md) |
| **Módulo 3** | **WIsualization** | Aplicación gráfica para análisis y visualización estadística: curvas de acumulación, patrones de actividad horaria, presencia/ausencia, mapas y métricas ecológicas. | [📖 Ver docs](Modulo3_WIsualization/README.md) |
| **Launcher** | **CamTrapFlow Launcher** | Interfaz gráfica centralizada que permite ejecutar los tres módulos anteriores desde un único punto de acceso. | [📖 Ver docs](Launcher/README.md) |

---

## 🧩 Arquitectura general

```text
CamTrapFlow/
│
├── Launcher/              → CamTrapFlow Launcher (GUI principal)
│   ├── README.md
│   └── ...
│
├── Modulo1_Img2WI/        → Extracción de imágenes desde video
│   ├── README.md
│   └── ...
│
├── Modulo2_WI2CamtrapDP/  → Conversión a Camtrap-DP
│   ├── README.md
│   └── ...
│
├── Modulo3_WIsualization/ → Visualización y análisis
│   ├── README.md
│   └── ...
│
├── README.md              → Este archivo
├── .gitignore
└── LICENSE
```

> **Nota:** Cada carpeta contiene su propio `README.md` con la documentación técnica detallada del módulo correspondiente, incluyendo requisitos, instalación, ejecución y flujo de trabajo específico.

---

## 🔁 Flujo de trabajo típico

```mermaid
graph LR
    A[Videos de cámara trampa] --> B[Módulo 1: Img2WI]
    B --> C[Imágenes estandarizadas]
    C --> D[Wildlife Insights]
    D --> E[Módulo 2: WI2CamtrapDP]
    D --> G[Módulo 3: WIsualization]
    E --> F[Camtrap Data Package]
    G --> H[Análisis y visualizaciones]
    
    style B fill:#4CAF50
    style E fill:#2196F3
    style G fill:#FF9800
```

### Paso a paso

1. **🎬 Procesamiento de video (Img2WI)**  
   Se convierten los videos provenientes de cámaras trampa en imágenes individuales, organizadas y con nomenclatura estandarizada.

2. **📤 Carga en Wildlife Insights**  
   Las imágenes generadas se cargan en la plataforma Wildlife Insights para su clasificación taxonómica y validación.

3. **📦 Estandarización científica (WI2CamtrapDP)** o **📊 Análisis y visualización (WIsualization)**  
   A partir de los datos descargados de Wildlife Insights, se pueden realizar dos procesos independientes:
   
   - **Módulo 2:** Convierte la exportación de Wildlife Insights al estándar Camtrap Data Package, garantizando interoperabilidad y calidad científica para publicación en GBIF y SIB Colombia.
   
   - **Módulo 3:** Realiza análisis estadísticos y visualizaciones que permiten la exploración ecológica de los datos: curvas de acumulación, patrones de actividad, mapas y métricas.

4. **🚀 Gestión unificada (CamTrapFlow Launcher)**  
   Todos los módulos pueden ejecutarse desde una sola aplicación gráfica, simplificando la operación para usuarios finales.

---

## 🖥️ Requisitos

### Para usuarios finales

- **Sistema Operativo:** Windows 10/11 (64-bit)
- **Espacio en disco:** Mínimo 2 GB libres
- **Memoria RAM:** Mínimo 4 GB (recomendado 8 GB)
- **No se requiere Python instalado** (uso mediante ejecutables `.exe`)

### Para desarrollo

- **Python:** 3.8+ (Img2WI y WI2CamtrapDP) | 3.12+ (WIsualization)
- **Git:** Para control de versiones
- **IDE recomendado:** VS Code, PyCharm o similar
- **Dependencias:** Ver `requirements.txt` en cada módulo

> **Nota:** Cada módulo define en su documentación interna sus dependencias exactas.

---

## 💻 Instalación

### Opción 1: Usuario final (ejecutables)

1. Descarga el ejecutable del **CamTrapFlow Launcher** desde [Releases]()
2. Ejecuta el instalador o descomprime el archivo ZIP
3. Abre `CamTrapFlowLauncher.exe`
4. Sigue las instrucciones en pantalla

### Opción 2: Desarrollador (desde código fuente)

```bash
# Clonar el repositorio
git clone https://github.com/tu-organizacion/CamTrapFlow.git
cd CamTrapFlow

# Navegar a cada módulo e instalar dependencias
cd Modulo1_Img2WI
pip install -r requirements.txt

cd ../Modulo2_WI2CamtrapDP
pip install -r requirements.txt

cd ../Modulo3_WIsualization
pip install -r requirements.txt

cd ../Launcher
pip install -r requirements.txt
```

---

## 🚀 Uso rápido

### Mediante Launcher (recomendado)

1. Abre **CamTrapFlow Launcher**
2. Selecciona el módulo que necesitas
3. Sigue el asistente gráfico
4. Revisa los resultados en la carpeta de salida

### Mediante línea de comandos (avanzado)

```bash
# Módulo 1: Convertir videos a imágenes
cd Modulo1_Img2WI
python main.py --input ./videos --output ./images

# Módulo 2: Convertir Wildlife Insights a Camtrap-DP
cd Modulo2_WI2CamtrapDP
python convert.py --input ./wi_export --output ./camtrap_dp

# Módulo 3: Análisis y visualización
cd Modulo3_WIsualization
python app.py
```

---

## 📚 Documentación

Para la documentación completa de cada componente consulte:

- 🚀 [**Launcher/README.md**](Launcher/README.md) → Documentación del CamTrapFlow Launcher
- 🎬 [**Modulo1_Img2WI/README.md**](Modulo1_Img2WI/README.md) → Documentación del módulo Img2WI
- 📦 [**Modulo2_WI2CamtrapDP/README.md**](Modulo2_WI2CamtrapDP/README.md) → Documentación del módulo WI2CamtrapDP
- 📊 [**Modulo3_WIsualization/README.md**](Modulo3_WIsualization/README.md) → Documentación del módulo WIsualization

### Recursos adicionales

- [Estándar Camtrap Data Package](https://tdwg.github.io/camtrap-dp/)
- [Wildlife Insights Platform](https://wildlifeinsights.org/)
- [GBIF Data Standards](https://www.gbif.org/standards)

---

## 📁 Política de datos

Este repositorio:

- ❌ **NO versiona** datos sensibles
- ❌ **NO versiona** datasets reales de campo
- ❌ **NO versiona** salidas intermedias de proyectos productivos
- ❌ **NO versiona** resultados pesados

Cada módulo indica en su `README`:

- ✅ Dónde deben ubicarse los datos de entrada
- ✅ Qué carpetas se usan para salidas locales
- ✅ Qué información no debe subirse a Git

### Esto garantiza:

- 🔒 Seguridad de la información
- ✅ Cumplimiento de buenas prácticas de ingeniería
- 📦 Repositorio liviano y mantenible
- 🚀 Tiempos de clonado y actualización óptimos

---

## 🎯 Alcance institucional

CamTrapFlow constituye una plataforma técnica diseñada para:

- ✅ Estandarizar flujos de datos de fototrampeo en Colombia
- ✅ Facilitar la publicación científica bajo estándares abiertos
- ✅ Garantizar trazabilidad, reproducibilidad y calidad de los datos
- ✅ Transferir capacidades técnicas a equipos de investigación y monitoreo
- ✅ Unificar herramientas dispersas en un solo ecosistema coherente

---

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de contribución

- Sigue las convenciones de código de Python (PEP 8)
- Documenta todas las funciones públicas
- Añade tests para nuevas funcionalidades
- Actualiza la documentación según sea necesario

---

## 👥 Autoría

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

## 📄 Licencia

Este proyecto se distribuye bajo la licencia definida en el archivo [LICENSE](LICENSE).

---

## 📧 Contacto

Para preguntas, sugerencias o reportar problemas:

- **Issues:** [GitHub Issues]()
- **Email:** [correo@humboldt.org.co]()
- **Web:** [Instituto Humboldt](http://www.humboldt.org.co/)

---

## 🧭 Nota final

> **CamTrapFlow no es un conjunto de scripts aislados.**  
> Es una plataforma técnica integral para la gestión, estandarización y análisis de datos de biodiversidad generados por cámaras trampa, alineada con estándares internacionales y con las necesidades operativas del Instituto Humboldt y la Red OTUS.

---

<div align="center">
  <em>Instituto de Investigación de Recursos Biológicos Alexander von Humboldt</em><br>
  <strong>Comprometidos con la conservación y el conocimiento de la biodiversidad colombiana</strong>
</div>
