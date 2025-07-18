# 📊 Mapa Eleitoral - Sistema de Análise de Dados Eleitorais

Sistema Django para visualização e análise de dados eleitorais do Rio de Janeiro com mapas interativos e blog educativo.

## 🚀 Funcionalidades

- **Mapas Interativos**: Visualização de dados eleitorais por bairro usando Folium
- **Filtros Dinâmicos**: Por ano, partido e candidato
- **Blog Educativo**: Artigos sobre sistema eleitoral brasileiro
- **API REST**: Endpoints para dados eleitorais
- **Analytics**: Tracking de visualizações e estatísticas

## 🔧 Instalação

### Pré-requisitos
- Python 3.11+
- MySQL 8.0+
- Redis (opcional, para cache em produção)

### Configuração Local

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd sitedjangoenvv5
```

2. **Crie ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale dependências**
```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Execute migrações**
```bash
cd siteDjangoProject
python manage.py migrate
python manage.py migrate --database=blog
```

6. **Colete arquivos estáticos**
```bash
python manage.py collectstatic
```

7. **Execute o servidor**
```bash
python manage.py runserver
```

## 🌍 Variáveis de Ambiente

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False

# Banco de dados principal
DATABASE_URL=mysql://user:password@host:port/database
DB_NAME=mapa_eleitoral
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306

# Banco de dados do blog
BLOG_DB_NAME=blog
BLOG_DB_USER=your-blog-db-user
BLOG_DB_PASSWORD=your-blog-db-password
BLOG_DB_HOST=localhost
BLOG_DB_PORT=3306

# Cache Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Segurança
SECURE_SSL_REDIRECT=True
DB_SSL=False
```

## 🏗️ Estrutura do Projeto

```
siteDjangoProject/
├── mapa_eleitoral/         # App principal
│   ├── models.py          # Modelos de dados
│   ├── views.py           # Views e APIs
│   ├── urls.py            # URLs do app
│   ├── templates/         # Templates HTML
│   ├── data/              # Arquivos GeoJSON
│   └── middleware.py      # Middleware customizado
├── siteDjango/            # Configurações Django
│   ├── settings.py        # Configurações principais
│   ├── urls.py            # URLs raiz
│   └── db_router.py       # Roteamento de banco
├── blog_posts/            # Artigos do blog
├── static/                # Arquivos estáticos
├── media/                 # Uploads de usuário
└── manage.py              # Script de gerenciamento
```

## 📊 Modelos de Dados

### DadoEleitoral
```python
class DadoEleitoral(models.Model):
    ano_eleicao = models.CharField(max_length=4)
    sg_partido = models.CharField(max_length=10)
    nm_urna_candidato = models.CharField(max_length=64)
    nm_bairro = models.CharField(max_length=100)
    qt_votos = models.DecimalField(max_digits=10)
    # ... outros campos
```

### BlogArticle
```python
class BlogArticle(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    total_views = models.PositiveIntegerField(default=0)
    # ... outros campos
```

## 🌐 APIs Disponíveis

### Endpoints Principais
- `GET /` - Página inicial com mapa
- `GET /blog/` - Lista de artigos do blog
- `GET /blog/{slug}/` - Artigo específico
- `GET /projeto/` - Sobre o projeto
- `GET /apoio/` - Página de apoio

### APIs AJAX
- `GET /get_anos_ajax/` - Lista anos disponíveis
- `GET /get_partidos_ajax/?ano={ano}` - Partidos por ano
- `GET /get_candidatos_ajax/?partido={partido}&ano={ano}` - Candidatos
- `GET /generate-map/?candidato={candidato}&partido={partido}&ano={ano}` - Gera mapa

## 🎨 Frontend

### Tecnologias
- **HTML5** semântico
- **CSS3** com Custom Properties
- **JavaScript** vanilla
- **Bootstrap 5** (grid system)
- **Folium** para mapas interativos

### Responsividade
- Design mobile-first
- Breakpoints: 480px, 768px, 1024px
- Componentes flexíveis

## 📈 Performance

### Cache
- **Redis** em produção
- **LocMem** em desenvolvimento
- Cache de queries por 2h-24h
- Cache de mapas por 12h

### Otimizações
- Compressão GZIP
- Arquivos estáticos com WhiteNoise
- Lazy loading de imagens
- Minificação de CSS/JS

## 🔒 Segurança

### Configurações
- HTTPS enforcement
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure headers

### Validações
- Validators em models
- Sanitização de inputs
- Rate limiting em APIs

## 📝 Blog System

### Funcionalidades
- Artigos em Markdown
- Frontmatter YAML
- Tracking de visualizações
- SEO otimizado
- Analytics integrado

### Formato do Artigo
```markdown
---
title: "Título do Artigo"
description: "Descrição para SEO"
keywords: "palavras, chave"
author: "Nome do Autor"
date: 2024-01-01
canonical: "https://exemplo.com/url-canonica"
---

# Conteúdo do Artigo

Texto em **Markdown** com suporte a:
- Listas
- Links
- Imagens
- Código
```

## 🧪 Testes

```bash
# Executar testes
python manage.py test

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deploy

### Produção
1. Configure variáveis de ambiente
2. Execute migrações
3. Colete arquivos estáticos
4. Configure servidor web (Nginx/Apache)
5. Use supervisor/systemd para processo

### Railway
```bash
# Deploy automático via Git
git push origin main
```

## 📊 Monitoramento

### Logs
- Requests lentos (>3s)
- Erros de aplicação
- Métricas de performance

### Métricas
- Response time
- Cache hit ratio
- Database queries
- Error rates

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## 🙋‍♂️ Suporte

Para dúvidas e suporte:
- Email: contato@mapaeleitoral.com.br
- GitHub Issues: [link-para-issues]
- Documentação: [link-para-docs]

---

Desenvolvido com ❤️ por [Seu Nome]