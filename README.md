# Mapa Eleitoral v5 - Democracia em Dados

Sistema de visualização interativa de dados eleitorais do Rio de Janeiro, desenvolvido com Django e tecnologias modernas.

## 🎯 Sobre o Projeto

O **Mapa Eleitoral** é uma plataforma web que democratiza o acesso aos dados eleitorais brasileiros através de visualizações interativas e mapas dinâmicos. O projeto promove a transparência democrática, tornando informações complexas acessíveis para cidadãos, pesquisadores, jornalistas e interessados em política.

## ✨ Funcionalidades

- 🗺️ **Mapas Interativos**: Visualização de resultados eleitorais por bairro
- 📊 **Análise por Região**: Filtros por ano, partido, candidato e localização
- 🔍 **Busca Avançada**: Sistema de filtros dinâmicos
- 📱 **Design Responsivo**: Interface otimizada para todos os dispositivos
- ⚡ **Performance Otimizada**: Cache inteligente e otimizações de banco
- 🔒 **Dados Confiáveis**: Informações diretas do TSE e fontes oficiais

## 🚀 Tecnologias

- **Backend**: Django 4.2+, Python 3.8+
- **Banco de Dados**: MySQL 8.0+
- **Cache**: Redis
- **Mapas**: Folium + GeoJSON
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Deployment**: Railway, Gunicorn

## 🎨 Novidades v5

### Páginas Adicionadas
- **Projeto**: Informações detalhadas sobre o sistema
- **Apoio**: Formas de contribuir com o projeto

### Melhorias de UI/UX
- Design minimalista e moderno
- Cards e ícones redimensionados
- Navegação intuitiva
- Performance otimizada

## 🛠️ Instalação Local

```bash
# Clone o repositório
git clone <repo-url>
cd siteDjangoProject

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Execute migrações
python manage.py migrate

# Colete arquivos estáticos
python manage.py collectstatic

# Execute o servidor
python manage.py runserver
```

## 🌐 Deploy

O projeto está configurado para deploy automático no Railway. Veja `railway.json` e `RAILWAY_CONFIG.md` para detalhes.

## 📈 Performance

- Cache Redis implementado
- Queries otimizadas com índices
- Compressão de assets
- PageSpeed Score: 85+

## 📚 Documentação

- `OTIMIZACOES.md` - Detalhes de otimizações implementadas
- `RAILWAY_CONFIG.md` - Configuração de deploy

## 🤝 Contribuição

Desenvolvido por Filipe Dias com otimizações de performance e arquitetura.