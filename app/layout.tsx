import type { Metadata } from 'next';
import { ThemeProvider } from '@/components/theme-provider';
import { LanguageProvider } from '@/i18n';
import { Toaster } from '@/components/ui/sonner';
import { ScrollToTop } from '@/components/scroll-to-top';
import Script from 'next/script';
import '@/index.css';

export const metadata: Metadata = {
  title: {
    default: 'Astrologia Online Grátis - Mapa Astral Completo e Interpretações | CosmoAstral',
    template: '%s | CosmoAstral',
  },
  description: 'Astrologia gratuita e profissional. Calcule seu mapa astral completo grátis, descubra seu mapa natal com interpretações detalhadas de planetas, signos e casas. Receba conselhos diários baseados em trânsitos planetários. Revolução Solar, Sinastria, Numerologia e muito mais. A melhor plataforma de astrologia online do Brasil.',
  keywords: [
    'astrologia',
    'astrologia online',
    'astrologia grátis',
    'astrologia brasileira',
    'mapa astral',
    'mapa astral grátis',
    'mapa astral completo',
    'mapa natal',
    'calcular mapa astral',
    'calcular mapa natal',
    'horóscopo',
    'horóscopo personalizado',
    'horóscopo diário',
    'interpretação astrológica',
    'interpretação mapa natal',
    'signos',
    'signos do zodíaco',
    'meu signo',
    'qual meu signo',
    'planetas',
    'planetas em signos',
    'casas astrológicas',
    'trânsitos planetários',
    'trânsitos astrológicos',
    'revolução solar',
    'retorno solar',
    'sinastria',
    'compatibilidade astrológica',
    'numerologia',
    'mapa numerológico',
    'ascendente',
    'meio do céu',
    'regente do mapa',
    'aspectos planetários',
    'astrologia karmica',
    'astrologia védica',
    'astrologia ocidental',
  ],
  authors: [{ name: 'CosmoAstral' }],
  creator: 'CosmoAstral',
  publisher: 'CosmoAstral',
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: 'https://cosmoastral.com.br/',
    siteName: 'CosmoAstral',
    title: 'Astrologia Online Grátis - Mapa Astral Completo | CosmoAstral',
    description: 'Plataforma completa de astrologia online gratuita. Calcule seu mapa astral grátis, descubra interpretações detalhadas de planetas, signos e casas. Revolução Solar, Sinastria, Numerologia. Conselhos diários baseados em trânsitos planetários.',
    images: [
      {
        url: 'https://cosmoastral.com.br/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'CosmoAstral - Astrologia Online',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Astrologia Online Grátis - Mapa Astral Completo',
    description: 'Plataforma completa de astrologia online. Calcule seu mapa astral, receba interpretações detalhadas e conselhos diários baseados em trânsitos planetários.',
    images: ['https://cosmoastral.com.br/twitter-image.jpg'],
  },
  alternates: {
    canonical: 'https://cosmoastral.com.br/',
  },
  metadataBase: new URL('https://cosmoastral.com.br'),
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <link rel="icon" type="image/svg+xml" href="/vite.svg" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="theme-color" content="#1a1a2e" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="CosmoAstral" />
        
        {/* Schema.org Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebApplication',
              name: 'CosmoAstral - Astrologia Online',
              alternateName: 'CosmoAstral',
              description: 'Plataforma completa de astrologia online gratuita. Calcule seu mapa astral completo, descubra interpretações detalhadas de planetas, signos e casas astrológicas. Receba conselhos diários baseados em trânsitos planetários.',
              url: 'https://cosmoastral.com.br',
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
              featureList: [
                'Mapa astral personalizado e completo',
                'Cálculo preciso de mapa natal',
                'Interpretações detalhadas de planetas em signos e casas',
                'Análise de aspectos planetários',
                'Conselhos diários baseados em trânsitos',
                'Visualização interativa do mapa natal',
                'Análise de ascendente, sol e lua',
                'Interpretação de casas astrológicas',
                'Revolução Solar',
                'Sinastria e compatibilidade',
                'Numerologia',
                'Trânsitos futuros',
              ],
            }),
          }}
        />
      </head>
      <body>
        <ThemeProvider>
          <LanguageProvider>
            {children}
            <Toaster richColors position="top-center" />
            <ScrollToTop />
          </LanguageProvider>
        </ThemeProvider>
        <Script
          src="https://accounts.google.com/gsi/client"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
