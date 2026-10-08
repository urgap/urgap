__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging

from urgap.util import iter_public_modules

logger = logging.getLogger(__name__)


__all__ = []

for mod in iter_public_modules(__name__):
    modname = mod.__name__.rsplit(".", 1)[-1]
    globals()[modname] = getattr(mod, modname)
    __all__.append(modname)
    logger.debug(f"imported uftype {modname}")
