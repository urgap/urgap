import importlib
import logging
import pkgutil

logger = logging.getLogger(__name__)


__all__ = []

for _, modname, ispkg in pkgutil.iter_modules(__path__):
    if ispkg:
        continue
    mod = importlib.import_module(f"{__name__}.{modname}")
    globals()[modname] = getattr(mod, modname)
    __all__.append(modname)
    logger.debug(f"imported uftype {modname}")
