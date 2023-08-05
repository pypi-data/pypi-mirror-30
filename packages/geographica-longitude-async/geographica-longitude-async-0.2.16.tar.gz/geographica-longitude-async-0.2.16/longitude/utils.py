from functools import partial

from longitude.exceptions import InvalidAttribute


def try_or_none(fn, allow=(BaseException)):
    def do_try_fn(value):
        try:
            return fn(value)
        except allow:
            return None

    return do_try_fn


def parse_spec_on_missing_default(key):
    raise InvalidAttribute(key, message='Missing attribute {}.')


def parse_spec_on_value_success_default(key, value):
    yield (key, value)


def parse_spec(
    spec,
    values,
    on_value_success=None,
    on_missing=None
):
    if on_value_success is None:
        on_value_success = parse_spec_on_value_success_default

    if on_missing is None:
        on_missing = parse_spec_on_missing_default

    for conf_param in spec:

        if len(conf_param) not in (2, 3):
            raise RuntimeError('Configuration param %s must have 2 or 3 elements.' % str(conf_param))

        config_param_name, ctype = conf_param[:2]

        if len(conf_param) == 3:
            default = conf_param[2]
        else:
            default = None

        value = values.get(config_param_name, default)

        if value is None:
            on_missing(config_param_name)

        if type == bool:
            value = value if isinstance(value, bool) else \
                value == '1'
        else:
            value = ctype(value)

        if value is None and default is not None:
            value = default

        if value is None:
            on_missing(config_param_name)

        on_value_success(config_param_name, value)


def compile_spec(
    spec,
    on_value_success=None,
    on_missing=None
):
    return partial(
        parse_spec,
        spec,
        on_value_success=on_value_success,
        on_missing=on_missing
    )
