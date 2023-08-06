# coding: utf-8

from jsonpath_ng.ext import parse


class NotFoundError(Exception):
    pass


def search(path, data, default=None, smart_unique=True, raise_not_found=False):
    """
    when not found:
    if raise_not_found is true, raise NotFoundError, else return default value.
    """
    expr = parse(path)
    resp = expr.find(data)

    if not resp:
        if raise_not_found:
            raise NotFoundError("Can't find by path: {}".format(path))
        else:
            return default

    if len(resp) == 1 and smart_unique:
        return resp[0].value
    else:
        return [match.value for match in resp]


search.NotFoundError = NotFoundError
