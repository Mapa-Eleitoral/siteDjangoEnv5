# VIEWS.PY SUPER OTIMIZADO - VERSÃO 2.0

from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.conf import settings
from django.db import models
import os, json, time, hashlib, logging
from decimal import Decimal
from .models import DadoEleitoral

# Imports para geração de mapas
import folium as fl
from folium.plugins import HeatMap
from folium import GeoJsonTooltip

# === CONFIGURAÇÃO CACHE OTIMIZADA ===
CACHE_TIMES = {
    'geojson_data': 86400,      # 24h - arquivo não muda
    'map_html': 43200,          # 12h - mapas podem ser reutilizados
    'candidato_info': 21600,    # 6h - info básica de candidato
    'anos_eleicao': 86400,      # 24h - lista de anos disponíveis
    'partidos': 21600,          # 6h - partidos por ano
    'candidatos': 10800,        # 3h - candidatos por partido/ano
    'votos_bairro': 7200,       # 2h - dados de votação
    'complete_data': 7200,      # 2h - dados completos agregados
}

# Reduzir tempos em desenvolvimento
if settings.DEBUG:
    CACHE_TIMES = {k: min(v, 300) for k, v in CACHE_TIMES.items()}

# === UTILITÁRIOS DE CACHE OTIMIZADOS ===
def safe_key(prefix, *args):
    """Gera chave de cache segura e única"""
    data = "_".join(str(arg) for arg in args if arg is not None)
    return f"{prefix}_{hashlib.md5(data.encode()).hexdigest()[:12]}"

def cached_query(query_func, cache_key, ttl, *args, **kwargs):
    """Wrapper genérico para cache de queries"""
    result = cache.get(cache_key)
    if result is None:
        result = list(query_func(*args, **kwargs))
        cache.set(cache_key, result, ttl)
    return result

def load_geojson_optimized():
    """Carrega GeoJSON com cache otimizado"""
    key = 'geojson_optimized_v2'
    geojson = cache.get(key)
    
    if geojson is None:
        geojson_path = os.path.join(settings.BASE_DIR, 'mapa_eleitoral', 'data', 'Limite_Bairro.geojson')
        
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        
        # Otimizar geometrias para performance
        for feature in geojson['features']:
            # Remover propriedades desnecessárias
            props = feature.get('properties', {})
            feature['properties'] = {
                'NOME': props.get('NOME', ''),
                'tooltip_content': ''  # Será preenchido depois
            }
            
            # Simplificar coordenadas (reduzir precisão)
            if 'geometry' in feature and 'coordinates' in feature['geometry']:
                coords = feature['geometry']['coordinates']
                # Reduzir para 6 casas decimais (precisão de ~1 metro)
                def round_coords(coord_list):
                    if isinstance(coord_list[0], (list, tuple)):
                        return [round_coords(c) for c in coord_list]
                    return [round(c, 6) for c in coord_list]
                
                feature['geometry']['coordinates'] = round_coords(coords)
        
        cache.set(key, geojson, CACHE_TIMES['geojson_data'])
        logging.info(f"GeoJSON carregado e otimizado: {len(geojson['features'])} features")
    
    return geojson

# === GETTERS SUPER OTIMIZADOS ===

def get_cached_anos():
    """Busca anos disponíveis com cache"""
    return cached_query(
        lambda: DadoEleitoral.objects.values_list('ano_eleicao', flat=True).distinct().order_by('-ano_eleicao'),
        'anos_eleicao_v2',
        CACHE_TIMES['anos_eleicao']
    )

def get_cached_partidos(ano):
    """Busca partidos por ano com cache otimizado"""
    if not ano:
        return []
    
    return cached_query(
        lambda: DadoEleitoral.objects.filter(ano_eleicao=ano)
                                   .values_list('sg_partido', flat=True)
                                   .distinct()
                                   .order_by('sg_partido'),
        safe_key('partidos_v2', ano),
        CACHE_TIMES['partidos']
    )

