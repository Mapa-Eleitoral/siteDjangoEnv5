# 🔐 Certificados EFI Bank

## 📁 **Esta pasta deve conter:**

### **Arquivos presentes:**
```
certificados/
├── homologacao-792139-mapa-eleitoral-homologacao.p12  ✅ Homologação
├── producao-792139-mapa-eleitoral-certificado.p12     ✅ Produção
└── README.md                                          # Este arquivo
```

### **Como obter os certificados:**

1. **Acesse**: https://gerencianet.com.br/
2. **Login** na sua conta EFI Bank
3. **Navegue**: API → Meus Certificados
4. **Baixe**:
   - Certificado de **Sandbox/Homologação** (.p12)
   - Certificado de **Produção** (.p12)

### **Colocar os arquivos aqui:**
- Arraste os arquivos baixados para esta pasta
- Mantenha os nomes originais ou renomeie para:
  - `sandbox_certificate.p12`
  - `production_certificate.p12`

### **Configuração automática:**
O sistema já está configurado para buscar os certificados nesta pasta.

---

## ⚠️ **IMPORTANTE:**

- **NÃO commitar** certificados no Git
- **Manter segurança** dos arquivos
- **Backup** em local seguro

---

## ✅ **Status:**
- [x] Certificado Sandbox ✅ `homologacao-792139-mapa-eleitoral-homologacao.p12`
- [x] Certificado Produção ✅ `producao-792139-mapa-eleitoral-certificado.p12`

*Certificados configurados e prontos para uso!*