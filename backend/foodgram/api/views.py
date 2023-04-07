from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from recipes.models import Tag
from users.models import User

"""
from .filters import TitleFilter
from .mixins import CreateDestroyListViewSet
"""

from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrStaffOrAuthenticatedCreateOrReadOnly,
)


from .serializers import (
    TagSerializer,
    UserSignUpSerializer,
    UserSerializer,
)

from .utils import check_confirmation_code

class SignUpViewSet(CreateModelMixin, GenericViewSet):
    """Вью регистрации пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )


class TokenObtainView(APIView):
    """Вью для получения токена."""

    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        if not confirmation_code:
            return Response(
                {'confirmation_code': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not username:
            return Response(
                {'username': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, username=username)

        if not check_confirmation_code(user, confirmation_code):
            return Response(
                {'confirmation_code': ['Неверный код подтверждения.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'token': str(RefreshToken.for_user(user).access_token)},
            status=status.HTTP_200_OK,
        )


class UserViewSet(ModelViewSet):
    """Вью для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=('get', 'patch', 'put'),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Метод для url: 'me/'."""
        if request.method == 'GET':
            serializer = self.get_serializer(
                instance=request.user,
                partial=True,
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(
            instance=request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid()
        serializer.save()

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TagViewSet(ModelViewSet):#CreateDestroyListViewSet):
    """Вью для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    #pagination_class = LimitOffsetPagination
    #filter_backends = (SearchFilter,)

    search_fields = ('name', )
