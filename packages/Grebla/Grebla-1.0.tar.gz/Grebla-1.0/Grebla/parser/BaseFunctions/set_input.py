from Grebla.parser import BaseGreblaParserExeption


class SetInput(object):
    args = None
    xpath = ""
    value = ""

    def __init__(self, grebla_struct, *args):
        self.grebla_struct = grebla_struct
        self.args = args
        self.__check_func()
        self.grebla_struct.run_list.append({
            "func": "set_input",
            "xpath": self.xpath,
            "value": self.value
        })

    def __check_func(self):
        if isinstance(self.args, tuple):
            args = self.args[0][0]
            if "xpath" in args:
                if not isinstance(args["xpath"], str):
                    raise BaseGreblaParserExeption(
                        "Укажите в поле xpath строку с селектором на элемент в функции set_input")
                self.xpath = args['xpath']
            else:
                raise BaseGreblaParserExeption(
                    "Вы не указали xpath строку с селектором на элемент в функции set_input")

            if "value" in args:
                if not isinstance(args["value"], str):
                    raise BaseGreblaParserExeption(
                        "Укажите в поле value строку с селектором на элемент в функции set_input")
                self.xpath = args['value']
            else:
                raise BaseGreblaParserExeption(
                    "Вы не указали value строку с селектором на элемент в функции set_input")

        else:
            raise BaseGreblaParserExeption("Не правильные параметры для функции set_input")
