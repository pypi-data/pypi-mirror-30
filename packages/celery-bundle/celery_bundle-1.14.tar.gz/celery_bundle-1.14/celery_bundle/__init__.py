import zope.event
import applauncher.kernel
import inject
from applauncher.kernel import Kernel
from celery import Celery, signals

@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass

class CeleryBundle(object):
    def __init__(self):
        self.config_mapping = {
            "celery": {
                "broker": 'pyamqp://guest@localhost//',
                "result_backend": "",
                "debug": False,
                "worker": True
                #"task_serializer": "json",
                #"accept_content": ['json']
            }
        }

        zope.event.subscribers.append(self.event_listener)
        self.app = Celery()
        self.app.log.setup()
        self.injection_bindings = {
             Celery: self.app
        }

    @inject.params(config=applauncher.kernel.Configuration)
    def start_sever(self, config):
        print("DENTRO")
        # Register mappings
        kernel = inject.instance(Kernel)
        for bundle in kernel.bundles:
            if hasattr(bundle, "register_tasks"):
                getattr(bundle, "register_tasks")()

        self.app.conf.update(
            broker_url=config.celery.broker,
            result_backend=config.celery.result_backend,
            task_track_started=True,
            result_expires=3600, # 1 hour
            task_serializer='json',
            accept_content=['json'],  # Ignore other content
            result_serializer='json',
            timezone='Europe/Madrid',
            enable_utc=True,
            task_acks_late=True
        )

        if config.celery.worker:
            argv = [
                'worker',
            ]
            if config.celery.debug:
                argv.append('--loglevel=DEBUG')

            self.app.worker_main(argv)

    @inject.params(kernel=Kernel)
    def event_listener(self, event, kernel):
        if isinstance(event, applauncher.kernel.KernelReadyEvent):
            config = inject.instance(applauncher.kernel.Configuration).celery
            if config.worker:
                kernel.run_service(self.start_sever)
            else:
                self.start_sever()
        elif isinstance(event, applauncher.kernel.KernelShutdownEvent):
            self.app.control.shutdown()

