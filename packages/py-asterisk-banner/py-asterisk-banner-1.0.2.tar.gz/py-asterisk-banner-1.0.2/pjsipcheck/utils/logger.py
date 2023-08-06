from pjsipcheck import settings

import logging


class Logger:
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self):
        self.log = logging.getLogger(settings.LOGGER_NAME)

    def setup(self, logfile, loglevel):
        logformat = '[%(asctime)s] - %(levelname)s - %(message)s'

        # create a file handler
        handler = logging.FileHandler(logfile)
        handler.setLevel(level=self.levels[loglevel])

        # create a logging format
        formatter = logging.Formatter(logformat)
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        logging.basicConfig(level=self.levels[loglevel])

        self.log.info("Archivo de log creado en la ruta: %s" % logfile)

        return self.log
