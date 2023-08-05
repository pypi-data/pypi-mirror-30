#!/usr/bin/env python

import sys 
from subprocess import call

def comments():
    CSI = '\033['
    print CSI + "31;32m" + u'Example to run:' + CSI + "0m"
    print CSI + "31;32m" + u' - dedepuyer -r beta\n - dedepuyer -r stable\n - dedepuyer -r preview' + CSI + "0m"

def main():
    try:
        options = sys.argv[1]
        arg = sys.argv[2]
        if options == '--help':
            comments()
        else:
            if options == '-r' and (arg == 'stable' or arg == 'beta' or arg == 'preview'):
                call("./bin/dedepuyer '%s' '%s'" % (options,arg), shell=True)
            else:
                CSI = "\x1B["
                print CSI + "31;40m" + u"Argument is not valid: Run with --help" + CSI + "0m"
    except Exception as e:
        print e
        comments()
        sys.exit(1)
