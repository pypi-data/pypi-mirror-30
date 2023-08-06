import validators as validators
from Grebla.parser.Exeptions import GreblaParserBaseUrlInvalid


class BaseUrl(object):

    def __init__(self, grebla_struct, *args):
        self.grebla_struct = grebla_struct
        self.grebla_struct.base_url = self.__check_set_url(args)

    def __check_set_url(self, arg):
        if isinstance(arg, str):
            if self._check_an_valid_url(arg):
                return arg
        elif isinstance(arg, tuple):
            url = arg[0][0]
            if isinstance(url, str):
                if self._check_an_valid_url(url):
                    return url
                else:
                    raise GreblaParserBaseUrlInvalid("Не валидный base_url")
            else:
                raise GreblaParserBaseUrlInvalid("Не валидный base_url - запишите значение base_url только строку")

    @staticmethod
    def _check_an_valid_url(url_):
        return validators.url(url_)
