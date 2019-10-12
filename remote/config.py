import globalConfig

Host = '0.0.0.0'
Port = 8887

# 日志
LogConf = globalConfig.LogConf
LogConf['loggers']['remote'] = {
    'handlers': ['console', 'access'],
    'level': 'DEBUG',
    'propagate': False,
}
