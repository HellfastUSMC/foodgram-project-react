from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views
app_name = 'api'

router = SimpleRouter()
router.register('users', views.UserViewset)
router.register('tags', views.TagViewset)
router.register('units', views.UnitViewset)
router.register('products', views.ProductViewset)
router.register('ingridients', views.IngridientViewset)
router.register('recipes', views.RecipeViewset)

urlpatterns = [
    path('v1/', include(router.urls)),
]