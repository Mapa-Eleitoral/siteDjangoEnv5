"""
URL configuration for siteDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# ====================================
# siteDjango/urls.py (URLs principais do projeto)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('doacoes/', include('doacoes.urls')),
    path('', include('mapa_eleitoral.urls')),
]

# Servir arquivos estáticos em produção (Railway)
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# URLs de segurança para evitar logs de erro
from django.http import HttpResponse, HttpResponseNotFound

def security_txt(request):
    return HttpResponseNotFound("Security endpoint disabled")

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /telescope/",
        "Disallow: /info.php",
        "Allow: /",
        "",
        f"Sitemap: https://{request.get_host()}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

# Adicionar URLs de segurança
urlpatterns += [
    path('robots.txt', robots_txt),
    path('telescope/requests', security_txt),
    path('info.php', security_txt),
]
