import type { Metadata } from 'next';
import { LandingPageClient } from './landing-client';

export const metadata: Metadata = {
  title: 'Astrologia Online Grátis - Mapa Astral Completo | CosmoAstral',
  description: 'Descubra os segredos das estrelas e transforme sua vida. Acesso 100% gratuito ao seu mapa astral completo com interpretações personalizadas de astrologia e numerologia.',
  keywords: 'astrologia online, mapa astral grátis, astrologia, numerologia, mapa natal, horóscopo personalizado, calcular mapa astral, astrologia brasileira',
  openGraph: {
    title: 'Astrologia Online Grátis - Mapa Astral Completo | CosmoAstral',
    description: 'Descubra os segredos das estrelas e transforme sua vida. Acesso 100% gratuito ao seu mapa astral completo com interpretações personalizadas.',
    url: 'https://cosmoastral.com.br/',
  },
  alternates: {
    canonical: 'https://cosmoastral.com.br/',
  },
};

export default function HomePage() {
  return <LandingPageClient />;
}
