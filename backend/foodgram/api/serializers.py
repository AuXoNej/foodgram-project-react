from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


from users.models import User
from recipes.models import Tag

from .utils import get_confirmation_code, send_confirmation_email

class UserSignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=256, required=True)

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Зарезервированный username. Используйте другой.'
            )

        return username

    def validate(self, data):
        email = data['email']
        username = data['username']
        user = User.objects.filter(Q(username=username) | Q(email=email))

        if user and (user.get().email != email
                     or user.get().username != username):
            raise serializers.ValidationError(
                'Имя пользователя или email не соответствуют.'
            )

        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        email = validated_data.get('email')
        send_confirmation_email(email, get_confirmation_code(user))
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_role(self, role):
        if not self.context['request'].user.is_admin:
            role = self.instance.role

        return role


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__' 