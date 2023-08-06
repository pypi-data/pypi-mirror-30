class BaseGreblaParserExeption(BaseException):
    msg = "error"

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


class GreblaParserFunctionAlready(BaseGreblaParserExeption):
    pass


class GreblaParserFunctionNameHaveSystem(BaseGreblaParserExeption):
    pass


class GreblaParserParserBaseExeptions(BaseGreblaParserExeption):
    pass


class GreblaParserBaseUrlInvalid(BaseGreblaParserExeption):
    pass


class GreblaParserGoTimeout(BaseGreblaParserExeption):
    pass


class GreblaParserGo(BaseGreblaParserExeption):
    pass


class GreblaParserGoNotSetUrl(BaseGreblaParserExeption):
    pass


class GreblaParserBaseUrlInvalid(BaseGreblaParserExeption):
    pass
