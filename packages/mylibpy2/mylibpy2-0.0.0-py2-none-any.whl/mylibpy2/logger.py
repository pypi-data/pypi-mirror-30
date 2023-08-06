#-*- coding: utf-8 -*-
import logging as _logging
import logging.handlers as _handlers
import os.path as _path
import datetime as _dt
import threading as _threading
import sys as _sys

class _MyFormatter(_logging.Formatter):
    converter = _dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime('%Y-%m-%d %H:%M:%S')
            s = '%s.%03d' % (t, record.msecs)
        return s


class Logger(object):
    def __init__(self, configs=None):
        self._logger = _logging.getLogger()
        if configs is None or type(configs) != list or len(configs) == 0:
            self._setConfigs([Logger.getDefaultConfig()])
        else:
            self._setConfigs(configs)
    
    @staticmethod
    def getDefaultConfig():
        return { 'type': 'stdout', 'level': 'debug', 'path': '', 'filename': '', 'size': 0 }
    
    def _setConfigs(self, configs=[]):
        self._logger.setLevel('DEBUG')
        del self._logger.handlers[:]

        for config in configs:
            if 'type' not in config:
                config['type'] = 'stdout'
            if 'level' not in config:
                config['level'] = 'debug'

            if config['type'] == 'file':
                handler = _handlers.RotatingFileHandler(_path.join(config['path'], config['filename']), maxBytes=config['size'], backupCount=99, encoding='utf-8')
            else:
                handler = _logging.StreamHandler(_sys.stdout)

            handler.setLevel(config['level'].upper())
            handler.setFormatter(_MyFormatter('%(asctime)s [%(levelname)s]%(message)s'))
            self._logger.addHandler(handler)
    
    def debug(self, *args, **kwargs):
        newArgs = list(args)
        newArgs[0] = '[%s] %s' % (_threading.current_thread().getName(), args[0])
        newArgs = tuple(newArgs)
        self._logger.debug(*newArgs, **kwargs)

    def info(self, *args, **kwargs):
        newArgs = list(args)
        newArgs[0] = '[%s] %s' % (_threading.current_thread().getName(), args[0])
        newArgs = tuple(newArgs)
        self._logger.info(*newArgs, **kwargs)

    def warn(self, *args, **kwargs):
        newArgs = list(args)
        newArgs[0] = '[%s] %s' % (_threading.current_thread().getName(), args[0])
        newArgs = tuple(newArgs)
        self._logger.warn(*newArgs, **kwargs)

    def error(self, *args, **kwargs):
        newArgs = list(args)
        newArgs[0] = '[%s] %s' % (_threading.current_thread().getName(), args[0])
        newArgs = tuple(newArgs)
        self._logger.error(*newArgs, **kwargs)

    def critical(self, *args, **kwargs):
        newArgs = list(args)
        newArgs[0] = '[%s] %s' % (_threading.current_thread().getName(), args[0])
        newArgs = tuple(newArgs)
        self._logger.critical(*newArgs, **kwargs)

if __name__ == '__main__':
    pass