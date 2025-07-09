from django.urls import path
from . import views

app_name = 'mapa_eleitoral'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('projeto/', views.projeto_view, name='projeto'),
    path('apoio/', views.apoio_view, name='apoio'),
    path('get_candidatos_ajax/', views.get_candidatos_ajax, name='get_candidatos_ajax'),
    path('get_partidos_ajax/', views.get_partidos_ajax, name='get_partidos_ajax'),
    path('get_anos_ajax/', views.get_anos_ajax, name='get_anos_ajax'),
    path('get_filter_data_ajax/', views.get_filter_data_ajax, name='get_filter_data_ajax'),
    path('clear-cache/', views.clear_cache_view, name='clear_cache'),
    path('cache-stats/', views.cache_stats_view, name='cache_stats'),
    path('healthcheck/', views.healthcheck_view, name='healthcheck'),
    path('debug-candidato/', views.debug_candidato_view, name='debug_candidato'),
    path('generate-map/', views.generate_map_view, name='generate_map'),
]

