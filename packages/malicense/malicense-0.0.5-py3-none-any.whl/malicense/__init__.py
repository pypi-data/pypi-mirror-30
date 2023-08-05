''' malicense.__init__: executed when malicense is imported '''

__version__ = '0.0.5'
version = __version__

import malicense
from .user import main
main(package=malicense, licfilename='LICENSE.txt')