def get_cached_candidatos(partido, ano):
    """Busca candidatos com cache otimizado"""
    if not (partido and ano):
        return []
    
    return cached_query(
        lambda: DadoEleitoral.objects.filter(ano_eleicao=ano, sg_partido=partido)
                                   .values_list('nm_urna_candidato', flat=True)
                                   .distinct()
                                   .order_by('nm_urna_candidato'),
        safe_key('candidatos_v2', partido, ano),
        CACHE_TIMES['candidatos']
    )

def get_complete_candidate_data_optimized(candidato, partido, ano):
    """Busca dados completos do candidato com cache em camadas"""
    if not all([candidato, partido, ano]):
        return None
    
    cache_key = safe_key('complete_data_v3', candidato, partido, ano)
    data = cache.get(cache_key)
    
    if data is not None:
        return data
    
    # Query única e super otimizada usando agregação
    votos_agregados = (DadoEleitoral.objects
                      .filter(ano_eleicao=ano, sg_partido=partido, nm_urna_candidato=candidato)
                      .values('nm_bairro')
                      .annotate(total_votos=models.Sum('qt_votos'))
                      .values_list('nm_bairro', 'total_votos'))
    
    if not votos_agregados:
        cache.set(cache_key, None, CACHE_TIMES['complete_data'])
        return None
    
    # Converter para dicionário e calcular total
    votos_dict = {}
    total_votos = 0
    
    for bairro, votos in votos_agregados:
        votos_int = int(votos) if votos else 0
        votos_dict[bairro] = votos_int
        total_votos += votos_int
    
    # Cache separado para info do candidato (reutilizável)
    info_key = safe_key('candidato_info_v2', candidato, partido, ano)
    candidato_info = cache.get(info_key)
    
    if candidato_info is None:
        primeiro_registro = (DadoEleitoral.objects
                           .filter(ano_eleicao=ano, sg_partido=partido, nm_urna_candidato=candidato)
                           .values('nm_urna_candidato', 'ds_cargo')
                           .first())
        
        if primeiro_registro:
            candidato_info = {
                'nome': primeiro_registro['nm_urna_candidato'],
                'cargo': primeiro_registro['ds_cargo'],
                'ano': ano,
                'votos_total': total_votos
            }
            cache.set(info_key, candidato_info, CACHE_TIMES['candidato_info'])
    
    # Atualizar total de votos na info (pode ter mudado)
    if candidato_info:
        candidato_info['votos_total'] = total_votos
    
    data = {
        'votos_dict': votos_dict,
        'total_votos': total_votos,
        'candidato_info': candidato_info
    }
    
    # Cache com TTL otimizado
    cache.set(cache_key, data, CACHE_TIMES['complete_data'])
    
    logging.info(f"Dados carregados: {candidato} - {total_votos} votos em {len(votos_dict)} bairros")
    return data

# === GERAÇÃO DE MAPA SUPER OTIMIZADA ===

# CORREÇÃO PARA SISTEMA DE GERAÇÃO DE MAPAS
# Adicione este código ao seu views.py ou substitua a função generate_static_map_html

