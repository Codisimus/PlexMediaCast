from flask import request


class MissingParamError(Exception):
    def __init__(self, name):
        self.name = name


class InvalidTokenError(Exception):
    pass


class NotFoundError(Exception):
    def __init__(self, name):
        self.name = name


class UnimplementedError(Exception):
    pass


class Object(object):
    pass


def get_attr(item, attr):
    return item[attr] if isinstance(item, dict) else getattr(item, attr)


def find_by_attr(items, attr, value, case_sensitive=True):
    if not case_sensitive:
        value = value.casefold()
    for item in items:
        item_value = get_attr(item, attr)
        if not case_sensitive:
            item_value = item_value.casefold()
        if item_value == value:
            return item
    return None


def has_param(name):
    return request.args.get(name) is not None


def get_param(*args, required=False, split=False, boolean=False, integer=False, default=None):
    for name in args:
        if has_param(name):
            value = request.args.get(name)
            if name == 'title':
                value = value.replace(' \' ', '\'')  # IFTTT fix
            convert = str2bool if boolean else int if integer else str
            return [convert(i) for i in value.split(',')] if split else convert(value)
    if required:
        raise MissingParamError('[' + ', '.join(args) + ']')
    else:
        return default


def as_specified(requested, actual):
    return not requested or requested.casefold() == actual.casefold()


def str2bool(value):
    return value.lower() in ("yes", "true", "t", "1")


def millis2minutes(value):
    return round(value / (1000 * 60))


def millis2minutesseconds(value):
    total_seconds = round(value / 1000)
    minutes, seconds = divmod(total_seconds, 60)
    return str(minutes) + ':' + str(seconds)
