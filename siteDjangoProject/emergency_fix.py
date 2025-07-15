#!/usr/bin/env python3
"""
EMERGENCY FIX PARA FRONTMATTER - DEPLOY RÁPIDO
Este script pode ser executado diretamente no servidor para corrigir o problema
"""

import os
import re

def fix_views_file():
    """Aplica o fix diretamente no arquivo views.py"""
    
    views_path = 'mapa_eleitoral/views.py'
    
    if not os.path.exists(views_path):
        print(f"❌ Arquivo {views_path} não encontrado")
        return False
    
    print(f"📝 Fazendo backup do views.py...")
    
    # Backup
    with open(views_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(f"{views_path}.backup", 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    # Fix para blog_view
    fix_blog_view = '''
                    # Processar frontmatter YAML se existir
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
                        except Exception as e:
                            print(f"Erro ao processar frontmatter: {e}")
'''
    
    # Aplicar fix
    # Procurar pelo padrão antigo e substituir
    old_pattern = r"# Usar markdown para converter\s+md = markdown\.Markdown\(extensions=\['meta'\]\)\s+html_content = md\.convert\(content\)"
    
    if re.search(old_pattern, original_content):
        new_content = re.sub(
            old_pattern,
            fix_blog_view.strip() + "\n                        \n                        # Converter markdown para HTML\n                        md = markdown.Markdown(extensions=['meta'])\n                        html_content = md.convert(content)",
            original_content
        )
        
        # Escrever arquivo corrigido
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Fix aplicado com sucesso!")
        return True
    else:
        print("⚠️ Padrão não encontrado - pode já estar corrigido")
        return False

def verify_yaml_import():
    """Verifica se PyYAML está disponível"""
    try:
        import yaml
        print("✅ PyYAML está disponível")
        return True
    except ImportError:
        print("❌ PyYAML não está instalado")
        print("Execute: pip install PyYAML")
        return False

def main():
    print("🚀 EMERGENCY FIX - FRONTMATTER YAML")
    print("=" * 50)
    
    # Verificar dependências
    if not verify_yaml_import():
        return
    
    # Aplicar fix
    if fix_views_file():
        print("\n✅ Fix aplicado com sucesso!")
        print("🔄 Agora reinicie o servidor Django:")
        print("   sudo systemctl restart django")
        print("   # ou")
        print("   pkill -f python && python manage.py runserver")
    else:
        print("\n❌ Não foi possível aplicar o fix")
        print("📋 Verifique se o arquivo views.py está correto")

if __name__ == "__main__":
    main()