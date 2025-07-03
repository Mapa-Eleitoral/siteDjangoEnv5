# Sistema de Doações - Mapa Eleitoral

## Visão Geral

Sistema completo de doações integrado ao EFI Bank (Gerencianet) para apoio financeiro ao projeto Mapa Eleitoral.

## Funcionalidades

### 🎯 Recursos Principais
- **Múltiplas formas de pagamento**: PIX, Cartão de Crédito, Boleto
- **Interface moderna e responsiva**: Design otimizado para mobile e desktop
- **Integração com EFI Bank**: API completa para processamento de pagamentos
- **Acompanhamento em tempo real**: Status de pagamento atualizado automaticamente
- **Painel administrativo**: Gestão completa das doações no Django Admin
- **Webhook**: Notificações automáticas de status de pagamento

### 💰 Fluxo de Doação
1. **Formulário de Doação**: Usuário preenche dados e escolhe valor
2. **Seleção de Pagamento**: PIX, cartão ou boleto
3. **Processamento**: Criação da cobrança via EFI Bank
4. **Pagamento**: Interface específica para cada método
5. **Confirmação**: Página de agradecimento e recibo

## Configuração

### 🔧 Dependências
```bash
pip install requests>=2.28.0
```

### ⚙️ Configuração EFI Bank
1. Acesse o Django Admin em `/admin/`
2. Vá para **Configurações EFI Bank**
3. Adicione suas credenciais:
   - Client ID
   - Client Secret
   - Caminho do certificado
   - Webhook URL
   - Modo (Sandbox/Produção)

### 🗄️ Banco de Dados
```bash
python manage.py makemigrations doacoes
python manage.py migrate
```

## Modelos

### Doacao
- **Dados do doador**: Nome, email, telefone, CPF
- **Valores**: Quantia, tipo de pagamento, status
- **EFI Bank**: IDs de transação, QR codes, códigos PIX
- **Controle**: Datas, mensagens, anonimato

### ConfiguracaoEFI
- **Credenciais**: Client ID, Secret, certificado
- **Configurações**: Sandbox, webhook, status ativo

### LogTransacao
- **Auditoria**: Logs completos de todas as interações com EFI Bank
- **Debugging**: Dados de requisições e respostas

## URLs

```python
/doacoes/                          # Página de doação
/doacoes/processar/               # Processamento do formulário
/doacoes/pagamento/<uuid>/        # Página de pagamento
/doacoes/status/<uuid>/           # API de status (JSON)
/doacoes/obrigado/<uuid>/         # Página de agradecimento
/doacoes/webhook/efi/             # Webhook EFI Bank
/doacoes/consultar/<uuid>/        # Consulta manual de pagamento
```

## Segurança

### 🔒 Medidas Implementadas
- **UUIDs**: IDs únicos e não sequenciais para doações
- **Validação**: Dados sanitizados e validados
- **CSRF Protection**: Proteção contra ataques CSRF
- **Webhook Security**: Validação de origem das notificações
- **Logs**: Auditoria completa de transações

### 🛡️ Dados Sensíveis
- Credenciais EFI Bank armazenadas de forma segura
- CPF/dados pessoais opcionais
- Logs detalhados para auditoria

## Desenvolvimento

### 🧪 Testes
```bash
python manage.py test doacoes
```

### 🔍 Debug
- Logs detalhados em desenvolvimento
- Performance indicators
- Cache inteligente para API calls

### 📱 Responsividade
- Design mobile-first
- Breakpoints otimizados
- Touch-friendly interfaces

## Monitoramento

### 📊 Métricas
- Taxa de conversão de doações
- Métodos de pagamento preferidos
- Valores médios por doação
- Tempo de processamento

### 🚨 Alertas
- Falhas de pagamento
- Erros de integração
- Webhooks não processados

## Manutenção

### 🔄 Tarefas Regulares
- Verificar status de doações pendentes
- Monitorar logs de erro
- Atualizar certificados EFI Bank
- Backup de dados de doações

### 📈 Otimizações
- Cache de dados estáticos
- Lazy loading de componentes
- Debounce em formulários
- Retry automático para falhas

## Suporte

### 📞 Contatos
- **Desenvolvedor**: Filipe Dias
- **Email**: mapaeleitoral@outlook.com
- **GitHub**: https://github.com/diasfilipe

### 🆘 Problemas Comuns
1. **Erro de certificado EFI**: Verificar path e validade
2. **Webhook não recebido**: Verificar URL e firewall
3. **Timeout de pagamento**: Verificar conectividade
4. **Dados não salvos**: Verificar permissões de banco

---

**Versão**: 1.0  
**Última Atualização**: Janeiro 2025  
**Compatibilidade**: Django 4.2+, Python 3.8+