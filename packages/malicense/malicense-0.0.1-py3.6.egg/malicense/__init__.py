''' malicense.__init__: executed when malicense is imported '''
import os.path

from .cmInterface import parseCmArgs, parseForServing
from .lib import isLicenseValid, rehash, invalid
from .socketcomm import startServer

def main(package=None,
         licfilename='LICENSE',
         snapfilename=None,
         warn_with=print,
         report_to=None,
         snap=False,
         **kwargs):
    ''' API version. Must specify either package or licfilename

        Two ways to specify. If package is None, licfilename must go to a real file.
        Default in this case means you assume its calling from the same directory.

        If package is a python package, this will find its top directory,
        then, licfilename is just the leaf.

        Args:
            snap (bool)

        :param str package: top level directory or python package
        :param func warn_with: function that will be called to say "unlicensed". None or False means it does nothing on invalid
        :param report_to: more inputs
    '''
    if package is not None:
        try:
            licfilename = package.__path__[0] + '/' + licfilename
        except AttributeError:
            raise TypeError(str(package) + ' is not a python module/package.')
    if snapfilename is None:
        snapfilename = os.path.join(os.path.dirname(licfilename), '.lichash')
    if warn_with is None:
        warn_with = lambda x: None
    newKwargs = locals()
    newKwargs.pop('kwargs')
    if snap:
        rehash(**newKwargs)
    else:
        if not isLicenseValid(**newKwargs):
            invalid(**newKwargs)


def cmMain():
    argStruct = parseCmArgs()
    main(**vars(argStruct))


def serve(port,
          logfilename='report.txt'):
    for accInfo in startServer(port):
        accStr = ',   '.join(accInfo)
        print(accStr)

        with open(logfilename, 'a+') as fx:
            fx.write(accStr + '\n')


def cmServe():
    argStruct = parseForServing()
    serve(**vars(argStruct))


# Run it on this package
import malicense
main(package=malicense, licfilename='LICENSE.txt')

