# Img2WI - Extractor de Imágenes para Cámaras Trampa

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Aplicación de escritorio para convertir automáticamente videos de cámaras trampa en secuencias de imágenes individuales, desarrollada para el Instituto Alexander von Humboldt. Facilita el procesamiento de videos de fauna para su posterior análisis o carga en plataformas como Wildlife Insights.

**Convierte tus videos (.MP4, .MOV, .AVI) en imágenes organizadas con un solo clic.**

## 🚀 Características Principales

- ✨ **Interfaz gráfica intuitiva** con PyQt5 - No requiere conocimientos técnicos
- 🎬 **Procesamiento dual**: wiutils (optimizado para MP4) + FFmpeg (AVI/MOV)
- ⚙️ **Offset configurable**: Extrae 1 imagen cada X segundos (0.5, 1, 2, 3, 4, 5 seg)
- 📁 **Organización automática**: Todas las imágenes en una sola carpeta con timestamp
- 🔢 **Nomenclatura sistemática**: `<nombre_video>_000001.jpg`, `<nombre_video>_000002.jpg`, etc.
- 📊 **Monitoreo en tiempo real**: Logs estructurados, barra de progreso y cronómetro
- ⏱️ **Detección de duración**: Muestra la duración de cada video procesado
- 🔄 **Procesamiento asíncrono**: La interfaz no se congela durante el proceso
- 📦 **Ejecutable portable**: Un solo archivo .exe sin instalación requerida
- 🎯 **Validación inteligente**: Detecta y alerta sobre formatos no soportados

## 📋 Requisitos Previos

### Para usar el ejecutable (.exe)
- ✅ **Ninguno** - Es completamente portable
- 💻 Windows 10/11 (64-bit)

