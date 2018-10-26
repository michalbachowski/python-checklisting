from checklisting.extras import has_module

if has_module('aiohttp'):
    from .stub import WebRunner, ChecklistHttpHandler
else:
    from .impl import WebRunner, ChecklistHttpHandler

__all__ = ['WebRunner', 'ChecklistHttpHandler']
