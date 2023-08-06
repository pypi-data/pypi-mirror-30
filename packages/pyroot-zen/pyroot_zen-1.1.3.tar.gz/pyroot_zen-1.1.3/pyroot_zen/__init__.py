"""

`pyroot_zen` package.

"""

__author__  = 'Chitsanu Khurewathanakul'
__email__   = 'chitsanu.khurewathanakul@gmail.com'
__license__ = 'GNU GPLv3'

## Import ROOT, if not already
import ROOT

## Unless it's documentation (sphinx, readthedocs), start the patching.
import os
if os.environ.get('READTHEDOCS') != 'True':
  import patch_ROOT
  del patch_ROOT
