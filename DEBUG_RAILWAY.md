# 🔍 Debug Railway - Sistema de Doações

## ❌ **Problema Identificado:**
`https://mapaeleitoral.com.br/doacoes/` não está funcionando

## 🔧 **Possíveis Causas:**

### 1. **Deploy não concluído:**
- Railway ainda fazendo build
- Erro durante deploy
- Migrações não executadas

### 2. **Configuração faltando:**
- App 'doacoes' não adicionada ao INSTALLED_APPS
- URLs não configuradas corretamente
- Erro 500 interno

### 3. **Banco de dados:**
- Migrações não aplicadas
- Tabelas não criadas
- Configuração EFI não executada

## 🚀 **Passos para Resolver:**

### **Passo 1: Verificar Railway Dashboard**
```
🌐 railway.app/dashboard
```
**Verificar:**
- [ ] Deploy status: Success/Failed?
- [ ] Build logs: Erros durante build?
- [ ] Runtime logs: Erros 500/404?

### **Passo 2: Verificar Migrações**
```bash
# No Railway
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
```

### **Passo 3: Configurar EFI Bank**
```bash
railway run python manage.py setup_efi_credentials --environment=production
```

### **Passo 4: Variáveis de Ambiente**
```env
# Verificar se estão configuradas:
DEBUG=False
EFI_SANDBOX=False
PIX_KEY=mapaeleitoral@outlook.com
```

### **Passo 5: Testar URLs**
```
✅ https://mapaeleitoral.com.br/         # Home
✅ https://mapaeleitoral.com.br/admin/   # Admin  
❌ https://mapaeleitoral.com.br/doacoes/ # Doações
```

## 🔍 **Comandos de Debug:**

### **Verificar App instalada:**
```python
# No shell Django
railway run python manage.py shell

from django.conf import settings
print('doacoes' in settings.INSTALLED_APPS)
```

### **Verificar URLs:**
```python
from django.urls import reverse
print(reverse('doacoes:doacao'))
```

### **Verificar tabelas:**
```bash
railway run python manage.py showmigrations doacoes
```

## 🎯 **Soluções Rápidas:**

### **Se erro 404:**
- URLs não configuradas
- App não instalada

### **Se erro 500:**
- Migrações faltando
- Configuração EFI não criada
- Variáveis de ambiente faltando

### **Se página em branco:**
- Templates não encontrados
- Erro de sintaxe

---

## 📞 **Próximos Passos:**

1. **Verificar logs Railway**
2. **Executar migrações**
3. **Configurar EFI**
4. **Testar novamente**