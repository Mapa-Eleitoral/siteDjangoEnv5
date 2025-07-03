# 📂 Pasta Certificados Criada!

## ✅ **Pasta criada em:**
```
/certificados/
├── README.md
├── .gitignore
└── (seus certificados aqui)
```

## 🔐 **Como Adicionar os Certificados:**

### 1. **Baixar do EFI Bank**
- Acesse: https://gerencianet.com.br/
- Login → API → Meus Certificados
- Baixe os arquivos .p12

### 2. **Colocar na Pasta**
```
certificados/
├── sandbox_certificate.p12      ← Certificado de homologação
├── production_certificate.p12   ← Certificado de produção
├── README.md
└── .gitignore
```

### 3. **Nomes dos Arquivos**
- **Homologação**: `sandbox_certificate.p12`
- **Produção**: `production_certificate.p12`

## ⚙️ **Configuração Automática:**

O arquivo `.env` já está configurado:
```env
EFI_CERTIFICATE_SANDBOX=./certificados/sandbox_certificate.p12
EFI_CERTIFICATE_PRODUCTION=./certificados/production_certificate.p12
```

## 🛡️ **Segurança:**

- ✅ **Pasta protegida** com .gitignore
- ✅ **Certificados não serão commitados**
- ✅ **README incluído** para orientação

## 🚀 **Próximos Passos:**

1. **Baixe os certificados** do painel EFI Bank
2. **Coloque na pasta** `/certificados/`
3. **Renomeie se necessário** para os nomes padrão
4. **Teste a integração** real

---

## 💡 **Por Enquanto:**

O sistema continua funcionando em **modo simulação** até você adicionar os certificados reais!

**Teste**: http://127.0.0.1:8000/doacoes/