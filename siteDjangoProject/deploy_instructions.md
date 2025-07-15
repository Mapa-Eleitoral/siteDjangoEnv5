# 🚀 INSTRUÇÕES DE DEPLOY - CORREÇÃO FRONTMATTER

## ⚠️ PROBLEMA IDENTIFICADO
O servidor em produção está mostrando frontmatter bruto (--- title: ...) porque não tem o código atualizado que processa YAML corretamente.

## 📁 ARQUIVOS QUE PRECISAM SER ATUALIZADOS EM PRODUÇÃO:

### 1. **mapa_eleitoral/views.py** 
**CRÍTICO** - Contém as correções para processar frontmatter YAML

### 2. **blog_posts/*.md** 
**TODOS OS ARTIGOS** - Agora têm frontmatter YAML estruturado

### 3. **padrao_editorial.txt**
**NOVO** - Documento com diretrizes editoriais

## 🔧 SOLUÇÕES PARA DEPLOY:

### Opção A: Git Push Manual
```bash
# No terminal do servidor ou localmente:
git push origin main

# Depois reiniciar o servidor Django
python manage.py collectstatic --noinput
# Restart do processo Django
```

### Opção B: Railway/Heroku Auto-Deploy
1. Verificar se o auto-deploy está ativado
2. Fazer um commit dummy para triggerar deploy:
```bash
git commit --allow-empty -m "Trigger deploy"
git push origin main
```

### Opção C: Upload Manual dos Arquivos Críticos
Se git não funcionar, subir manualmente:
- `mapa_eleitoral/views.py` (MAIS IMPORTANTE)
- Todos os arquivos em `blog_posts/`

## ✅ VERIFICAÇÃO PÓS-DEPLOY:

### 1. Teste Básico:
Acesse: https://mapaeleitoral.com.br/blog/abstencao_rio_2016/

**ANTES (Problema):**
```
--- title: "Abstenção Eleitoral Rio de Janeiro 2016: Análise Detalhada por Turnos" description: "Análise completa da abs...
```

**DEPOIS (Correto):**
```
Título limpo: "Abstenção Eleitoral Rio de Janeiro 2016: Análise Detalhada por Turnos"
Descrição profissional
Conteúdo formatado
```

### 2. Verificação SEO:
- Ver código fonte da página
- Procurar por `<meta name="description"` 
- Deve conter description do frontmatter, não frontmatter bruto

## 🐛 SE AINDA NÃO FUNCIONAR:

### 1. Verificar PyYAML no Servidor:
```bash
python -c "import yaml; print('OK')"
```

### 2. Verificar Logs do Django:
```bash
tail -f django.log
# ou
python manage.py shell
# >>> import yaml
```

### 3. Restart Manual do Servidor:
```bash
# Restart do processo Django/gunicorn
sudo systemctl restart django
# ou
pkill -f python
python manage.py runserver
```

## 📝 COMMITS QUE PRECISAM ESTAR EM PRODUÇÃO:

1. **7fe6b79** - Revisão editorial completa: frontmatter SEO, correção encoding, estrutura profissional
2. **1daa5e6** - Fix: Processamento correto de frontmatter YAML nos artigos do blog

## 🆘 SE NADA FUNCIONAR:

Posso criar uma versão simplificada que não usa YAML, mas processar o frontmatter de forma mais básica. Mas o ideal é fazer o deploy correto da versão atual.

---

**Status**: ✅ Código local perfeito, ⚠️ Produção precisa de deploy
**Prioridade**: 🔥 ALTA - Blog está com frontmatter bruto