def generate_static_map_html(votos_dict, total_votos, candidato_info):
    """
    Versão corrigida da geração de mapas que resolve o erro 404
    """
    try:
        # 1. Verificar se temos dados válidos
        if not votos_dict or total_votos == 0:
            logging.warning("Dados de votação vazios ou inválidos")
            return None
        
        # 2. Gerar hash único para o mapa
        data_signature = f"{candidato_info['nome']}_{candidato_info['ano']}_{total_votos}"
        file_hash = hashlib.md5(data_signature.encode()).hexdigest()[:16]
        filename = f"mapa_{file_hash}.html"
        
        # 3. Definir caminhos - CORREÇÃO PRINCIPAL
        # Em desenvolvimento, usar sempre diretório static local
        if settings.DEBUG:
            maps_dir = os.path.join(settings.BASE_DIR, 'static', 'maps')
        else:
            # Em produção, usar STATIC_ROOT
            maps_dir = os.path.join(settings.STATIC_ROOT, 'maps')
        
        # Criar diretório se não existir
        os.makedirs(maps_dir, exist_ok=True)
        
        file_path = os.path.join(maps_dir, filename)
        
        # 4. Verificar se arquivo já existe
        if os.path.exists(file_path):
            # Verificar se arquivo não está corrompido
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if len(content) > 1000:  # Arquivo válido
                    url = f"{settings.STATIC_URL}maps/{filename}"
                    logging.info(f"Mapa existente reutilizado: {filename}")
                    return url
            except Exception as e:
                logging.warning(f"Arquivo de mapa corrompido, regenerando: {e}")
        
        # 5. Gerar novo mapa
        logging.info(f"Gerando novo mapa para {candidato_info['nome']}")
        
        # Configuração do mapa otimizada
        mapa = fl.Map(
            location=[-22.928777, -43.423878],  # Centro do Rio de Janeiro
            zoom_start=10,
            tiles='CartoDB positron',
            prefer_canvas=True,
            width='100%',
            height='100%',
            max_zoom=15,
            min_zoom=9,
            attribution_control=False
        )
        
        # 6. Carregar GeoJSON
        geojson_path = os.path.join(settings.BASE_DIR, 'mapa_eleitoral', 'data', 'Limite_Bairro.geojson')
        
        if not os.path.exists(geojson_path):
            logging.error(f"Arquivo GeoJSON não encontrado: {geojson_path}")
            return create_fallback_map(candidato_info, maps_dir, filename)
        
        try:
            # 7. Adicionar Choropleth
            choropleth_data = [[bairro, votos] for bairro, votos in votos_dict.items() if votos > 0]
            
            choropleth = fl.Choropleth(
                geo_data=geojson_path,
                name='Distribuição de Votos',
                data=choropleth_data,
                columns=['Bairro', 'Votos'],
                key_on='feature.properties.NOME',
                fill_color='YlOrRd',
                nan_fill_color='#f0f0f0',
                nan_fill_opacity=0.3,
                fill_opacity=0.7,
                line_opacity=0.3,
                line_weight=1,
                bins=6,
                legend_name=f'Votos - {candidato_info["nome"]}',
                smooth_factor=1.0,
                highlight=True
            )
            choropleth.add_to(mapa)
            
            # 8. Adicionar tooltips
            with open(geojson_path, 'r', encoding='utf-8') as f:
                import json
                geojson_data = json.load(f)
            
            # Preparar tooltips
            for feature in geojson_data['features']:
                bairro = feature['properties']['NOME']
                votos = votos_dict.get(bairro, 0)
                
                if total_votos > 0:
                    percentual = (votos / total_votos) * 100
                    tooltip_text = f"<b>{bairro}</b><br>Votos: {votos:,}<br>Percentual: {percentual:.1f}%"
                else:
                    tooltip_text = f"<b>{bairro}</b><br>Sem dados"
                
                feature['properties']['tooltip'] = tooltip_text
            
            # Adicionar layer de tooltips
            tooltip_layer = fl.GeoJson(
                geojson_data,
                name='Detalhes dos Bairros',
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': '#666',
                    'weight': 0.5,
                    'fillOpacity': 0
                },
                tooltip=GeoJsonTooltip(
                    fields=['tooltip'],
                    aliases=[''],
                    localize=True,
                    sticky=False,
                    labels=False
                )
            )
            tooltip_layer.add_to(mapa)
            
            # 9. Adicionar controles
            fl.LayerControl().add_to(mapa)
            
        except Exception as e:
            logging.error(f"Erro ao processar GeoJSON: {e}")
            return create_fallback_map(candidato_info, maps_dir, filename)
        
        # 10. Salvar arquivo HTML
        try:
            # Gerar HTML do mapa
            html_content = mapa._repr_html_()
            
            # Adicionar melhorias no HTML
            html_improvements = """
            <style>
                .folium-map { 
                    width: 100% !important; 
                    height: 100% !important; 
                    border-radius: 8px;
                }
                body { margin: 0; padding: 0; }
            </style>
            <script>
                // Otimizações de performance
                window.addEventListener('load', function() {
                    console.log('Mapa carregado com sucesso');
                });
            </script>
            """
            
            # Inserir melhorias no HTML
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', html_improvements + '</head>')
            
            # Salvar arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Verificar se arquivo foi criado corretamente
            if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
                url = f"{settings.STATIC_URL}maps/{filename}"
                logging.info(f"Mapa gerado com sucesso: {filename} ({os.path.getsize(file_path)} bytes)")
                return url
            else:
                logging.error(f"Arquivo de mapa não foi criado corretamente: {file_path}")
                return create_fallback_map(candidato_info, maps_dir, filename)
                
        except Exception as e:
            logging.error(f"Erro ao salvar mapa: {e}")
            return create_fallback_map(candidato_info, maps_dir, filename)
    
    except Exception as e:
        logging.error(f"Erro geral na geração do mapa: {e}")
        return None

