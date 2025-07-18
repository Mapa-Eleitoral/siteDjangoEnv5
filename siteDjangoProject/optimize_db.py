#!/usr/bin/env python
"""
Script para otimizar o banco de dados do sistema eleitoral
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Setup Django
sys.path.append('/mnt/c/users/filip/onedrive/mapaeleitoral/sitedjangoenvv5/siteDjangoProject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siteDjango.settings')
django.setup()

from mapa_eleitoral.models import DadoEleitoral
from django.db import connection
from django.core.cache import cache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_indexes():
    """Cria índices otimizados para performance"""
    with connection.cursor() as cursor:
        indexes = [
            # Índices compostos para queries frequentes
            "CREATE INDEX IF NOT EXISTS idx_ano_partido_candidato ON eleicoes_rio (ANO_ELEICAO, SG_PARTIDO, NM_URNA_CANDIDATO)",
            "CREATE INDEX IF NOT EXISTS idx_ano_bairro_votos ON eleicoes_rio (ANO_ELEICAO, NM_BAIRRO, QT_VOTOS)",
            "CREATE INDEX IF NOT EXISTS idx_candidato_nome ON eleicoes_rio (NM_URNA_CANDIDATO)",
            "CREATE INDEX IF NOT EXISTS idx_zona_secao ON eleicoes_rio (ZONA_SECAO)",
            "CREATE INDEX IF NOT EXISTS idx_partido_ano ON eleicoes_rio (SG_PARTIDO, ANO_ELEICAO)",
            
            # Índices para agregações
            "CREATE INDEX IF NOT EXISTS idx_votos_sum ON eleicoes_rio (QT_VOTOS, ANO_ELEICAO)",
            "CREATE INDEX IF NOT EXISTS idx_bairro_performance ON eleicoes_rio (NM_BAIRRO, ANO_ELEICAO, SG_PARTIDO)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.info(f"Índice criado: {index_sql}")
            except Exception as e:
                logger.warning(f"Erro ao criar índice: {e}")

def analyze_database_performance():
    """Analisa performance do banco de dados"""
    with connection.cursor() as cursor:
        # Verificar estatísticas das tabelas
        cursor.execute("SHOW TABLE STATUS LIKE 'eleicoes_rio'")
        table_stats = cursor.fetchone()
        
        if table_stats:
            logger.info(f"Estatísticas da tabela eleicoes_rio:")
            logger.info(f"  Linhas: {table_stats[4]}")
            logger.info(f"  Tamanho dados: {table_stats[6] / 1024 / 1024:.2f} MB")
            logger.info(f"  Tamanho índices: {table_stats[8] / 1024 / 1024:.2f} MB")
        
        # Verificar índices existentes
        cursor.execute("SHOW INDEX FROM eleicoes_rio")
        indexes = cursor.fetchall()
        
        logger.info(f"Índices existentes: {len(indexes)}")
        for idx in indexes:
            logger.info(f"  {idx[2]} - {idx[4]}")

def optimize_database():
    """Otimiza o banco de dados"""
    with connection.cursor() as cursor:
        try:
            # Otimizar tabela
            cursor.execute("OPTIMIZE TABLE eleicoes_rio")
            logger.info("Tabela eleicoes_rio otimizada")
            
            # Analisar tabela
            cursor.execute("ANALYZE TABLE eleicoes_rio")
            logger.info("Estatísticas da tabela atualizadas")
            
        except Exception as e:
            logger.error(f"Erro na otimização: {e}")

def clear_application_cache():
    """Limpa cache da aplicação"""
    try:
        cache.clear()
        logger.info("Cache da aplicação limpo")
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")

def preload_frequent_data():
    """Pré-carrega dados frequentemente acessados no cache"""
    from mapa_eleitoral.views import get_cached_anos, get_cached_partidos, get_cached_candidatos
    
    try:
        # Pré-carregar anos
        anos = get_cached_anos()
        logger.info(f"Anos pré-carregados: {len(anos)}")
        
        # Pré-carregar partidos dos anos mais recentes
        for ano in anos[:3]:  # Apenas os 3 anos mais recentes
            partidos = get_cached_partidos(ano)
            logger.info(f"Partidos do ano {ano}: {len(partidos)}")
            
            # Pré-carregar candidatos dos partidos principais
            partidos_principais = ['PSD', 'PT', 'PSOL', 'PP', 'PL']
            for partido in partidos_principais:
                if partido in partidos:
                    candidatos = get_cached_candidatos(partido, ano)
                    logger.info(f"Candidatos {partido}/{ano}: {len(candidatos)}")
        
        logger.info("Dados frequentes pré-carregados")
        
    except Exception as e:
        logger.error(f"Erro ao pré-carregar dados: {e}")

def main():
    """Função principal de otimização"""
    logger.info("=== INICIANDO OTIMIZAÇÃO DO BANCO DE DADOS ===")
    
    # 1. Analisar performance atual
    logger.info("1. Analisando performance atual...")
    analyze_database_performance()
    
    # 2. Criar índices otimizados
    logger.info("2. Criando índices otimizados...")
    create_database_indexes()
    
    # 3. Otimizar tabelas
    logger.info("3. Otimizando tabelas...")
    optimize_database()
    
    # 4. Limpar cache
    logger.info("4. Limpando cache...")
    clear_application_cache()
    
    # 5. Pré-carregar dados frequentes
    logger.info("5. Pré-carregando dados frequentes...")
    preload_frequent_data()
    
    logger.info("=== OTIMIZAÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    main()