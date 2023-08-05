import zope.event.classhandler
import inject
import applauncher.kernel
from applauncher.kernel import InjectorReadyEvent
from fluent import handler
import json


class FluentBundle(object):
    def __init__(self):
        self.log_handlers = []
        self.config_mapping = {
            "fluent": {
                "host": "localhost",
                "port": 24224,
                "tag": "app",
                "format": "{ " +
                        "'host': '%(hostname)s'," +
                        "'where': '%(module)s.%(funcName)s'," +
                        "'type': '%(levelname)s'," +
                        "'stack_trace': '%(exc_text)s'" +
                        "}"
            }
        }

        zope.event.classhandler.handler(InjectorReadyEvent, self.configure_logger)

    def configure_logger(self, event):
        config = inject.instance(applauncher.kernel.Configuration)
        logger_config = config.fluent
        h = handler.FluentHandler(logger_config.tag, host=logger_config.host, port=logger_config.port)
        formatter = handler.FluentRecordFormatter(json.loads(logger_config.format.replace("'", '"')))
        h.setFormatter(formatter)
        self.log_handlers.append(h)

