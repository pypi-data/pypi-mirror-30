# coding: utf-8

from jsonpath_ng.ext import parse


class NotFoundError(Exception):
    pass


def search(path, data, unique=False, raise_not_found=False):
    expr = parse(path)
    resp = expr.find(data)

    if not resp:
        if raise_not_found:
            raise NotFoundError("Can't find by path: {}".format(path))
        else:
            return None
    if unique:
        return resp[0].value
    else:
        return [match.value for match in resp]


search.NotFoundError = NotFoundError
