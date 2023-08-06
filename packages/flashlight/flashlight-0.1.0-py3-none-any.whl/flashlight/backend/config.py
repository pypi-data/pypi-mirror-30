import os

from flashlight.backend import cli

FLHOME = cli.args.FLHOME
BIGFILE = os.path.join(FLHOME, 'big.json')
DATAFOLDER = os.path.join(FLHOME, 'data')
HOST = cli.args.HOST
PORT = cli.args.PORT
OPEN_BROWSER = cli.args.OPEN_BROWSER
