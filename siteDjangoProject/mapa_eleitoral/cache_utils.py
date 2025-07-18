"""
Utilitários avançados de cache para o sistema eleitoral
"""
import hashlib
import json
import logging
from functools import wraps
from django.core.cache import caches
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador avançado de cache com múltiplas camadas"""
    
    def __init__(self):
        self.electoral_cache = caches['electoral_data']
        self.maps_cache = caches['maps']
        self.api_cache = caches['api']
        self.blog_cache = caches['blog']
        self.default_cache = caches['default']
    
    def get_cache_by_type(self, cache_type):
        """Retorna cache específico por tipo"""
        cache_mapping = {
            'electoral': self.electoral_cache,
            'maps': self.maps_cache,
            'api': self.api_cache,
            'blog': self.blog_cache,
            'default': self.default_cache
        }
        return cache_mapping.get(cache_type, self.default_cache)
    
    def safe_key(self, prefix, *args):
        """Gera chave de cache segura e única"""
        data = "_".join(str(arg) for arg in args if arg is not None)
        return f"{prefix}_{hashlib.md5(data.encode()).hexdigest()[:12]}"
    
    def cached_query(self, query_func, cache_key, ttl, cache_type='default', *args, **kwargs):
        """Wrapper genérico para cache de queries com tipo específico"""
        cache_instance = self.get_cache_by_type(cache_type)
        result = cache_instance.get(cache_key)
        
        if result is None:
            result = list(query_func(*args, **kwargs))
            cache_instance.set(cache_key, result, ttl)
            logger.info(f"Cache miss for {cache_key} - loaded {len(result)} items")
        else:
            logger.debug(f"Cache hit for {cache_key}")
        
        return result
    
    def invalidate_pattern(self, pattern, cache_type='default'):
        """Invalida cache por padrão (simulado com prefixo)"""
        cache_instance = self.get_cache_by_type(cache_type)
        # Como LocMemCache não suporta pattern matching, usamos versioning
        cache_instance.clear()
        logger.info(f"Cache cleared for type: {cache_type}")
    
    def warm_up_cache(self):
        """Aquece o cache com dados frequentemente acessados"""
        from .models import DadoEleitoral
        
        logger.info("Iniciando aquecimento do cache...")
        
        # Carregar anos mais recentes
        anos = list(DadoEleitoral.objects.values_list('ano_eleicao', flat=True)
                   .distinct().order_by('-ano_eleicao')[:3])
        
        self.electoral_cache.set('anos_eleicao_v3', anos, 
                               settings.CACHE_TIMES['anos_eleicao'])
        
        # Carregar partidos principais para anos recentes
        partidos_principais = ['PSD', 'PT', 'PSOL', 'PP', 'PL', 'REPUBLICANOS']
        
        for ano in anos:
            partidos = list(DadoEleitoral.objects.filter(ano_eleicao=ano)
                           .values_list('sg_partido', flat=True)
                           .distinct().order_by('sg_partido'))
            
            cache_key = self.safe_key('partidos_v3', ano)
            self.electoral_cache.set(cache_key, partidos, 
                                   settings.CACHE_TIMES['partidos'])
            
            # Carregar candidatos dos partidos principais
            for partido in partidos_principais:
                if partido in partidos:
                    candidatos = list(DadoEleitoral.objects
                                     .filter(ano_eleicao=ano, sg_partido=partido)
                                     .values_list('nm_urna_candidato', flat=True)
                                     .distinct().order_by('nm_urna_candidato'))
                    
                    cache_key = self.safe_key('candidatos_v3', partido, ano)
                    self.electoral_cache.set(cache_key, candidatos, 
                                           settings.CACHE_TIMES['candidatos'])
        
        logger.info("Aquecimento do cache concluído")
    
    def get_cache_stats(self):
        """Retorna estatísticas do cache"""
        stats = {}
        
        for cache_name in ['default', 'electoral_data', 'maps', 'api', 'blog']:
            cache_instance = caches[cache_name]
            # LocMemCache não tem estatísticas nativas, simulamos
            stats[cache_name] = {
                'backend': str(cache_instance.__class__.__name__),
                'location': getattr(cache_instance, '_cache', {}).get('_location', 'N/A'),
                'max_entries': getattr(cache_instance, '_max_entries', 'N/A'),
                'timeout': getattr(cache_instance, 'default_timeout', 'N/A')
            }
        
        return stats

# Instância global do gerenciador de cache
cache_manager = CacheManager()

def smart_cache(cache_type='default', timeout=3600, vary_on=None):
    """Decorator inteligente para cache com tipo específico"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Aplicar cache_page com cache específico
            cached_view = cache_page(timeout, cache=cache_type)(view_func)
            
            # Aplicar vary_on se especificado
            if vary_on:
                cached_view = vary_on_headers(*vary_on)(cached_view)
            
            return cached_view(request, *args, **kwargs)
        return wrapper
    return decorator

