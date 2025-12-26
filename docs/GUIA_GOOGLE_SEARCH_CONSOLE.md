# 🔍 Guia de Configuração do Google Search Console

Este guia explica passo a passo como configurar o Google Search Console para o site CosmoAstral.

---

## 📋 Pré-requisitos

- Conta Google (Gmail)
- Acesso ao domínio `cosmoastral.com.br`
- Site já publicado e acessível

---

## 🚀 Passo 1: Acessar o Google Search Console

1. Acesse: https://search.google.com/search-console
2. Faça login com sua conta Google
3. Se for a primeira vez, clique em **"Começar"** ou **"Add Property"**

---

## 🏠 Passo 2: Adicionar Propriedade

### Opção A: Adicionar por Domínio (Recomendado)

1. Selecione **"Domínio"** (Domain)
2. Digite: `cosmoastral.com.br`
3. Clique em **"Continuar"**

### Opção B: Adicionar por Prefixo de URL

1. Selecione **"Prefixo de URL"** (URL prefix)
2. Digite: `https://cosmoastral.com.br`
3. Clique em **"Continuar"**

---

## ✅ Passo 3: Verificar Propriedade

O Google precisa verificar que você é o dono do site. Escolha um método:

### Método 1: Tag HTML (Mais Fácil)

1. O Google mostrará uma tag HTML como esta:

   ```html
   <meta
     name="google-site-verification"
     content="ABC123XYZ..."
   />
   ```

2. **Adicione esta tag ao arquivo `app/layout.tsx`**:

   - Abra `app/layout.tsx`
   - Adicione a tag dentro do `<head>`
   - Exemplo:

   ```tsx
   <head>
     <meta
       name="google-site-verification"
       content="ABC123XYZ..."
     />
     {/* ... outras meta tags ... */}
   </head>
   ```

3. Faça commit e deploy do site
4. Volte ao Google Search Console e clique em **"Verificar"**

### Método 2: Arquivo HTML

1. Baixe o arquivo HTML fornecido pelo Google
2. Faça upload para a pasta `public/` do projeto
3. Faça commit e deploy
4. Clique em **"Verificar"** no Google Search Console

### Método 3: DNS (Para Domínio)

1. Adicione um registro TXT no DNS do seu domínio
2. Use o valor fornecido pelo Google
3. Aguarde propagação (pode levar algumas horas)
4. Clique em **"Verificar"**

---

## 🗺️ Passo 4: Enviar Sitemap

Após verificar a propriedade:

1. No menu lateral, clique em **"Sitemaps"** (Mapa do site)
2. No campo **"Adicionar um novo sitemap"**, digite:
   ```
   sitemap.xml
   ```
   Ou a URL completa:
   ```
   https://cosmoastral.com.br/sitemap.xml
   ```
3. Clique em **"Enviar"** (Submit)

**Status esperado:** ✅ "Enviado com sucesso"

---

## 📊 Passo 5: Verificar Status

Após alguns dias, você poderá ver:

- **Cobertura:** Quantas páginas foram indexadas
- **Performance:** Queries de busca, impressões, cliques
- **Melhorias:** Problemas encontrados pelo Google

---

## 🔍 Passo 6: Testar Rich Results (Opcional)

1. Acesse: https://search.google.com/test/rich-results
2. Cole a URL: `https://cosmoastral.com.br/`
3. Clique em **"Testar URL"**
4. Verifique se o structured data (JSON-LD) é reconhecido

**Resultado esperado:** ✅ Structured data detectado corretamente

---

## 📱 Passo 7: Testar Mobile-Friendly (Opcional)

1. Acesse: https://search.google.com/test/mobile-friendly
2. Cole a URL: `https://cosmoastral.com.br/`
3. Clique em **"Testar URL"**

**Resultado esperado:** ✅ Página é compatível com dispositivos móveis

---

## ⚠️ Troubleshooting

### Problema: Verificação falha

**Soluções:**

- Verifique se a tag HTML está no `<head>` e não no `<body>`
- Aguarde alguns minutos após o deploy
- Limpe o cache do navegador
- Verifique se o site está acessível publicamente

### Problema: Sitemap não encontrado

**Soluções:**

- Verifique se `public/sitemap.xml` existe
- Acesse `https://cosmoastral.com.br/sitemap.xml` no navegador
- Verifique se o arquivo está bem formatado (XML válido)
- Aguarde alguns minutos após o deploy

### Problema: Páginas não indexadas

**Soluções:**

- Verifique se `robots.txt` permite indexação
- Verifique se as páginas têm conteúdo relevante
- Use a ferramenta "Solicitar indexação" no Search Console
- Aguarde alguns dias (indexação pode levar tempo)

---

## 📈 Próximos Passos

Após configurar o Search Console:

1. **Monitorar Performance:**

   - Acompanhe queries de busca
   - Veja quais páginas têm mais cliques
   - Identifique oportunidades de melhoria

2. **Corrigir Problemas:**

   - Resolva erros de rastreamento
   - Corrija páginas com problemas
   - Melhore páginas com baixo desempenho

3. **Otimizar:**
   - Use dados do Search Console para melhorar SEO
   - Crie conteúdo baseado em queries populares
   - Melhore CTR (Click-Through Rate)

---

## ✅ Checklist

- [ ] Propriedade adicionada no Google Search Console
- [ ] Propriedade verificada com sucesso
- [ ] Sitemap enviado: `https://cosmoastral.com.br/sitemap.xml`
- [ ] Sitemap processado com sucesso
- [ ] Rich Results testado (opcional)
- [ ] Mobile-Friendly testado (opcional)

---

## 📚 Referências

- [Google Search Console Help](https://support.google.com/webmasters)
- [Sitemap Guidelines](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)
- [Rich Results Test](https://search.google.com/test/rich-results)
- [Mobile-Friendly Test](https://search.google.com/test/mobile-friendly)

---

**Última atualização:** 2025-01-15  
**Status:** ✅ Guia completo e pronto para uso
