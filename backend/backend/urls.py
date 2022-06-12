from django.conf import settings  # temp for dev server
from django.conf.urls.static import static  # temp for dev server
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # temp for dev server
