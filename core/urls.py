from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),  # URL do Admin
    path('', RedirectView.as_view(url='/admin/', permanent=True)),  # Redireciona a raiz para /admin/
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
