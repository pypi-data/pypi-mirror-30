# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""

Examples::

  $ python -m eidreader

  Read the Belgian eid card in reader and display the data to stdout.

  $ python -m eidreader https://my.server.com/123
  $ python -m eidreader beid://https://my.server.com/123

  Send the data to https://my.server.com/123

If url is a string of type "beid://https://foo.bar.hjk", remove the
first scheme.  This is to support calling this directly as a protocol
handler.

"""

import logging
logger = logging.getLogger(__name__)

import argparse
import requests
from eidreader import eid2dict

SCHEMESEP = '://'

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("url", default=None, nargs='?')
    args = parser.parse_args()
    url = args.url
    
    if url:
        lst = url.split(SCHEMESEP, 2)
        if len(lst) == 3:
            url = lst[1] + SCHEMESEP + lst[2]
        elif len(lst) == 2:
            pass
            # url = lst[1]
        else:
            quit("Invalid URL {}".format(url))

        data = eid2dict()
        print("POST to {}: {}".format(url, data))
        r = requests.post(url, data=data)
        print("POST returned {}".format(r))
    else:
        print(eid2dict())

if __name__ == '__main__':    
    main()
