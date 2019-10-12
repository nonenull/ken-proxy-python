# 日志
import os

LogPath = './logs'
LogConf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(name)s [%(asctime)s] %(levelname)s : %(message)s'
        },
        'verbose': {
            'format': '%(name)s [%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(module)s.%(funcName)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'standard': {
            'format': '%(name)s %(asctime)s [%(levelname)s]- %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': "DEBUG",
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'access': {
            'level': "INFO",
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LogPath, 'access.log'),
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
