# Configuração de Variáveis de Ambiente - Railway

Configure essas variáveis no Railway Dashboard em **Settings → Environment Variables**:

## 🔧 Variáveis Obrigatórias:

### DATABASE_URL
```
mysql://root:MHOyVWaRdBsIxajzheoDtesardXtYhmP@gondola.proxy.rlwy.net:29860/eleicoes
```

### SECRET_KEY (gere uma nova)
```bash
# No terminal local, gere uma chave:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Exemplo:
```
django-insecure-xyz123abc456def789ghi012jkl345mno678pqr901stu234vwx567yz890
```

### DEBUG
```
false
```

## 🚀 Variáveis Opcionais:

### REDIS_URL (para cache avançado)
```
# Se você adicionar Redis no Railway:
redis://default:password@redis-host:port
```

### Configurações de Segurança
```
SECURE_SSL_REDIRECT=true
SECURE_HSTS_SECONDS=31536000
```

## 📝 Passos para configurar:

1. **Railway Dashboard** → Seu projeto
2. **Settings** → **Environment Variables** 
3. **Add Variable** para cada uma
4. **Deploy** será feito automaticamente

## 🧪 Teste após configuração:

- https://sitedjangoenv4-production.up.railway.app/
- https://sitedjangoenv4-production.up.railway.app/healthcheck/

## 🗄️ Banco de Dados:

Lembre-se de executar os índices MySQL para performance:
```sql
-- Execute no seu banco MySQL:
mysql -h gondola.proxy.rlwy.net -P 29860 -u root -pMHOyVWaRdBsIxajzheoDtesardXtYhmP eleicoes < siteDjangoProject/create_indexes.sql
```

## 🔍 Debug:

Se der problema, verifique logs no Railway e teste:
- `/healthcheck/` para verificar conexão do banco
- `/admin/` para verificar se Django está funcionando