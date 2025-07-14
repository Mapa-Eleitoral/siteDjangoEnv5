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
    
    def query_candidatos():
        candidatos = (DadoEleitoral.objects
                     .filter(ano_eleicao=ano, sg_partido=partido)
                     .values_list('nm_urna_candidato', flat=True)
                     .distinct()
                     .order_by('nm_urna_candidato'))
        
        # Garantir que candidatos existem antes de retornar
        candidatos_list = list(candidatos)
        
        # Log para debug
        if not candidatos_list:
            logging.warning(f"Nenhum candidato encontrado para {partido} em {ano}")
        else:
            logging.info(f"Encontrados {len(candidatos_list)} candidatos para {partido} em {ano}")
        
        return candidatos_list
    
    return cached_query(
        query_candidatos,
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
    
    # Decodificar URL encoding se necessário
    import urllib.parse
    candidato_decoded = urllib.parse.unquote(candidato)
    
    # Tentar diferentes variações do nome para máxima compatibilidade
    candidato_variants = [
        candidato,
        candidato_decoded,
        candidato.upper(),
        candidato_decoded.upper(),
        candidato.strip(),
        candidato_decoded.strip()
    ]
    
    # Optimized query with single database hit
    votos_agregados = None
    candidato_encontrado = None
    
    # Build Q object for multiple variants in single query
    from django.db.models import Q
    q_variants = Q()
    for variant in candidato_variants:
        q_variants |= Q(nm_urna_candidato=variant)
    
    # Add case-insensitive search
    q_variants |= Q(nm_urna_candidato__iexact=candidato_decoded)
    
    # Single optimized query with all variants
    votos_agregados = (DadoEleitoral.objects
                      .filter(ano_eleicao=ano, sg_partido=partido)
                      .filter(q_variants)
                      .values('nm_bairro', 'nm_urna_candidato')
                      .annotate(total_votos=models.Sum('qt_votos'))
                      .order_by('nm_bairro'))
    
    if votos_agregados.exists():
        # Get the actual candidate name found
        candidato_encontrado = votos_agregados.first()['nm_urna_candidato']
        logging.info(f"Candidato encontrado: '{candidato_encontrado}' (original: '{candidato}')")
        
        # Convert to simple format for compatibility
        votos_agregados = votos_agregados.values_list('nm_bairro', 'total_votos')
    
    # Log para debug
    if not votos_agregados or not votos_agregados.exists():
        logging.warning(f"Candidato não encontrado: '{candidato}' / '{candidato_decoded}' - Ano: {ano} - Partido: {partido}")
        
        # Buscar candidatos similares para debug
        candidatos_similares = (DadoEleitoral.objects
                               .filter(ano_eleicao=ano, sg_partido=partido)
                               .filter(nm_urna_candidato__icontains=candidato_decoded.split()[0] if candidato_decoded else candidato.split()[0])
                               .values_list('nm_urna_candidato', flat=True)
                               .distinct()[:5])
        
        if candidatos_similares:
            logging.info(f"Candidatos similares encontrados: {list(candidatos_similares)}")
        
        cache.set(cache_key, None, CACHE_TIMES['complete_data'])
        return None
    
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

def generate_dynamic_map_html(votos_dict, total_votos, candidato_info):
    """
    Gera mapa dinamicamente e retorna HTML inline (sem salvar arquivo)
    """
    try:
        # 1. Verificar se temos dados válidos
        if not votos_dict or total_votos == 0:
            logging.warning("Dados de votação vazios ou inválidos")
            return None
        
        logging.info(f"Gerando mapa dinâmico para {candidato_info['nome']}")
        
        # 2. Configuração do mapa otimizada
        mapa = fl.Map(
            location=[-22.928777, -43.423878],  # Centro do Rio de Janeiro
            zoom_start=11,
            tiles='CartoDB positron',
            prefer_canvas=True,
            width='100%',
            height='80%',
            max_zoom=15,
            min_zoom=9,
            attribution_control=False
        )
        
        # 3. Carregar GeoJSON
        geojson_path = os.path.join(settings.BASE_DIR, 'mapa_eleitoral', 'data', 'Limite_Bairro.geojson')
        
        if not os.path.exists(geojson_path):
            logging.error(f"Arquivo GeoJSON não encontrado: {geojson_path}")
            return create_fallback_map_html(candidato_info)
        
        try:
            # 4. Adicionar Choropleth
            choropleth_data = [[bairro, votos] for bairro, votos in votos_dict.items() if votos > 0]
            
            choropleth = fl.Choropleth(
                geo_data=geojson_path,
                name='Distribuição de Votos',
                data=choropleth_data,
                columns=['Bairro', 'Votos'],
                key_on='feature.properties.NOME',
                fill_color='Greens',
                nan_fill_color='#f0f0f0',
                nan_fill_opacity=0.3,
                fill_opacity=0.7,
                line_opacity=0.3,
                line_weight=1,
                bins=10,
                legend_name=f'Votos - {candidato_info["nome"]}',
                smooth_factor=1.0,
                highlight=True,
                
            )
            choropleth.add_to(mapa)
            
            # 5. Adicionar tooltips
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
            
            # 6. Adicionar controles
            fl.LayerControl().add_to(mapa)
            
        except Exception as e:
            logging.error(f"Erro ao processar GeoJSON: {e}")
            return create_fallback_map_html(candidato_info)
        
        # 7. Gerar HTML dinâmico (SEM salvar arquivo)
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
                    console.log('Mapa dinâmico carregado com sucesso');
                });
            </script>
            """
            
            # Inserir melhorias no HTML
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', html_improvements + '</head>')
            
            logging.info(f"Mapa dinâmico gerado com sucesso para {candidato_info['nome']}")
            return html_content  # Retornar HTML direto, não URL
                
        except Exception as e:
            logging.error(f"Erro ao gerar HTML do mapa: {e}")
            return create_fallback_map_html(candidato_info)
    
    except Exception as e:
        logging.error(f"Erro geral na geração do mapa dinâmico: {e}")
        return create_fallback_map_html(candidato_info)

def create_fallback_map_html(candidato_info):
    """
    Cria um mapa simples de fallback em caso de erro (HTML dinâmico)
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
        
        # Retornar HTML direto
        html_content = fallback_map._repr_html_()
        logging.info(f"Mapa de fallback criado para {candidato_info['nome']}")
        return html_content
            
    except Exception as e:
        logging.error(f"Erro ao criar mapa de fallback: {e}")
        return None




