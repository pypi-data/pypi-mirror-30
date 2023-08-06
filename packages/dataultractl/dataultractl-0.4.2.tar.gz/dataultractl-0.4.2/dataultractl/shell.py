# -*- coding: utf-8 -*-
import sys
from .client import Client


def main():
    try:
        Client().main(sys.argv[1:])
    except Exception as e:
        msg = e.message
        if not msg or msg == '':
            msg = "error"
        print "ERROR: %s" % msg
        # print msg
        sys.exit(1)

if __name__ == "__main__":
    main()
