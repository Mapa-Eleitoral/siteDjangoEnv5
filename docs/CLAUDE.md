# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based electoral mapping system for Rio de Janeiro, called "Mapa Eleitoral - Democracia em Dados". It provides interactive visualization of electoral data by neighborhoods, allowing users to query candidate votes by party, year, and region through dynamic maps.

## Key Commands

### Development Setup
```bash
# Navigate to Django project directory
cd siteDjangoProject

# Run development server
python manage.py runserver

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create superuser (if needed)
python manage.py createsuperuser
```

### Production Build
```bash
# Build script for production
./build.sh

# Or manually:
pip install -r requirements.txt
python siteDjangoProject/manage.py collectstatic --no-input
python siteDjangoProject/manage.py migrate
```

### Database Operations
```bash
# Apply database indexes for performance
mysql -u username -p database_name < siteDjangoProject/create_indexes.sql

# Create and apply migrations for donations
python siteDjangoProject/manage.py makemigrations doacoes
python siteDjangoProject/manage.py migrate

# Setup EFI Bank credentials (sandbox environment)
python siteDjangoProject/manage.py setup_efi_credentials --environment=sandbox

# Check database health
python siteDjangoProject/manage.py shell
```

## Architecture

### Project Structure
- **siteDjangoProject/**: Main Django project directory
  - **manage.py**: Django management script
  - **siteDjango/**: Django settings and configuration
  - **mapa_eleitoral/**: Main application with electoral data models and views
  - **doacoes/**: Donations system with EFI Bank integration
  - **static/**: Static files (CSS, JS, maps)
  - **templates/**: HTML templates

### Key Components

#### Database Model
- **DadoEleitoral**: Core model mapping to `eleicoes_rio` MySQL table
- Fields include: year, candidate, party, neighborhood, votes, coordinates
- Optimized with strategic database indexes

#### Views Architecture
- **home_view**: Main page with electoral data visualization
- **AJAX APIs**: Optimized endpoints for dynamic data loading
- **Map Generation**: Dynamic Folium map creation with choropleth visualization
- **Caching Strategy**: Multi-layer caching (Redis in production, LocMem in development)

#### Performance Optimizations
- **Database**: Connection pooling, optimized queries, strategic indexes
- **Caching**: Redis with HiredisParser, fallback to local memory cache
- **Static Files**: WhiteNoise with compression and long-term caching
- **Maps**: Dynamic HTML generation without file saving

### Technology Stack
- **Backend**: Django 4.2+, MySQL 8.0+, Redis
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Maps**: Folium + GeoJSON for interactive choropleth maps
- **Deployment**: Railway with Gunicorn (2 workers, 4 threads)

## Development Notes

### File Locations
- Electoral data model: `siteDjangoProject/mapa_eleitoral/models.py`
- Main views: `siteDjangoProject/mapa_eleitoral/views.py`
- Donations system: `siteDjangoProject/doacoes/`
- EFI Bank integration: `siteDjangoProject/doacoes/efi_service.py`
- Django settings: `siteDjangoProject/siteDjango/settings.py`
- GeoJSON data: `siteDjangoProject/mapa_eleitoral/data/Limite_Bairro.geojson`

### Cache Configuration
- Cache keys use MD5 hashes for security
- Different TTL for different data types (24h for static data, 2h for dynamic)
- Automatic fallback from Redis to local memory cache

### Map Generation
- Uses Folium for choropleth visualization
- Dynamic HTML generation without file persistence
- Optimized GeoJSON processing with coordinate precision reduction
- Fallback maps for error handling

### Performance Monitoring
- `/healthcheck/`: Application health status
- `/cache-stats/`: Cache statistics (admin only)
- Automatic cleanup of old map files
- Logging for slow queries and performance issues

## Important Notes

- Always work within the `siteDjangoProject` directory for Django commands
- Database is MySQL with specific optimizations for electoral data queries
- The system uses managed=False for the main model as it connects to existing data
- Redis is required for production but has local memory fallback for development
- GeoJSON file is critical for map generation and should not be modified
- Performance optimizations are extensively documented in `OTIMIZACOES.md`

## Design Guidelines

### UI/UX Standards
- **❌ NO EMOJIS**: Never use emojis in any interface elements
- **✅ FontAwesome Icons**: Use only FontAwesome flat icons (fas fa-*)
- **📏 Compact Design**: Prefer smaller, more compact cards and elements
- **🎨 Clean Layout**: Minimal, professional design aesthetic
- **📱 Mobile-First**: Always consider responsive design (3 col → 2 col → 1 col)

### Icon Usage
- **Charts/Analytics**: `fas fa-chart-bar`, `fas fa-chart-line`
- **Politics/Government**: `fas fa-university`, `fas fa-vote-yea`
- **Data/Research**: `fas fa-brain`, `fas fa-search`
- **Time/Calendar**: `fas fa-calendar-alt`, `fas fa-clock`
- **Views/Eyes**: `fas fa-eye`, `fas fa-users`