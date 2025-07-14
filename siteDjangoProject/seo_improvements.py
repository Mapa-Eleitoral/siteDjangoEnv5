#!/usr/bin/env python3
"""
SEO Improvements for Mapa Eleitoral Blog
Advanced technical SEO implementations
"""

# 1. SITEMAP AUTOMÁTICO
def generate_sitemap():
    """Gerar sitemap.xml dinamicamente"""
    from django.contrib.sitemaps import Sitemap
    from mapa_eleitoral.models import BlogArticle
    
    class BlogSitemap(Sitemap):
        changefreq = "weekly"
        priority = 0.8
        
        def items(self):
            return BlogArticle.objects.filter(is_active=True)
        
        def lastmod(self, obj):
            return obj.updated_at
        
        def location(self, obj):
            return f'/blog/{obj.slug}/'

# 2. BREADCRUMBS STRUCTURE
def add_breadcrumbs():
    """JSON-LD breadcrumbs para navegação"""
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "https://mapaeleitoral.com.br/"
            },
            {
                "@type": "ListItem", 
                "position": 2,
                "name": "Blog",
                "item": "https://mapaeleitoral.com.br/blog/"
            },
            {
                "@type": "ListItem",
                "position": 3, 
                "name": "{{ article.title }}",
                "item": "{{ article.canonical_url }}"
            }
        ]
    }

# 3. CORE WEB VITALS OPTIMIZATION
def optimize_performance():
    """Otimizações para Core Web Vitals"""
    optimizations = {
        'LCP': [
            'Preload critical resources',
            'Optimize images (WebP)',
            'Minify CSS/JS',
            'Use CDN for static files'
        ],
        'FID': [
            'Defer non-critical JavaScript',
            'Code splitting',
            'Remove unused code',
            'Optimize third-party scripts'
        ],
        'CLS': [
            'Set image dimensions',
            'Reserve space for ads',
            'Avoid inserting content',
            'Use transform animations'
        ]
    }

# 4. STRUCTURED DATA EXPANSION
def advanced_schema():
    """Schema mais detalhado para artigos"""
    article_schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",  # Mais específico que Article
        "headline": "{{ article.title }}",
        "image": "{{ article.featured_image|default:'default.jpg' }}",
        "datePublished": "{{ article.date|date:'c' }}",
        "dateModified": "{{ article.updated_at|date:'c' }}",
        "author": {
            "@type": "Person",
            "name": "Filipe Dias",
            "url": "https://github.com/diasfilipe",
            "sameAs": [
                "https://linkedin.com/in/diasfilipe",
                "https://twitter.com/diasfilipe"
            ]
        },
        "publisher": {
            "@type": "Organization",
            "name": "Mapa Eleitoral",
            "logo": {
                "@type": "ImageObject",
                "url": "https://mapaeleitoral.com.br/static/logo.png"
            }
        },
        "mainEntityOfPage": "{{ article.canonical_url }}",
        "articleSection": "Political Analysis",
        "keywords": "{{ article.keywords }}",
        "wordCount": "{{ article.word_count }}",
        "timeRequired": "PT{{ article.reading_time }}M"
    }

# 5. INTERNAL LINKING ALGORITHM
def smart_internal_linking():
    """Algoritmo para sugerir links internos automaticamente"""
    def suggest_related_articles(current_article):
        # Buscar artigos relacionados por:
        # 1. Keywords em comum
        # 2. Categoria similar  
        # 3. Mesmo período temporal
        # 4. Mesmo localização geográfica
        
        related = BlogArticle.objects.filter(
            keywords__icontains=current_article.primary_keyword,
            is_active=True
        ).exclude(
            id=current_article.id
        )[:5]
        
        return related

# 6. FAQ SCHEMA AUTOMATION
def generate_faq_schema(article_content):
    """Extrair perguntas do conteúdo e gerar FAQ schema"""
    import re
    
    # Buscar padrões de pergunta no markdown
    questions = re.findall(r'### (.+\?)', article_content)
    
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    
    for question in questions:
        faq_schema["mainEntity"].append({
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "..." # Extrair resposta automaticamente
            }
        })

# 7. READING TIME CALCULATOR
def calculate_reading_time(content):
    """Calcular tempo de leitura automaticamente"""
    words = len(content.split())
    reading_speed = 200  # palavras por minuto (português)
    minutes = max(1, round(words / reading_speed))
    return minutes

# 8. KEYWORD DENSITY ANALYZER
def analyze_keyword_density(content, target_keyword):
    """Analisar densidade da keyword principal"""
    words = content.lower().split()
    keyword_count = content.lower().count(target_keyword.lower())
    density = (keyword_count / len(words)) * 100
    
    recommendations = {
        'current_density': density,
        'target_density': '1-3%',
        'status': 'optimal' if 1 <= density <= 3 else 'needs_optimization'
    }
    
    return recommendations