#!/usr/bin/env python3
"""
SCRIPT DE DEPLOY RÁPIDO
Este script cria instruções para aplicar as mudanças manualmente no servidor
"""

print("🚀 DEPLOY MANUAL - INSTRUÇÕES PASSO A PASSO")
print("=" * 60)

print("\n📂 ARQUIVOS QUE PRECISAM SER ATUALIZADOS NO SERVIDOR:")
print("\n1. mapa_eleitoral/views.py")
print("   → Contém o fix para processamento de frontmatter YAML")
print("   → CRÍTICO: Este arquivo resolve o problema do frontmatter bruto")

print("\n2. Todos os arquivos em blog_posts/*.md")
print("   → Agora têm frontmatter YAML estruturado")
print("   → Encoding corrigido (sem caracteres �)")

print("\n📋 OPÇÕES PARA DEPLOY:")

print("\n🔧 OPÇÃO A: Upload Manual FTP/SSH")
print("1. Conectar no servidor via FTP ou SSH")
print("2. Fazer backup do views.py atual:")
print("   cp mapa_eleitoral/views.py mapa_eleitoral/views.py.backup")
print("3. Substituir mapa_eleitoral/views.py pelo arquivo local")
print("4. Uploar todos os arquivos da pasta blog_posts/")

print("\n🔧 OPÇÃO B: Git Clone Temporário")
print("1. No servidor, criar pasta temporária:")
print("   mkdir /tmp/deploy_temp")
print("   cd /tmp/deploy_temp")
print("2. Clonar repositório:")
print("   git clone https://github.com/diasfilipe/sitedjangoenvv5.git")
print("3. Copiar arquivos:")
print("   cp sitedjangoenvv5/siteDjangoProject/mapa_eleitoral/views.py /path/to/production/mapa_eleitoral/")
print("   cp -r sitedjangoenvv5/siteDjangoProject/blog_posts/* /path/to/production/blog_posts/")

print("\n🔧 OPÇÃO C: Railway CLI")
print("1. Instalar Railway CLI se não tiver")
print("2. railway login")
print("3. railway up")

print("\n⚠️ DEPENDÊNCIA CRÍTICA:")
print("Verificar se PyYAML está instalado no servidor:")
print("python -c \"import yaml; print('PyYAML OK')\"")
print("Se não estiver: pip install PyYAML")

print("\n🔄 APÓS O DEPLOY:")
print("1. Reiniciar o servidor Django:")
print("   sudo systemctl restart django")
print("   # ou")
print("   pkill -f python && python manage.py runserver")

print("\n✅ TESTAR:")
print("Acessar: https://mapaeleitoral.com.br/blog/abstencao_rio_2016/")
print("DEVE mostrar título limpo, não frontmatter bruto")

print("\n" + "=" * 60)
print("STATUS: Código local está perfeito ✅")
print("PROBLEMA: Produção precisa ser atualizada ⚠️")