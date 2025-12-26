import { useEffect } from 'react';

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string;
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  canonicalUrl?: string;
}

/**
 * Componente para gerenciar meta tags dinâmicas de SEO
 * Atualiza as meta tags da página baseado no contexto atual
 */
export function SEOHead({
  title = 'Astrologia Online Grátis - Mapa Astral Completo | Cosmos Astral',
  description = 'Plataforma completa de astrologia online gratuita. Calcule seu mapa astral, descubra interpretações detalhadas de planetas, signos e casas. Conselhos diários baseados em trânsitos planetários.',
  keywords = 'astrologia, astrologia online, astrologia grátis, mapa astral, mapa natal, horóscopo, signos, planetas, casas astrológicas',
  ogTitle,
  ogDescription,
  ogImage = 'https://cosmoastral.com.br/og-image.jpg',
  canonicalUrl = 'https://cosmoastral.com.br/',
}: SEOHeadProps) {
  useEffect(() => {
    // Atualizar título
    if (title) {
      document.title = title;
      updateMetaTag('title', title);
    }

    // Atualizar description
    updateMetaTag('description', description, 'name');

    // Atualizar keywords
    if (keywords) {
      updateMetaTag('keywords', keywords, 'name');
    }

    // Atualizar Open Graph
    updateMetaTag('og:title', ogTitle || title, 'property');
    updateMetaTag('og:description', ogDescription || description, 'property');
    if (ogImage) {
      updateMetaTag('og:image', ogImage, 'property');
    }
    updateMetaTag('og:url', canonicalUrl, 'property');

    // Atualizar Twitter Cards
    updateMetaTag('twitter:title', ogTitle || title, 'name');
    updateMetaTag('twitter:description', ogDescription || description, 'name');
    if (ogImage) {
      updateMetaTag('twitter:image', ogImage, 'name');
    }

    // Atualizar canonical URL
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', canonicalUrl);

    // Adicionar structured data (JSON-LD) para melhor SEO
    addStructuredData({
      title: ogTitle || title,
      description: ogDescription || description,
      url: canonicalUrl,
      image: ogImage,
    });
  }, [title, description, keywords, ogTitle, ogDescription, ogImage, canonicalUrl]);

  return null; // Componente não renderiza nada
}

/**
 * Adiciona structured data (JSON-LD) para melhor indexação no Google
 */
function addStructuredData(data: {
  title: string;
  description: string;
  url: string;
  image?: string;
}) {
  // Remover structured data anterior se existir
  const existingScript = document.querySelector('script[type="application/ld+json"][data-seo="true"]');
  if (existingScript) {
    existingScript.remove();
  }

  // Criar novo structured data
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: data.title,
    description: data.description,
    url: data.url,
    applicationCategory: 'LifestyleApplication',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'BRL',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.8',
      ratingCount: '150',
    },
    ...(data.image && {
      image: data.image,
    }),
  };

  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.setAttribute('data-seo', 'true');
  script.textContent = JSON.stringify(structuredData);
  document.head.appendChild(script);
}

/**
 * Função auxiliar para atualizar ou criar meta tags
 */
function updateMetaTag(property: string, content: string, attribute: 'name' | 'property' = 'property') {
  let meta = document.querySelector(`meta[${attribute}="${property}"]`);
  
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute(attribute, property);
    document.head.appendChild(meta);
  }
  
  meta.setAttribute('content', content);
}

/**
 * Hook para atualizar SEO baseado na view atual
 */
export function useSEO(view: string, additionalData?: Record<string, string>) {
  useEffect(() => {
    const seoConfig: Record<string, SEOHeadProps> = {
      landing: {
        title: 'Astrologia Online Grátis - Mapa Astral Completo | CosmoAstral',
        description: 'Descubra os segredos das estrelas e transforme sua vida. Acesso 100% gratuito ao seu mapa astral completo com interpretações personalizadas de astrologia e numerologia.',
        keywords: 'astrologia online, mapa astral grátis, astrologia, numerologia, mapa natal, horóscopo personalizado, calcular mapa astral, astrologia brasileira',
        canonicalUrl: 'https://cosmoastral.com.br/',
      },
      auth: {
        title: 'Astrologia Online Grátis - Faça Login | CosmoAstral',
        description: 'Acesse sua conta no CosmoAstral e descubra seu mapa astral completo. Calcule seu mapa natal e receba interpretações personalizadas de astrologia.',
        keywords: 'astrologia online, login astrologia, mapa astral, calcular mapa natal',
        canonicalUrl: 'https://cosmoastral.com.br/login',
      },
      dashboard: {
        title: 'Dashboard - Seu Mapa Astral Completo | CosmoAstral',
        description: 'Visualize seu mapa astral completo com interpretações detalhadas de planetas, signos e casas. Receba conselhos diários baseados em trânsitos planetários.',
        keywords: 'mapa astral completo, dashboard astrologia, interpretação astrológica, trânsitos planetários',
        canonicalUrl: 'https://cosmoastral.com.br/dashboard',
      },
      interpretation: {
        title: 'Interpretação Astrológica Detalhada | CosmoAstral',
        description: 'Descubra interpretações detalhadas dos planetas em seu mapa astral. Análise completa de signos, casas e aspectos planetários.',
        keywords: 'interpretação astrológica, planetas em signos, casas astrológicas, aspectos planetários',
        canonicalUrl: 'https://cosmoastral.com.br/interpretation',
      },
    };

    const config = seoConfig[view] || seoConfig.landing;
    
    // Aplicar SEO
    if (config.title) document.title = config.title;
    if (config.description) updateMetaTag('description', config.description, 'name');
    if (config.keywords) updateMetaTag('keywords', config.keywords, 'name');
    if (config.ogTitle) updateMetaTag('og:title', config.ogTitle, 'property');
    if (config.ogDescription) updateMetaTag('og:description', config.ogDescription, 'property');
  }, [view, additionalData]);
}

