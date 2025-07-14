# 📚 Documentação do Projeto - Mapa Eleitoral

## 🎯 **Visão Geral**

Esta pasta contém toda a documentação do projeto Mapa Eleitoral, organizada por categorias para facilitar a consulta e manutenção.

---

## 📁 **Estrutura da Documentação**

### 🚀 **Configuração e Deploy**
- **[CLAUDE.md](./CLAUDE.md)** - Instruções principais do projeto para o Claude AI
- **[v5.md](./v5.md)** - Notas específicas da versão 5.0
- **[produto_viavel.md](./produto_viavel.md)** - Documentação do produto viável

### 📊 **Blog e Tracking**
- **[BLOG_TRACKING_GUIDE.md](./BLOG_TRACKING_GUIDE.md)** - 📖 **Guia completo do sistema de tracking**
- **[QUICK_COMMANDS.md](./QUICK_COMMANDS.md)** - ⚡ **Comandos rápidos para administração**

### 📋 **Geral**
- **[README.md](./README.md)** - Documentação geral do projeto
- **[INDEX.md](./INDEX.md)** - Este arquivo (índice da documentação)

---

## 🔥 **Acesso Rápido**

### 📊 **Para Trabalhar com o Blog:**
1. **Setup inicial**: Ver [QUICK_COMMANDS.md](./QUICK_COMMANDS.md#setup-inicial)
2. **Ver estatísticas**: Ver [QUICK_COMMANDS.md](./QUICK_COMMANDS.md#verificar-estatísticas)
3. **Criar admin**: Ver [BLOG_TRACKING_GUIDE.md](./BLOG_TRACKING_GUIDE.md#sistema-de-login-e-permissões)
4. **Analytics**: Acessar `/blog-analytics/` após login

### ⚙️ **Para Configurar o Projeto:**
1. **Comandos Django**: Ver [CLAUDE.md](./CLAUDE.md#key-commands)
2. **Deploy produção**: Ver [CLAUDE.md](./CLAUDE.md#production-build)
3. **Banco de dados**: Ver [CLAUDE.md](./CLAUDE.md#database-operations)

### 🐛 **Para Resolver Problemas:**
1. **Troubleshooting**: Ver [BLOG_TRACKING_GUIDE.md](./BLOG_TRACKING_GUIDE.md#troubleshooting)
2. **Quick fixes**: Ver [QUICK_COMMANDS.md](./QUICK_COMMANDS.md#quick-fixes)

---

## 🎯 **Documentos por Urgência**

### 🚨 **URGENTE** (consulta diária)
- [QUICK_COMMANDS.md](./QUICK_COMMANDS.md) - Comandos essenciais

### 📚 **IMPORTANTE** (consulta semanal)  
- [BLOG_TRACKING_GUIDE.md](./BLOG_TRACKING_GUIDE.md) - Sistema completo
- [CLAUDE.md](./CLAUDE.md) - Configuração do projeto

### 📖 **REFERÊNCIA** (consulta eventual)
- [produto_viavel.md](./produto_viavel.md) - Produto viável
- [v5.md](./v5.md) - Versão 5.0

---

## 🔧 **Como Usar Esta Documentação**

### 👨‍💻 **Para Desenvolvedores:**
1. Leia primeiro [CLAUDE.md](./CLAUDE.md) para entender o projeto
2. Use [QUICK_COMMANDS.md](./QUICK_COMMANDS.md) para tarefas diárias
3. Consulte [BLOG_TRACKING_GUIDE.md](./BLOG_TRACKING_GUIDE.md) para analytics

### 👤 **Para Administradores:**
1. Use [QUICK_COMMANDS.md](./QUICK_COMMANDS.md) para criar usuários
2. Acesse `/blog-analytics/` para ver estatísticas
3. Consulte [BLOG_TRACKING_GUIDE.md](./BLOG_TRACKING_GUIDE.md) para manutenção

### 📊 **Para Analytics:**
1. Login em `/admin/`
2. Acesse `/blog-analytics/` 
3. Use comandos em [QUICK_COMMANDS.md](./QUICK_COMMANDS.md#verificar-estatísticas)

---

## 🌐 **URLs Importantes**

```
📱 Frontend:
/                     → Página inicial
/blog/                → Lista de artigos  
/blog/slug/           → Artigo específico
/projeto/             → Sobre o projeto
/apoio/               → Como apoiar

🔧 Admin:
/admin/               → Interface administrativa
/blog-analytics/      → Dashboard de analytics (staff only)
/cache-stats/         → Status do cache (admin only)
/healthcheck/         → Health check da aplicação
```

---

## 📝 **Como Atualizar Esta Documentação**

### ➕ **Adicionar Novo Documento:**
1. Crie o arquivo `.md` na pasta `docs/`
2. Adicione entrada neste INDEX.md
3. Categorize adequadamente
4. Atualize o índice

### 🔄 **Atualizar Documento Existente:**
1. Edite o arquivo diretamente
2. Atualize data no final do documento
3. Se necessário, atualize este INDEX.md

### 🗂️ **Reorganizar:**
1. Mova arquivos conforme necessário
2. Atualize todos os links neste INDEX.md
3. Teste todos os links internos

---

## 📊 **Status dos Documentos**

| Documento | Status | Última Atualização | Completude |
|-----------|--------|-------------------|------------|
| CLAUDE.md | ✅ Atual | Jul/2025 | 100% |
| BLOG_TRACKING_GUIDE.md | ✅ Atual | Jul/2025 | 100% |
| QUICK_COMMANDS.md | ✅ Atual | Jul/2025 | 100% |
| produto_viavel.md | ⚠️ Revisar | Jul/2025 | 80% |
| v5.md | ✅ Atual | Jul/2025 | 100% |
| README.md | ✅ Atual | Jul/2025 | 100% |

---

## 🔗 **Links Externos Úteis**

- **Django Docs**: https://docs.djangoproject.com/
- **Railway Docs**: https://docs.railway.app/
- **MySQL Docs**: https://dev.mysql.com/doc/
- **Redis Docs**: https://redis.io/documentation
- **Folium Docs**: https://python-visualization.github.io/folium/

---

## 📞 **Suporte**

### 🆘 **Em caso de problemas:**
1. Consulte [BLOG_TRACKING_GUIDE.md](./BLOG_TRACKING_GUIDE.md#troubleshooting)
2. Verifique [QUICK_COMMANDS.md](./QUICK_COMMANDS.md#quick-fixes)
3. Use comandos de debug nos documentos

### 📧 **Contato:**
- **Desenvolvido por**: Claude (Anthropic) + Filipe Dias
- **Projeto**: Mapa Eleitoral - Democracia em Dados
- **Website**: https://mapaeleitoral.com.br

---

**💡 Dica**: Marque esta pasta como favorita para acesso rápido à documentação!

**🔄 Última atualização**: 14/07/2025