def cache_response(cache_type='api', timeout=3600, key_prefix=''):
    """Decorator para cache de respostas JSON"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Gerar chave baseada na URL e parâmetros
            cache_key = cache_manager.safe_key(
                f"{key_prefix}_{view_func.__name__}",
                request.get_full_path()
            )
            
            cache_instance = cache_manager.get_cache_by_type(cache_type)
            response_data = cache_instance.get(cache_key)
            
            if response_data is None:
                response = view_func(request, *args, **kwargs)
                
                # Apenas cache respostas JSON bem-sucedidas
                if isinstance(response, JsonResponse) and response.status_code == 200:
                    response_data = json.loads(response.content)
                    cache_instance.set(cache_key, response_data, timeout)
                    logger.debug(f"Cached response for {cache_key}")
                
                return response
            else:
                logger.debug(f"Cache hit for {cache_key}")
                return JsonResponse(response_data)
        
        return wrapper
    return decorator

def invalidate_cache_on_change(cache_types=None, patterns=None):
    """Decorator para invalidar cache quando dados mudam"""
    if cache_types is None:
        cache_types = ['electoral']
    if patterns is None:
        patterns = ['*']
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Invalidar cache após mudanças
            if request.method in ['POST', 'PUT', 'DELETE']:
                for cache_type in cache_types:
                    for pattern in patterns:
                        cache_manager.invalidate_pattern(pattern, cache_type)
                logger.info(f"Cache invalidated for {cache_types} with patterns {patterns}")
            
            return response
        return wrapper
    return decorator

# Funções utilitárias para templates
def get_cached_template_data(template_name, context_data, timeout=86400):
    """Cache de dados para templates"""
    cache_key = cache_manager.safe_key('template', template_name, 
                                      json.dumps(context_data, sort_keys=True))
    
    cached_data = cache_manager.default_cache.get(cache_key)
    
    if cached_data is None:
        # Processar dados do template
        cached_data = context_data  # Processamento específico aqui
        cache_manager.default_cache.set(cache_key, cached_data, timeout)
    
    return cached_data

def preload_critical_data():
    """Pré-carrega dados críticos no cache"""
    logger.info("Iniciando pré-carregamento de dados críticos...")
    
    # Usar o warm_up_cache do cache_manager
    cache_manager.warm_up_cache()
    
    # Pré-carregar dados de blog mais acessados
    from .models import BlogArticle
    
    try:
        popular_articles = BlogArticle.get_most_viewed(limit=10)
        blog_data = [
            {
                'slug': article.slug,
                'title': article.title,
                'views': article.total_views
            }
            for article in popular_articles
        ]
        
        cache_manager.blog_cache.set('popular_articles', blog_data, 
                                   settings.CACHE_TIMES['blog_articles'])
        
        logger.info(f"Pré-carregados {len(blog_data)} artigos populares")
    except Exception as e:
        logger.error(f"Erro ao pré-carregar dados do blog: {e}")
    
    logger.info("Pré-carregamento concluído")