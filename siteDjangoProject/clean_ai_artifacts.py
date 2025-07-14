#!/usr/bin/env python3
"""
Script para limpar artefatos de IA dos arquivos markdown
Remove padrões como :contentReference[oaicite:X]{index=X}
"""

import os
import re
import glob

def clean_ai_artifacts(file_path):
    """Remove artefatos de IA de um arquivo markdown"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Padrões de artefatos de IA para remover
        patterns = [
            r':contentReference\[oaicite:\d+\]\{index:\d+\}',  # ChatGPT artifacts
            r'\[oaicite:\d+\]',  # Simplified citations
            r':contentReference\[[^\]]+\]',  # Any content reference
            r'\{index:\d+\}',  # Index references
            r'†source†',  # Source markers
            r'【[^】]+】',  # Chinese brackets citations
        ]
        
        original_content = content
        
        # Remove cada padrão
        for pattern in patterns:
            content = re.sub(pattern, '', content)
        
        # Limpar espaços duplos resultantes
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Se houve mudanças, salvar arquivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip() + '\n')
            
            return True, f"Artefatos removidos de {file_path}"
        else:
            return False, f"Nenhum artefato encontrado em {file_path}"
            
    except Exception as e:
        return False, f"Erro ao processar {file_path}: {e}"

def scan_blog_posts():
    """Escanear todos os arquivos markdown em busca de artefatos"""
    blog_dir = 'blog_posts'
    if not os.path.exists(blog_dir):
        print(f"Diretório {blog_dir} não encontrado")
        return
    
    markdown_files = glob.glob(os.path.join(blog_dir, '*.md'))
    
    if not markdown_files:
        print("Nenhum arquivo .md encontrado")
        return
    
    print(f"Verificando {len(markdown_files)} arquivos markdown...")
    
    cleaned_count = 0
    for file_path in markdown_files:
        was_cleaned, message = clean_ai_artifacts(file_path)
        print(f"  {message}")
        if was_cleaned:
            cleaned_count += 1
    
    print(f"\n✅ Processo concluído: {cleaned_count} arquivos limpos")

if __name__ == "__main__":
    scan_blog_posts()