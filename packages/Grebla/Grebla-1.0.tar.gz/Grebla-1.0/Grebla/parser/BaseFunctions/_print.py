from Grebla.parser.Exeptions import *


class Print(object):
    args = None
    text = ""

    def __init__(self, grebla_struct, *args):
        self.grebla_struct = grebla_struct
        self.args = args
        self.__check()
        self.grebla_struct.run_list.append({

                "func": "print",
                "text": self.text,
            })

    def __check(self):
        if isinstance(self.args, tuple):
            args = self.args[0][0]
            self.text = args

        else:
            raise GreblaParserGo("Не правильная структура функции print")


