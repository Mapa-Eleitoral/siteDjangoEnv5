# ⚡ Comandos Rápidos - Blog Tracking

## 🚀 **Setup Inicial**

```bash
# 1. Ativar ambiente virtual
cd siteDjangoProject

# 2. Aplicar migrations (se necessário)
../Scripts/python.exe manage.py migrate

# 3. Criar superusuário
../Scripts/python.exe manage.py createsuperuser
```

---

## 📊 **Verificar Estatísticas**

```bash
# Abrir Django shell
../Scripts/python.exe manage.py shell
```

```python
# Comandos dentro do shell:
from mapa_eleitoral.models import BlogArticle, BlogArticleView

# 📈 Estatísticas gerais
print(f"Total de artigos: {BlogArticle.objects.count()}")
print(f"Total de visualizações: {sum(a.total_views for a in BlogArticle.objects.all())}")

# 🏆 Top 5 mais visualizados
for i, article in enumerate(BlogArticle.objects.order_by('-total_views')[:5], 1):
    print(f"{i}º. {article.title}: {article.total_views} views")

# 📅 Visualizações hoje
from datetime import datetime
hoje = datetime.now().date()
views_hoje = BlogArticleView.objects.filter(viewed_at__date=hoje).count()
print(f"Visualizações hoje: {views_hoje}")

# 📊 Últimos 7 dias
from datetime import timedelta
semana = datetime.now() - timedelta(days=7)
views_semana = BlogArticleView.objects.filter(viewed_at__gte=semana).count()
print(f"Visualizações últimos 7 dias: {views_semana}")
```

---

## 🔧 **Configurações Rápidas**

### ⏱️ **Alterar Cooldown Anti-spam**

```python
# Arquivo: mapa_eleitoral/models.py (linha ~99)
cache.set(cache_key, True, timeout=3600)  # 1 hora (3600 segundos)

# Opções:
# 30 minutos: timeout=1800
# 2 horas: timeout=7200  
# 1 dia: timeout=86400
```

### 📊 **Alterar Quantidade no Top**

```python
# Arquivo: mapa_eleitoral/views.py (linha ~868)
most_viewed_blog_articles = BlogArticle.get_most_viewed(limit=3)

# Para top 5: limit=5
# Para top 10: limit=10
```

---

## 🧹 **Manutenção**

### 🔄 **Limpar Cache**

```bash
../Scripts/python.exe manage.py shell
```

```python
from django.core.cache import cache
cache.clear()
print("Cache limpo!")
```

### 🗑️ **Limpar Dados Antigos**

```python
# Deletar visualizações antigas (manter últimos 6 meses)
from datetime import datetime, timedelta
from mapa_eleitoral.models import BlogArticleView

cutoff = datetime.now() - timedelta(days=180)
deleted = BlogArticleView.objects.filter(viewed_at__lt=cutoff).delete()
print(f"Deletados {deleted[0]} registros antigos")
```

### ⚠️ **Reset Completo (CUIDADO!)**

```python
# ATENÇÃO: Isso apaga TODOS os dados de tracking!
from mapa_eleitoral.models import BlogArticle, BlogArticleView

BlogArticleView.objects.all().delete()
BlogArticle.objects.all().delete()
print("Todos os dados de tracking foram deletados!")
```

---

## 🐛 **Debug Rápido**

### ✅ **Testar Sistema**

```python
# No Django shell:
from mapa_eleitoral.models import get_or_create_blog_article

# Criar artigo de teste
test_article = get_or_create_blog_article('test_slug', 'Artigo de Teste')

# Simular visualizações
for i in range(5):
    view_counted = test_article.increment_views(f'192.168.1.{i}', f'TestBrowser/{i}')
    print(f"View {i+1} contada: {view_counted}")

print(f"Total views do teste: {test_article.get_views_count()}")
```

### 🔍 **Verificar Artigo Específico**

```python
from mapa_eleitoral.models import BlogArticle

# Por slug
article = BlogArticle.objects.get(slug='abstencao_rio2024')
print(f"Título: {article.title}")
print(f"Views: {article.total_views}")
print(f"Criado em: {article.created_at}")
print(f"Ativo: {article.is_active}")

# Ver últimas 10 visualizações
for view in article.views.order_by('-viewed_at')[:10]:
    print(f"- {view.viewed_at}: {view.ip_address}")
```

---

## 🌐 **URLs Importantes**

```bash
# 📚 Blog
/blog/                    # Lista de artigos
/blog/nome-do-artigo/     # Artigo específico

# 📊 Analytics (apenas admin)
/blog-analytics/          # Dashboard JSON

# 👤 Admin
/admin/                   # Interface administrativa
```

---

## 🔐 **Comandos de Usuário**

```bash
# Criar superusuário
../Scripts/python.exe manage.py createsuperuser

# Alterar senha de usuário
../Scripts/python.exe manage.py changepassword username

# Listar usuários
../Scripts/python.exe manage.py shell
```

```python
from django.contrib.auth.models import User
for user in User.objects.all():
    print(f"Username: {user.username}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")
```

---

## 📱 **Comandos de Produção**

```bash
# Backup do banco (MySQL)
mysqldump -u username -p database_name > backup_$(date +%Y%m%d).sql

# Restart do servidor (Railway)
# (usar interface web do Railway)

# Verificar logs
tail -f django.log
```

---

## 🎯 **Quick Fixes**

### ❌ **Erro "no such table"**
```bash
../Scripts/python.exe manage.py migrate
```

### ❌ **Seção "Mais Acessados" vazia**
```python
# Acessar alguns artigos para gerar dados:
# /blog/abstencao_rio2024/
# /blog/evolucao_partidaria_brasil/
# /blog/abstencao_rio_2016/
```

### ❌ **Analytics retorna 403**
```bash
# Fazer login como admin primeiro:
# /admin/
```

### ❌ **Cache não funciona**
```python
# Testar cache:
from django.core.cache import cache
cache.set('test', 'ok', 60)
print(cache.get('test'))  # Deve retornar 'ok'
```

---

## 📋 **Checklist de Deploy**

- [ ] Migrations aplicadas
- [ ] Superusuário criado  
- [ ] Cache funcionando
- [ ] URLs acessíveis
- [ ] Analytics protegidas
- [ ] Backup realizado

---

**💡 Cola este arquivo na sua área de trabalho para acesso rápido!**