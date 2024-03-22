STDOUT = None  # subprocess.DEVNULL
STDERR = None  # subprocess.DEVNULL

BINS_DIR = 'bins'
CONFIGS_DIR = 'configs'
INTERP_CFG_DIR = 'interpolation_configs'
INTERP_DIR = 'interpolation'
CONTACT_CFG_DIR = 'contact_configs'
CONTACT_DIR = 'contact'
BOUNDARY_DIR = 'boundary'

DIMS = 3

BASE_CONF = f'template{DIMS}D.conf'
INTERP_CFG = f'template{DIMS}D.cfg'
CONTACT_CFG = f'template{DIMS}D.cfg'
MAIN_CONF = f'main_template{DIMS}D.conf'

RECT_DIR = 'rect_new'
BUILD_COMM = f'{RECT_DIR}/rect/build/rect'
PREPARE_FILE = 'prepare.sh'
PREPARE_ALL = f'bash ./{PREPARE_FILE}'

INTERP_COMM1 = f'direction=1 interpolation=barycentric {RECT_DIR}/rect/build/interpolation'
INTERP_COMM2 = f'direction=2 interpolation=barycentric {RECT_DIR}/rect/build/interpolation'
CONTACT_COMM = f'{RECT_DIR}/rect/build/contact_finder'

BOUNDARY_CUTTER = 'boundary_cutter.py'

AXES = {'X': 0, 'Y': 1, 'Z': 2}

# _______________ Contacts _______________ #
RectGridInterpolationCorrector = 'RectGridInterpolationCorrector'
GlueRectElasticContact = f'GlueRectElasticContact{DIMS}D'

# _______________ Fillers _______________ #
RectNoReflectFiller = 'RectNoReflectFiller'
RectNoReflectFillerConditional = 'RectNoReflectFillerConditional'
# _______________ Correctors _______________ #

ForceRectElasticBoundary = f'ForceRectElasticBoundary{DIMS}D'
