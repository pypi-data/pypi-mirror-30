from functools import partial
from .exceptions import ValidationError


def validate_max_length(maxl, x):
    if len(x) > maxl:
        raise ValidationError('length cannot be higher than {}'.format(maxl))


def validate_not_blank(x):
    if not x:
        raise ValidationError('cannot be empty')


def validate_choices_in(choices, x):
    if choices and x not in choices:
        raise ValidationError('value {} not in available choices'.format(x))


max_length = lambda maxl: partial(validate_max_length, maxl)
not_blank = validate_not_blank
choices_in = lambda choices: partial(validate_choices_in, choices)


def combine_validations(*validators):
    def combined_validator(x):
        valid = True

        for validate in validators:
            ret = validate(x)
            valid = valid and (ret is None or ret)

        return valid

    return combined_validator