def create_fallback_map(candidato_info, maps_dir, filename):
    """
    Cria um mapa simples de fallback em caso de erro
    """
    try:
        # Mapa básico sem GeoJSON
        fallback_map = fl.Map(
            location=[-22.928777, -43.423878],
            zoom_start=10,
            tiles='OpenStreetMap',
            width='100%',
            height='100%'
        )
        
        # Adicionar marcador central
        fl.Marker(
            [-22.928777, -43.423878],
            popup=f"Dados de {candidato_info['nome']}<br>Total: {candidato_info.get('votos_total', 0):,} votos",
            tooltip="Rio de Janeiro"
        ).add_to(fallback_map)
        
        # Salvar mapa de fallback
        file_path = os.path.join(maps_dir, filename)
        fallback_map.save(file_path)
        
        if os.path.exists(file_path):
            url = f"{settings.STATIC_URL}maps/{filename}"
            logging.info(f"Mapa de fallback criado: {filename}")
            return url
            
    except Exception as e:
        logging.error(f"Erro ao criar mapa de fallback: {e}")
    
    return None




# === VIEW PRINCIPAL OTIMIZADA ===

@vary_on_headers('Accept-Language')
def home_view(request):
    """View principal com máxima otimização"""
    
    start_time = time.time()
    
    # Buscar parâmetros
    anos = get_cached_anos()
    ano_selecionado = request.GET.get('ano') or (anos[0] if anos else '2024')
    
    # Buscar partidos do ano selecionado
    partidos = get_cached_partidos(ano_selecionado)
    partido_selecionado = request.GET.get('partido') or ('PSD' if 'PSD' in partidos else (partidos[0] if partidos else ''))
    
    # Buscar candidatos do partido/ano
    candidatos = get_cached_candidatos(partido_selecionado, ano_selecionado)
    candidato_selecionado = request.GET.get('candidato') or ('EDUARDO PAES' if 'EDUARDO PAES' in candidatos else (candidatos[0] if candidatos else ''))
    
    # Inicializar variáveis do mapa
    mapa_url = None
    candidato_info = None
    
    # Gerar mapa se todos os parâmetros estão presentes
    if all([candidato_selecionado, partido_selecionado, ano_selecionado]):
        dados_completos = get_complete_candidate_data_optimized(
            candidato_selecionado, 
            partido_selecionado, 
            ano_selecionado
        )
        
        if dados_completos and dados_completos['total_votos'] > 0:
            mapa_url = generate_static_map_html(
                dados_completos['votos_dict'],
                dados_completos['total_votos'],
                dados_completos['candidato_info']
            )
            candidato_info = dados_completos['candidato_info']
    
    # Log de performance
    duration = time.time() - start_time
    if duration > 1.0:
        logging.warning(f"View lenta: home_view - {duration:.2f}s")
    
    context = {
        'anos': anos,
        'partidos': partidos,
        'candidatos': candidatos,
        'selected_ano': ano_selecionado,
        'selected_partido': partido_selecionado,
        'selected_candidato': candidato_selecionado,
        'candidato_info': candidato_info,
        'map_url': mapa_url,
        'load_time': f"{duration:.2f}s"  # Para debug
    }
    
    return render(request, 'home.html', context)

