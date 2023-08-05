from modislock_webservice import create_app
import multiprocessing
from gunicorn.app.base import BaseApplication
from gunicorn.six import iteritems


def number_of_workers():
    """Returns number of workers WSGI should generate

    :return int workers:
    """
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(BaseApplication):
    """Standalone WSGI application that bypasses calling gunicorn from command line

    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def init(self, parser, opts, args):
        # TODO for CLI
        pass

    def load_config(self):
        """This method is used to load the configuration from one or several input(s).
        Custom Command line, configuration file.

        """
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main():
    run_options = {
        'bind': '%s:%s' % ('127.0.0.1', '8888'),
        'workers': number_of_workers(),
        'proc_name': 'modislock',
        'pidfile': '/tmp/modislock.pid',
        'cert': '/var/www/resources/modislock.local.cert',
        'key': '/var/www/resources/modislock.local.key'
    }

    StandaloneApplication(create_app(), run_options).run()


if __name__ == '__main__':
    main()
