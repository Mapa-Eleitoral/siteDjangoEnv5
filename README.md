# Mapa Eleitoral - Democracia em Dados

Sistema interativo de visualização de dados eleitorais do Rio de Janeiro.

## 📋 Sobre o Projeto

Sistema web desenvolvido em Django para visualização interativa de dados eleitorais por bairros do Rio de Janeiro. Permite consultar votação de candidatos por partido, ano e região através de mapas dinâmicos.

## 🚀 Tecnologias

- **Backend**: Django 4.2+
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Banco**: MySQL 8.0+
- **Mapas**: Folium + GeoJSON
- **Deploy**: Railway
- **Cache**: Redis (com fallback LocMem)

## 📊 Funcionalidades

- ✅ Visualização de mapas eleitorais por bairro
- ✅ Filtros por ano, partido e candidato
- ✅ Geração dinâmica de mapas via AJAX
- ✅ Cache otimizado para performance
- ✅ Interface responsiva
- ✅ Google Analytics integrado

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