# === VIEW PRINCIPAL OTIMIZADA ===

@vary_on_headers('Accept-Language')
def home_view(request):
    """View principal com máxima otimização para Core Web Vitals"""
    
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
    
    # Verificar se deve gerar mapa
    show_map = all([candidato_selecionado, partido_selecionado, ano_selecionado])
    map_data = None
    
    if show_map:
        dados_completos = get_complete_candidate_data_optimized(
            candidato_selecionado, 
            partido_selecionado, 
            ano_selecionado
        )
        
        if dados_completos and dados_completos['total_votos'] > 0:
            candidato_info = dados_completos['candidato_info']
            # Preparar dados para o mapa dinâmico
            map_data = {
                'candidato': candidato_selecionado,
                'partido': partido_selecionado,
                'ano': ano_selecionado
            }
    
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
        'map_data': map_data,  # Dados para gerar mapa dinamicamente
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
    """API otimizada para buscar partidos com fallback"""
    ano = request.GET.get('ano')
    
    # Fallback: usar ano mais recente se não especificado
    if not ano:
        anos_disponiveis = get_cached_anos()
        ano = anos_disponiveis[0] if anos_disponiveis else '2024'
        logging.warning(f"Ano não especificado em get_partidos_ajax, usando fallback: {ano}")
    
    try:
        partidos = get_cached_partidos(ano)
        return JsonResponse({
            'partidos': partidos,
            'count': len(partidos),
            'status': 'success',
            'ano_usado': ano
        })
    except Exception as e:
        logging.error(f"Erro em get_partidos_ajax: {e}")
        return JsonResponse({
            'error': 'Erro interno',
            'partidos': [],
            'count': 0,
            'status': 'error'
        }, status=500)

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

