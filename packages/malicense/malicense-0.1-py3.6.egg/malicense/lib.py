import hashlib
import getpass
import socket

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


def rehash(licfilename, hashfilename='.lichash', **kwargs):
    # Run this after LICENSE has been changed
    with open(hashfilename, 'w') as fx:
        fx.write(generateHash(licfilename))


def isLicenseValid(licfilename, hashfilename='.lichash', **kwargs):
    try:
        with open(hashfilename) as fx:
            assaved = fx.read()
        asgenerated = generateHash(licfilename)
    except IOError:
        pass
    else:
        if asgenerated == assaved:
            return True
    return False


def invalid(warn_with=print, report_to=None, **kwargs):
    ''' What to do when the verification fails

        If warn_with == 'raise', an exception will be raised

        example  report_to='120.0.0.1:8000'
    '''
    # Show a warning
    if warn_with is not None:
        if warn_with == 'raise':
            raise Unlicenced('Unlicenced version')
        elif warn_with != False:
            warn_with('Unlicenced version')

    # Report to authorities
    if report_to is not None:
        # Get some info
        username = getpass.getuser()
        hostname = socket.gethostname()
        ipaddress = socket.gethostbyname(hostname)
        domainname = socket.getfqdn()

        # Send a report
        targethost, port = report_to.split(':')
        sendMessage(targethost, port, username)


