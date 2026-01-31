# mapa_eleitoral/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogArticle


class StaticViewSitemap(Sitemap):
    """Sitemap para páginas estáticas do site"""
    priority = 0.8
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['mapa_eleitoral:home', 'mapa_eleitoral:projeto', 'mapa_eleitoral:blog', 'mapa_eleitoral:apoio']

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    """Sitemap para artigos do blog"""
    changefreq = "weekly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return BlogArticle.objects.filter(is_active=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('mapa_eleitoral:blog_post', kwargs={'slug': obj.slug})
