from django.urls import include, path
from rest_framework.routers import SimpleRouter
from django.views.generic import TemplateView

from . import views
app_name = 'api'

router = SimpleRouter()
router.register('users', views.UserViewset)
router.register('tags', views.TagViewset)
router.register('products', views.ProductViewset)
router.register('ingridients', views.IngridientViewset)
router.register('recipes', views.RecipeViewset)

urlpatterns = [
    #path('v1/', include('djoser.urls')),
    #path('v1/', include('djoser.urls.jwt')),
    path('v1/users/me/', views.UserMeViewset.as_view({'get': 'retrieve'})),
    path('v1/', include(router.urls)),
]