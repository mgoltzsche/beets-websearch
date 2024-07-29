from beets import config
from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from optparse import OptionParser
from beetsplug.web import ReverseProxied


class WebSearchPlugin(BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.config.add(
            {
                'host': '127.0.0.1',
                'port': 8331,
                'cors': '',
                'cors_supports_credentials': False,
                'reverse_proxy': False,
                'include_paths': False,
            }
        )

    def commands(self):
        p = OptionParser()
        p.add_option('-d', '--debug', action='store_true', default=False, help='debug mode')
        c = Subcommand('websearch', parser=p, help='serve the music library via HTTP')
        c.func = self._run_server
        return [c]

    def _run_server(self, lib, opts, args):
        from beetsplug.websearch.gen.main import app
        import uvicorn

        # TODO: configure app: self._configure_app(app, lib)
        uvicorn.run(app, port=5000, log_level=opts.debug and 'debug' or 'info')

    def _configure_app(self, app, lib):
        app.config['lib'] = lib
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        app.config['INCLUDE_PATHS'] = self.config['include_paths']
        app.config['READONLY'] = True

        if self.config['cors']:
            # TODO: CORS support
            ...

        if self.config['reverse_proxy']:
            # TODO: make the app reverse-proxy-aware
            #app.wsgi_app = ReverseProxied(app.wsgi_app)
            ...
