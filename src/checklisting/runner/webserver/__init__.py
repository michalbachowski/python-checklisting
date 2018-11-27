from checklisting.extras import has_module

if has_module('aiohttp'):
    from .impl import WebserverRunner, WebserverRunnerFactory
else:
    from .stub import WebserverRunner, WebserverRunnerFactory

__all__ = ['WebserverRunner', 'WebserverRunnerFactory']
