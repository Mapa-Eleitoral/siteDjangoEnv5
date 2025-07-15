-- ===================================================
-- MIGRAÇÃO DAS TABELAS DO BLOG PARA DATABASE SEPARADO
-- ===================================================
-- Este script deve ser executado no MySQL Railway para:
-- 1. Criar as tabelas do blog no database 'blog'
-- 2. Migrar dados existentes do database 'eleicoes' (se houver)
-- 3. Configurar as migrations do Django

-- ===================================================
-- 1. CONECTAR AO DATABASE BLOG
-- ===================================================
USE blog;

-- ===================================================
-- 2. CRIAR TABELA DE MIGRATIONS DO DJANGO
-- ===================================================
CREATE TABLE IF NOT EXISTS `django_migrations` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `app` varchar(255) NOT NULL,
    `name` varchar(255) NOT NULL,
    `applied` datetime(6) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ===================================================
-- 3. CRIAR TABELA BLOG_ARTICLES
-- ===================================================
CREATE TABLE IF NOT EXISTS `blog_articles` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `slug` varchar(100) NOT NULL,
    `title` varchar(200) NOT NULL,
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    `is_active` tinyint(1) NOT NULL DEFAULT 1,
    `total_views` int unsigned NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `slug` (`slug`),
    KEY `idx_blog_slug` (`slug`),
    KEY `idx_blog_views` (`total_views`),
    KEY `idx_active_views` (`is_active`,`total_views`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ===================================================
-- 4. CRIAR TABELA BLOG_ARTICLE_VIEWS
-- ===================================================
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
    CONSTRAINT `blog_article_views_article_id_fk` 
        FOREIGN KEY (`article_id`) 
        REFERENCES `blog_articles` (`id`) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ===================================================
-- 5. REGISTRAR MIGRATIONS APLICADAS
-- ===================================================
INSERT IGNORE INTO `django_migrations` (`app`, `name`, `applied`) VALUES 
    ('mapa_eleitoral', '0003_blogarticle_blogarticleview', NOW());

-- ===================================================
-- 6. MIGRAR DADOS EXISTENTES (SE HOUVER)
-- ===================================================
-- NOTA: Execute este bloco apenas se existirem dados no database 'eleicoes'

-- Migrar artigos do blog
INSERT IGNORE INTO `blog`.`blog_articles` 
SELECT * FROM `eleicoes`.`blog_articles` 
WHERE EXISTS (SELECT 1 FROM `eleicoes`.`blog_articles` LIMIT 1);

-- Migrar visualizações dos artigos
INSERT IGNORE INTO `blog`.`blog_article_views` 
SELECT * FROM `eleicoes`.`blog_article_views` 
WHERE EXISTS (SELECT 1 FROM `eleicoes`.`blog_article_views` LIMIT 1);

-- ===================================================
-- 7. VERIFICAR CRIAÇÃO DAS TABELAS
-- ===================================================
SHOW TABLES;

-- Verificar estrutura das tabelas criadas
DESCRIBE blog_articles;
DESCRIBE blog_article_views;
DESCRIBE django_migrations;

-- Contar registros migrados
SELECT 'blog_articles' as tabela, COUNT(*) as total FROM blog_articles
UNION ALL
SELECT 'blog_article_views' as tabela, COUNT(*) as total FROM blog_article_views
UNION ALL
SELECT 'django_migrations' as tabela, COUNT(*) as total FROM django_migrations;

-- ===================================================
-- 8. COMANDOS DE VERIFICAÇÃO PARA DJANGO
-- ===================================================
-- Após executar este SQL, no Django execute:
-- 
-- python manage.py migrate --database=blog --fake mapa_eleitoral 0003
-- python manage.py showmigrations --database=blog
-- python manage.py dbshell --database=blog

SELECT 'Migração das tabelas do blog concluída!' as status;