import importlib
import inspect
import types
from typing import Any, Dict, Iterator

_EXTRAS = {
    'aiohttp': 'web',
    'psutil': 'system',
}

_MODULES: Dict[str, types.ModuleType] = {}


for module_name in _EXTRAS.keys():
    try:
        _MODULES[module_name] = importlib.import_module(module_name)
    except ImportError:
        pass


MODULE_IS_NOT_EXTRAS_TEMPLATE = 'Module [{}] is not part of any extras, please use standard import statement'
MISSING_MODULE_ERROR_TEMPLATE = 'Please install [{0}] extras to use [{1}] (required by [{2}]): ' + \
                                'pip install checklisting[{0}]'


def list_extra_modules() -> Iterator[str]:
    return iter(_EXTRAS.keys())


def has_module(module_name: str) -> bool:
    return module_name in _MODULES


def import_module(module_name: str) -> Any:
    if has_module(module_name):
        return _MODULES[module_name]
    if module_name not in _EXTRAS:
        raise RuntimeError(MODULE_IS_NOT_EXTRAS_TEMPLATE.format(module_name))
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    raise RuntimeError(MISSING_MODULE_ERROR_TEMPLATE.format(_EXTRAS[module_name], module_name, mod.__name__))
