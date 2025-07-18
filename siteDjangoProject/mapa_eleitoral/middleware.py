"""
Performance monitoring middleware for electoral map application
"""
import time
import logging


class OptimizedPerformanceMiddleware:
    """Middleware otimizado para monitoramento de performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Headers de otimização pré-request
        if request.path.startswith('/static/'):
            # Otimização para arquivos estáticos
            pass
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log apenas requests realmente lentos
        if duration > 2.0:  # Reduzido para 2s
            logging.warning(
                f"Request lento: {request.method} {request.path} - "
                f"{duration:.2f}s - User: {getattr(request.user, 'username', 'anonymous')}"
            )
        
        # Headers de performance otimizados
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        # Headers de compressão
        if not request.path.startswith('/admin/'):
            response['Vary'] = 'Accept-Encoding'
            
        # Cache headers otimizados
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=2592000'  # 30 dias
            response['Expires'] = 'Thu, 31 Dec 2024 23:59:59 GMT'
        elif request.path == '/':
            response['Cache-Control'] = 'public, max-age=600'  # 10 minutos
        elif request.path.startswith('/get_') and request.path.endswith('_ajax/'):
            response['Cache-Control'] = 'public, max-age=1800'  # 30 minutos
        elif request.path == '/generate-map/':
            response['Cache-Control'] = 'private, max-age=3600'  # 1 hora
        elif request.path.startswith('/blog/'):
            response['Cache-Control'] = 'public, max-age=3600'  # 1 hora para blog
        
        # Headers de performance adicionais
        if hasattr(response, 'content') and len(response.content) > 1000:
            response['Content-Encoding'] = 'gzip'
        
        return response