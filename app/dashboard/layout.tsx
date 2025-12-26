import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Dashboard - Seu Mapa Astral Completo | CosmoAstral',
  description: 'Visualize seu mapa astral completo com interpretações detalhadas de planetas, signos e casas. Receba conselhos diários baseados em trânsitos planetários.',
  keywords: 'mapa astral completo, dashboard astrologia, interpretação astrológica, trânsitos planetários, mapa natal',
  openGraph: {
    title: 'Dashboard - Seu Mapa Astral Completo | CosmoAstral',
    description: 'Visualize seu mapa astral completo com interpretações detalhadas de planetas, signos e casas.',
    url: 'https://cosmoastral.com.br/dashboard',
  },
  alternates: {
    canonical: 'https://cosmoastral.com.br/dashboard',
  },
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
