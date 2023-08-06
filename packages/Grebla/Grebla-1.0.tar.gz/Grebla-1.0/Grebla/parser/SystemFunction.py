class Functions(object):

    def select(self, path):
        pass

    def go(self, url):
        pass

    def set_input(self, path, value):
        pass

    def submit(self, path=None):
        pass

    def print(self, msg):
        pass

    @staticmethod
    def list_functions():
        return [
            "select", "go", "set_input", "submit", "print", "base_url"
        ]