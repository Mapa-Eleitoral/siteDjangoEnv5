#!/bin/bash

# Configurações do banco
HOST="gondola.proxy.rlwy.net"
PORT="29860"
USER="root"
PASS="MHOyVWaRdBsIxajzheoDtesardXtYhmP"

echo "🔧 Executando migração das tabelas do blog..."

# Tentar diferentes caminhos para o MySQL
MYSQL_CMD=""

# Verificar se mysql está disponível
if command -v mysql &> /dev/null; then
    MYSQL_CMD="mysql"
elif command -v /usr/bin/mysql &> /dev/null; then
    MYSQL_CMD="/usr/bin/mysql"
elif command -v /mnt/c/Program\ Files/MySQL/MySQL\ Server\ 8.0/bin/mysql.exe &> /dev/null; then
    MYSQL_CMD="/mnt/c/Program\ Files/MySQL/MySQL\ Server\ 8.0/bin/mysql.exe"
elif command -v /mnt/c/Windows/System32/mysql.exe &> /dev/null; then
    MYSQL_CMD="/mnt/c/Windows/System32/mysql.exe"
else
    echo "❌ MySQL client não encontrado!"
    echo "📋 Instruções para instalar:"
    echo "   - Windows: Baixe MySQL Client de https://dev.mysql.com/downloads/mysql/"
    echo "   - WSL: sudo apt install mysql-client"
    echo "   - Use Railway Dashboard como alternativa"
    exit 1
fi

echo "✅ MySQL encontrado: $MYSQL_CMD"

# Executar comandos
echo "🔄 Conectando ao database 'blog'..."

$MYSQL_CMD -h $HOST -P $PORT -u $USER -p$PASS -D blog << 'EOF'
-- Criar tabela de migrations
CREATE TABLE IF NOT EXISTS django_migrations (
    id bigint NOT NULL AUTO_INCREMENT,
    app varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    applied datetime(6) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Criar tabela blog_articles
CREATE TABLE IF NOT EXISTS blog_articles (
    id bigint NOT NULL AUTO_INCREMENT,
    slug varchar(100) NOT NULL,
    title varchar(200) NOT NULL,
    created_at datetime(6) NOT NULL,
    updated_at datetime(6) NOT NULL,
    is_active tinyint(1) NOT NULL DEFAULT 1,
    total_views int unsigned NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Criar tabela blog_article_views
CREATE TABLE IF NOT EXISTS blog_article_views (
    id bigint NOT NULL AUTO_INCREMENT,
    viewed_at datetime(6) NOT NULL,
    ip_address varchar(15) DEFAULT NULL,
    user_agent varchar(200) DEFAULT NULL,
    article_id bigint NOT NULL,
    PRIMARY KEY (id),
    KEY article_id (article_id),
    CONSTRAINT blog_article_views_article_id_fk 
        FOREIGN KEY (article_id) 
        REFERENCES blog_articles (id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Registrar migration
INSERT IGNORE INTO django_migrations (app, name, applied) VALUES 
    ('mapa_eleitoral', '0003_blogarticle_blogarticleview', NOW());

-- Verificar criação
SHOW TABLES;
SELECT 'Migração concluída com sucesso!' as status;
EOF

echo "✅ Migração executada!"
echo "📋 Próximos passos:"
echo "   - Teste: python manage.py showmigrations --database=blog"
echo "   - Verifique: python manage.py dbshell --database=blog"