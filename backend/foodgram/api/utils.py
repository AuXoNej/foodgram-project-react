from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator


def get_confirmation_code(user) -> str:
    return default_token_generator.make_token(user)


def check_password(user, password) -> bool:
    return password == user.password


def send_confirmation_email(email: str, confirmation_code: str) -> None:
    send_mail(
        subject='Код подтверждения на сервисе YamDB',
        message=(f'Вы зарегистрировались на сервисе YamDB.\n'
                 f'Код подтверждения: {confirmation_code}'),
        from_email=settings.FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
