-- Script de otimização de índices para eleicoes_rio
-- Execute este script no seu banco MySQL para melhorar a performance

-- Índice composto principal para queries mais comuns
CREATE INDEX idx_candidato_completo 
ON eleicoes_rio (ano_eleicao, sg_partido, nm_urna_candidato, nm_bairro);

-- Índice para busca por ano (usado nos filtros)
CREATE INDEX idx_ano_eleicao 
ON eleicoes_rio (ano_eleicao);

-- Índice para busca de partidos por ano
CREATE INDEX idx_ano_partido 
ON eleicoes_rio (ano_eleicao, sg_partido);

-- Índice para agregação de votos por bairro
CREATE INDEX idx_votos_bairro 
ON eleicoes_rio (ano_eleicao, sg_partido, nm_urna_candidato, nm_bairro, qt_votos);

-- Índice para ordenação de candidatos
CREATE INDEX idx_candidatos_ordenados 
ON eleicoes_rio (ano_eleicao, sg_partido, nm_urna_candidato);

-- Verificar se os índices foram criados
SHOW INDEX FROM eleicoes_rio;