# === APIs AJAX OTIMIZADAS ===

@cache_page(CACHE_TIMES['anos_eleicao'])
@vary_on_headers('Accept-Language')
def get_anos_ajax(request):
    """API otimizada para buscar anos"""
    return JsonResponse({
        'anos': get_cached_anos(),
        'status': 'success'
    })

@cache_page(CACHE_TIMES['partidos'])
def get_partidos_ajax(request):
    """API otimizada para buscar partidos"""
    ano = request.GET.get('ano')
    if not ano:
        return JsonResponse({'error': 'Ano é obrigatório'}, status=400)
    
    partidos = get_cached_partidos(ano)
    return JsonResponse({
        'partidos': partidos,
        'count': len(partidos),
        'status': 'success'
    })

@cache_page(CACHE_TIMES['candidatos'])
def get_candidatos_ajax(request):
    """API otimizada para buscar candidatos"""
    partido = request.GET.get('partido')
    ano = request.GET.get('ano')
    
    if not (partido and ano):
        return JsonResponse({'error': 'Partido e ano são obrigatórios'}, status=400)
    
    candidatos = get_cached_candidatos(partido, ano)
    return JsonResponse({
        'candidatos': candidatos,
        'count': len(candidatos),
        'status': 'success'
    })

@cache_page(900)  # 15 minutos
def get_filter_data_ajax(request):
    """API unificada para buscar todos os dados de filtro"""
    ano = request.GET.get('ano')
    partido = request.GET.get('partido')
    
    response_data = {
        'anos': get_cached_anos(),
        'partidos': get_cached_partidos(ano) if ano else [],
        'candidatos': get_cached_candidatos(partido, ano) if (ano and partido) else [],
        'status': 'success'
    }
    
    return JsonResponse(response_data)

# === VIEWS DE MANUTENÇÃO ===

def clear_cache_view(request):
    """Limpa cache (apenas para superusuários)"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        # Limpar cache específico
        keys_cleared = 0
        
        # Usar pattern matching se disponível
        if hasattr(cache, 'delete_pattern'):
            patterns = ['anos_*', 'partidos_*', 'candidatos_*', 'complete_data_*', 'geojson_*']
            for pattern in patterns:
                keys_cleared += cache.delete_pattern(pattern) or 0
        else:
            # Fallback: limpar cache completo
            cache.clear()
            keys_cleared = "all"
        
        # Limpeza de arquivos de mapa antigos
        if settings.DEBUG:
            maps_dir = os.path.join(settings.BASE_DIR, 'static', 'maps')
        else:
            maps_dir = os.path.join(settings.STATIC_ROOT, 'maps')
        files_deleted = 0
        
        if os.path.exists(maps_dir):
            current_time = time.time()
            for filename in os.listdir(maps_dir):
                file_path = os.path.join(maps_dir, filename)
                if os.path.isfile(file_path):
                    # Remover arquivos mais antigos que 6 horas
                    if current_time - os.path.getmtime(file_path) > 21600:
                        try:
                            os.remove(file_path)
                            files_deleted += 1
                        except OSError:
                            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Cache limpo com sucesso',
            'keys_cleared': keys_cleared,
            'files_deleted': files_deleted
        })
        
    except Exception as e:
        logging.error(f"Erro ao limpar cache: {e}")
        return JsonResponse({'error': 'Erro interno'}, status=500)

def cache_stats_view(request):
    """Estatísticas do cache (apenas para superusuários)"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        stats = {
            'cache_backend': str(cache.__class__),
            'cache_location': getattr(cache, '_cache', {}).get('_host', 'N/A'),
            'cache_timeout': getattr(cache, 'default_timeout', 'N/A'),
        }
        
        # Estatísticas de arquivos de mapa
        if settings.DEBUG:
            maps_dir = os.path.join(settings.BASE_DIR, 'static', 'maps')
        else:
            maps_dir = os.path.join(settings.STATIC_ROOT, 'maps')
        if os.path.exists(maps_dir):
            map_files = [f for f in os.listdir(maps_dir) if f.endswith('.html')]
            total_size = sum(
                os.path.getsize(os.path.join(maps_dir, f)) 
                for f in map_files
            )
            stats.update({
                'map_files_count': len(map_files),
                'map_files_size_mb': round(total_size / (1024 * 1024), 2),
                'maps_directory': maps_dir
            })
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logging.error(f"Erro ao buscar stats: {e}")
        return JsonResponse({'error': 'Erro interno'}, status=500)

