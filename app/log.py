from datetime import datetime

class Log():
    I = 'INFO'
    E = 'ERROR'
    D = 'DEBUG'
    W = 'WARN'
    V = 'VERBOSE'

    @staticmethod
    def L(level: str, msg: str, *args: any):
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "[{}]".format(level), msg.format(*args))
