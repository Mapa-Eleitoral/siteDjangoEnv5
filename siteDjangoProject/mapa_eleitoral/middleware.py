"""
Middleware para segurança, rate limiting e monitoramento de performance
"""
import time
import logging
from collections import defaultdict
from django.http import HttpResponseForbidden, HttpResponseNotFound

logger = logging.getLogger(__name__)


class BotBlockerMiddleware:
    """
    Middleware que bloqueia requisições de scanners/bots maliciosos.
    Rejeita imediatamente requests para paths suspeitos (.php, wp-admin, etc.)
    sem processar views, economizando CPU e banda.
    """

    # Extensões de arquivo que nunca existirão num projeto Django
    BLOCKED_EXTENSIONS = ('.php', '.asp', '.aspx', '.jsp', '.cgi', '.env')

    # Paths que são alvos comuns de scanners WordPress/CMS
    BLOCKED_PREFIXES = (
        '/wp-', '/wordpress/', '/wp/',
        '/sites/default/', '/uploads/', '/files/',
        '/.trash', '/.git/', '/.svn/',
    )

    # Paths exatos que scanners procuram
    BLOCKED_EXACT = {
        '/wp-login.php', '/wp-admin/', '/wp-content/',
        '/xmlrpc.php', '/admin.php',
    }

    def __init__(self, get_response):
        self.get_response = get_response
        # Contador de IPs bloqueados (em memória, reset com restart)
        self._blocked_count = defaultdict(int)

    def __call__(self, request):
        path = request.path.rstrip('/').lower()
        # Normalizar paths com // duplicado
        while '//' in path:
            path = path.replace('//', '/')

        if self._is_suspicious(path):
            ip = self._get_client_ip(request)
            self._blocked_count[ip] += 1

            # Log apenas a cada 10 tentativas por IP para evitar spam de log
            if self._blocked_count[ip] <= 3 or self._blocked_count[ip] % 50 == 0:
                logger.info(
                    f"Bot bloqueado: {request.method} {request.path} "
                    f"- IP: {ip} (tentativa #{self._blocked_count[ip]})"
                )

            return HttpResponseNotFound(b"", content_type="text/plain")

        return self.get_response(request)

    def _is_suspicious(self, path):
        """Verifica se o path é de um scanner/bot malicioso"""
        # Extensões bloqueadas
        if any(path.endswith(ext) for ext in self.BLOCKED_EXTENSIONS):
            return True

        # Prefixos bloqueados
        if any(path.startswith(prefix) for prefix in self.BLOCKED_PREFIXES):
            return True

        # Paths exatos
        if path in self.BLOCKED_EXACT or f"{path}/" in self.BLOCKED_EXACT:
            return True

        return False

    @staticmethod
    def _get_client_ip(request):
        """Extrai IP real do cliente (considerando proxies como Railway)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class RateLimitMiddleware:
    """
    Rate limiting simples em memória para endpoints AJAX.
    Limita requisições por IP para evitar abuso.
    """

    # Configuração: max requests por janela de tempo (em segundos)
    RATE_LIMITS = {
        '/get_zonas_secoes_ajax/': (10, 60),     # 10 req/min
        '/get_votos_zona_secao_ajax/': (30, 60),  # 30 req/min
        '/get_candidatos_ajax/': (20, 60),         # 20 req/min
        '/get_partidos_ajax/': (20, 60),           # 20 req/min
        '/get_filter_data_ajax/': (20, 60),        # 20 req/min
        '/generate-map/': (10, 60),                # 10 req/min
        '/get_anos_ajax/': (20, 60),               # 20 req/min
    }

    def __init__(self, get_response):
        self.get_response = get_response
        # {ip: {path: [timestamps]}}
        self._requests = defaultdict(lambda: defaultdict(list))

    def __call__(self, request):
        path = request.path

        if path in self.RATE_LIMITS:
            ip = BotBlockerMiddleware._get_client_ip(request)
            max_requests, window = self.RATE_LIMITS[path]

            now = time.time()
            timestamps = self._requests[ip][path]

            # Remover timestamps fora da janela
            self._requests[ip][path] = [
                t for t in timestamps if now - t < window
            ]

            if len(self._requests[ip][path]) >= max_requests:
                logger.warning(
                    f"Rate limit excedido: {ip} em {path} "
                    f"({len(self._requests[ip][path])}/{max_requests} em {window}s)"
                )
                return HttpResponseForbidden(
                    b'{"error": "Too many requests. Please wait."}',
                    content_type="application/json"
                )

            self._requests[ip][path].append(now)

            # Limpeza periódica de IPs antigos (a cada ~1000 requests)
            if sum(len(paths) for paths in self._requests.values()) > 5000:
                self._cleanup(now)

        return self.get_response(request)

    def _cleanup(self, now):
        """Remove entradas expiradas para evitar memory leak"""
        max_window = max(w for _, w in self.RATE_LIMITS.values())
        ips_to_delete = []
        for ip, paths in self._requests.items():
            paths_to_delete = []
            for path, timestamps in paths.items():
                paths[path] = [t for t in timestamps if now - t < max_window]
                if not paths[path]:
                    paths_to_delete.append(path)
            for p in paths_to_delete:
                del paths[p]
            if not paths:
                ips_to_delete.append(ip)
        for ip in ips_to_delete:
            del self._requests[ip]


class OptimizedPerformanceMiddleware:
    """Middleware otimizado para monitoramento de performance"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

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