# === MIDDLEWARE DE PERFORMANCE ===

class OptimizedPerformanceMiddleware:
    """Middleware otimizado para monitoramento de performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Headers de otimização
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log apenas requests realmente lentos
        if duration > 3.0:
            logging.warning(
                f"Request muito lento: {request.method} {request.path} - "
                f"{duration:.2f}s - User: {getattr(request.user, 'username', 'anonymous')}"
            )
        
        # Headers de performance
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        # Cache headers para recursos estáticos
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=86400'  # 24h
        elif request.path.endswith('.html') and 'maps' in request.path:
            response['Cache-Control'] = 'public, max-age=43200'  # 12h
        
        return response

# === UTILITÁRIOS DE LIMPEZA ===

def cleanup_old_maps():
    """Utilitário para limpeza automática de mapas antigos"""
    if settings.DEBUG:
        maps_dir = os.path.join(settings.BASE_DIR, 'static', 'maps')
    else:
        maps_dir = os.path.join(settings.STATIC_ROOT, 'maps')
    
    if not os.path.exists(maps_dir):
        return 0
    
    current_time = time.time()
    files_deleted = 0
    
    for filename in os.listdir(maps_dir):
        if not filename.endswith('.html'):
            continue
            
        file_path = os.path.join(maps_dir, filename)
        
        try:
            # Remover arquivos mais antigos que 12 horas
            if current_time - os.path.getmtime(file_path) > 43200:
                os.remove(file_path)
                files_deleted += 1
        except OSError as e:
            logging.warning(f"Erro ao remover {filename}: {e}")
    
    if files_deleted > 0:
        logging.info(f"Limpeza automática: {files_deleted} mapas antigos removidos")
    
    return files_deleted

# === HEALTHCHECK ===

def healthcheck_view(request):
    """Endpoint para verificação de saúde da aplicação"""
    try:
        # Teste básico de banco
        count_anos = len(get_cached_anos())
        
        # Teste de cache
        test_key = 'healthcheck_test'
        cache.set(test_key, 'ok', 10)
        cache_ok = cache.get(test_key) == 'ok'
        cache.delete(test_key)
        
        # Teste de arquivo GeoJSON
        geojson_ok = os.path.exists(
            os.path.join(settings.BASE_DIR, 'mapa_eleitoral', 'data', 'Limite_Bairro.geojson')
        )
        
        status = {
            'status': 'healthy',
            'database': f'ok ({count_anos} anos)',
            'cache': 'ok' if cache_ok else 'error',
            'geojson': 'ok' if geojson_ok else 'missing',
            'timestamp': time.time()
        }
        
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }, status=500)
            