# mapa_eleitoral/models.py
from django.db import models
from django.utils import timezone
from django.core.cache import cache

class DadoEleitoral(models.Model):
    """
    Model que mapeia para a tabela eleicoes_rio existente no MySQL
    """
    # Campo ID adicionado (corresponde à coluna id criada no MySQL)
    id = models.AutoField(primary_key=True)
    
    # Mapeando exatamente os campos da sua tabela MySQL
    ano_eleicao = models.CharField(max_length=4, db_column='ANO_ELEICAO', verbose_name="Ano da Eleição")
    sg_uf = models.CharField(max_length=2, db_column='SG_UF', verbose_name="Código UF")
    nm_ue = models.CharField(max_length=64, db_column='NM_UE', verbose_name="Nome da Unidade Eleitoral")
    ds_cargo = models.CharField(max_length=50, db_column='DS_CARGO', verbose_name="Descrição do Cargo")
    nr_candidato = models.CharField(max_length=8, db_column='NR_CANDIDATO', verbose_name="Número do Candidato")
    nm_candidato = models.CharField(max_length=64, db_column='NM_CANDIDATO', verbose_name="Nome do Candidato")
    nm_urna_candidato = models.CharField(max_length=64, db_column='NM_URNA_CANDIDATO', verbose_name="Nome na Urna")
    nr_cpf_candidato = models.CharField(max_length=11, db_column='NR_CPF_CANDIDATO', verbose_name="CPF do Candidato")
    nr_partido = models.CharField(max_length=100, db_column='NR_PARTIDO', verbose_name="Número do Partido")
    sg_partido = models.CharField(max_length=10, db_column='SG_PARTIDO', verbose_name="Sigla do Partido")
    nr_turno = models.IntegerField(db_column='NR_TURNO', verbose_name="Número do Turno")
    qt_votos = models.DecimalField(max_digits=10, decimal_places=0, db_column='QT_VOTOS', verbose_name="Quantidade de Votos")
    nm_bairro = models.CharField(max_length=100, db_column='NM_BAIRRO', verbose_name="Nome do Bairro")
    zona_secao = models.CharField(max_length=20, db_column='ZONA_SECAO', verbose_name="Zona-Seção", null=True, blank=True)
    nr_latitude = models.CharField(max_length=100, db_column='NR_LATITUDE', verbose_name="Latitude")
    nr_longitude = models.CharField(max_length=100, db_column='NR_LONGITUDE', verbose_name="Longitude")
    
    class Meta:
        db_table = 'eleicoes_rio'  
        managed = False  
        verbose_name = "Dado Eleitoral"
        verbose_name_plural = "Dados Eleitorais"
        # Indexes for performance optimization
        indexes = [
            models.Index(fields=['ano_eleicao', 'sg_partido'], name='idx_ano_partido'),
            models.Index(fields=['ano_eleicao', 'nm_bairro'], name='idx_ano_bairro'),
            models.Index(fields=['nm_urna_candidato'], name='idx_candidato'),
            models.Index(fields=['ano_eleicao', 'sg_partido', 'nm_urna_candidato'], name='idx_completo'),
            models.Index(fields=['zona_secao'], name='idx_zona_secao'),
        ]
    
    def __str__(self):
        return f"{self.nm_urna_candidato} ({self.sg_partido}) - {self.nm_bairro}: {self.qt_votos} votos"


# ===== MODELOS PARA TRACKING DE BLOG =====

class BlogArticle(models.Model):
    """
    Modelo para armazenar informações básicas dos artigos do blog
    """
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug do Artigo")
    title = models.CharField(max_length=200, verbose_name="Título")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Cache do contador total de visualizações
    total_views = models.PositiveIntegerField(default=0, verbose_name="Total de Visualizações")
    
    class Meta:
        db_table = 'blog_articles'
        verbose_name = "Artigo do Blog"
        verbose_name_plural = "Artigos do Blog"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['slug'], name='idx_blog_slug'),
            models.Index(fields=['total_views'], name='idx_blog_views'),
            models.Index(fields=['is_active', 'total_views'], name='idx_active_views'),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.total_views} views)"
    
    def increment_views(self, ip_address=None, user_agent=None):
        """
        Incrementa o contador de visualizações com proteção contra spam
        """
        # Criar chave única para cache anti-spam
        cache_key = f"view_cooldown_{self.slug}_{ip_address}_{hash(user_agent or '')}"
        
        # Verificar se esta visualização já foi contada recentemente (cooldown de 1 hora)
        if not cache.get(cache_key):
            # Incrementar contador - FORÇAR DATABASE BLOG
            self.total_views = models.F('total_views') + 1
            self.save(update_fields=['total_views'], using='blog')
            
            # Registrar visualização detalhada - FORÇAR DATABASE BLOG
            BlogArticleView.objects.using('blog').create(
                article=self,
                ip_address=ip_address[:15] if ip_address else None,  # Truncar para segurança
                user_agent=(user_agent[:200] if user_agent else None)  # Truncar para performance
            )
            
            # Definir cooldown de 1 hora para este IP/User-Agent
            cache.set(cache_key, True, timeout=3600)  # 1 hora
            
            # Atualizar cache do contador
            cache.delete(f"article_views_{self.slug}")
            
            return True
        return False
    
    def get_views_count(self):
        """
        Retorna o número de visualizações (com cache)
        """
        cache_key = f"article_views_{self.slug}"
        views = cache.get(cache_key)
        
        if views is None:
            # Buscar do banco e cachear - FORÇAR DATABASE BLOG
            self.refresh_from_db(fields=['total_views'], using='blog')
            views = self.total_views
            cache.set(cache_key, views, timeout=300)  # Cache de 5 minutos
        
        return views

    @classmethod
    def get_most_viewed(cls, limit=3):
        """
        Retorna os artigos mais visualizados
        """
        return cls.objects.using('blog').filter(is_active=True).order_by('-total_views')[:limit]


class BlogArticleView(models.Model):
    """
    Modelo para registrar cada visualização individual (para analytics detalhadas)
    """
    article = models.ForeignKey(BlogArticle, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(default=timezone.now, verbose_name="Data da Visualização")
    ip_address = models.CharField(max_length=15, null=True, blank=True, verbose_name="IP Address")
    user_agent = models.CharField(max_length=200, null=True, blank=True, verbose_name="User Agent")
    
    class Meta:
        db_table = 'blog_article_views'
        verbose_name = "Visualização de Artigo"
        verbose_name_plural = "Visualizações de Artigos"
        indexes = [
            models.Index(fields=['article', 'viewed_at'], name='idx_article_date'),
            models.Index(fields=['viewed_at'], name='idx_view_date'),
            models.Index(fields=['ip_address', 'viewed_at'], name='idx_ip_date'),
        ]
    
    def __str__(self):
        return f"{self.article.title} - {self.viewed_at.strftime('%d/%m/%Y %H:%M')}"


# Função helper para obter ou criar artigo
def get_or_create_blog_article(slug, title=None):
    """
    Obtém ou cria um artigo do blog baseado no slug
    """
    try:
        article = BlogArticle.objects.using('blog').get(slug=slug)
        # Atualizar título se fornecido e diferente
        if title and article.title != title:
            article.title = title
            article.save(update_fields=['title'], using='blog')
        return article
    except BlogArticle.DoesNotExist:
        # Criar novo artigo - FORÇAR DATABASE BLOG
        return BlogArticle.objects.using('blog').create(
            slug=slug,
            title=title or slug.replace('_', ' ').title()
        )