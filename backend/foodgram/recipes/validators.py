from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

validate_color = RegexValidator(
    r'^#([0-9a-fA-F]{3,6})$',
    'Не валидный hex-код'
)


def validate_name(value):
    alphabet_small = ('abcdefghijklmnopqrstuvwxyz'
                      'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    alphabet_big = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')

    for letter_index in len(value):
        if not (value[letter_index] in alphabet_small
                or value[letter_index] in alphabet_big):
            raise ValidationError(
                'Поле должно содержать только буквы.'
            )

        if letter_index == 0:
            if not value[letter_index] in alphabet_big:
                raise ValidationError(
                    'Поле должно начинаться с заглавной буквы.'
                )
        else:
            if not value[letter_index] in alphabet_small:
                raise ValidationError(
                    'Заглавной может быть только первая буква.'
                )
