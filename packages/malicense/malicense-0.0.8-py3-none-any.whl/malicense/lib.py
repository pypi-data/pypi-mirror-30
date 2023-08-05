''' malicense.lib.py '''
import hashlib
import codecs
import zlib

import getpass
import socket
from subprocess import check_output, CalledProcessError
import os
import sys
import io

from .socketcomm import sendMessage

class Unlicensed(Exception):
    pass


def hash_sha256(string):
    ''' Returns the hash of string encoded via the SHA-256 algorithm from hashlib'''
    return hashlib.sha256(string.encode()).hexdigest()


def generateHash(licfilename):
    with open(licfilename) as fx:
        contents = fx.read()
    return hash_sha256(contents)


def rehash(licfilename, snapfilename='.licsnap', **kwargs):
    with open(snapfilename, 'w') as fx:
        fx.write(generateHash(licfilename))


def isLicenseValid(licfilename, snapfilename='.licsnap', **kwargs):
    try:
        with open(snapfilename) as fx:
            assaved = fx.read()
        asgenerated = generateHash(licfilename)
    except IOError:
        pass
    else:
        if asgenerated == assaved:
            return True
    return False


def resolveTarget(report_to):
    if type(report_to) is bytes:
        report_to = codecs.decode(zlib.decompress(report_to).decode(), 'rot13')
    return report_to.split(':')


def encodeTarget(target):
    return zlib.compress(codecs.encode(target, 'rot13').encode())


def collectMsg(**kwargs):
    try: project = kwargs['package'].__name__
    except:
        try: project = os.path.basename(kwargs['licfilename'])
        except: project = 'nothing'
    try: username = getpass.getuser()
    except: username = 'no one'
    try: domainname = socket.getfqdn()
    except:
        try: domainname = socket.gethostname()
        except: domainname = 'nowhere'
    msg = '\nViolation in {} by {} from {}'.format(project,
                                                 username,
                                                 domainname)

    def rw(ex):
        with open(os.devnull, 'w') as devnull:
            return check_output(ex, stderr=devnull).decode('utf-8').strip()
    try: rw(['git', 'rev-parse'])
    except: pass
    else:
        try:
            gitpath = rw(['git', 'rev-parse', '--show-toplevel'])
            def gitconf(item): return rw(['git', 'config', '--global', '--get', item])
            try: gitname = gitconf('user.name')
            except: gitname = 'no one'
            try: gitemail = gitconf('user.email')
            except: gitemail = 'unset@sp.ace'
            msg += '\n{} ({}) is a git user'.format(gitname, gitemail)
        except: pass

    return msg


def invalid(warn_with=print, report_to=None, **kwargs):
    ''' What to do when the verification fails

        If warn_with == 'raise', an exception will be raised;
        however, that will make a very informative traceback
    '''
    # Show a warning
    if warn_with is not None:
        if warn_with == 'raise':
            raise Unlicenced('Unlicenced version')
        elif warn_with != False:
            warn_with('Unlicenced version')
    if report_to is not None:
        sendMessage(*resolveTarget(report_to), collectMsg(**kwargs))

