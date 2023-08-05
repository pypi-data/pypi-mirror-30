''' malicense.__init__: executed when malicense is imported '''

from .user import main

import malicense
main(package=malicense, licfilename='LICENSE.txt')
