from gofri.lib.http.filter import Filter
from gofri.lib.decorate.tools import _wrap_http
from gofri.lib.http.filter import FILTERS
from gofri.lib.http.handler import RequestHandler


class GofriFilter:
    def __init__(self, urls=[], filter_all=False, order=0):
        self.urls = urls
        self.filter_all = filter_all
        self.order = order

    def __call__(self, cls):
        if not Filter in cls.__bases__:
            cls._continue = Filter._continue
        filter_obj = cls()
        filter_obj.urls = self.urls
        filter_obj.filter_all = self.filter_all
        filter_obj.order = self.order
        FILTERS.append(filter_obj)

class GET(RequestHandler):
    def __init__(self, path, headers="", json="", params=""):
        super().__init__(headers, json, params)
        self.path = path


    def __call__(self, func):
        return _wrap_http(self.path, ["GET"], func, self)


class POST(RequestHandler):
    def __init__(self, path, headers="", body="", json="", params=""):
        super().__init__(headers, json, params)
        self.path = path
        self.body = [param.strip() for param in body.split(";")]

    def __call__(self, func):
        return _wrap_http(self.path, ["POST"], func, self)


class HEAD(RequestHandler):
    def __init__(self, path, headers="", body="", json="", params=""):
        super().__init__(headers, json, params)
        self.path = path
        self.body = [param.strip() for param in body.split(";")]

    def __call__(self, func):
        return _wrap_http(self.path, ["HEAD"], func, self)


class PUT(RequestHandler):
    def __init__(self, path, headers="", body="", json="", params=""):
        super().__init__(headers, json, params)
        self.path = path
        self.body = [param.strip() for param in body.split(";")]

    def __call__(self, func):
        return _wrap_http(self.path, ["PUT"], func, self)


class DELETE(RequestHandler):
    def __init__(self, path, headers="", body="", json="", params=""):
        super().__init__(headers, json, params)
        self.path = path
        self.body = [param.strip() for param in body.split(";")]

    def __call__(self, func):
        return _wrap_http(self.path, ["DELETE"], func, self)
