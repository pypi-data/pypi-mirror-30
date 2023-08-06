__version__ = '0.3'
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
from .logger import critical, error, warning, info, debug
from .configuration import init_config as __init_config, configure
from .logger import get_logger
__init_config()