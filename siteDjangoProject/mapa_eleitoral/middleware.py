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
        
        # Headers de otimização
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log apenas requests realmente lentos
        if duration > 3.0:
            logging.warning(
                f"Request muito lento: {request.method} {request.path} - "
                f"{duration:.2f}s - User: {getattr(request.user, 'username', 'anonymous')}"
            )
        
        # Headers de performance otimizados
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        # Headers de performance seguros
        if not request.path.startswith('/admin/'):
            response['Vary'] = 'Accept-Encoding'
            
        # Cache headers conservadores e seguros
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=86400'  # 24h seguro
        elif request.path == '/':
            response['Cache-Control'] = 'public, max-age=300'  # 5 minutos
        elif request.path.startswith('/get_') and request.path.endswith('_ajax/'):
            response['Cache-Control'] = 'public, max-age=600'  # 10 minutos
        elif request.path == '/generate-map/':
            response['Cache-Control'] = 'private, max-age=1800'  # 30min privado
        
        return response