from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

validate_color = RegexValidator(
    r'^#([0-9a-fA-F]{3,6})$',
    'Не валидный hex-код'
)


def validate_name(value):
    name = str(value)
    alphabet_small = ('abcdefghijklmnopqrstuvwxyz'
                      'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    alphabet_big = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')

    for letter_index in len(name):
        if not (name[letter_index] in alphabet_small
                or name[letter_index] in alphabet_big):
            raise ValidationError(
                'Поле может содержать только буквы.'
            )

        if letter_index == 0:
            if not name[letter_index] in alphabet_big:
                raise ValidationError(
                    'В начале должна быть заглавная буква'
                )
        else:
            if not name[letter_index] in alphabet_small:
                raise ValidationError(
                    'Заглавной может быть только первая буква.'
                )
