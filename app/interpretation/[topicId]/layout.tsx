import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Interpretação Astrológica Detalhada | CosmoAstral',
  description: 'Descubra interpretações detalhadas dos planetas em seu mapa astral. Análise completa de signos, casas e aspectos planetários.',
  keywords: 'interpretação astrológica, planetas em signos, casas astrológicas, aspectos planetários, análise mapa natal',
  openGraph: {
    title: 'Interpretação Astrológica Detalhada | CosmoAstral',
    description: 'Descubra interpretações detalhadas dos planetas em seu mapa astral.',
    url: 'https://cosmoastral.com.br/interpretation',
  },
  alternates: {
    canonical: 'https://cosmoastral.com.br/interpretation',
  },
};

export default function InterpretationLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
