# boletas.spec
# Archivo de configuración de PyInstaller para Boletas V1
# Genera una carpeta ejecutable (onedir) sin compresión UPX para evitar
# falsas alarmas en Windows Defender / SmartScreen.

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# ── Recopilar todos los archivos de paquetes con submodulos complejos ──────
rl_datas,  rl_bins,  rl_hidden  = collect_all('reportlab')
pil_datas, pil_bins, pil_hidden = collect_all('PIL')
fl_datas,  fl_bins,  fl_hidden  = collect_all('flask')
sq_datas,  sq_bins,  sq_hidden  = collect_all('sqlalchemy')

# ─────────────────────────────────────────────────────────────────────────────
a = Analysis(
    ['lanzador.py'],
    pathex=['.'],
    binaries=[] + rl_bins + pil_bins + fl_bins + sq_bins,
    datas=[
        # Recursos propios de la aplicación
        ('templates',  'templates'),
        ('static',     'static'),
        ('boletas.ico', '.'),      # Icono accesible desde sys._MEIPASS
    ] + rl_datas + pil_datas + fl_datas + sq_datas,
    hiddenimports=[
        # Flask y dependencias
        'flask',
        'flask_sqlalchemy',
        'jinja2',
        'jinja2.ext',
        'markupsafe',
        'click',
        'itsdangerous',
        'werkzeug',
        'werkzeug.security',
        'werkzeug.utils',
        'werkzeug.serving',
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.pysqlite',
        'sqlalchemy.pool',
        # Estándar
        'email',
        'email.mime',
        'email.mime.multipart',
        'email.mime.text',
        'charset_normalizer',
        'urllib.request',
        # Tkinter (viene con Python en Windows)
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
    ] + rl_hidden + pil_hidden + fl_hidden + sq_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir paquetes pesados no usados
        'matplotlib', 'numpy', 'pandas', 'scipy',
        'pytest', 'IPython', 'jupyter', 'notebook',
        'sphinx', 'docutils', 'pygments',
        'PyQt5', 'PyQt6', 'wx', 'gtk',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Boletas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # ← SIN UPX: reduce detecciones falsas de antivirus
    console=False,      # ← Sin ventana de consola (modo Windows)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='boletas.ico',
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,          # ← SIN UPX en todas las DLLs también
    upx_exclude=[],
    name='Boletas',
)
