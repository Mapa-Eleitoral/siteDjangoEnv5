#!/usr/bin/env python3
"""
Script de deploy de emergência para corrigir frontmatter em produção
"""

import os
import shutil
from datetime import datetime

def create_deploy_package():
    """Criar pacote com arquivos essenciais para deploy"""
    
    print("🚀 Criando pacote de deploy para correção de frontmatter...")
    
    # Arquivos críticos que precisam ser deployados
    critical_files = [
        'mapa_eleitoral/views.py',
        'mapa_eleitoral/models.py', 
        'siteDjango/settings.py',
        'siteDjango/db_router.py',
        'requirements.txt',
        '.env'
    ]
    
    # Criar diretório de deploy
    deploy_dir = f"deploy_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(deploy_dir, exist_ok=True)
    
    print(f"📦 Criando pacote em: {deploy_dir}")
    
    # Copiar arquivos críticos
    for file_path in critical_files:
        if os.path.exists(file_path):
            # Criar diretório de destino se necessário
            dest_path = os.path.join(deploy_dir, file_path)
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copiar arquivo
            shutil.copy2(file_path, dest_path)
            print(f"✅ Copiado: {file_path}")
        else:
            print(f"❌ Arquivo não encontrado: {file_path}")
    
    # Criar instruções de deploy
    instructions = """
# 🚀 INSTRUÇÕES DE DEPLOY - CORREÇÃO FRONTMATTER

## Problema
- Produção mostra frontmatter bruto: `--- title: "..." ---`
- Local funciona corretamente

## Solução
1. PyYAML adicionado ao requirements.txt
2. Database blog configurado corretamente
3. Models atualizados para usar database correto

## Deploy Manual (Railway)

### Opção 1: Git Push
```bash
git add .
git commit -m "Fix: Frontmatter processing and database routing"
git push origin main
```

### Opção 2: Upload Manual
1. **Substitua** os seguintes arquivos na produção:
   - `mapa_eleitoral/views.py` 
   - `mapa_eleitoral/models.py`
   - `siteDjango/settings.py`
   - `requirements.txt`

2. **Instale** dependência:
   ```bash
   pip install PyYAML>=6.0.0
   ```

3. **Reinicie** o serviço Django

## Verificação
Após deploy, acesse:
- https://mapaeleitoral.com.br/blog/abstencao_rio_2016/

**Antes**: `--- title: "Abstenção..." ---`
**Depois**: Título formatado + conteúdo limpo

## Arquivos Principais Alterados

### 1. requirements.txt
- ✅ Adicionado: `PyYAML>=6.0.0`

### 2. mapa_eleitoral/views.py (linhas 865-899)
- ✅ Processamento YAML frontmatter
- ✅ Fallback se PyYAML não disponível

### 3. mapa_eleitoral/models.py
- ✅ BlogArticle.objects.using('blog')
- ✅ increment_views() usa database correto

### 4. siteDjango/settings.py
- ✅ Database 'blog' configurado
- ✅ DATABASE_ROUTERS habilitado
- ✅ Credenciais Railway como fallback

## Teste Local
```bash
python manage.py runserver
# Acesse: http://localhost:8000/blog/
```

## Status Esperado
- ✅ Blog mostra títulos corretos
- ✅ Frontmatter processado
- ✅ Views contadas no database blog
- ✅ Sem frontmatter bruto

---
**PRIORIDADE: ALTA** 🔥
**IMPACTO**: Todo o blog funcionando corretamente
**TEMPO**: 5-10 minutos após deploy
"""
    
    # Salvar instruções
    with open(os.path.join(deploy_dir, 'DEPLOY_INSTRUCTIONS.md'), 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"📋 Instruções salvas em: {deploy_dir}/DEPLOY_INSTRUCTIONS.md")
    
    # Resumo final
    print(f"""
🎉 Pacote de deploy criado com sucesso!

📂 Localização: {deploy_dir}/
📄 Arquivos incluídos: {len(critical_files)} arquivos críticos
📋 Instruções: DEPLOY_INSTRUCTIONS.md

🚀 Próximos passos:
1. Revisar arquivos no pacote
2. Fazer git commit + push OU upload manual
3. Verificar PyYAML instalado na produção
4. Testar: https://mapaeleitoral.com.br/blog/

💡 O frontmatter deve aparecer formatado, não bruto!
    """)
    
    return deploy_dir

if __name__ == "__main__":
    deploy_dir = create_deploy_package()
    print(f"✅ Deploy package criado: {deploy_dir}")