# camtrapdp.spec  (PyInstaller >= 6.x)
# Compila con:  pyinstaller camtrapdp.spec

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE
import sys

hiddenimports = (
    collect_submodules("frictionless")
    + ["PyQt5.QtPrintSupport", "tatsu"]
)

# <-- OJO: solo pares (src, dst); copiará carpetas completas
datas = [
    ("ui/camtrapdp.ui", "ui"),
    ("assets", "assets"),
    ("camtrapdp/schemas", "camtrapdp/schemas"),
]

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="WI2CamtrapDP",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI sin consola
    icon="assets/app_icon.ico" if sys.platform.startswith("win") else None,
)

# Si prefieres salida en carpeta (onedir), cambia a COLLECT.
