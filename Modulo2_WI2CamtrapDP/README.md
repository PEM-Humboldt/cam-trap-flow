# WI2CamtrapDP 📦🐾

**Wildlife Insights to Camtrap Data Package Converter**

Herramienta de escritorio para convertir exportaciones de [Wildlife Insights](https://www.wildlifeinsights.org/) al estándar [Camtrap-DP](https://camtrap-dp.tdwg.org/) (Camera Trap Data Package) v1.0.2 para publicación científica y análisis estandarizado de datos de fototrampeo.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 Características Principales

- ✅ **Conversión automatizada** de proyectos Wildlife Insights a Camtrap-DP
- ✅ **Validación integrada** con Frictionless Framework v5.x
- ✅ **Interfaz gráfica intuitiva** (PyQt5)
- ✅ **Gestión robusta de taxonomía** (detección de datos incompletos, múltiples identificaciones)
- ✅ **Conversión automática de zonas horarias** a ISO-8601 UTC
- ✅ **Empaquetado automático** en ZIP con datapackage.json + CSVs
- ✅ **Plantilla de correo** para publicación en SIB Colombia
- ✅ **Distribución como ejecutable** (.exe) sin necesidad de Python instalado

---

## 📋 Requisitos

### Para Usuarios Finales (Ejecutable)
- **Sistema Operativo:** Windows 10/11 (64-bit)
- No requiere Python ni dependencias instaladas

### Para Desarrolladores (Código Fuente)
- **Python:** 3.8 o superior
- **Sistema Operativo:** Windows, macOS, Linux
- **Dependencias:** Ver [requirements.txt](requirements.txt)

---

## 🚀 Instalación y Uso

### Opción 1: Descargar Ejecutable (Recomendado para Usuarios)

1. Descarga la última versión desde [Releases](https://github.com/tu-usuario/WI2CamtrapDP/releases)
2. Extrae el archivo ZIP
3. Ejecuta `Camtrap DP.exe`
4. **¡Listo!** No requiere instalación adicional

### Opción 2: Ejecutar desde Código Fuente (Para Desarrolladores)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/WI2CamtrapDP.git
cd WI2CamtrapDP

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python app.py
```

---

## 📖 Flujo de Trabajo

1. **Exportar proyecto desde Wildlife Insights:**
   - Inicia sesión en [Wildlife Insights](https://www.wildlifeinsights.org/)
   - Selecciona tu proyecto (NO iniciativa)
   - Descarga la exportación completa (ZIP con 4 archivos CSV)

2. **Abrir WI2CamtrapDP:**
   - Ejecuta la aplicación (`.exe` o `python app.py`)
   - Haz clic en "Examinar" y selecciona el ZIP de Wildlife Insights

3. **Configurar opciones:**
   - ☑️ **Validar con Frictionless:** Verifica la estructura del paquete
   - ☑️ **Crear paquete ZIP:** Genera archivo comprimido final
   - ☑️ **Abrir carpeta al terminar:** Acceso rápido a resultados
   - 🕐 **Zona horaria:** Predeterminado `America/Bogota` (ajustar si es necesario)

4. **Procesar:**
   - Haz clic en "Procesar"
   - Monitorea el progreso en la barra y logs

5. **Resultados generados:**
   ```
   WI2CamtrapDP_{nombre_proyecto}/
   ├── output/
   │   ├── deployments.csv
   │   ├── media.csv
   │   ├── observations.csv
   │   └── datapackage.json
   └── WI2CamtrapDP_{nombre_proyecto}.zip
   ```

6. **Publicar (opcional):**
   - Haz clic en "Plantilla de Correo"
   - Copia el texto generado para enviar al SIB Colombia

---

## 📂 Estructura del Proyecto

```
WI2CamtrapDP/
├── app.py                      # Aplicación principal (GUI)
├── requirements.txt            # Dependencias Python
├── camtrapdp.spec             # Configuración PyInstaller
├── .gitignore                 # Exclusiones Git
├── README.md                  # Este archivo
├── GUIA_DESARROLLO.md         # Guía detallada para desarrollo local
├── LICENSE                    # Licencia del proyecto
├── CONTRIBUTING.md            # Guía de contribución
├── GITHUB_QUICKSTART.md       # Guía rápida de GitHub
│
├── camtrapdp/                 # Paquete principal
│   ├── __init__.py           # Inicialización del módulo
│   ├── config.py             # Configuración por defecto
│   ├── processor.py          # Motor de transformación WI → Camtrap-DP
│   ├── utils.py              # Utilidades (fechas, MIME, limpieza texto)
│   ├── validator.py          # Validación con Frictionless
│   └── schemas/              # Esquemas JSON Camtrap-DP v1.0.2
│       ├── camtrap-dp-profile.json
│       ├── deployments-table-schema.json
│       ├── media-table-schema.json
│       └── observations-table-schema.json
│
├── ui/
│   └── camtrapdp.ui          # Diseño interfaz Qt Designer
│
├── assets/                   # Recursos visuales
│   ├── app_icon.ico          # Icono de la aplicación
│   ├── app_icon.png          # Icono PNG
│   └── logo_humboldt.png     # Logo institucional
│
├── build/                    # Archivos temporales de PyInstaller (generado)
│   └── camtrapdp/           # Análisis y TOC de compilación
│
└── dist/                     # Ejecutable distribuible (generado)
    └── Camtrap DP.exe       # Aplicación standalone
```

**Nota:** Las carpetas `build/` y `dist/` se generan automáticamente al compilar con PyInstaller y están excluidas del control de versiones (`.gitignore`).

---

## 🔧 Compilar Ejecutable

Para generar el archivo `.exe` desde el código fuente:

```bash
# 1. Instalar PyInstaller (si no está instalado)
pip install pyinstaller

# 2. Limpiar compilaciones anteriores (recomendado)
rmdir /s /q build
rmdir /s /q dist

# 3. Compilar usando el archivo .spec
python -m PyInstaller camtrapdp.spec --clean

# 4. El ejecutable estará en dist/
# Windows: dist/Camtrap DP.exe
```

**Nota:** El archivo `.spec` ya incluye toda la configuración necesaria (icono, recursos, dependencias ocultas).

### Estructura Post-Compilación

Después de compilar, el proyecto contendrá:

```
WI2CamtrapDP/
├── build/                 # Archivos temporales de PyInstaller (se puede eliminar)
│   └── camtrapdp/
│       ├── Analysis-00.toc
│       ├── EXE-00.toc
│       ├── PKG-00.toc
│       ├── PYZ-00.pyz
│       ├── warn-camtrapdp.txt
│       └── xref-camtrapdp.html
│
└── dist/                  # Ejecutable listo para distribuir
    └── Camtrap DP.exe    # ⭐ Aplicación lista para usar (95-110 MB)
```

**⚠️ Importante:** Solo distribuye el contenido de `dist/`. Las carpetas `build/` son temporales y pueden eliminarse.

---

## 📊 Entrada y Salida

### **Entrada: Wildlife Insights Export**

Archivo ZIP con **4 archivos CSV** (exportación de PROYECTO):

| Archivo | Descripción |
|---------|-------------|
| `projects.csv` | Metadatos del proyecto (nombre, coordinador, licencias, objetivos) |
| `cameras.csv` | Información de equipos (fabricante, modelo, serial) |
| `deployments.csv` | Despliegues espaciotemporales (coordenadas, fechas, ubicaciones) |
| `images_{id}.csv` | Registros fotográficos + identificaciones taxonómicas |

⚠️ **Importante:** Solo procesa exportaciones de **PROYECTO** (un solo archivo `images_*.csv`). Las exportaciones de INICIATIVA (múltiples archivos `images_*.csv`) no son soportadas.

### **Salida: Camtrap-DP v1.0.2**

Paquete estandarizado con **3 tablas CSV + metadatos JSON:**

| Archivo | Descripción | Campos Clave |
|---------|-------------|--------------|
| `deployments.csv` | Despliegues de cámaras | deploymentID, locationName, latitude, longitude, deploymentStart/End, cameraModel |
| `media.csv` | Archivos multimedia | mediaID, deploymentID, captureMethod, timestamp, filePath, fileMediatype |
| `observations.csv` | Observaciones taxonómicas | observationID, mediaID, scientificName, vernacularName, count, observationType |
| `datapackage.json` | Metadatos del paquete | Título, descripción, licencias, contribuidores, esquemas de validación |

---

## 🔍 Validaciones Críticas

La herramienta implementa validaciones para garantizar calidad de datos:

### ❌ **Detención del Proceso:**
- **"No CV Result"** detectado en campos taxonómicos (`genus`, `species`, `common_name`, `family`, `order`)
- Exportación de **INICIATIVA** en lugar de **PROYECTO** (múltiples `images_*.csv`)
- Campos requeridos vacíos en `deployments.csv`

### ⚠️ **Advertencias (Continúa el Proceso):**
- Campos opcionales vacíos (e.g., `cameraModel`, `age`, `sex`)
- Coordenadas fuera de rango (se reemplazan por NA)
- Timestamps malformados (se corrigen o descartan)

### ✅ **Validación Opcional con Frictionless:**
- Verifica estructura completa del Data Package
- Valida tipos de datos y restricciones
- Genera reporte detallado por recurso/campo/fila

---

## 🛠️ Transformaciones Principales

### 1. **Taxonomía (Wildlife Insights → Darwin Core)**
```python
# Entrada WI:
genus: "Leopardus"
species: "tigrinus"
common_name: "Oncilla"

# Salida Camtrap-DP:
scientificName: "Leopardus tigrinus"
vernacularName: "Oncilla"
observationType: "animal"
```

### 2. **Fechas (Local → ISO-8601 UTC)**
```python
# Entrada WI (America/Bogota GMT-5):
timestamp: "2023-05-15 14:23:11"

# Salida Camtrap-DP:
timestamp: "2023-05-15T19:23:11Z"  # +5 horas a UTC
```

### 3. **Observaciones Múltiples**
```python
# Si una foto tiene 2 especies identificadas:
# WI: 2 filas con mismo image_id
# Camtrap-DP: 1 fila en media.csv + 2 filas en observations.csv
```

### 4. **Clasificación de Observaciones**
| Valor en `common_name` | `observationType` | `scientificName` |
|------------------------|-------------------|------------------|
| "Blank" | blank | blank |
| "Human" | human | Homo sapiens |
| "Vehicle" | vehicle | blank |
| "Unknown" | unknown | blank |
| "Unclassified" | unclassified | blank |
| Nombre de especie | animal | Genus species |

---

## 🐛 Solución de Problemas

### **Error: "Se encontraron valores 'No CV Result'"**
**Causa:** Registros sin identificación taxonómica completa en Wildlife Insights.

**Solución:**
1. Revisar los registros listados en el log de errores
2. Completar identificaciones en Wildlife Insights
3. Exportar nuevamente el proyecto
4. Reintentar el procesamiento

### **Error: "La exportación parece ser de una INICIATIVA"**
**Causa:** El ZIP contiene múltiples archivos `images_*.csv` (varios proyectos).

**Solución:**
- Exportar cada **proyecto individual** por separado desde Wildlife Insights
- Procesar cada proyecto de forma independiente

### **Advertencia: "No se encontró información de modelo de cámara"**
**Causa:** Los campos `make` y `model` están vacíos en `cameras.csv`.

**Solución:**
- Esta es solo una advertencia; el proceso continúa
- El campo `cameraModel` se omitirá en `deployments.csv` (es opcional)

---

## 🤝 Contribuciones

Desarrollado por el **Instituto de Investigación de Recursos Biológicos Alexander von Humboldt** en el marco del proyecto de gestión de datos de fototrampeo para la Red OTUS.

### Colaboradores:
- **Cristian C. Acevedo** - Desarrollo principal
- **Angélica Diaz-Pulido** - Coordinación científica

### Cómo Contribuir:
1. Fork el repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📚 Referencias

- **Camtrap-DP Standard:** https://camtrap-dp.tdwg.org/
- **Wildlife Insights:** https://www.wildlifeinsights.org/
- **Frictionless Framework:** https://framework.frictionlessdata.io/
- **SIB Colombia:** https://sibcolombia.net/
- **Instituto Humboldt:** http://www.humboldt.org.co/

---

## 📞 Contacto y Soporte

Para preguntas, problemas o sugerencias:
- **Issues:** [GitHub Issues](https://github.com/tu-usuario/WI2CamtrapDP/issues)
- **Email:** adiaz@humboldt.org.co
- **Documentación completa:** [Wiki del proyecto](https://github.com/tu-usuario/WI2CamtrapDP/wiki)

---

## 📜 Cómo Citar

Si utilizas esta herramienta en tu investigación, por favor cítala como:

> Acevedo, C. C., & Diaz-Pulido, A. (2025). *WI2CamtrapDP: Wildlife Insights to Camtrap Data Package Converter* (v1.0.0) [Software]. Red OTUS, Instituto de Investigación de Recursos Biológicos Alexander von Humboldt. https://github.com/tu-usuario/WI2CamtrapDP

---

**⭐ Si te resulta útil, considera darle una estrella al repositorio!**
