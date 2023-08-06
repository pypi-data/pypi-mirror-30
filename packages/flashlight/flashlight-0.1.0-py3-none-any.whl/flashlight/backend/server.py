import os
import webbrowser

from sanic import Sanic
from sanic.log import logger

from flashlight.backend import utility, config

root_path = utility.get_root_path(__file__)
app = Sanic('FlashLightServer')
app.static('/', os.path.join(root_path, 'frontend/dist'))
app.static('/', os.path.join(root_path, 'frontend/dist/index.html'))


def run(debug=False):
    """ Runs the server with configurations """
    bus = utility.Bus()
    if os.path.isdir(config.DATAFOLDER):
        bus.status = utility.compact_files(config.DATAFOLDER, config.BIGFILE)
    else:
        bus.status = utility.init_homefolder(config.DATAFOLDER, config.BIGFILE)
    if bus.status is True:
        bus.clear()
        logger.info('Starting FlashLight server using Sanic')
        # TODO Support https
        if config.OPEN_BROWSER:
            url = 'http://{}:{}'.format(config.HOST, config.PORT)
            webbrowser.open(url)
        app.run(host=config.HOST, port=config.PORT, debug=debug)


if __name__ == '__main__':
    run()
