'''
from subpackage import * -  is frowned up, don't add any submodules to __all__
'''
__all__ = []
# __all__ = [
#     'collection',
#     'objects',
# ]
from multigetattr import multi_getattr
from nearly_equal import nearly_equal
