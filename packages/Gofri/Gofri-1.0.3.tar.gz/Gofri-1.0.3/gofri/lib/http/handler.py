class RequestHandler(object):
    def __init__(self, headers="", json="", params=""):
        self.path = None
        self.headers = [param.strip() for param in headers.split(";")]
        self.json = [param.strip() for param in json.split(";")]
        self.params = [param.strip() for param in params.split(";")]