# === MIDDLEWARE MOVED TO middleware.py ===
# OptimizedPerformanceMiddleware moved to mapa_eleitoral.middleware

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
        
        # Teste de dados básicos
        total_registros = DadoEleitoral.objects.count()
        
        status = {
            'status': 'healthy',
            'database': f'ok ({count_anos} anos, {total_registros:,} registros)',
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

def debug_candidato_view(request):
    """Debug específico para problemas de candidatos"""
    if not settings.DEBUG and not request.user.is_superuser:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    candidato = request.GET.get('candidato', '')
    partido = request.GET.get('partido', '')
    ano = request.GET.get('ano', '')
    
    if not all([candidato, partido, ano]):
        return JsonResponse({
            'error': 'Parâmetros obrigatórios: candidato, partido, ano'
        }, status=400)
    
    import urllib.parse
    candidato_decoded = urllib.parse.unquote(candidato)
    
    debug_info = {
        'parametros_recebidos': {
            'candidato_original': candidato,
            'candidato_decoded': candidato_decoded,
            'partido': partido,
            'ano': ano
        },
        'testes': {}
    }
    
    # Teste 1: Busca exata
    exact_match = DadoEleitoral.objects.filter(
        ano_eleicao=ano, 
        sg_partido=partido, 
        nm_urna_candidato=candidato_decoded
    ).exists()
    debug_info['testes']['busca_exata'] = exact_match
    
    # Teste 2: Busca case-insensitive
    case_insensitive = DadoEleitoral.objects.filter(
        ano_eleicao=ano, 
        sg_partido=partido, 
        nm_urna_candidato__iexact=candidato_decoded
    ).exists()
    debug_info['testes']['case_insensitive'] = case_insensitive
    
    # Teste 3: Candidatos do partido/ano
    candidatos_disponiveis = list(DadoEleitoral.objects.filter(
        ano_eleicao=ano, 
        sg_partido=partido
    ).values_list('nm_urna_candidato', flat=True).distinct()[:10])
    debug_info['candidatos_disponiveis'] = candidatos_disponiveis
    
    # Teste 4: Busca parcial
    candidatos_similares = list(DadoEleitoral.objects.filter(
        ano_eleicao=ano, 
        sg_partido=partido,
        nm_urna_candidato__icontains=candidato_decoded.split()[0] if candidato_decoded else candidato.split()[0]
    ).values_list('nm_urna_candidato', flat=True).distinct()[:5])
    debug_info['candidatos_similares'] = candidatos_similares
    
    return JsonResponse(debug_info, json_dumps_params={'ensure_ascii': False})

def projeto_view(request):
    """View para página do projeto"""
    return render(request, 'projeto.html')

def apoio_view(request):
    """View para página de apoio"""
    return render(request, 'apoio.html')

def blog_view(request):
    """View para página de blog com estudos eleitorais"""
    import os
    import markdown
    from datetime import datetime
    from .models import BlogArticle, get_or_create_blog_article
    
    # Caminho para os artigos do blog - múltiplas tentativas
    current_dir = os.path.dirname(__file__)  # mapa_eleitoral
    project_dir = os.path.dirname(current_dir)  # siteDjangoProject
    
    # Possíveis localizações dos artigos
    possible_paths = [
        # Estrutura local de desenvolvimento
        os.path.join(os.path.dirname(os.path.dirname(project_dir)), 'produtos', 'blog', 'post'),
        # Dentro do projeto Django
        os.path.join(project_dir, 'blog_posts'),
        os.path.join(current_dir, 'blog_posts'),
        # Na raiz do projeto
        os.path.join(project_dir, 'produtos', 'blog', 'post'),
        # Caminho absoluto para desenvolvimento
        '/mnt/c/users/filip/onedrive/mapaeleitoral/produtos/blog/post'
    ]
    
    blog_path = None
    for path in possible_paths:
        if os.path.exists(path):
            blog_path = path
            break
    
    articles = []
    
    # Verificar se encontrou um diretório válido
    if blog_path and os.path.exists(blog_path):
        # Ler todos os arquivos .md do diretório
        for filename in os.listdir(blog_path):
            if filename.endswith('.md'):
                filepath = os.path.join(blog_path, filename)
                try:
                    # Tentar diferentes encodings
                    encodings = ['utf-8', 'latin-1', 'cp1252']
                    content = None
                    for encoding in encodings:
                        try:
                            with open(filepath, 'r', encoding=encoding) as f:
                                content = f.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None:
                        print(f"Não foi possível decodificar {filename}")
                        continue
                        
                    # Processar o conteúdo se não estiver vazio
                    if content.strip():
                        # Processar frontmatter YAML se existir
                        title = filename.replace('.md', '').replace('_', ' ').title()
                        description = ""
                        keywords = ""
                        author = "Filipe Dias"
                        date_from_content = None
                        excerpt = ""
                        
                        # Verificar se há frontmatter YAML
                        if content.startswith('---'):
                            try:
                                import yaml
                                # Dividir frontmatter do conteúdo
                                parts = content.split('---', 2)
                                if len(parts) >= 3:
                                    frontmatter_str = parts[1].strip()
                                    content_body = parts[2].strip()
                                    
                                    # Parse do frontmatter YAML
                                    frontmatter = yaml.safe_load(frontmatter_str)
                                    
                                    if frontmatter:
                                        title = frontmatter.get('title', title)
                                        description = frontmatter.get('description', '')
                                        keywords = frontmatter.get('keywords', '')
                                        author = frontmatter.get('author', author)
                                        
                                        # Parse da data
                                        if 'date' in frontmatter:
                                            try:
                                                date_str = frontmatter['date']
                                                date_from_content = datetime.strptime(date_str, '%Y-%m-%d')
                                            except:
                                                pass
                                        
                                        # Usar description como excerpt
                                        excerpt = description
                                    
                                    # Usar o conteúdo sem frontmatter para markdown
                                    content = content_body
                            except ImportError:
                                # Se PyYAML não estiver disponível, fallback para método antigo
                                pass
                            except Exception as e:
                                print(f"Erro ao processar frontmatter em {filename}: {e}")
                        
                        # Se não há frontmatter, usar método antigo
                        if not excerpt:
                            # Extrair título da primeira linha se começar com #
                            if content.startswith('#'):
                                title = content.split('\n')[0].replace('#', '').strip()
                            
                            # Procurar por **Resumo**: ou usar primeiros 200 chars
                            lines = content.split('\n')
                            for line in lines:
                                if line.startswith('**Resumo**:'):
                                    excerpt = line.replace('**Resumo**:', '').strip()
                                    break
                                elif line.startswith('**Data**:'):
                                    try:
                                        date_str = line.replace('**Data**:', '').strip()
                                        date_from_content = datetime.strptime(date_str, '%Y-%m-%d')
                                    except:
                                        pass
                            
                            if not excerpt:
                                excerpt = content.replace('#', '').replace('\n', ' ').strip()[:200] + '...'
                        
                        # Usar data do conteúdo ou data de modificação do arquivo
                        if not date_from_content:
                            stat = os.stat(filepath)
                            date_modified = datetime.fromtimestamp(stat.st_mtime)
                        else:
                            date_modified = date_from_content
                        
                        # Converter markdown para HTML
                        md = markdown.Markdown(extensions=['meta'])
                        html_content = md.convert(content)
                        
                        # Obter ou criar registro no banco para tracking
                        slug = filename.replace('.md', '')
                        blog_article = get_or_create_blog_article(slug, title)
                        view_count = blog_article.get_views_count()
                        
                        articles.append({
                            'title': title,
                            'slug': slug,
                            'excerpt': excerpt,
                            'description': description,
                            'keywords': keywords,
                            'author': author,
                            'date': date_modified,
                            'content': html_content,
                            'filename': filename,
                            'view_count': view_count
                        })
                except Exception as e:
                    print(f"Erro ao processar {filename}: {e}")
                    continue
    
    # Ordenar artigos por data (mais recentes primeiro)
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    # ===== ARTIGOS MAIS ACESSADOS (DADOS REAIS DO BANCO) =====
    # Buscar os 4 artigos mais visualizados do banco de dados
    most_viewed_blog_articles = BlogArticle.get_most_viewed(limit=4)
    
    # Combinar dados do banco com dados dos arquivos markdown
    most_accessed_articles = []
    for blog_article in most_viewed_blog_articles:
        # Encontrar o artigo correspondente na lista de artigos
        for article in articles:
            if article['slug'] == blog_article.slug:
                article_copy = article.copy()
                article_copy['access_count'] = blog_article.total_views
                most_accessed_articles.append(article_copy)
                break
    
    # ===== FALLBACK PARA CONFIGURAÇÃO MANUAL (caso não haja dados no banco ainda) =====
    # Se não há artigos com visualizações no banco, usar configuração manual temporária
    if not most_accessed_articles:
        fallback_slugs = ['abstencao_rio2024', 'evolucao_partidaria_brasil', 'abstencao_rio_2016']
        for slug in fallback_slugs:
            for article in articles:
                if article['slug'] == slug:
                    article_copy = article.copy()
                    article_copy['access_count'] = 0  # Começar com 0 visualizações
                    most_accessed_articles.append(article_copy)
                    break
    
    context = {
        'articles': articles,
        'articles_count': len(articles),
        'most_accessed_articles': most_accessed_articles
    }
    
    return render(request, 'blog.html', context)

def blog_post_view(request, slug):
    """View para exibir um post individual do blog"""
    import os
    import markdown
    from datetime import datetime
    from django.http import Http404
    from .models import get_or_create_blog_article
    
    # Caminho para os artigos do blog - múltiplas tentativas
    current_dir = os.path.dirname(__file__)  # mapa_eleitoral
    project_dir = os.path.dirname(current_dir)  # siteDjangoProject
    
    # Possíveis localizações dos artigos
    possible_paths = [
        # Estrutura local de desenvolvimento
        os.path.join(os.path.dirname(os.path.dirname(project_dir)), 'produtos', 'blog', 'post'),
        # Dentro do projeto Django
        os.path.join(project_dir, 'blog_posts'),
        os.path.join(current_dir, 'blog_posts'),
        # Na raiz do projeto
        os.path.join(project_dir, 'produtos', 'blog', 'post'),
        # Caminho absoluto para desenvolvimento
        '/mnt/c/users/filip/onedrive/mapaeleitoral/produtos/blog/post'
    ]
    
    filepath = None
    for path in possible_paths:
        test_filepath = os.path.join(path, f"{slug}.md")
        if os.path.exists(test_filepath):
            filepath = test_filepath
            break
    
    if not filepath or not os.path.exists(filepath):
        raise Http404("Artigo não encontrado")
    
    try:
        # Tentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        content = None
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise Http404("Não foi possível decodificar o artigo")
            
        if not content.strip():
            raise Http404("Artigo vazio")
        
        # Processar frontmatter YAML se existir
        title = slug.replace('_', ' ').title()
        description = ""
        keywords = ""
        author = "Filipe Dias"
        canonical = ""
        date_from_content = None
        
        # Verificar se há frontmatter YAML
        if content.startswith('---'):
            try:
                import yaml
                # Dividir frontmatter do conteúdo
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_str = parts[1].strip()
                    content_body = parts[2].strip()
                    
                    # Parse do frontmatter YAML
                    frontmatter = yaml.safe_load(frontmatter_str)
                    
                    if frontmatter:
                        title = frontmatter.get('title', title)
                        description = frontmatter.get('description', '')
                        keywords = frontmatter.get('keywords', '')
                        author = frontmatter.get('author', author)
                        canonical = frontmatter.get('canonical', '')
                        
                        # Parse da data
                        if 'date' in frontmatter:
                            try:
                                date_str = frontmatter['date']
                                date_from_content = datetime.strptime(date_str, '%Y-%m-%d')
                            except:
                                pass
                    
                    # Usar o conteúdo sem frontmatter para markdown
                    content = content_body
            except Exception as e:
                print(f"Erro ao processar frontmatter: {e}")
        
        # Fallback para método antigo se não há frontmatter
        if not title or title == slug.replace('_', ' ').title():
            if content.startswith('#'):
                title = content.split('\n')[0].replace('#', '').strip()
        
        if not description:
            # Extrair primeiro parágrafo significativo
            lines = content.split('\n')
            for line in lines:
                clean_line = line.strip().replace('#', '').replace('**', '')
                if len(clean_line) > 50 and not line.startswith('**Data**:'):
                    description = clean_line[:160] + '...'
                    break
        
        # Converter markdown para HTML
        md = markdown.Markdown(extensions=['meta', 'codehilite', 'toc'])
        html_content = md.convert(content)
        
        # Definir excerpt baseado na descrição ou conteúdo
        excerpt = description or content.replace('#', '').replace('\n', ' ').strip()[:200] + '...'
        
        # Usar data do frontmatter ou data de modificação do arquivo
        if date_from_content:
            date_modified = date_from_content
        else:
            stat = os.stat(filepath)
            date_modified = datetime.fromtimestamp(stat.st_mtime)
        
        # ===== TRACKING DE VISUALIZAÇÕES =====
        # Obter ou criar registro do artigo no banco
        blog_article = get_or_create_blog_article(slug, title)
        
        # Registrar visualização (com proteção anti-spam)
        def get_client_ip(request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        
        # Incrementar contador de visualizações
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        view_counted = blog_article.increment_views(ip_address, user_agent)
        
        # Obter contador atual de visualizações
        view_count = blog_article.get_views_count()
        
        article = {
            'title': title,
            'slug': slug,
            'excerpt': excerpt,
            'description': description,
            'keywords': keywords,
            'author': author,
            'canonical': canonical,
            'date': date_modified,
            'content': html_content,
            'filename': f"{slug}.md",
            'view_count': view_count,
            'view_counted': view_counted,
            'canonical_url': canonical or f"https://mapaeleitoral.com.br/blog/{slug}/"
        }
        
        context = {
            'article': article
        }
        
        return render(request, 'blog_post.html', context)
        
    except Exception as e:
        print(f"Erro ao processar {slug}: {e}")
        raise Http404("Erro ao carregar o artigo")

def blog_analytics_view(request):
    """View simples para analytics do blog (apenas para admins)"""
    from django.http import JsonResponse
    from .models import BlogArticle, BlogArticleView
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Verificação simples de admin (pode ser melhorada)
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    # Estatísticas gerais
    total_articles = BlogArticle.objects.count()
    total_views = sum(article.total_views for article in BlogArticle.objects.all())
    
    # Top 10 artigos mais visualizados
    top_articles = BlogArticle.objects.filter(is_active=True).order_by('-total_views')[:10]
    
    # Visualizações dos últimos 7 dias
    last_week = datetime.now() - timedelta(days=7)
    recent_views = BlogArticleView.objects.filter(viewed_at__gte=last_week).count()
    
    # Estatísticas por dia (últimos 7 dias)
    daily_stats = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        views_count = BlogArticleView.objects.filter(
            viewed_at__gte=day_start,
            viewed_at__lt=day_end
        ).count()
        
        daily_stats.append({
            'date': day_start.strftime('%d/%m'),
            'views': views_count
        })
    
    analytics_data = {
        'total_articles': total_articles,
        'total_views': total_views,
        'recent_views_7_days': recent_views,
        'top_articles': [
            {
                'title': article.title,
                'slug': article.slug,
                'views': article.total_views,
                'url': f'/blog/{article.slug}/'
            }
            for article in top_articles
        ],
        'daily_stats': list(reversed(daily_stats)),  # Ordem cronológica
        'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    
    return JsonResponse(analytics_data, json_dumps_params={'ensure_ascii': False, 'indent': 2})

def generate_map_view(request):
    """View para gerar mapas dinamicamente via AJAX"""
    candidato = request.GET.get('candidato')
    partido = request.GET.get('partido')
    ano = request.GET.get('ano')
    
    if not all([candidato, partido, ano]):
        return JsonResponse({
            'error': 'Parâmetros obrigatórios: candidato, partido, ano'
        }, status=400)
    
    try:
        
        # Buscar dados do candidato
        dados_completos = get_complete_candidate_data_optimized(candidato, partido, ano)
        
        if not dados_completos or dados_completos['total_votos'] == 0:
            return JsonResponse({
                'error': 'Candidato não encontrado ou sem dados de votação',
                'candidato': candidato,
                'partido': partido,
                'ano': ano
            }, status=404)
        
        # Gerar mapa dinâmico
        html_content = generate_dynamic_map_html(
            dados_completos['votos_dict'],
            dados_completos['total_votos'],
            dados_completos['candidato_info']
        )
        
        if not html_content:
            return JsonResponse({
                'error': 'Erro ao gerar mapa'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'html': html_content,
            'candidato_info': dados_completos['candidato_info']
        })
        
    except Exception as e:
        logging.error(f"Erro ao gerar mapa: {e}")
        return JsonResponse({
            'error': 'Erro interno do servidor'
        }, status=500)

def get_zonas_secoes_ajax(request):
    """API para buscar zonas-seções disponíveis"""
    ano = request.GET.get('ano')
    
    if not ano:
        return JsonResponse({
            'error': 'Parâmetro ano é obrigatório'
        }, status=400)
    
    try:
        # Buscar zonas-seções distintas para o ano
        zonas_secoes = (DadoEleitoral.objects
                       .filter(ano_eleicao=ano, zona_secao__isnull=False)
                       .values_list('zona_secao', flat=True)
                       .distinct()
                       .order_by('zona_secao'))
        
        zonas_secoes_list = list(zonas_secoes)
        
        # Separar e organizar por zona e seção
        zonas_organizadas = {}
        for zona_secao in zonas_secoes_list:
            if '-' in zona_secao:
                try:
                    zona, secao = zona_secao.split('-')
                    zona = zona.strip()
                    secao = secao.strip()
                    
                    if zona not in zonas_organizadas:
                        zonas_organizadas[zona] = []
                    
                    zonas_organizadas[zona].append({
                        'secao': secao,
                        'zona_secao': zona_secao
                    })
                except ValueError:
                    continue
        
        # Ordenar seções dentro de cada zona
        for zona in zonas_organizadas:
            zonas_organizadas[zona].sort(key=lambda x: int(x['secao']) if x['secao'].isdigit() else x['secao'])
        
        return JsonResponse({
            'success': True,
            'zonas_secoes': zonas_secoes_list,
            'zonas_organizadas': zonas_organizadas
        })
        
    except Exception as e:
        logging.error(f"Erro ao buscar zonas-seções: {e}")
        return JsonResponse({
            'error': 'Erro interno do servidor'
        }, status=500)

def get_votos_zona_secao_ajax(request):
    """API para buscar votos por zona-seção específica"""
    ano = request.GET.get('ano')
    zona_secao = request.GET.get('zona_secao')
    
    if not all([ano, zona_secao]):
        return JsonResponse({
            'error': 'Parâmetros obrigatórios: ano, zona_secao'
        }, status=400)
    
    try:
        # Buscar votos por candidato na zona-seção
        votos_por_candidato = (DadoEleitoral.objects
                              .filter(ano_eleicao=ano, zona_secao=zona_secao)
                              .values('nm_urna_candidato', 'sg_partido')
                              .annotate(total_votos=models.Sum('qt_votos'))
                              .order_by('-total_votos'))
        
        if not votos_por_candidato:
            return JsonResponse({
                'success': True,
                'data': [],
                'total_votos': 0,
                'zona_secao': zona_secao,
                'message': 'Nenhum candidato encontrado para esta zona-seção'
            })
        
        votos_list = list(votos_por_candidato)
        total_votos_zona_secao = sum(item['total_votos'] or 0 for item in votos_list)
        
        resultado = []
        for item in votos_list:
            votos = item['total_votos'] or 0
            resultado.append({
                'candidato': item['nm_urna_candidato'],
                'partido': item['sg_partido'],
                'votos': int(votos),
                'percentual': round((votos / total_votos_zona_secao) * 100, 1) if total_votos_zona_secao > 0 else 0
            })
        
        # Separar zona e seção para display
        zona = ""
        secao = ""
        if '-' in zona_secao:
            try:
                zona, secao = zona_secao.split('-')
                zona = zona.strip()
                secao = secao.strip()
            except ValueError:
                pass
        
        return JsonResponse({
            'success': True,
            'data': resultado,
            'total_votos': total_votos_zona_secao,
            'zona_secao': zona_secao,
            'zona': zona,
            'secao': secao
        })
        
    except Exception as e:
        logging.error(f"Erro ao buscar votos por zona-seção: {e}")
        return JsonResponse({
            'error': 'Erro interno do servidor'
        }, status=500)
            