#!/usr/bin/env python3
"""
Teste simples das configurações de database sem Django completo
"""

# Primeiro, testar se conseguimos importar as configurações
try:
    import sys
    import os
    
    # Adicionar o diretório do projeto ao path
    sys.path.insert(0, '.')
    
    print("🔧 Testando configurações básicas...")
    
    # Testar importação do decouple
    try:
        from decouple import config
        print("✅ python-decouple importado com sucesso")
        
        # Testar variáveis de ambiente
        db_host = config('DB_HOST', default='localhost')
        db_name = config('DB_NAME', default='mapa_eleitoral')
        print(f"✅ DB_HOST: {db_host}")
        print(f"✅ DB_NAME: {db_name}")
        
    except ImportError as e:
        print(f"❌ Erro ao importar decouple: {e}")
    
    # Testar importação do Django settings
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siteDjango.settings')
        
        from siteDjango.settings import DATABASES, DATABASE_ROUTERS
        print("✅ Django settings importado com sucesso")
        print(f"✅ Databases configurados: {list(DATABASES.keys())}")
        print(f"✅ Database routers: {DATABASE_ROUTERS}")
        
        # Verificar configuração específica
        if 'blog' in DATABASES:
            print(f"✅ Blog database: {DATABASES['blog']['NAME']}")
        else:
            print("❌ Blog database não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao importar Django settings: {e}")
    
    # Testar conexão MySQL básica
    try:
        import mysql.connector
        print("✅ mysql-connector-python disponível")
        
        # Testar conexão básica
        config_dict = {
            'host': config('DB_HOST', default='gondola.proxy.rlwy.net'),
            'port': config('DB_PORT', default=29860, cast=int),
            'user': config('DB_USER', default='root'),
            'password': config('DB_PASSWORD', default='MHOyVWaRdBsIxajzheoDtesardXtYhmP'),
        }
        
        # Testar database blog
        try:
            conn = mysql.connector.connect(database='blog', **config_dict)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM blog_articles")
            count = cursor.fetchone()[0]
            print(f"✅ Conexão com database 'blog': {count} artigos encontrados")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ Erro ao conectar com database 'blog': {e}")
        
        # Testar database eleicoes
        try:
            conn = mysql.connector.connect(database='eleicoes', **config_dict)
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"✅ Conexão com database 'eleicoes': {len(tables)} tabelas encontradas")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ Erro ao conectar com database 'eleicoes': {e}")
            
    except ImportError as e:
        print(f"❌ mysql-connector-python não disponível: {e}")
    
    print("\n🎯 Resumo do teste:")
    print("Se todos os ✅ apareceram acima, a configuração está correta!")
    print("Caso contrário, verifique as dependências e configurações.")
    
except Exception as e:
    print(f"❌ Erro geral no teste: {e}")
    import traceback
    traceback.print_exc()