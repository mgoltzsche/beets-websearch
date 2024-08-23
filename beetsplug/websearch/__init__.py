from beets import config
from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from optparse import OptionParser
from beetsplug.web import ReverseProxied
from beetsplug.websearch.webapp import create_app, configure_app


class WebSearchPlugin(BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.config.add(
            {
                'host': '127.0.0.1',
                'port': 5000,
                'cors': '',
                'cors_supports_credentials': False,
                'reverse_proxy': False,
                'include_paths': False,
                'state_dir': '/tmp',
            }
        )

    def commands(self):
        p = OptionParser()
        p.add_option('-d', '--debug', action='store_true', default=False, help='debug mode')
        c = Subcommand('websearch', parser=p, help='serve the music library via HTTP')
        c.func = self._run_server
        return [c]

    def _run_server(self, lib, opts, args):
        app = create_app()
        port = self.config['port'].get(int)

        import uvicorn

        configure_app(app, lib)
        uvicorn.run(app, port=port, log_level=opts.debug and 'debug' or 'info')
