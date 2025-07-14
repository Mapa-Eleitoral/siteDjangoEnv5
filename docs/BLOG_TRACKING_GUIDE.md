# 📊 Guia Completo: Sistema de Tracking do Blog

## 🎯 **Visão Geral**

Sistema completo de tracking de visualizações implementado para o blog do Mapa Eleitoral, com contadores automáticos, proteção anti-spam, analytics detalhadas e ranking dinâmico dos artigos mais acessados.

---

## 📋 **Status Atual**

- ✅ **Modelos do banco criados** (`BlogArticle`, `BlogArticleView`)
- ✅ **Migrations aplicadas** (tabelas `blog_articles` e `blog_article_views`)
- ✅ **Views atualizadas** (tracking automático em `blog_post_view`)
- ✅ **Template atualizado** (seção "Mais Acessados" dinâmica)
- ✅ **Analytics dashboard** (`/blog-analytics/`)
- ✅ **Sistema funcionando** e coletando dados

---

## 🔧 **Configurações Principais**

### ⏱️ **Tempos de Cache e Cooldown**

```python
# Arquivo: mapa_eleitoral/models.py

# Cooldown anti-spam (linha ~99)
cache.set(cache_key, True, timeout=3600)  # 1 HORA

# Cache de contadores (linha ~118)  
cache.set(cache_key, views, timeout=300)  # 5 MINUTOS
```

### 📊 **Número de Artigos no Ranking**

```python
# Arquivo: mapa_eleitoral/views.py (linha ~868)
most_viewed_blog_articles = BlogArticle.get_most_viewed(limit=3)  # TOP 3

# Para alterar para TOP 5:
most_viewed_blog_articles = BlogArticle.get_most_viewed(limit=5)
```

### 🎨 **Personalização da Seção "Mais Acessados"**

```html
<!-- Arquivo: mapa_eleitoral/templates/blog.html (linha ~554) -->
<h2 class="section-title">
    <i class="fas fa-fire"></i>
    Artigos Mais Acessados  <!-- Altere este texto -->
</h2>
```

---

## 🌐 **URLs e Endpoints**

### 📚 **Blog URLs**
- **Lista de artigos**: `/blog/`
- **Artigo individual**: `/blog/{slug}/`
  - Exemplo: `/blog/abstencao_rio2024/`
  - **⚠️ IMPORTANTE**: Cada acesso conta uma visualização!

### 📈 **Analytics URLs**
- **Dashboard JSON**: `/blog-analytics/` *(apenas para admins)*

---

## 👤 **Sistema de Login e Permissões**

### 🔐 **Como Criar Usuário Admin**

```bash
# No terminal, dentro da pasta siteDjangoProject:
../Scripts/python.exe manage.py createsuperuser

# Preencha:
# Username: seu_usuario
# Email: seu@email.com  
# Password: sua_senha_segura
```

### 🚪 **Como Fazer Login**

1. **Acesse**: `https://mapaeleitoral.com.br/admin/`
2. **Login**: Use as credenciais criadas acima
3. **Analytics**: Após logado, acesse `/blog-analytics/`

### 👥 **Permissões**

```python
# Analytics só para staff/admin (views.py linha ~994)
if not request.user.is_staff:
    return JsonResponse({'error': 'Acesso negado'}, status=403)

# Para liberar analytics para todos (NÃO RECOMENDADO):
# Comentar ou remover as linhas 994-995
```

---

## 🗃️ **Estrutura do Banco de Dados**

### 📋 **Tabela: blog_articles**
```sql
- id (PK)
- slug (unique) → Nome do arquivo .md
- title → Título extraído do artigo  
- total_views → Contador de visualizações
- created_at → Data de criação
- updated_at → Última atualização
- is_active → Se está ativo (default: True)
```

### 📊 **Tabela: blog_article_views**
```sql
- id (PK)
- article_id (FK) → Referência ao artigo
- viewed_at → Timestamp da visualização
- ip_address → IP do visitante (primeiros 15 chars)
- user_agent → Browser do visitante (primeiros 200 chars)
```

---

## 📈 **Como Monitorar**

### 🔍 **Ver Estatísticas Rápidas**

```bash
# No Django shell:
../Scripts/python.exe manage.py shell

# Comandos úteis:
from mapa_eleitoral.models import BlogArticle, BlogArticleView

# Total de artigos
BlogArticle.objects.count()

# Total de visualizações
sum(a.total_views for a in BlogArticle.objects.all())

# Top 5 mais visualizados
BlogArticle.objects.order_by('-total_views')[:5]

# Visualizações hoje
from datetime import datetime, timedelta
hoje = datetime.now().date()
BlogArticleView.objects.filter(viewed_at__date=hoje).count()
```

### 📊 **Analytics Dashboard (JSON)**

Acesse `/blog-analytics/` como admin para ver:

