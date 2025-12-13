import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Astrologia Online Grátis - Faça Login | CosmoAstral',
  description: 'Acesse sua conta no CosmoAstral e descubra seu mapa astral completo. Calcule seu mapa natal e receba interpretações personalizadas de astrologia.',
  keywords: 'astrologia online, login astrologia, mapa astral, calcular mapa natal, astrologia grátis',
  openGraph: {
    title: 'Astrologia Online Grátis - Faça Login | CosmoAstral',
    description: 'Acesse sua conta no CosmoAstral e descubra seu mapa astral completo.',
    url: 'https://cosmoastral.com.br/login',
  },
  alternates: {
    canonical: 'https://cosmoastral.com.br/login',
  },
};

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
