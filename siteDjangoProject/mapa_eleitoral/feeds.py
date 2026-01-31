# mapa_eleitoral/feeds.py
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from .models import BlogArticle
import os


class LatestBlogPostsFeed(Feed):
    """RSS Feed para artigos do blog"""
    title = "Mapa Eleitoral - Democracia em Dados"
    link = "/blog/"
    description = "Artigos educacionais sobre o sistema eleitoral brasileiro e análise de dados eleitorais do Rio de Janeiro"
    feed_type = Rss201rev2Feed

    # Configurações de idioma e autoria
    language = "pt-br"
    author_name = "Equipe Mapa Eleitoral"
    author_email = "contato@mapaeleitoral.com.br"

    # Configurações de cache
    ttl = 3600  # 1 hora

    def items(self):
        """Retorna os 10 artigos mais recentes"""
        return BlogArticle.objects.filter(is_active=True).order_by('-updated_at')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        """Retorna uma descrição do artigo a partir do arquivo markdown"""
        from pathlib import Path
        import frontmatter

        blog_posts_dir = Path(__file__).resolve().parent.parent / 'blog_posts'
        file_path = blog_posts_dir / f'{item.slug}.md'

        try:
            if file_path.exists():
                post = frontmatter.load(file_path)
                # Retorna a descrição do frontmatter ou os primeiros 200 caracteres do conteúdo
                description = post.metadata.get('description', '')
                if not description and post.content:
                    # Pega os primeiros 200 caracteres do conteúdo
                    description = post.content[:200].strip() + '...'
                return description
            return item.title
        except Exception:
            return item.title

    def item_pubdate(self, item):
        """Data de publicação do artigo"""
        return item.created_at

    def item_updateddate(self, item):
        """Data de última atualização"""
        return item.updated_at

    def item_link(self, item):
        """Link para o artigo completo"""
        return reverse('mapa_eleitoral:blog_post', kwargs={'slug': item.slug})

    def item_guid(self, item):
        """GUID único para cada item"""
        return f"https://mapaeleitoral.com.br/blog/{item.slug}/"

    def item_guid_is_permalink(self, item):
        """O GUID é um permalink permanente"""
        return True

    def item_categories(self, item):
        """Categorias do artigo"""
        return ['Política', 'Eleições', 'Democracia', 'Brasil', 'Rio de Janeiro']
