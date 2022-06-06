from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
#from rest_framework.authtoken.views import obtain_auth_token
# from django.views.generic import TemplateView

from . import views
app_name = 'api'

router = SimpleRouter()
router.register('users', views.UserViewset)
router.register('tags', views.TagViewset, basename='Tag')
router.register('products', views.ProductViewset)
router.register('ingridients', views.IngridientViewset)
router.register('recipes', views.RecipeViewset, basename='Recipe')

urlpatterns = [
    #path('', include('djoser.urls')),
    #path('', include('djoser.urls.jwt')),
    #path('auth/token/login/', obtain_auth_token, name='api_get_token'),
    path(
        'recipes/<int:recipe_id>/favorite/',
        views.AddToFavoriteView.as_view(),
        name='recipe_add_2_fav'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        views.AddToShoppingCartView.as_view({'post': 'post', 'delete': 'delete'}),
        name='recipe_add_2_fav'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        views.SubscribeView.as_view(),
        name='subscribition'
    ),
    path('auth/token/login/', TokenObtainPairView.as_view(), name='token_login'),
    path('auth/token/logout/', views.TokenLogout.as_view(), name='token_logout'),
    #path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/me/', views.UserMeViewset.as_view({'get': 'retrieve'})),
    path(
        'users/set_password/',
        views.UserSetPasswordViewset.as_view(),
        name='set_password'
    ),
    path('', include(router.urls)),
]