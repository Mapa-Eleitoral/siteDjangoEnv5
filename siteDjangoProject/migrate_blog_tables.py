#!/usr/bin/env python3
"""
Script para migrar tabelas do blog do database 'eleicoes' para o database 'blog'
"""

import mysql.connector
import os
from decouple import config

def get_db_config():
    """Obter configuração do banco de dados"""
    return {
        'host': config('DB_HOST', default='gondola.proxy.rlwy.net'),
        'port': config('DB_PORT', default=29860, cast=int),
        'user': config('DB_USER', default='root'),
        'password': config('DB_PASSWORD', default='MHOyVWaRdBsIxajzheoDtesardXtYhmP'),
    }

def create_blog_tables():
    """Criar tabelas do blog no database 'blog'"""
    
    db_config = get_db_config()
    
    # SQL para criar as tabelas do blog
    create_blog_articles_sql = """
    CREATE TABLE IF NOT EXISTS `blog_articles` (
        `id` bigint NOT NULL AUTO_INCREMENT,
        `slug` varchar(100) NOT NULL,
        `title` varchar(200) NOT NULL,
        `created_at` datetime(6) NOT NULL,
        `updated_at` datetime(6) NOT NULL,
        `is_active` tinyint(1) NOT NULL,
        `total_views` int unsigned NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE KEY `slug` (`slug`),
        KEY `idx_blog_slug` (`slug`),
        KEY `idx_blog_views` (`total_views`),
        KEY `idx_active_views` (`is_active`,`total_views`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    
    create_blog_article_views_sql = """
    CREATE TABLE IF NOT EXISTS `blog_article_views` (
        `id` bigint NOT NULL AUTO_INCREMENT,
        `viewed_at` datetime(6) NOT NULL,
        `ip_address` varchar(15) DEFAULT NULL,
        `user_agent` varchar(200) DEFAULT NULL,
        `article_id` bigint NOT NULL,
        PRIMARY KEY (`id`),
        KEY `article_id` (`article_id`),
        KEY `idx_article_date` (`article_id`,`viewed_at`),
        KEY `idx_view_date` (`viewed_at`),
        KEY `idx_ip_date` (`ip_address`,`viewed_at`),
        CONSTRAINT `blog_article_views_article_id_fk` FOREIGN KEY (`article_id`) REFERENCES `blog_articles` (`id`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    
    create_migrations_table_sql = """
    CREATE TABLE IF NOT EXISTS `django_migrations` (
        `id` bigint NOT NULL AUTO_INCREMENT,
        `app` varchar(255) NOT NULL,
        `name` varchar(255) NOT NULL,
        `applied` datetime(6) NOT NULL,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    
    try:
        # Conectar ao database blog
        print("Conectando ao database 'blog'...")
        blog_conn = mysql.connector.connect(database='blog', **db_config)
        blog_cursor = blog_conn.cursor()
        
        # Criar tabela de migrations primeiro
        print("Criando tabela django_migrations...")
        blog_cursor.execute(create_migrations_table_sql)
        
        # Criar tabelas do blog
        print("Criando tabela blog_articles...")
        blog_cursor.execute(create_blog_articles_sql)
        
        print("Criando tabela blog_article_views...")
        blog_cursor.execute(create_blog_article_views_sql)
        
        # Registrar migrations aplicadas
        migrations_to_insert = [
            ('mapa_eleitoral', '0003_blogarticle_blogarticleview', '2025-07-15 06:00:00'),
        ]
        
        for app, name, applied in migrations_to_insert:
            blog_cursor.execute(
                "INSERT IGNORE INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                (app, name, applied)
            )
        
        blog_conn.commit()
        print("✅ Tabelas do blog criadas com sucesso no database 'blog'!")
        
        # Migrar dados existentes se houver
        print("Verificando dados existentes no database 'eleicoes'...")
        eleicoes_conn = mysql.connector.connect(database='eleicoes', **db_config)
        eleicoes_cursor = eleicoes_conn.cursor()
        
        # Verificar se existem dados nas tabelas do blog no database eleicoes
        try:
            eleicoes_cursor.execute("SELECT COUNT(*) FROM blog_articles")
            articles_count = eleicoes_cursor.fetchone()[0]
            
            if articles_count > 0:
                print(f"Encontrados {articles_count} artigos no database 'eleicoes'. Migrando...")
                
                # Migrar artigos
                eleicoes_cursor.execute("SELECT * FROM blog_articles")
                articles = eleicoes_cursor.fetchall()
                
                for article in articles:
                    blog_cursor.execute(
                        "INSERT IGNORE INTO blog_articles (id, slug, title, created_at, updated_at, is_active, total_views) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        article
                    )
                
                # Migrar visualizações
                eleicoes_cursor.execute("SELECT * FROM blog_article_views")
                views = eleicoes_cursor.fetchall()
                
                for view in views:
                    blog_cursor.execute(
                        "INSERT IGNORE INTO blog_article_views (id, viewed_at, ip_address, user_agent, article_id) VALUES (%s, %s, %s, %s, %s)",
                        view
                    )
                
                blog_conn.commit()
                print(f"✅ Migrados {articles_count} artigos e suas visualizações!")
            else:
                print("Nenhum dado encontrado para migrar.")
                
        except mysql.connector.Error as e:
            print(f"Tabelas do blog não existem no database 'eleicoes': {e}")
        
        # Fechar conexões
        eleicoes_cursor.close()
        eleicoes_conn.close()
        blog_cursor.close()
        blog_conn.close()
        
        print("✅ Migração completa!")
        
    except mysql.connector.Error as e:
        print(f"❌ Erro durante a migração: {e}")
        return False
    
    return True

def verify_blog_setup():
    """Verificar se as tabelas foram criadas corretamente"""
    db_config = get_db_config()
    
    try:
        conn = mysql.connector.connect(database='blog', **db_config)
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        expected_tables = ['blog_articles', 'blog_article_views', 'django_migrations']
        
        print("\nTabelas no database 'blog':")
        for table in tables:
            status = "✅" if table in expected_tables else "❓"
            print(f"  {status} {table}")
        
        # Verificar estrutura das tabelas
        for table in ['blog_articles', 'blog_article_views']:
            if table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"\nEstrutura da tabela {table}:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Erro ao verificar setup: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando migração das tabelas do blog...")
    
    if create_blog_tables():
        verify_blog_setup()
        print("\n🎉 Migração concluída com sucesso!")
        print("\nPróximos passos:")
        print("1. Teste a conectividade do Django com o database 'blog'")
        print("2. Verifique se os modelos BlogArticle e BlogArticleView funcionam")
        print("3. Teste as views do blog")
    else:
        print("\n❌ Migração falhou!")