# CamTrapFlow Launcher

**Interfaz Gráfica Unificada de Gestión de Datos de Fototrampeo**

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Licencia](https://img.shields.io/badge/licencia-MIT-orange)

---

## 📋 Descripción

**CamTrapFlow Launcher** es una aplicación de escritorio que centraliza el acceso a tres herramientas especializadas para el procesamiento completo de datos de fototrampeo, desde la extracción de frames de video hasta la publicación de datos estandarizados.

Esta aplicación proporciona un punto de entrada unificado para:

- **Img2WI**: Extracción de frames de video a intervalos definidos para Wildlife Insights
- **WI2CamtrapDP**: Conversión de exportaciones de Wildlife Insights a formato Camtrap Data Package (v1.0.2)
- **WIsualization**: Generación de visualizaciones y análisis estadísticos (curvas de acumulación, actividad horaria, presencia/ausencia)

---

## ✨ Características Principales

### Interfaz de Usuario
- 🖥️ **Interfaz moderna y responsive** optimizada para laptops (1366x768+)
- 🎨 **Diseño profesional** con paleta corporativa basada en Material Design
- 📊 **Tarjetas informativas** para cada módulo con descripciones claras
- ⏳ **Diálogos de carga** con feedback visual progresivo y barra de progreso animada

### Funcionalidad Técnica
- 🚀 **Lanzamiento independiente** de cada módulo como proceso separado
- ⚙️ **Configuración externa** vía `config.json` para duraciones y dimensiones
- 📝 **Logging completo** en `launcher.log` para diagnóstico y troubleshooting
- 🔧 **Compatible con PyInstaller** (one-file y modo desarrollo)
- 🗂️ **Gestión robusta de rutas** para recursos empaquetados (_MEIPASS)

### Experiencia de Usuario
- 🎯 **Acceso centralizado** a todas las herramientas desde una única aplicación
- ⚡ **Lanzamiento rápido** con tiempos configurables por módulo
- 🔒 **Prevención de lanzamientos múltiples** mediante deshabilitación de botones
- 📖 **Información contextual** sobre cada herramienta directamente en la interfaz

---

## 📦 Requisitos

### Requisitos del Sistema
- **Sistema Operativo**: Windows 10/11 (optimizado para Windows)
- **Resolución mínima**: 1000x600 píxeles (recomendado: 1366x768+)
- **RAM**: 4GB mínimo (8GB recomendado)

### Requisitos de Python (solo para desarrollo)
```
Python 3.8+
tkinter (incluido en instalaciones estándar de Python)
```

### Módulos Ejecutables Requeridos
El launcher requiere que los siguientes ejecutables estén disponibles en la carpeta `bin/`:
- `Img2WI.exe`
- `WI2CamtrapDP.exe`
- `WIsualization.exe`

---

## 📁 Estructura de Archivos

```
Launcher_CamTrapFlow_CTF/
│
├── Lanzador.py              # Script principal del launcher
├── config.json              # Archivo de configuración (opcional)
├── launcher.log             # Log de ejecución (generado automáticamente)
├── README.md                # Este archivo
│
├── assets/                  # Recursos gráficos
│   ├── icon.ico            # Icono de la aplicación
│   └── logo_humboldt.png   # Logo institucional
│
└── bin/                     # Ejecutables de los módulos
    ├── Img2WI.exe
    ├── WI2CamtrapDP.exe
    └── WIsualization.exe
```

---

## 🚀 Instalación y Uso

### Opción 1: Ejecutable Portable (Recomendado)

1. **Descargar** el ejecutable `CamTrapFlow.exe` desde la carpeta de releases
2. **Colocar** el ejecutable en una carpeta junto con:
   - Carpeta `assets/` (con iconos y logos)
   - Carpeta `bin/` (con los tres módulos .exe)
   - `config.json` (opcional, para personalización)
3. **Ejecutar** `CamTrapFlow.exe`

### Opción 2: Desde Código Fuente

1. **Clonar** o descargar el repositorio:
```bash
git clone <repositorio>
cd Launcher_CamTrapFlow_CTF
```

2. **Asegurar** que Python 3.8+ esté instalado:
```bash
python --version
```

3. **Ejecutar** el launcher:
```bash
python Lanzador.py
```

### Opción 3: Crear Ejecutable con PyInstaller

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable one-file
pyinstaller CamTrapFlow.spec

# El ejecutable estará en la carpeta dist/
```

---

## ⚙️ Configuración

### Archivo `config.json`

El launcher acepta un archivo de configuración opcional para personalizar tiempos de carga y dimensiones de ventana:

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

#### Parámetros de Configuración

**`durations_ms`**: Tiempo que el diálogo de carga permanece visible (en milisegundos)
- Ajustar según el tiempo de arranque real de cada módulo
- Valores muy bajos pueden cerrar el diálogo antes de que la ventana del módulo aparezca
- Valores muy altos mantienen el diálogo visible innecesariamente

**`window`**: Dimensiones de la ventana del launcher
- `default_width/height`: Tamaño inicial de la ventana
- `min_width/height`: Tamaño mínimo permitido al redimensionar

---

## 📖 Uso de los Módulos

### 🎬 Módulo 1 - Img2WI
**Extracción de frames de video**

- Procesa lotes de videos de fototrampeo
- Extrae imágenes a intervalos configurables
- Prepara archivos para carga en Wildlife Insights
- Soporta múltiples formatos de video

### 🧩 Módulo 2 - WI2CamtrapDP
**Conversión a estándar Camtrap Data Package**

- Convierte exportaciones ZIP de Wildlife Insights
- Genera archivos Camtrap-DP v1.0.2 estándar
- Incluye validación con Frictionless Framework
- Prepara datos para publicación en GBIF/SIB Colombia

### 📊 Módulo 3 - WIsualization
**Visualizaciones y análisis**

- Genera curvas de acumulación de especies
- Crea calendarios de muestreo
- Analiza patrones de actividad horaria
- Produce mapas de presencia/ausencia
- Compatible con datos de WI y Camtrap-DP

---

## 🔧 Troubleshooting

### El launcher no inicia

**Problema**: Al hacer doble clic no ocurre nada o se cierra inmediatamente

**Soluciones**:
1. Verificar que las carpetas `assets/` y `bin/` estén en el mismo directorio
2. Revisar el archivo `launcher.log` para mensajes de error
3. Ejecutar desde terminal para ver errores en consola:
   ```bash
   CamTrapFlow.exe
   ```

### Módulo no se encuentra

**Problema**: Error "Archivo no encontrado"

**Soluciones**:
1. Verificar que el ejecutable existe en `bin/`:
   - `bin/Img2WI.exe`
   - `bin/WI2CamtrapDP.exe`
   - `bin/WIsualization.exe`
2. Verificar permisos de ejecución de los archivos
3. Revisar rutas en `launcher.log`

### Diálogo de carga permanece mucho tiempo

**Problema**: El diálogo de "Cargando..." no se cierra

**Soluciones**:
1. Esperar: algunos módulos tardan en cargar (especialmente WIsualization)
2. Ajustar tiempos en `config.json` si el problema es recurrente
3. Verificar que el módulo efectivamente se haya abierto (puede estar detrás de otras ventanas)

### Iconos o logos no se muestran

**Problema**: Ventana sin icono o con icono por defecto

**Soluciones**:
1. Verificar existencia de archivos en `assets/`:
   - `assets/icon.ico`
   - `assets/logo_humboldt.png`
2. Los iconos son opcionales; la funcionalidad no se ve afectada
3. Revisar `launcher.log` para advertencias sobre recursos faltantes

### Problemas de resolución o interfaz cortada

**Problema**: Texto cortado o botones no visibles

**Soluciones**:
1. Aumentar tamaño de ventana manualmente
2. Ajustar `default_width` y `default_height` en `config.json`
3. Verificar que la resolución de pantalla sea al menos 1000x600

---

## 📝 Logging

El launcher genera automáticamente un archivo `launcher.log` con información detallada:

- **INFO**: Eventos importantes (inicio, lanzamiento de módulos)
- **WARNING**: Recursos faltantes, errores no críticos
- **ERROR**: Errores críticos que impiden operaciones

Para debug más detallado, editar `Lanzador.py` y cambiar:
```python
logging.basicConfig(level=logging.DEBUG)  # Cambiar INFO a DEBUG
```

---

## 🏗️ Desarrollo y Compilación

### Estructura de Desarrollo

```python
# Puntos clave del código:

def resource_path(*parts):
    """Gestión de rutas compatible con PyInstaller"""
    # Usa _MEIPASS en ejecutables, __file__ en desarrollo

def exe_path(exe_name):
    """Localización inteligente de ejecutables"""
    # Busca en _MEIPASS/bin, bin/, o directorio base

def lanzar(exe_name, human_name, module_info):
    """Lanzamiento de módulos con feedback visual"""
    # subprocess.Popen para ejecución no bloqueante
```

### Compilar con PyInstaller

El proyecto incluye un archivo `CamTrapFlow.spec` para compilación:

```bash
# Opción 1: Usar spec file (recomendado)
pyinstaller CamTrapFlow.spec

# Opción 2: Comando manual
pyinstaller --onefile --windowed \
    --name="CamTrapFlow" \
    --icon="assets/icon.ico" \
    --add-data="assets;assets" \
    --add-data="bin;bin" \
    --add-data="config.json;." \
    Lanzador.py
```

---

## 📚 Dependencias de Terceros

### Módulos Python Estándar
- `tkinter` - Interfaz gráfica
- `subprocess` - Lanzamiento de procesos
- `logging` - Sistema de logs
- `json` - Configuración
- `pathlib` - Gestión de rutas
- `contextlib` - Context managers

### Bibliotecas de Desarrollo (opcional)
- `pyinstaller` - Empaquetado de ejecutables

---

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

---

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo `LICENSE`.

---

## 🔗 Referencias

- **Wildlife Insights**: https://www.wildlifeinsights.org/
- **Camtrap Data Package**: https://camtrap-dp.tdwg.org/
- **GBIF**: https://www.gbif.org/
- **SIB Colombia**: https://biodiversidad.co/


---

## 🔄 Historial de Versiones

### v1.0.0 (24 de diciembre de 2025)
- ✨ Lanzamiento inicial
- 🎨 Interfaz gráfica moderna con diseño responsive
- 🚀 Soporte para tres módulos: Img2WI, WI2CamtrapDP, WIsualization
- ⚙️ Sistema de configuración externa
- 📝 Logging completo
- 📦 Compatible con PyInstaller

---

**© 2025 Instituto de Investigación de Recursos Biológicos Alexander von Humboldt**
