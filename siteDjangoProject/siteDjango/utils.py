"""
Utilitários para otimização de performance
"""

def add_headers(headers, path, url):
    """
    Adiciona headers customizados para arquivos estáticos
    Otimizado para PageSpeed Insights
    """
    # Headers de cache agressivo para arquivos com hash
    if any(x in path for x in ['.min.', '.hash.', '-']):
        headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    
    # Headers específicos por tipo de arquivo
    if path.endswith(('.css', '.js')):
        headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        headers['Content-Encoding'] = 'gzip'
    elif path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
        headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        headers['Content-Type'] = f'image/{path.split(".")[-1]}'
    elif path.endswith('.woff2'):
        headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        headers['Content-Type'] = 'font/woff2'
    
    # Headers de performance
    headers['X-Content-Type-Options'] = 'nosniff'
    headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return headers