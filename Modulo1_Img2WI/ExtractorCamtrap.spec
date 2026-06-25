# ExtractorCamtrap.spec — build ONE-FILE reproducible con PyQt5, ffmpeg y recursos
# Uso:  python -m PyInstaller ExtractorCamtrap.spec --clean

from PyInstaller.utils.hooks import collect_all

# Reúne todo lo necesario de PyQt5 (plugins/platforms, etc.)
datas, binaries, hiddenimports = collect_all('PyQt5')

# Si usas 'wiutils' (opcional). Si no está instalado, se ignora sin romper el build.
try:
    d2, b2, h2 = collect_all('wiutils')
    datas += d2
    binaries += b2
    hiddenimports += h2
except Exception:
    pass

# Incluir ffmpeg embebido (build STATIC x64 recomendado) y el icono de la app
binaries += [("app/bin/ffmpeg.exe", ".")]
datas += [("resources/icons/app_icon.png", "resources/icons")]

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ONE-FILE: empaqueta todo directamente en el EXE (no hay COLLECT)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Img2WI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # ventana de consola oculta (GUI)
    icon='resources/icons/app_icon.png',
)
