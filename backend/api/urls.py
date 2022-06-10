from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

app_name = 'api'

router = SimpleRouter()
router.register('users', views.UserViewset, basename='users')
router.register('tags', views.TagViewset, basename='tags')
router.register('ingredients', views.ProductViewset, basename='ingredients')
router.register('recipes', views.RecipeViewset, basename='recipes')

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        views.AddToFavoriteView.as_view(),
        name='recipe_add_2_fav'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        views.AddToShoppingCartView.as_view(
            {'post': 'post', 'delete': 'delete'}
        ),
        name='recipe_add_2_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        views.ExportShoppingCart.as_view({'get': 'get'}),
        name='export_cart'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        views.SubscribeView.as_view({'post': 'post', 'delete': 'delete'}),
        name='un-subscribe'
    ),
    path(
        'users/subscriptions/',
        views.SubscribeListView.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path(
        'auth/token/login/',
        TokenObtainPairView.as_view(),
        name='token_login'
    ),
    path(
        'auth/token/logout/',
        views.TokenLogout.as_view(),
        name='token_logout'
    ),
    path('users/me/', views.UserViewset.as_view({'get': 'retrieve'})),
    path(
        'users/set_password/',
        views.UserSetPasswordViewset.as_view(),
        name='set_password'
    ),
    path('', include(router.urls)),
]
