import re

from django.core.exceptions import ValidationError


def validate_color(value):
    if not re.search(r'^#([0-9a-fA-F]{3,6})$', value):
        raise ValidationError(
            'Не валидный hex-код'
        )
