# 🛠️ Guía de Desarrollo Local - WI2CamtrapDP

**Documento técnico para desarrolladores y colaboradores**

Esta guía proporciona instrucciones detalladas para configurar, ejecutar y desarrollar el proyecto WI2CamtrapDP en tu máquina local.

---

## 📋 Tabla de Contenidos

1. [Descripción General del Proyecto](#-descripción-general-del-proyecto)
2. [Requisitos Previos](#-requisitos-previos)
3. [Instalación Paso a Paso](#-instalación-paso-a-paso)
4. [Ejecución en Modo Desarrollo](#-ejecución-en-modo-desarrollo)
5. [Estructura del Código](#-estructura-del-código)
6. [Compilación del Ejecutable](#-compilación-del-ejecutable)
7. [Desarrollo y Modificaciones](#-desarrollo-y-modificaciones)
8. [Depuración y Testing](#-depuración-y-testing)
9. [Buenas Prácticas](#-buenas-prácticas)
10. [Solución de Problemas Comunes](#-solución-de-problemas-comunes)

---

## 🎯 Descripción General del Proyecto

**WI2CamtrapDP** es una aplicación de escritorio desarrollada en Python que convierte exportaciones de proyectos de **Wildlife Insights** al estándar internacional **Camtrap Data Package (Camtrap-DP) v1.0.2**.

### Tecnologías Principales

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.8+ | Lenguaje base |
| PyQt5 | 5.15.9+ | Interfaz gráfica de usuario |
| pandas | 2.0.0+ | Procesamiento de datos tabulares |
| frictionless | 5.14.0+ | Validación de Data Packages |
| PyInstaller | 6.x | Compilación a ejecutable standalone |

### Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────────────┐
│                      app.py (GUI)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PyQt5 Interface                                      │  │
│  │  - File selection                                     │  │
│  │  - Configuration options                              │  │
│  │  - Progress tracking (table + log)                    │  │
│  │  - Results display                                    │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                           │
│                 ▼                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         camtrapdp.processor.process_zip()            │  │
│  │  Core transformation engine (WI → Camtrap-DP)        │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                           │
│                 ├────► camtrapdp.utils (date/MIME/text)    │
│                 ├────► camtrapdp.validator (Frictionless)  │
│                 └────► camtrapdp.schemas/ (JSON schemas)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Requisitos Previos

### 1. Python 3.8 o Superior

Verifica tu versión de Python:

```bash
python --version
# o
python3 --version
```

**Si no tienes Python instalado:**
- **Windows:** Descarga desde [python.org](https://www.python.org/downloads/)
  - ✅ Marca "Add Python to PATH" durante la instalación
- **macOS:** `brew install python@3.11`
- **Linux:** `sudo apt-get install python3 python3-pip` (Debian/Ubuntu)

### 2. Git (Opcional pero Recomendado)

Para clonar el repositorio:

```bash
git --version
```

Si no está instalado: [Descargar Git](https://git-scm.com/downloads)

### 3. Editor de Código (Recomendado)

- **Visual Studio Code** (recomendado) - [Descargar](https://code.visualstudio.com/)
- **PyCharm Community** - [Descargar](https://www.jetbrains.com/pycharm/download/)
- **Sublime Text** - [Descargar](https://www.sublimetext.com/)

---

## 📦 Instalación Paso a Paso

### Opción A: Clonar desde GitHub (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/WI2CamtrapDP.git

# 2. Navegar al directorio del proyecto
cd WI2CamtrapDP
```

### Opción B: Descargar ZIP Manual

1. Ve al repositorio en GitHub
2. Clic en "Code" → "Download ZIP"
3. Extrae el archivo ZIP
4. Abre terminal en la carpeta extraída

---

### Configuración del Entorno Virtual

**¿Por qué usar un entorno virtual?**
- Aísla las dependencias del proyecto
- Evita conflictos con otros proyectos Python
- Facilita la reproducibilidad

#### Windows

```cmd
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Verificar activación (debería mostrar "(venv)" al inicio del prompt)
```

#### macOS/Linux

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Verificar activación (debería mostrar "(venv)" al inicio del prompt)
```

---

### Instalación de Dependencias

Con el entorno virtual activado:

```bash
# Actualizar pip (recomendado)
python -m pip install --upgrade pip

# Instalar todas las dependencias del proyecto
pip install -r requirements.txt

# Verificar instalación exitosa
pip list
```

**Salida esperada (abreviada):**
```
Package           Version
----------------- -------
PyQt5             5.15.9
pandas            2.0.3
numpy             1.24.3
frictionless      5.14.0
pytz              2023.3
...
```

---

## ▶️ Ejecución en Modo Desarrollo

### Ejecución Básica

```bash
# Asegúrate de tener el entorno virtual activado
python app.py
```

**Resultado esperado:**
- Se abre la ventana de la aplicación
- Interfaz gráfica lista para uso
- Consola muestra mensajes de inicialización (si hay)

### Ejecución con Logs de Depuración (Avanzado)

Para ver más detalles en la consola:

```bash
# Windows
set PYTHONUNBUFFERED=1
python app.py

# macOS/Linux
PYTHONUNBUFFERED=1 python app.py
```

---

## 🗂️ Estructura del Código

### Módulos Principales

#### 1. `app.py` - Aplicación GUI

**Responsabilidades:**
- Interfaz gráfica (PyQt5)
- Manejo de eventos de usuario
- Visualización de progreso y resultados
- Integración con el procesador

**Componentes clave:**
```python
class AspectLabel(QLabel):
    """Widget personalizado para logos/imágenes escalables"""

class Worker(QObject):
    """Ejecuta procesamiento en hilo separado (no bloquea UI)"""

def main():
    """Punto de entrada de la aplicación"""
```

#### 2. `camtrapdp/processor.py` - Motor de Transformación

**Responsabilidades:**
- Lectura y validación de ZIP de Wildlife Insights
- Transformación de datos (WI → Camtrap-DP)
- Construcción de tablas CSV (deployments, media, observations)
- Generación de datapackage.json
- Validación con Frictionless (opcional)
- Empaquetado final en ZIP

**Función principal:**
```python
def process_zip(
    zip_path: Path,
    out_dir: Path,
    logger: Callable = None,
    report_progress: Callable = None,
    validate: bool = True,
    make_zip: bool = True,
    overwrite: bool = False,
    timezone_hint: str = "America/Bogota"
) -> Path:
    """
    API principal para procesar exportación de Wildlife Insights.
    
    Returns:
        Path: Directorio de trabajo con resultados
    """
```

#### 3. `camtrapdp/utils.py` - Utilidades

**Funciones clave:**
```python
def to_iso_utc(timestamp_str: str, tz_hint: str) -> str:
    """Convierte timestamp local a ISO-8601 UTC"""

def ext_to_mediatype(file_path: str) -> str:
    """Mapea extensión de archivo a MIME type"""

def clean_text_general(text: str) -> str:
    """Limpia texto para compatibilidad SIB Colombia"""
```

#### 4. `camtrapdp/validator.py` - Validación

```python
def validate_datapackage(dp_path: Path) -> Tuple[bool, Any]:
    """
    Valida un Data Package con Frictionless Framework.
    
    Returns:
        Tuple[bool, Report]: (es_válido, reporte_detallado)
    """
```

#### 5. `camtrapdp/config.py` - Configuración

```python
@dataclass
class Options:
    """Opciones de configuración del procesador"""
    timezone_hint: str = "America/Bogota"
    validate: bool = True
    make_zip: bool = True
    open_folder_after: bool = True
    overwrite: bool = False
```

---

## 🏗️ Compilación del Ejecutable

### Requisitos Adicionales

```bash
# Instalar PyInstaller (si no está en requirements.txt)
pip install pyinstaller
```

### Proceso de Compilación

```bash
# 1. Limpiar compilaciones anteriores (IMPORTANTE)
# Windows:
rmdir /s /q build
rmdir /s /q dist

# macOS/Linux:
rm -rf build/ dist/

# 2. Compilar usando el archivo .spec
python -m PyInstaller camtrapdp.spec --clean

# 3. Verificar que se generó el ejecutable
# Windows: dist/Camtrap DP.exe
# macOS: dist/Camtrap DP.app
# Linux: dist/Camtrap DP
```

### Prueba del Ejecutable

```bash
# Windows
"dist\Camtrap DP.exe"

# macOS
open "dist/Camtrap DP.app"

# Linux
./dist/Camtrap\ DP
```

**Tamaño esperado:** ~95-110 MB (incluye Python runtime + dependencias)

---

## 🔨 Desarrollo y Modificaciones

### Flujo de Trabajo Recomendado

```bash
# 1. Crear rama para nueva funcionalidad
git checkout -b feature/mi-nueva-caracteristica

# 2. Realizar modificaciones en el código

# 3. Probar cambios en modo desarrollo
python app.py

# 4. Validar que no se rompió nada
# (Ejecutar pruebas, verificar funcionalidades existentes)

# 5. Commit de cambios
git add .
git commit -m "Añadir: descripción clara del cambio"

# 6. Push a GitHub
git push origin feature/mi-nueva-caracteristica

# 7. Crear Pull Request en GitHub
```

### Modificar la Interfaz Gráfica

La interfaz está diseñada en **Qt Designer** (`ui/camtrapdp.ui`):

```bash
# 1. Instalar Qt Designer (viene con PyQt5-tools)
pip install pyqt5-tools

# 2. Abrir el archivo .ui en Designer
# Windows:
venv\Scripts\pyqt5-tools designer.exe ui\camtrapdp.ui

# macOS/Linux:
designer ui/camtrapdp.ui

# 3. Realizar cambios visuales en Designer

# 4. Guardar archivo .ui

# 5. NO es necesario convertir a .py (se carga dinámicamente en app.py)

# 6. Probar cambios
python app.py
```

### Modificar el Procesador (Lógica de Negocio)

Ejemplo: Añadir validación personalizada

```python
# Editar: camtrapdp/processor.py

def process_zip(...):
    # ... código existente ...
    
    # Añadir nueva validación
    _log("Validando campos personalizados...")
    if not _validate_custom_fields(df_images):
        raise ValueError("❌ Error en validación personalizada")
    
    # ... continuar proceso ...
```

### Añadir Nueva Zona Horaria por Defecto

```python
# Editar: app.py

# Buscar esta línea:
idx = max(0, w.cbTimezone.findData("America/Bogota"))

# Cambiar a tu zona horaria preferida:
idx = max(0, w.cbTimezone.findData("America/Mexico_City"))
```

---

## 🐛 Depuración y Testing

### Depuración con Print Statements

```python
# En processor.py o app.py
print(f"DEBUG: Variable = {variable}")
print(f"DEBUG: Tipo = {type(variable)}")
print(f"DEBUG: Columnas CSV = {df.columns.tolist()}")
```

### Depuración con Visual Studio Code

**1. Crear archivo `.vscode/launch.json`:**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: App GUI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/app.py",
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

**2. Establecer breakpoints:**
- Clic en el margen izquierdo del editor (aparece un círculo rojo)

**3. Iniciar depuración:**
- Presiona `F5` o ve a "Run and Debug"

### Testing Manual Básico

**Casos de prueba esenciales:**

1. **Archivo ZIP válido:**
   - Seleccionar ZIP de Wildlife Insights (proyecto, no iniciativa)
   - Verificar que procesa correctamente
   - Revisar que genera todos los archivos esperados

2. **Archivo ZIP inválido:**
   - Intentar procesar un ZIP que no es de WI
   - Verificar que muestra error claro

3. **Iniciativa (múltiples projects):**
   - Seleccionar ZIP de iniciativa
   - Verificar que detecta y rechaza correctamente

4. **Datos con "No CV Result":**
   - Procesar ZIP con registros sin identificación taxonómica
   - Verificar que detiene el proceso y lista registros problemáticos

5. **Validación Frictionless:**
   - Activar/desactivar checkbox de validación
   - Verificar que se ejecuta/omite según configuración

---

## ✅ Buenas Prácticas

### Estilo de Código

**Seguir PEP 8 (Guía de estilo de Python):**

```bash
# Instalar herramientas de linting
pip install flake8 black

# Verificar estilo
flake8 app.py camtrapdp/

# Formatear automáticamente
black app.py camtrapdp/
```

### Documentación de Funciones

**Usar docstrings tipo Google/NumPy:**

```python
def mi_funcion(param1: str, param2: int) -> bool:
    """
    Descripción breve de la función.
    
    Explicación más detallada del comportamiento, casos de uso, etc.
    
    Args:
        param1: Descripción del primer parámetro
        param2: Descripción del segundo parámetro
        
    Returns:
        bool: Descripción del valor de retorno
        
    Raises:
        ValueError: Cuándo y por qué se lanza esta excepción
        
    Example:
        >>> mi_funcion("test", 42)
        True
        
    Note:
        Información adicional, advertencias, etc.
    """
    # Implementación...
```

### Control de Versiones

**Commits significativos:**

```bash
# ✅ Buenos commits
git commit -m "Añadir: validación de coordenadas GPS"
git commit -m "Corregir: bug en conversión de fechas UTC"
git commit -m "Refactorizar: función de limpieza de texto"

# ❌ Evitar commits vagos
git commit -m "fix"
git commit -m "cambios varios"
git commit -m "wip"
```

---

## ⚠️ Solución de Problemas Comunes

### Error: `ModuleNotFoundError: No module named 'PyQt5'`

**Causa:** Dependencias no instaladas o entorno virtual no activado.

**Solución:**
```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

---

### Error: `FileNotFoundError: [Errno 2] No such file or directory: 'ui/camtrapdp.ui'`

**Causa:** Ejecutando desde directorio incorrecto.

**Solución:**
```bash
# Navegar al directorio raíz del proyecto
cd WI2CamtrapDP

# Verificar que estás en el lugar correcto
ls -la  # macOS/Linux
dir     # Windows

# Deberías ver: app.py, requirements.txt, ui/, assets/, etc.

# Ejecutar desde aquí
python app.py
```

---

### Error: `UnicodeDecodeError` al leer CSV

**Causa:** Archivos CSV con codificación incorrecta.

**Solución:** Ya implementada en `processor.py`:
```python
# El código intenta múltiples codificaciones automáticamente
df = pd.read_csv(f, encoding="utf-8")
# Si falla, intenta latin-1, cp1252, etc.
```

---

### Advertencia: `QApplication: invalid style override passed`

**Causa:** Problema cosmético de PyQt5 en algunas configuraciones.

**Solución:** Ignorar (no afecta funcionalidad) o establecer:
```bash
# Windows
set QT_STYLE_OVERRIDE=

# macOS/Linux
export QT_STYLE_OVERRIDE=
```

---

### PyInstaller: `ModuleNotFoundError` en ejecutable compilado

**Causa:** Módulo no detectado automáticamente por PyInstaller.

**Solución:** Añadir al `hiddenimports` en `camtrapdp.spec`:
```python
hiddenimports = (
    collect_submodules("frictionless")
    + ["PyQt5.QtPrintSupport", "tatsu", "tu_modulo_faltante"]
)
```

---

## 📚 Recursos Adicionales

### Documentación de Tecnologías

- **PyQt5:** https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **pandas:** https://pandas.pydata.org/docs/
- **Frictionless:** https://framework.frictionlessdata.io/
- **PyInstaller:** https://pyinstaller.org/en/stable/

### Estándares y Especificaciones

- **Camtrap-DP v1.0.2:** https://camtrap-dp.tdwg.org/
- **Darwin Core:** https://dwc.tdwg.org/
- **ISO 8601 (Fechas):** https://en.wikipedia.org/wiki/ISO_8601

### Tutoriales Python

- **Real Python:** https://realpython.com/
- **Python Official Tutorial:** https://docs.python.org/3/tutorial/

---

## 🤝 Soporte y Comunidad

### Reportar Problemas

Si encuentras un bug o tienes una sugerencia:

1. Ve a [GitHub Issues](https://github.com/tu-usuario/WI2CamtrapDP/issues)
2. Clic en "New Issue"
3. Describe el problema con:
   - Pasos para reproducir
   - Comportamiento esperado vs. actual
   - Capturas de pantalla (si aplica)
   - Logs de error completos

### Contribuir al Proyecto

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guía completa.

---

## 📝 Checklist de Configuración Inicial

- [ ] Python 3.8+ instalado y verificado
- [ ] Git instalado (opcional)
- [ ] Repositorio clonado o descargado
- [ ] Entorno virtual creado (`python -m venv venv`)
- [ ] Entorno virtual activado (`venv\Scripts\activate`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Aplicación ejecutada correctamente (`python app.py`)
- [ ] Editor de código configurado (VS Code recomendado)

---

## 📞 Contacto

**Desarrollador Principal:** Cristian C. Acevedo  
**Organización:** Instituto Humboldt - Red OTUS  
**Email:** adiaz@humboldt.org.co  
**GitHub:** https://github.com/tu-usuario/WI2CamtrapDP

---

## 📜 Cita Recomendada

> Acevedo, C. C., & Diaz-Pulido, A. (2025). *WI2CamtrapDP: Wildlife Insights to Camtrap Data Package Converter* (v1.0.0) [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt.

---

**Última actualización:** 24 de diciembre de 2025  
**Versión del documento:** 1.0.0
