from Grebla.parser.greblascruct import GreblaStruct
from Grebla.parser.Exeptions import *


class Go(object):
    args = None
    url = None
    urls = None
    timeout = 1

    def __init__(self, grebla_struct, *args):
        self.grebla_struct = grebla_struct
        self.args = args
        self.__check_go()
        self.grebla_struct.run_list.append({

                "func": "go",
                "timeout": self.timeout,
                "urls": self.urls or self.url
            })

    def __check_go(self):
        if isinstance(self.args, tuple):
            args = self.args[0][0]

            if "timeout" in args:
                self._set_timeout(args['timeout'])
            else:
                self._set_timeout(1)
            if "url" in args:
                self.url = args['url']
            elif isinstance(args, list):
                self.urls = args
            elif isinstance(args, str):
                self.urls = args

        else:
            raise GreblaParserGo("Не правильная структура функции go")

    def _set_timeout(self, timeout):
        if not isinstance(timeout, int) or isinstance(timeout, float):
            raise GreblaParserGoTimeout("Укажите в параметре функции go timeout чилсо")

        self.timeout = timeout

