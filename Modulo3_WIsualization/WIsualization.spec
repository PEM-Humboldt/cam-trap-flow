# build.spec  (PyInstaller 6.x)
from PyInstaller.utils.hooks import collect_all

# Recolectar datos/binarios de librerías que incluyen recursos nativos
datas_mpl, bins_mpl, hidden_mpl = collect_all('matplotlib')
datas_sci, bins_sci, hidden_sci = collect_all('scipy')

block_cipher = None

a = Analysis(
    ['src/humboldt_viz/__main__.py'],
    pathex=['src'],  # añade src al sys.path del build
    binaries=bins_mpl + bins_sci,
    datas=datas_mpl + datas_sci + [
        ('src/humboldt_viz/resources', 'humboldt_viz/resources'),
    ],
    hiddenimports=list(set(
        hidden_mpl + hidden_sci + [
            'matplotlib.backends.backend_qt5agg',
            'PyQt5.sip',
        ]
    )),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='WIsualization',       # ejecutable único para distribución fácil
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                  # si no tienes UPX instalado, PyInstaller solo avisará
    console=False,             # GUI (sin consola)
    icon='src/humboldt_viz/resources/icons/app.ico',
)
