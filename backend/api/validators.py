import re

from django.core.validators import RegexValidator
from rest_framework.validators import ValidationError


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            '"me" в качестве логина использовать нельзя!'
        )
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'Введены некорректные символы!'
        )
    return value


color_validator = RegexValidator(
    regex='^#[A-Fa-f0-9]{6}$',
    message='Цветовой код должен быть в формате HEX (например, #FFFFFF).'
)
