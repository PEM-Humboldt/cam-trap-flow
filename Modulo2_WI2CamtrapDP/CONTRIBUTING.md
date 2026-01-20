# Guía de Contribución 🤝

¡Gracias por tu interés en contribuir a **WI2CamtrapDP**! Este documento proporciona lineamientos para contribuir al proyecto de manera efectiva.

---

## 🌟 Cómo Puedes Contribuir

Existen varias formas de contribuir al proyecto:

1. **Reportar bugs** 🐛
2. **Sugerir nuevas funcionalidades** 💡
3. **Mejorar la documentación** 📚
4. **Enviar código** 💻
5. **Probar y validar** ✅

---

## 📋 Proceso de Contribución

### 1. Fork y Configuración

```bash
# 1. Fork el repositorio en GitHub

# 2. Clonar tu fork
git clone https://github.com/tu-usuario/WI2CamtrapDP.git
cd WI2CamtrapDP

# 3. Añadir el repositorio upstream
git remote add upstream https://github.com/repo-original/WI2CamtrapDP.git

# 4. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 5. Instalar dependencias
pip install -r requirements.txt
```

### 2. Crear una Rama

```bash
# Siempre crear una nueva rama para tus cambios
git checkout -b feature/nombre-descriptivo

# O para bug fixes
git checkout -b fix/descripcion-del-bug
```

**Nomenclatura de Ramas:**
- `feature/` - Nueva funcionalidad
- `fix/` - Corrección de bug
- `docs/` - Mejoras en documentación
- `refactor/` - Refactorización sin cambios funcionales
- `test/` - Añadir o mejorar tests

### 3. Realizar Cambios

- **Mantén commits pequeños y enfocados**
- **Escribe mensajes de commit descriptivos**

```bash
# Formato recomendado de commits
git commit -m "Tipo: Descripción breve

Explicación detallada de los cambios (si es necesario)

Fixes #numero-issue"
```

**Tipos de commit:**
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Documentación
- `style:` Formato, espacios (no cambia lógica)
- `refactor:` Refactorización de código
- `test:` Añadir tests
- `chore:` Mantenimiento

### 4. Enviar Pull Request

```bash
# 1. Push a tu fork
git push origin feature/nombre-descriptivo

# 2. Ir a GitHub y crear Pull Request
# 3. Completar la plantilla del PR
```

---

## 📝 Estándares de Código

### Python (PEP 8)

```python
# ✅ CORRECTO
def convertir_timestamp(fecha, zona_horaria="America/Bogota"):
    """
    Convierte fecha local a ISO-8601 UTC.
    
    Args:
        fecha (str): Fecha en formato 'YYYY-MM-DD HH:MM:SS'
        zona_horaria (str): Zona horaria del timestamp
        
    Returns:
        str: Fecha en formato ISO-8601 con sufijo Z
    """
    # Implementación
    pass

# ❌ INCORRECTO
def convertir(f,z="America/Bogota"): # Sin docstring, nombres poco descriptivos
    pass
```

### Convenciones del Proyecto

1. **Nombres de variables:**
   - Variables: `snake_case`
   - Constantes: `MAYUSCULAS_CON_GUION`
   - Clases: `PascalCase`

2. **Docstrings:**
   - Todas las funciones públicas deben tener docstrings
   - Formato Google Style

3. **Imports:**
   ```python
   # Orden de imports:
   # 1. Librerías estándar
   import os
   import sys
   
   # 2. Librerías de terceros
   import pandas as pd
   from PyQt5 import QtWidgets
   
   # 3. Módulos locales
   from camtrapdp import processor
   from camtrapdp.utils import convert_timestamp
   ```

4. **Manejo de errores:**
   ```python
   # ✅ CORRECTO: Específico y con mensaje
   try:
       resultado = procesar_archivo(ruta)
   except FileNotFoundError as e:
       raise RuntimeError(f"Archivo no encontrado: {ruta}") from e
   
   # ❌ INCORRECTO: Genérico y sin contexto
   try:
       procesar()
   except Exception:
       pass
   ```

