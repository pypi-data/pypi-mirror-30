from Grebla.parser import SystemFunction
from Grebla.parser.Exeptions import BaseGreblaParserExeption
from Grebla.parser.Kernel import Kernel


class Dump(object):
    yaml = None
    dom = {"main": []}
    debug = True

    def __init__(self, yaml_file):
        self.yaml = yaml_file
        self.check_set_debug_mode()
        self.check_syntax()

    def check_set_debug_mode(self):
        if "debug" in self.yaml:
            debug = self.yaml['debug']
            if isinstance(debug, bool):
                Dump.debug = self.yaml['debug']
            elif isinstance(debug, int):
                if debug == 1:
                    Dump.debug = True
                elif debug == 0:
                    Dump.debug = False
                else:
                    raise BaseGreblaParserExeption("Не допустимая значение для поля debug поставте 0, 1 или воще уберите")
            else:
                raise BaseGreblaParserExeption("Не допустимая значение для поля debug поставте 0, 1 или воще уберите")

        else:
            Dump.debug = False

    def check_syntax(self):
        run_functions = self.yaml['run']
        for func_dict in run_functions:
            for func_name, func_args in func_dict.items():
                self.call_func(func_name, func_args)
                break

    @staticmethod
    def call_func(func_name, func_arg):
        if func_name in SystemFunction.Functions.list_functions():
            getattr(Kernel(), func_name)(func_arg)



