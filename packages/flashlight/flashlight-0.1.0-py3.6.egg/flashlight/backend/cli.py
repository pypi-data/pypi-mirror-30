import os
import argparse
from pathlib import Path

USERHOME = str(Path.home())
parser = argparse.ArgumentParser(
    description='Flash the light into the darkness of Neural Networks', epilog='No more help!!'
)
parser.add_argument(
    '--dir',
    help='FlashLight home directory',
    default=os.path.join(USERHOME, '.FlashLight'),
    type=str,
    dest='FLHOME',
)
parser.add_argument(
    '--host', help='IP address FlashLight server uses', default='0.0.0.0', type=str, dest='HOST'
)
parser.add_argument(
    '--port', help='Port address FlashLight server uses', default='8000', type=str, dest='PORT'
)
parser.add_argument(
    '--ob',
    help='Open default browser on FlashLight server start',
    action='store_true',
    dest='OPEN_BROWSER',
)
args = parser.parse_args()
if __name__ == '__main__':
    print(args)
