from Grebla.parser.greblascruct import GreblaStruct
from Grebla.parser.BaseFunctions import Go, SetInput, Print
from Grebla.parser.BaseFunctions.base_url import BaseUrl


class Kernel(object):
    GreblaStructargs = GreblaStruct()

    def base_url(self, *args):
        BaseUrl(self.GreblaStructargs, args)

    def go(self, *args):
        Go(self.GreblaStructargs, args)

    def set_input(self, *args):
        SetInput(self.GreblaStructargs, args)

    def print(self, *args):
        Print(self.GreblaStructargs, args)