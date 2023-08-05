# -*- encoding: utf-8 -*-
from modislock_webservice import create_app
from celery import Celery

celery_worker = None


def make_celery(app):
    """Creates a Celery Instance

    :param app:
    :return:
    """
    global celery_worker

    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    celery_worker = celery
    return celery


def main():
    app = create_app()
    celery = make_celery(app)

    log_level = 'INFO' if app.config.get('DEBUG') is False else 'DEBUG'

    app.logger.info('Celery worker staring with the following params:\nBroker {}\nBackend {}\nDebug {}'
                    .format(app.config['CELERY_BROKER_URL'],
                            app.config['CELERY_RESULT_BACKEND'],
                            app.config['DEBUG']))

    argv = [
        'worker',
        '--loglevel=' + log_level,
        '--purge'
    ]
    celery.worker_main(argv)


if __name__ == '__main__':
    main()
