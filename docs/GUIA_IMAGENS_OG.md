# 🖼️ Guia de Criação de Imagens OG (Open Graph)

Este guia explica como criar as imagens Open Graph para compartilhamento em redes sociais.

---

## 📐 Especificações Técnicas

### og-image.jpg (Open Graph)

- **Dimensões:** 1200 x 630 pixels
- **Formato:** JPG ou PNG
- **Tamanho máximo:** 8 MB (recomendado: < 1 MB)
- **Aspect ratio:** 1.91:1
- **Localização:** `public/og-image.jpg`

### twitter-image.jpg (Twitter Cards)

- **Dimensões:** 1200 x 630 pixels (ou 1200 x 675 para Twitter)
- **Formato:** JPG ou PNG
- **Tamanho máximo:** 5 MB (recomendado: < 1 MB)
- **Aspect ratio:** 1.91:1 ou 16:9
- **Localização:** `public/twitter-image.jpg`

---

## 🎨 Conteúdo Recomendado

### Elementos Essenciais:

1. **Logo/Branding:** CosmoAstral
2. **Título:** "Astrologia Online Grátis"
3. **Subtítulo:** "Mapa Astral Completo e Interpretações"
4. **Visual:** Elementos astrológicos (estrelas, planetas, signos)
5. **Cores:** Seguir paleta do site (tema escuro/espacial)

### Texto Sugerido:

```
CosmoAstral
Astrologia Online Grátis
Mapa Astral Completo e Interpretações
```

---

## 🛠️ Ferramentas para Criar

### Opção 1: Canva (Recomendado - Grátis)

1. Acesse: https://www.canva.com
2. Crie um design: **"Post do Facebook"** (1200x630px)
3. Adicione:
   - Logo CosmoAstral
   - Texto principal
   - Elementos visuais astrológicos
4. Exporte como JPG (alta qualidade)
5. Salve como `og-image.jpg` e `twitter-image.jpg`

### Opção 2: Figma

1. Crie um frame: 1200 x 630px
2. Adicione elementos de design
3. Exporte como JPG ou PNG

### Opção 3: Photoshop / GIMP

1. Crie novo documento: 1200 x 630px
2. Adicione camadas com elementos
3. Exporte como JPG (qualidade 90-95%)

### Opção 4: Placeholder (Temporário)

Se não tiver as imagens prontas, você pode usar um placeholder SVG:

```svg
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="630" fill="#1a1a2e"/>
  <text x="600" y="250" font-family="Arial" font-size="48" fill="#fff" text-anchor="middle">CosmoAstral</text>
  <text x="600" y="320" font-family="Arial" font-size="32" fill="#a0a0a0" text-anchor="middle">Astrologia Online Grátis</text>
  <text x="600" y="380" font-family="Arial" font-size="24" fill="#888" text-anchor="middle">Mapa Astral Completo e Interpretações</text>
</svg>
```

**⚠️ Nota:** Placeholders são temporários. Substitua por imagens profissionais.

---

## 📦 Como Adicionar ao Projeto

### Passo 1: Criar as Imagens

Crie `og-image.jpg` e `twitter-image.jpg` seguindo as especificações acima.

### Passo 2: Colocar na Pasta Public

```
public/
  ├── og-image.jpg
  └── twitter-image.jpg
```

### Passo 3: Verificar URLs

As URLs já estão configuradas em `app/layout.tsx`:

- `https://cosmoastral.com.br/og-image.jpg`
- `https://cosmoastral.com.br/twitter-image.jpg`

### Passo 4: Testar

1. Use o [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
2. Cole a URL: `https://cosmoastral.com.br/`
3. Clique em **"Scrape Again"**
4. Verifique se a imagem aparece corretamente

---

## ✅ Checklist

- [ ] Imagem `og-image.jpg` criada (1200x630px)
- [ ] Imagem `twitter-image.jpg` criada (1200x630px)
- [ ] Imagens salvas em `public/`
- [ ] Tamanho de arquivo < 1 MB cada
- [ ] Imagens testadas no Facebook Sharing Debugger
- [ ] Imagens testadas no Twitter Card Validator

---

## 🔗 Ferramentas de Teste

### Facebook / Open Graph:

- https://developers.facebook.com/tools/debug/

### Twitter Cards:

- https://cards-dev.twitter.com/validator

### LinkedIn:

- https://www.linkedin.com/post-inspector/

---

## 💡 Dicas de Design

1. **Legibilidade:** Texto deve ser legível mesmo em tamanho pequeno
2. **Contraste:** Use cores com bom contraste
3. **Branding:** Mantenha consistência com o site
4. **Simplicidade:** Evite elementos demais
5. **Mobile:** Considere como a imagem aparece em mobile

---

## 📚 Referências

- [Open Graph Protocol](https://ogp.me/)
- [Twitter Cards](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)
- [Facebook Sharing Best Practices](https://developers.facebook.com/docs/sharing/webmasters)

---

**Última atualização:** 2025-01-15  
**Status:** ✅ Guia completo