### Para desarrollo desde código fuente
- 🐍 Python 3.8 o superior
- 📦 Dependencias Python (ver `requirements.txt`)
- 🎥 FFmpeg (build STATIC x64) - [Descargar aquí](https://www.gyan.dev/ffmpeg/builds/)
  - Debe colocarse en `app/bin/ffmpeg.exe`
  - También funciona si está en el PATH del sistema

## 🔧 Instalación y Uso

### Opción 1: Usar el ejecutable (Recomendado para usuarios finales)

1. Descargar `Img2WI.exe` desde [Releases](../../releases)
2. Ejecutar el archivo - ¡Listo! No requiere instalación

### Opción 2: Ejecutar desde código fuente (Desarrolladores)

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd Modulo1_Img2WI
   ```

2. **Crear entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar FFmpeg:**
   - Descargar [FFmpeg build static x64](https://www.gyan.dev/ffmpeg/builds/)
   - Extraer `ffmpeg.exe` del archivo ZIP
   - Colocar en `app/bin/ffmpeg.exe`
   - Alternativamente, instalar FFmpeg en el PATH del sistema

5. **Ejecutar la aplicación:**
   ```bash
   python app/main.py
   ```

## 🎯 Guía de Uso

1. **Seleccionar carpeta**: Click en "📁 Seleccionar carpeta del proyecto"
2. **Configurar offset**: Elegir cada cuántos segundos extraer una imagen (recomendado: 1 seg)
3. **Iniciar proceso**: Click en "▶️ Iniciar procesamiento"
4. **Ver resultados**: Las imágenes se guardan en `Img2WI_<nombre_proyecto>_<timestamp>/`

### Formatos soportados
- ✅ `.MP4` (procesado con wiutils, fallback a FFmpeg)
- ✅ `.MOV` (procesado con FFmpeg)
- ✅ `.AVI` (procesado con FFmpeg)

### Carpeta de salida
Se genera automáticamente con el formato:
```
Img2WI_<nombre_de_tu_carpeta>_HH-MM_DD_MM_AAAA/
```

**Ejemplo:** `Img2WI_MiProyectoCamaras_14-30_24_12_2025/`

## 📦 Compilación del Ejecutable

### Método Automático (Recomendado)

1. **Verificar requisitos previos:**
   - ✅ Todas las dependencias de `requirements.txt` instaladas
   - ✅ FFmpeg ubicado en `app/bin/ffmpeg.exe`

2. **Ejecutar script de compilación:**
   ```bash
   build.bat
   ```

3. **Resultado:**
   - Ejecutable: `dist/Img2WI.exe`
   - Tamaño aproximado: ~150-200 MB (incluye Python, PyQt5, FFmpeg)
   - Todo en un solo archivo portable

### Método Manual

```bash
python -m PyInstaller ExtractorCamtrap.spec --clean
```

### Qué incluye el ejecutable
- ✅ Intérprete Python embebido
- ✅ Todas las librerías Python necesarias
- ✅ FFmpeg para procesamiento de video
- ✅ Iconos y recursos de la interfaz
- ✅ No requiere instalación de Python en el sistema

### Notas sobre PyInstaller
- Los directorios `build/` y `dist/` se generan automáticamente
- El proceso puede tardar 2-5 minutos
- El antivirus puede marcar falsos positivos (es normal con PyInstaller)

## 📁 Estructura del Proyecto

```
Modulo1_Img2WI/
├── app/
│   ├── bin/
│   │   └── ffmpeg.exe          # FFmpeg embebido
│   ├── main.py                 # Punto de entrada
│   ├── ui_main.py             # Interfaz gráfica
│   └── processor.py           # Lógica de procesamiento
├── resources/
│   └── icons/
│       ├── app_icon.png       # Icono de la aplicación
│       └── logo_humboldt.png  # Logo institucional
├── .gitignore                 # Archivos ignorados por Git
├── ExtractorCamtrap.spec     # Configuración PyInstaller
├── requirements.txt          # Dependencias Python
├── THIRD_PARTY_NOTICES.txt  # Licencias de terceros
└── README.md                # Este archivo
```

## 🛠️ Tecnologías y Arquitectura

### Stack Tecnológico
- **Python 3.8+**: Lenguaje de programación principal
- **PyQt5**: Framework para interfaz gráfica multiplataforma
  - QThread: Procesamiento asíncrono
  - Signals/Slots: Comunicación entre hilos
- **PyInstaller 6.3+**: Empaquetado en ejecutable standalone
- **FFmpeg**: Motor de procesamiento de video (formatos universales)
- **wiutils**: Biblioteca especializada para videos de cámaras trampa

### Arquitectura de la Aplicación
```
┌─────────────────┐
│   main.py       │  ← Punto de entrada
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   ui_main.py    │  ← Interfaz gráfica (PyQt5)
│                 │    - VideoProcessorWindow
│                 │    - Worker (QThread)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  processor.py   │  ← Lógica de negocio
│                 │    - Extracción de frames
│                 │    - Renombrado automático
│                 │    - Detección de duración
└─────────────────┘
```

### Flujo de Procesamiento
1. Usuario selecciona carpeta con videos
2. Aplicación escanea recursivamente archivos .mp4/.mov/.avi
3. Por cada video:
   - Detecta duración con ffprobe
   - Extrae frames según offset configurado
   - Renombra imágenes con nomenclatura estándar
4. Reporta estadísticas finales

## 📝 Notas Importantes

### ✅ Ventajas
- **Portable**: El ejecutable incluye todo (Python, librerías, FFmpeg)
- **Sin instalación**: Copiar y ejecutar, funciona inmediatamente
- **Organizado**: Todas las imágenes en una carpeta con timestamp
- **Trazable**: Nomenclatura secuencial por video
- **Eficiente**: Procesamiento asíncrono, UI responsiva

### ⚠️ Consideraciones
- **Espacio en disco**: Videos grandes generan muchas imágenes
  - Ejemplo: Video de 60 seg con offset=1 → 60 imágenes (~5-15 MB)
- **Tiempo de procesamiento**: Depende de:
  - Número de videos
  - Duración total
  - Offset seleccionado (menor offset = más imágenes = más tiempo)
- **FFmpeg requerido**: Para desarrollo, debe estar en `app/bin/`
- **Carpetas temporales**: `build/` y `dist/` se crean durante compilación
  - Están en `.gitignore`, no se suben a Git
  - Se pueden eliminar después de obtener el .exe

### 🐛 Solución de Problemas

**"FFmpeg no encontrado"**
- Verificar que `ffmpeg.exe` esté en `app/bin/ffmpeg.exe`
- O instalar FFmpeg en el PATH del sistema

**"No se encontraron videos"**
- Verificar que los archivos sean .MP4, .MOV o .AVI
- Revisar que no estén en carpetas ocultas

**"El ejecutable no abre"**
- Ejecutar como administrador
- Verificar que el antivirus no lo bloquee
- Descargar nuevamente si está corrupto

## 🤝 Contribuciones

Este proyecto es parte del desarrollo de software para el Instituto Humboldt - Contrato 25_064.

## 📄 Licencia

Ver archivo `THIRD_PARTY_NOTICES.txt` para información sobre licencias de componentes de terceros.

## 👥 Autor y Créditos

**Desarrollado por:** Cristian C. Acevedo  
**Organización:** Instituto de Investigación de Recursos Biológicos Alexander von Humboldt - Red OTUS  
**Proyecto:** Producto 8 - Desarrollo de Software CTF (CamTrapFlow) y Dashboards  
**Contrato:** 25_064  
**Año:** 2025  

### 📚 Cómo Citar

Acevedo, C. C., & Diaz-Pulido, A. (2025). *Img2WI - Extractor de Imágenes para Cámaras Trampa (v1.0.0)* [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. https://github.com/[usuario]/[repositorio]

---

<div align="center">
  <img src="resources/icons/logo_humboldt.png" alt="Instituto Humboldt" height="60">
  <br>
  <em>Instituto Alexander von Humboldt - Investigación en biodiversidad y servicios ecosistémicos</em>
</div>
