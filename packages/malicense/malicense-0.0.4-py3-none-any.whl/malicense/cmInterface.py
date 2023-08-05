''' malicense.cmInterface.py: Command-line interfacing functions '''

import argparse
from . import version

def parseCmArgs():
    ''' Parse command-line args specific for malicense

        Of course you can't give it a python package this way, just files

        Returns:
            (obj): processed arguments structure
    '''
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=\
        '''Verify LICENSE files''')

    # File in and out arguments
    parser.add_argument('licfile', type=argparse.FileType('r'),
                        help='The license file')
    parser.add_argument('snapfile', nargs='?', type=argparse.FileType('rw'),
                        default=None, help='The snapshot file')

    # Processing options
    parser.add_argument('-s', '--snap', action='store_true', help='Make a snapshot')
    parser.add_argument('-q', '--quiet', action='store_true', help='Disable warning')
    parser.add_argument('-r', '--report-to', default=None, help='Address to send report. Example - 120.0.0.1:8000')
    parser.add_argument('-v', '--version', action='store_true')

    args = parser.parse_args()

    # Some preprocessing
    if args.version:
        print('Version ' + version)
    args.licfilename = args.licfile.name
    del args.licfile
    if args.snapfile is not None:
        args.snapfilename = args.snapfile.name
    else:
        args.snapfilename = None
    del args.snapfile
    args.warnWith = None if args.quiet else print
    del args.quiet

    return args


def parseForServing():
    ''' Parse command-line args specific for malicense-serve

        Returns:
            (obj): processed arguments structure
    '''
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=\
        '''Serve LICENSE validity logger''')

    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('-f', '--logfile', argparse.FileType('rw'), default='report.txt')

    args = parser.parse_args()
    args.logfilename = args.logfile.name
    del args.logfile
    return args

