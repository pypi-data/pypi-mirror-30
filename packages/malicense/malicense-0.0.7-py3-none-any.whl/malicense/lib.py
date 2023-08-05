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


class NoStdStreams(object):
    def __init__(self,stdout = None, stderr = None):
        self.devnull = open(os.devnull,'w')
        self._stdout = stdout or self.devnull or sys.stdout
        self._stderr = stderr or self.devnull or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.devnull.close()


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
    try:
        with NoStdStreams():
            gitpath = rw(['git', 'rev-parse', '--show-toplevel', '2>/dev/null'])
        print(gitpath)
    except: pass
    else:
        def gitconf(item): return rw(['git', 'config', '--global', '--get', item])
        gitname = gitconf('user.name')
        gitemail = gitconf('user.email')
        msg += '\n{} ({}) is a git user'.format(gitname, gitemail)

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

