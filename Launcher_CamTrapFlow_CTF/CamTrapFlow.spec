# -*- mode: python ; coding: utf-8 -*-
"""
CamTrapFlow PyInstaller Spec File
Configuración para generar ejecutable one-file de Launcher_CamTrapFlow.exe

Uso: python -m PyInstaller CamTrapFlow.spec --clean
"""

import sys
from pathlib import Path

# Rutas base
SCRIPT_DIR = Path.cwd()
ASSETS_DIR = SCRIPT_DIR / 'assets'
BIN_DIR = SCRIPT_DIR / 'bin'

# Configuración de datos empaquetados
datas_list = []

# Agregar assets si existen
if ASSETS_DIR.exists():
    if (ASSETS_DIR / 'icon.ico').exists():
        datas_list.append((str(ASSETS_DIR / 'icon.ico'), 'assets'))
    if (ASSETS_DIR / 'logo_humboldt.png').exists():
        datas_list.append((str(ASSETS_DIR / 'logo_humboldt.png'), 'assets'))

# Agregar ejecutables de módulos como data files (no como binaries)
if BIN_DIR.exists():
    if (BIN_DIR / 'Img2WI.exe').exists():
        datas_list.append((str(BIN_DIR / 'Img2WI.exe'), 'bin'))
    if (BIN_DIR / 'WI2CamtrapDP.exe').exists():
        datas_list.append((str(BIN_DIR / 'WI2CamtrapDP.exe'), 'bin'))
    if (BIN_DIR / 'WIsualization.exe').exists():
        datas_list.append((str(BIN_DIR / 'WIsualization.exe'), 'bin'))

# Agregar config.json si existe
if (SCRIPT_DIR / 'config.json').exists():
    datas_list.append((str(SCRIPT_DIR / 'config.json'), '.'))

block_cipher = None

a = Analysis(
    ['Lanzador.py'],
    pathex=[],
    binaries=[],  # Vacío - los .exe de módulos van en datas
    datas=datas_list,
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.messagebox'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas'],  # Excluir librerías pesadas no necesarias
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Launcher_CamTrapFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola - aplicación GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ASSETS_DIR / 'icon.ico') if (ASSETS_DIR / 'icon.ico').exists() else None,
)
