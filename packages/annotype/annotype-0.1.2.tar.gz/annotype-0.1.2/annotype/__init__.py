from functools import wraps
from inspect import isclass, signature
from marshmallow import (
    Schema,
    ValidationError,
    fields
)


def annotyped(load=False):
    def decorator(func_or_cls):
        if isclass(func_or_cls):
            for attr in func_or_cls.__dict__:
                func = getattr(func_or_cls, attr)
                if callable(func):
                    setattr(func_or_cls, attr, _annotype_func(func, load))
            return func_or_cls
        else:
            return _annotype_func(func_or_cls, load)
    return decorator


def _annotype_func(func, load):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _args = []
        _kwargs = {}
        _errors = {}

        for param in signature(func).parameters.values():
            annon = func.__annotations__.get(param.name)

            if _param_is_positionnal(param):
                try:
                    value = args[len(_args)]
                except IndexError:
                    value = kwargs[param.name]
                finally:
                    value, errors = _parse(value, annon, load)
                    _args.append(value)
                    if errors:
                        _errors[param.name] = errors

            elif _param_is_keyword(param):
                try:
                    value = kwargs[param.name]
                except KeyError:
                    pass
                else:
                    value, errors = _parse(value, annon, load=load)
                    _kwargs[param.name] = value
                    if errors:
                        _errors[param.name] = errors

        if _errors:
            raise TypeError(_errors)

        return func(*_args, **_kwargs)
    return wrapper


def _parse(value, target, load):
    if target is None:
        return value, {}

    if load:
        return _load(value, target)
    return _validate(value, target)


def _load(value, target):
    if isclass(target) and issubclass(target, Schema):
        load = target().load
    elif isinstance(target, fields.Field):
        load = target.deserialize

    try:
        value = load(value) if load else value
    except ValidationError as err:
        errors = err.messages
    else:
        errors = {}

    return value, errors


def _validate(value, target):
    validate = None
    if isclass(target) and issubclass(target, Schema):
        validate = target().validate
    elif isinstance(target, fields.Field):
        validate = target.validate
    else:
        return value, {}

    errors = validate(value) if validate else {}

    return value, errors


def _param_is_positionnal(param):
    return (
        param.kind == param.POSITIONAL_OR_KEYWORD and
        param.default is param.empty
    )


def _param_is_keyword(param):
    return (
        param.kind == param.POSITIONAL_OR_KEYWORD and
        param.default is not param.empty
    ) or param.kind == param.KEYWORD_ONLY
