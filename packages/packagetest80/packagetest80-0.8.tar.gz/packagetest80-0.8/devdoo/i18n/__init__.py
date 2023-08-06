from . import config
from . import resource_loader
from .config import set, get
from .resource_loader import I18nFileLoadError, register_loader, load_config
from .translations import add as add_translation
from .translator import t

resource_loader.init_loaders()

load_path = config.get('load_path')
