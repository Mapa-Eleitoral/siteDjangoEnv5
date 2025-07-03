# 🚀 Deploy Railway - Sistema de Doações

## ✅ **Pré-requisitos Verificados:**

### **Configurações Locais:**
- ✅ Sistema de doações funcionando
- ✅ Certificados EFI Bank configurados
- ✅ Modo produção ativo
- ✅ PIX real testado (R$ 1,00)

## 🔧 **Configurações Railway:**

### **1. Variáveis de Ambiente (.env para Railway):**
```env
# Django
SECRET_KEY=seu_secret_key_production
DEBUG=False
DATABASE_URL=mysql://user:pass@host:port/database

# EFI Bank - Produção
EFI_SANDBOX=False
EFI_CLIENT_ID_PRODUCTION=Client_Id_7949b42e84a24dbc9990f758c38b3395296212d4
EFI_CLIENT_SECRET_PRODUCTION=Client_Secret_4aeb1f33e2ce33723b2212afec2566d2dd250553
PIX_KEY=mapaeleitoral@outlook.com

# Certificados (Railway)
EFI_CERTIFICATE_PRODUCTION=./certificados/producao-792139-mapa-eleitoral-certificado.p12

# Cache Redis
REDIS_URL=redis://red-xxxxx:6379/0
```

### **2. Arquivos para Upload:**
```
certificados/
├── producao-792139-mapa-eleitoral-certificado.p12  ← IMPORTANTE
└── .gitignore
```

### **3. Configuração Webhook EFI Bank:**
```
URL: https://mapaeleitoral.com.br/doacoes/webhook/efi/
Eventos: PIX, Cobrança
```

## 📋 **Checklist Deploy:**

### **Antes do Deploy:**
- [ ] Testar sistema localmente com produção
- [ ] Fazer backup do banco de dados atual
- [ ] Verificar certificados na pasta
- [ ] Confirmar variáveis de ambiente

### **Durante o Deploy:**
- [ ] Upload de certificados para Railway
- [ ] Configurar variáveis de ambiente
- [ ] Executar migrações
- [ ] Configurar comando setup EFI produção

### **Após o Deploy:**
- [ ] Teste de doação R$ 1,00
- [ ] Configurar webhook no painel EFI
- [ ] Verificar logs de erro
- [ ] Teste completo do fluxo

## 🎯 **Comandos Railway:**

### **Setup Inicial:**
```bash
# Conectar ao projeto
railway link

# Deploy
railway up

# Configurar banco
railway run python manage.py migrate
railway run python manage.py setup_efi_credentials --environment=production
```

### **Variáveis de Ambiente:**
```bash
railway variables set EFI_SANDBOX=False
railway variables set DEBUG=False
railway variables set PIX_KEY=mapaeleitoral@outlook.com
```

## 🔒 **Segurança Produção:**

### **Certificados:**
- ✅ Upload seguro para Railway
- ✅ Paths corretos configurados
- ✅ Não commitar no Git

### **Dados Sensíveis:**
- ✅ Credenciais em variáveis de ambiente
- ✅ DEBUG=False em produção
- ✅ HTTPS obrigatório

### **Monitoramento:**
- ✅ Logs Railway para debug
- ✅ Admin Django para gestão
- ✅ Webhook para confirmações

## 🎊 **Resultado Esperado:**

### **URLs Funcionais:**
```
https://mapaeleitoral.com.br/doacoes/          ← Página de doação
https://mapaeleitoral.com.br/admin/            ← Admin Django
https://mapaeleitoral.com.br/doacoes/webhook/  ← Webhook EFI
```

### **Funcionalidades:**
- 💰 **Doações reais** via PIX
- 📊 **Gestão completa** no admin
- 🔔 **Notificações automáticas** via webhook
- 📱 **Interface responsiva** mobile/desktop

---

## 🚀 **PRONTO PARA DEPLOY!**

Sistema totalmente configurado para receber doações em produção!