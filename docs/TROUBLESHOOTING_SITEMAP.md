# 🔧 Troubleshooting: Sitemap não Reconhecido pelo Google

Este guia ajuda a resolver problemas quando o Google não reconhece o sitemap.

---

## ✅ Verificações Iniciais

### 1. Sitemap Está Acessível?

**Teste manual:**

1. Acesse: `https://cosmoastral.com.br/sitemap.xml`
2. O arquivo deve abrir no navegador mostrando o XML
3. Se retornar 404, o arquivo não está sendo servido corretamente

**Solução:**

- Verifique se `public/sitemap.xml` existe
- No Next.js, arquivos em `public/` são servidos automaticamente
- Verifique se o deploy foi feito corretamente

---

### 2. Content-Type Correto?

O sitemap deve ser servido com `Content-Type: application/xml` ou `text/xml`.

**Teste:**

```bash
curl -I https://cosmoastral.com.br/sitemap.xml
```

**Deve retornar:**

```
Content-Type: application/xml
# ou
Content-Type: text/xml
```

**Se estiver incorreto:**

- No Vercel, arquivos `.xml` em `public/` são servidos automaticamente com o tipo correto
- Se usar outro servidor, configure o Content-Type manualmente

---

### 3. Formato XML Válido?

**Validação local:**

```bash
# Usar o script de validação
python3 validate_sitemap.py
```

**Deve mostrar:**

- ✅ XML bem formado
- ✅ Namespace correto
- ✅ URLs válidas
- ✅ Datas no formato correto

---

### 4. URLs no Sitemap São Acessíveis?

**Teste cada URL:**

1. `https://cosmoastral.com.br/` → Deve retornar 200
2. `https://cosmoastral.com.br/login` → Deve retornar 200
3. `https://cosmoastral.com.br/dashboard` → Deve retornar 200
4. `https://cosmoastral.com.br/interpretation` → Deve retornar 200

**Se alguma URL retornar 404:**

- Remova do sitemap ou corrija a URL
- O Google pode rejeitar sitemaps com URLs inacessíveis

---

## 🔍 Problemas Comuns e Soluções

### Problema 1: "Sitemap não encontrado" no Google Search Console

**Possíveis causas:**

- URL do sitemap incorreta
- Arquivo não está acessível publicamente
- Problema de CORS ou autenticação

**Soluções:**

1. Verifique a URL: `https://cosmoastral.com.br/sitemap.xml`
2. Teste no navegador (deve abrir o XML)
3. Verifique se não há autenticação bloqueando
4. Verifique `robots.txt` (deve permitir acesso ao sitemap)

---

### Problema 2: "Sitemap contém erros"

**Possíveis causas:**

- XML mal formado
- URLs inválidas
- Datas no formato incorreto
- Prioridades fora do range (0.0-1.0)

**Soluções:**

1. Execute: `python3 validate_sitemap.py`
2. Corrija erros encontrados
3. Verifique formato de data: `YYYY-MM-DDThh:mm:ss+00:00`
4. Verifique prioridades: devem estar entre 0.0 e 1.0

---

### Problema 3: "Nenhuma URL indexada"

**Possíveis causas:**

- URLs retornam 404
- URLs bloqueadas por `robots.txt`
- Conteúdo não indexável (JavaScript não renderizado)
- Site muito novo (Google precisa de tempo)

**Soluções:**

1. Verifique se todas as URLs retornam 200
2. Verifique `robots.txt` (não deve bloquear as páginas)
3. Teste renderização JavaScript (Google pode não renderizar JS)
4. Aguarde alguns dias (indexação pode levar tempo)

---

### Problema 4: Sitemap não atualiza no Google

**Possíveis causas:**

- Cache do Google
- `lastmod` não mudou
- Google não re-rastreou ainda

**Soluções:**

1. Atualize `lastmod` para data atual
2. Use "Solicitar indexação" no Search Console
3. Aguarde 24-48 horas para re-rastreamento

---

## 🛠️ Soluções Avançadas

### Opção 1: Sitemap Dinâmico (Next.js)

Se o sitemap estático não funcionar, crie um sitemap dinâmico:

**Criar `app/sitemap.ts`:**

```typescript
import {MetadataRoute} from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = "https://cosmoastral.com.br";

  return [
    {
      url: `${baseUrl}/`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1.0,
    },
    {
      url: `${baseUrl}/login`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${baseUrl}/dashboard`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
    {
      url: `${baseUrl}/interpretation`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.8,
    },
  ];
}
```

**Vantagens:**

- Sempre atualizado automaticamente
- Gerenciado pelo Next.js
- Content-Type correto garantido

---

### Opção 2: Route Handler (Next.js)

**Criar `app/sitemap.xml/route.ts`:**

```typescript
import {NextResponse} from "next/server";

export async function GET() {
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://cosmoastral.com.br/</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <!-- ... outras URLs ... -->
</urlset>`;

  return new NextResponse(sitemap, {
    headers: {
      "Content-Type": "application/xml",
    },
  });
}
```

---

## 📋 Checklist de Validação

Antes de enviar o sitemap ao Google:

- [ ] Sitemap acessível em `https://cosmoastral.com.br/sitemap.xml`
- [ ] XML bem formado (validação passou)
- [ ] Content-Type correto (`application/xml`)
- [ ] Todas as URLs retornam 200 (não 404)
- [ ] URLs são absolutas (começam com `https://`)
- [ ] Datas no formato ISO 8601 (`YYYY-MM-DDThh:mm:ss+00:00`)
- [ ] Prioridades entre 0.0 e 1.0
- [ ] `changefreq` válido (always, hourly, daily, weekly, monthly, yearly, never)
- [ ] `robots.txt` permite indexação
- [ ] Sitemap não excede 50MB ou 50.000 URLs

---

## 🔗 Ferramentas Úteis

### Validação Online:

- [XML Validator](https://www.xmlvalidation.com/)
- [Sitemap Validator](https://www.xml-sitemaps.com/validate-xml-sitemap.html)

### Teste de Acessibilidade:

- [Google Search Console](https://search.google.com/search-console)
- [Bing Webmaster Tools](https://www.bing.com/webmasters)

### Debug:

- `curl -I https://cosmoastral.com.br/sitemap.xml` (verificar headers)
- `python3 validate_sitemap.py` (validação local)

---

## 📚 Referências

- [Google Sitemap Guidelines](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Next.js Sitemap](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap)
- [Sitemap Protocol](https://www.sitemaps.org/protocol.html)

---

**Última atualização:** 2025-12-17  
**Status:** ✅ Guia completo de troubleshooting
