#!/usr/bin/env python3
"""
Script para testar a configuração dos databases separados
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siteDjango.settings')
django.setup()

def test_database_connections():
    """Testar conexões com ambos os databases"""
    print("🔧 Testando conexões dos databases...")
    
    from django.db import connections
    
    # Testar database default (eleicoes)
    try:
        default_conn = connections['default']
        default_conn.ensure_connection()
        print("✅ Database 'default' (eleicoes): Conectado")
        
        # Verificar tabelas no database default
        with default_conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"   Tabelas: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Database 'default': Erro - {e}")
    
    # Testar database blog
    try:
        blog_conn = connections['blog']
        blog_conn.ensure_connection()
        print("✅ Database 'blog': Conectado")
        
        # Verificar tabelas no database blog
        with blog_conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"   Tabelas: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Database 'blog': Erro - {e}")

def test_database_router():
    """Testar o database router"""
    print("\n🔀 Testando Database Router...")
    
    from mapa_eleitoral.models import DadoEleitoral, BlogArticle, BlogArticleView
    from django.db import router
    
    # Testar roteamento para leitura
    dado_db = router.db_for_read(DadoEleitoral)
    blog_article_db = router.db_for_read(BlogArticle)
    blog_view_db = router.db_for_read(BlogArticleView)
    
    print(f"✅ DadoEleitoral → Database: '{dado_db}'")
    print(f"✅ BlogArticle → Database: '{blog_article_db}'")
    print(f"✅ BlogArticleView → Database: '{blog_view_db}'")
    
    # Verificar se o roteamento está correto
    if dado_db == 'default' and blog_article_db == 'blog' and blog_view_db == 'blog':
        print("🎉 Database Router funcionando corretamente!")
    else:
        print("⚠️ Database Router pode ter problemas de configuração")

def test_model_operations():
    """Testar operações básicas dos models"""
    print("\n📊 Testando operações dos models...")
    
    from mapa_eleitoral.models import DadoEleitoral, BlogArticle
    
    # Testar DadoEleitoral (database default)
    try:
        dados_count = DadoEleitoral.objects.using('default').count()
        print(f"✅ DadoEleitoral: {dados_count} registros no database 'default'")
    except Exception as e:
        print(f"❌ DadoEleitoral: Erro - {e}")
    
    # Testar BlogArticle (database blog)
    try:
        articles_count = BlogArticle.objects.using('blog').count()
        print(f"✅ BlogArticle: {articles_count} registros no database 'blog'")
        
        # Listar artigos
        if articles_count > 0:
            articles = BlogArticle.objects.using('blog').all()[:3]
            for article in articles:
                print(f"   📝 {article.slug} - {article.total_views} views")
                
    except Exception as e:
        print(f"❌ BlogArticle: Erro - {e}")

def test_automatic_routing():
    """Testar roteamento automático (sem especificar using)"""
    print("\n🤖 Testando roteamento automático...")
    
    from mapa_eleitoral.models import DadoEleitoral, BlogArticle
    
    try:
        # Deve usar database 'default' automaticamente
        dados_count = DadoEleitoral.objects.count()
        print(f"✅ DadoEleitoral (automático): {dados_count} registros")
    except Exception as e:
        print(f"❌ DadoEleitoral (automático): Erro - {e}")
    
    try:
        # Deve usar database 'blog' automaticamente
        articles_count = BlogArticle.objects.count()
        print(f"✅ BlogArticle (automático): {articles_count} registros")
    except Exception as e:
        print(f"❌ BlogArticle (automático): Erro - {e}")

def show_settings_summary():
    """Mostrar resumo das configurações"""
    print("\n⚙️ Resumo das Configurações:")
    print(f"📁 Databases configurados: {list(settings.DATABASES.keys())}")
    print(f"🔀 Database Router: {settings.DATABASE_ROUTERS}")
    print(f"🏠 Default database: {settings.DATABASES['default']['NAME']}")
    print(f"📝 Blog database: {settings.DATABASES['blog']['NAME']}")

if __name__ == "__main__":
    print("🚀 Testando configuração dos databases separados...\n")
    
    show_settings_summary()
    test_database_connections()
    test_database_router()
    test_model_operations()
    test_automatic_routing()
    
    print("\n✨ Teste concluído!")
    print("\n📋 Se todos os testes passaram:")
    print("   ✅ Databases estão separados corretamente")
    print("   ✅ Router está funcionando")
    print("   ✅ Models acessam os databases corretos")
    print("\n🔧 Próximo: Testar as views do blog no Django")