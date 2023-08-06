import logging
import logging.handlers


class Logger(object):
    @classmethod
    def tcp(cls, name, level=logging.DEBUG, host='localhost'):
        logger=logging.getLogger(name)
        logger.setLevel(level)
        handler = logging.handlers.SocketHandler(host, logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(handler)
        return logger

    @classmethod
    def null(cls):
        logger=logging.getLogger()
        logger.setLevel(logging.ERROR)
        handler=logging.NullHandler()
        logger.addHandler(handler)
        return logger


if __name__ == "__main__":
    pass
