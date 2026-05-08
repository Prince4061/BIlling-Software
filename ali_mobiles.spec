# -*- mode: python ; coding: utf-8 -*-
# ali_mobiles.spec — PyInstaller Build Configuration
# Build command: pyinstaller ali_mobiles.spec --clean

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# ── Collect tricky packages (DLLs + data + hidden imports) ──────────────
datas    = []
binaries = []
hiddenimports = []

for pkg in ['webview', 'reportlab', 'PIL']:
    try:
        tmp = collect_all(pkg)
        datas     += tmp[0]
        binaries  += tmp[1]
        hiddenimports += tmp[2]
    except Exception:
        pass

# ── Our app files ────────────────────────────────────────────────────────
datas += [
    ('templates',  'templates'),   # HTML templates
    ('static',     'static'),      # CSS / JS / images
    ('logic',      'logic'),       # Python logic modules
]

# ── Analysis ─────────────────────────────────────────────────────────────
a = Analysis(
    ['desktop_run.py'],
    pathex=['d:\\Ali Mobiles Billing Software'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + [
        # Flask + Werkzeug
        'flask', 'flask.templating', 'flask.json', 'flask.cli',
        'flask.debughelpers', 'flask.signals',
        'jinja2', 'jinja2.ext', 'jinja2.environment',
        'jinja2.loaders', 'jinja2.runtime',
        'werkzeug', 'werkzeug.serving', 'werkzeug.routing',
        'werkzeug.exceptions', 'werkzeug.middleware',
        'werkzeug.middleware.proxy_fix',
        'werkzeug.middleware.shared_data',
        'click',
        'itsdangerous', 'blinker',
        # Data
        'pandas', 'pandas.core', 'pandas.io',
        'pandas.io.excel', 'pandas.io.parsers',
        'openpyxl', 'openpyxl.workbook',
        'openpyxl.styles', 'openpyxl.chart',
        'openpyxl.drawing', 'openpyxl.utils',
        'et_xmlfile',
        # Networking (for WhatsApp sender)
        'requests', 'requests.adapters',
        'certifi', 'urllib3', 'charset_normalizer', 'idna',
        # Logic modules
        'logic', 'logic.bill_logic', 'logic.excel_handler',
        'logic.pdf_generator', 'logic.report_generator',
        'logic.whatsapp_sender',
        # ReportLab
        'reportlab', 'reportlab.pdfgen', 'reportlab.pdfgen.canvas',
        'reportlab.lib', 'reportlab.lib.pagesizes',
        'reportlab.lib.colors', 'reportlab.lib.units',
        'reportlab.lib.styles', 'reportlab.lib.enums',
        'reportlab.platypus', 'reportlab.platypus.tables',
        'reportlab.platypus.flowables',
        'reportlab.platypus.paragraph',
        'reportlab.graphics',
        # Image handling
        'PIL', 'PIL.Image', 'PIL.ImageFont', 'PIL.ImageDraw',
        # Python stdlib
        'threading', 'webbrowser', 'base64', 'datetime',
        'json', 'os', 'sys', 'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # ─ Exclude heavy unused packages to keep EXE small ─────────────────
    excludes=[
        # ML / AI (very heavy)
        'torch', 'torchvision', 'torchaudio',
        'transformers', 'tensorflow', 'keras',
        'faiss', 'huggingface_hub',
        'sklearn', 'scipy', 'matplotlib',
        'cv2', 'imageio',
        # AWS SDK (pulled in as dependency but not needed)
        'boto3', 'botocore', 'awscli', 's3transfer',
        # Notebook / IPython
        'notebook', 'IPython', 'ipykernel', 'ipython_genutils',
        'jupyter', 'nbformat', 'nbconvert',
        # GUI toolkits we don't use
        'tkinter', '_tkinter',
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'wx',
        # Other heavy unused
        'pyarrow', 'multiprocessing',
        'cryptography', 'Crypto',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AliMobilesBilling',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
