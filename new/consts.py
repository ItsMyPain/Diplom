BINS_DIR = 'bins'
CONFIGS_DIR = 'configs'
INTERP_CFG_DIR = 'interpolation_configs'
INTERP_DIR = 'interpolation'
CONTACT_CFG_DIR = 'contact_configs'
CONTACT_DIR = 'contact'
BOUNDARY_CFG_DIR = 'boundary_configs'
BOUNDARY_DIR = 'boundary'

TEMPLATE_DIR = 'templates'
TEMPLATE_CONFIG = f'{TEMPLATE_DIR}/config_template.conf'
TEMPLATE_INTERP_CFG = f'{TEMPLATE_DIR}/interpolation_template.cfg'
TEMPLATE_CONTACT_CFG = f'{TEMPLATE_DIR}/contact_template.cfg'
TEMPLATE_CUT_BOUNDARY_CFG = f'{TEMPLATE_DIR}/cut_boundary_template.cfg'

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
BOUNDARY_CUTTER_V2 = 'boundary_cutter_v2.py'
BOUNDARY_CUTTER = 'boundary_cutter.py'

# _____ NODE _____ #
ElasticMetaNode3D = 'ElasticMetaNode3D'

# _____ FACTORY _____ #
BINGridFactory = 'BINGridFactory'
RectGridFactory = 'RectGridFactory'

# _____ SCHEMA _____ #
ElasticCurveSchema3DRusanov3 = 'ElasticCurveSchema3DRusanov3'
ElasticRectSchema3DRusanov3 = 'ElasticRectSchema3DRusanov3'

# _____ FILLER _____ #
RectNoReflectFiller = 'RectNoReflectFiller'
RectNoReflectFillerConditional = 'RectNoReflectFillerConditional'

# _____ CORRECTOR _____ #
ForceRectElasticBoundary = 'ForceRectElasticBoundary3D'

# _____ CONTACT _____ #
GlueRectElasticContact = 'GlueRectElasticContact3D'
RectGridInterpolationCorrector = 'RectGridInterpolationCorrector'

# _____ CONDITION _____ #
RectNodeMatchConditionNoneOf = "RectNodeMatchConditionNoneOf"
RectNodeMatchConditionInFixedSet = "RectNodeMatchConditionInFixedSet"
