from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    #CategoryViewSet,
    #CommentViewSet,
    #GenreViewSet,
    #ReviewViewSet,
    SignUpViewSet,
    #TitleViewSet,
    TagViewSet,
    TokenObtainView,
    UserViewSet
)


app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('auth/signup', SignUpViewSet, basename='signup')
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')

"""

router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment',
)
"""

urlpatterns = [
    path('', include(router_v1.urls), name='api_v1'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
]