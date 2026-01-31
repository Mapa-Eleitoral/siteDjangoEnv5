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
from django.contrib.sitemaps.views import sitemap
from mapa_eleitoral.sitemaps import StaticViewSitemap, BlogSitemap

# Configuração de sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mapa_eleitoral.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
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
    """Arquivo robots.txt otimizado para SEO"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Allow: /blog/",
        "Allow: /projeto/",
        "Allow: /apoio/",
        "",
        "# Áreas administrativas",
        "Disallow: /admin/",
        "Disallow: /cache-stats/",
        "Disallow: /blog-analytics/",
        "Disallow: /clear-cache/",
        "Disallow: /debug-candidato/",
        "",
        "# APIs (para evitar crawling desnecessário)",
        "Disallow: /get_candidatos_ajax/",
        "Disallow: /get_partidos_ajax/",
        "Disallow: /get_anos_ajax/",
        "Disallow: /get_filter_data_ajax/",
        "Disallow: /generate-map/",
        "Disallow: /get_zonas_secoes_ajax/",
        "Disallow: /get_votos_zona_secao_ajax/",
        "",
        "# Endpoints de segurança",
        "Disallow: /telescope/",
        "Disallow: /info.php",
        "",
        "# Sitemaps",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
        f"Sitemap: https://{request.get_host()}/rss.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

# Adicionar URLs de segurança
urlpatterns += [
    path('robots.txt', robots_txt),
    path('telescope/requests', security_txt),
    path('info.php', security_txt),
]
