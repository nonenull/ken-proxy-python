import globalConfig

# 本地proxy监听
Host = '127.0.0.1'
Port = 1081

# 远程代理服务器
ServerHost = '127.0.0.1'
ServerPort = 8887
ServerUser = 'fucker'
ServerPassword = '123456'

# 日志
LogConf = globalConfig.LogConf
LogConf['loggers']['local'] = {
    'handlers': ['console', 'access'],
    'level': 'DEBUG',
    'propagate': False,
}
