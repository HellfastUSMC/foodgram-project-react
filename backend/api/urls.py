from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views
app_name = 'api'

router = SimpleRouter()
router.register('users', views.UserViewset)
router.register('tags', views.TagViewset)

urlpatterns = [
    path('v1/', include(router.urls)),
]