```json
{
  "total_articles": 5,
  "total_views": 127,
  "recent_views_7_days": 45,
  "top_articles": [
    {
      "title": "Abstenção Rio 2024",
      "slug": "abstencao_rio2024", 
      "views": 89,
      "url": "/blog/abstencao_rio2024/"
    }
  ],
  "daily_stats": [
    {"date": "08/07", "views": 12},
    {"date": "09/07", "views": 8}
  ]
}
```

---

## 🛠️ **Manutenção**

### 🧹 **Limpeza de Dados Antigos**

```python
# Deletar visualizações antigas (opcional)
from datetime import datetime, timedelta
from mapa_eleitoral.models import BlogArticleView

# Manter apenas últimos 6 meses
cutoff = datetime.now() - timedelta(days=180)
BlogArticleView.objects.filter(viewed_at__lt=cutoff).delete()
```

### 🔄 **Reset de Contadores**

```python
# CUIDADO: Isso zera todos os contadores!
from mapa_eleitoral.models import BlogArticle, BlogArticleView

# Opção 1: Zerar apenas contadores
BlogArticle.objects.update(total_views=0)

# Opção 2: Deletar tudo e começar do zero
BlogArticleView.objects.all().delete()
BlogArticle.objects.all().delete()
```

### ⚡ **Limpar Cache**

```python
# No Django shell:
from django.core.cache import cache
cache.clear()  # Limpa todo o cache
```

---

## 🚀 **Próximos Passos**

### 🔥 **Melhorias Prioritárias**

1. **📱 Google Analytics 4 Integration**
   ```html
   <!-- Adicionar no template base -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
   ```

2. **📧 Email Alerts para Artigos Virais**
   ```python
   # Quando um artigo passar de X visualizações em Y tempo
   if article.total_views > 1000:
       send_viral_alert_email(article)
   ```

3. **🎯 A/B Testing de Títulos**
   ```python
   # Testar diferentes títulos e ver qual converte mais
   class BlogArticleVariant(models.Model):
       article = models.ForeignKey(BlogArticle)
       title_variant = models.CharField(max_length=200)
       conversion_rate = models.FloatField()
   ```

### 🔮 **Funcionalidades Futuras**

4. **📊 Heat Maps** - Ver onde usuários clicam
5. **🔍 SEO Tracking** - Rastrear origem do tráfego
6. **⏱️ Tempo de Leitura** - Medir engagement
7. **🏷️ Tags Automáticas** - Categorização por IA
8. **📝 Comentários** - Sistema de discussão
9. **🔗 Compartilhamento Social** - Botões para redes sociais
10. **📱 PWA** - App mobile do blog

### 🎨 **Melhorias de UX**

11. **🔍 Busca Interna** - Pesquisar artigos
12. **📑 Paginação** - Para muitos artigos
13. **🌙 Dark Mode** - Tema escuro
14. **📖 Modo Leitura** - Layout limpo para leitura
15. **🔖 Favoritos** - Salvar artigos

---

## ⚠️ **Troubleshooting**

### 🐛 **Problemas Comuns**

**❌ Erro: "Table doesn't exist"**
```bash
# Rodar migrations:
../Scripts/python.exe manage.py migrate
```

**❌ Analytics retorna 403**
```bash
# Criar superuser:
../Scripts/python.exe manage.py createsuperuser
```

**❌ Visualizações não contam**
```python
# Verificar se cache está funcionando:
from django.core.cache import cache
cache.set('test', 'ok', 60)
print(cache.get('test'))  # Deve retornar 'ok'
```

**❌ Seção "Mais Acessados" vazia**
```python
# Verificar se há artigos no banco:
from mapa_eleitoral.models import BlogArticle
print(BlogArticle.objects.count())

# Se 0, acessar alguns artigos para criar registros
```

### 🔧 **Debug Mode**

```python
# Ativar debug temporariamente (views.py):
print(f"Artigo: {slug}")
print(f"IP: {ip_address}")
print(f"View contada: {view_counted}")
print(f"Total views: {view_count}")
```

---

## 📞 **Suporte**

### 📧 **Contatos**
- **Desenvolvedor**: Claude (Anthropic)
- **Implementação**: Sistema Django completo
- **Documentação**: Este arquivo

### 🔗 **Links Úteis**
- **Django Docs**: https://docs.djangoproject.com/
- **Cache Framework**: https://docs.djangoproject.com/en/4.2/topics/cache/
- **Admin Interface**: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/

---

## 📝 **Changelog**

### 🆕 **v1.0 (Julho 2025)**
- ✅ Sistema de tracking implementado
- ✅ Proteção anti-spam
- ✅ Analytics dashboard
- ✅ Seção "Mais Acessados" dinâmica
- ✅ Cache para performance
- ✅ Documentação completa

---

**💡 Dica**: Mantenha este arquivo atualizado conforme implementar novas funcionalidades!

**🔄 Última atualização**: 14/07/2025