---

## 🧪 Testing

### Ejecutar Tests Existentes

```bash
# Cuando se implementen tests
pytest tests/
```

### Añadir Nuevos Tests

```python
# tests/test_processor.py
import pytest
from camtrapdp.processor import clasificar_observacion

def test_clasificar_observacion_humano():
    """Verifica que 'Human' se clasifique correctamente."""
    resultado = clasificar_observacion("Human", "", "")
    assert resultado["observationType"] == "human"
    assert resultado["scientificName"] == "Homo sapiens"

def test_clasificar_observacion_blank():
    """Verifica que 'Blank' se clasifique como blank."""
    resultado = clasificar_observacion("Blank", "", "")
    assert resultado["observationType"] == "blank"
    assert resultado["scientificName"] == "blank"
```

---

## 📚 Documentación

### Actualizar README.md

Si tu contribución afecta el uso de la herramienta:
- Actualizar sección correspondiente en README.md
- Añadir ejemplos si es necesario

### Comentarios en Código

```python
# ✅ BUENO: Explica el "por qué"
# Normalizar a mayúsculas porque Camtrap-DP requiere
# nombres de género capitalizados según nomenclatura linneana
genus = genus_raw.capitalize()

# ❌ MALO: Explica el "qué" (obvio del código)
# Capitalizar genus
genus = genus_raw.capitalize()
```

---

## 🐛 Reportar Bugs

### Información Necesaria

Al reportar un bug, incluye:

1. **Descripción clara** del problema
2. **Pasos para reproducir:**
   ```
   1. Abrir aplicación
   2. Seleccionar archivo X
   3. Hacer clic en "Procesar"
   4. Ver error Y
   ```
3. **Comportamiento esperado** vs **comportamiento actual**
4. **Entorno:**
   - Sistema operativo (Windows 10, macOS 13, etc.)
   - Versión de Python (si aplica)
   - Versión de la aplicación
5. **Logs y capturas de pantalla** (si es posible)
6. **Archivo de prueba** (si es relevante y no contiene datos sensibles)

### Plantilla de Issue

```markdown
**Descripción del Bug:**
Breve descripción del problema

**Pasos para Reproducir:**
1. 
2. 
3. 

**Comportamiento Esperado:**
Lo que debería suceder

**Comportamiento Actual:**
Lo que está sucediendo

**Entorno:**
- SO: Windows 10 Pro 64-bit
- Python: 3.10.5 (si aplica)
- Versión: 1.0.0

**Logs/Capturas:**
[Adjuntar logs o imágenes]
```

---

## 💡 Sugerir Funcionalidades

### Plantilla de Feature Request

```markdown
**¿Qué problema resuelve esta funcionalidad?**
Descripción clara del problema o necesidad

**Solución Propuesta:**
Cómo debería funcionar la nueva característica

**Alternativas Consideradas:**
Otras formas de resolver el problema

**Contexto Adicional:**
Casos de uso, ejemplos, mockups
```

---

## ✅ Checklist Antes de Enviar PR

- [ ] El código sigue los estándares PEP 8
- [ ] He añadido/actualizado docstrings
- [ ] He probado los cambios localmente
- [ ] He actualizado la documentación (si es necesario)
- [ ] Los tests existentes pasan (si existen)
- [ ] He añadido tests para nueva funcionalidad (si aplica)
- [ ] El commit tiene mensaje descriptivo
- [ ] He actualizado CHANGELOG.md (si existe)

---

## 📞 ¿Preguntas?

Si tienes dudas sobre cómo contribuir:
- Abre un **Issue** con la etiqueta `question`
- Envía email a: adiaz@humboldt.org.co

---

## 🎉 Reconocimiento

Todos los contribuidores serán listados en:
- Sección de agradecimientos del README
- Archivo CONTRIBUTORS.md
- Release notes

**¡Gracias por hacer este proyecto mejor!** 🚀
