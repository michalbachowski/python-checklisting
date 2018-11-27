from checklisting.extras import has_module

if has_module('aiohttp'):
    from .impl import WebRunner, ChecklistHttpHandler
else:
    from .stub import WebRunner, ChecklistHttpHandler

__all__ = ['WebRunner', 'ChecklistHttpHandler']

