from django.core.validators import RegexValidator

validate_color = RegexValidator(
    r'^#([0-9a-fA-F]{3,6})$',
    'Не валидный hex-код'
)

validate_name = RegexValidator(
    r'^[A-Za-zА-Яа-я]{1,}$',
    'Поле может содержать только буквы.'
)
