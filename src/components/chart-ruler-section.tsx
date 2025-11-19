import { useState, useEffect } from 'react';
import { AstroCard } from './astro-card';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { apiService } from '../services/api';
import { UIIcons } from './ui-icons';

interface ChartRulerSectionProps {
  ascendant: string;
  ruler: string;
  rulerSign: string;
  rulerHouse: number;
}

export const ChartRulerSection = ({ ascendant, ruler, rulerSign, rulerHouse }: ChartRulerSectionProps) => {
  const [interpretation, setInterpretation] = useState<{
    concept: string;
    positioning: string;
    influence: string;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const AscendantIcon = zodiacSigns.find(z => z.name === ascendant)?.icon;
  const RulerIcon = planets.find(p => p.name === ruler)?.icon;
  const RulerSignIcon = zodiacSigns.find(z => z.name === rulerSign)?.icon;

  useEffect(() => {
    const fetchInterpretation = async () => {
      try {
        setIsLoading(true);
        const response = await apiService.getChartRulerInterpretation({
          ascendant,
          ruler,
          rulerSign,
          rulerHouse,
        });

        // Parsear a interpretação do Groq em seções
        const interpretationText = response.interpretation;
        
        // Extrair conceito, posicionamento e influência da resposta
        const concept = `Seu Ascendente é ${ascendant}, portanto, seu planeta regente é ${ruler}.`;
        const positioning = `No seu mapa, ${ruler} está em ${rulerSign} na sua Casa ${rulerHouse}.`;
        
        // Usar a interpretação do Groq como influência
        const influence = interpretationText || `Este posicionamento revela aspectos fundamentais sobre sua jornada de vida e como você expressa sua essência no mundo. O planeta regente atua como seu guia cósmico, influenciando sua abordagem à vida e suas prioridades naturais.`;

        setInterpretation({
          concept,
          positioning,
          influence,
        });
      } catch (error) {
        console.error('Erro ao buscar interpretação do regente:', error);
        // Fallback para interpretação padrão
        setInterpretation({
          concept: `Seu Ascendente é ${ascendant}, portanto, seu planeta regente é ${ruler}.`,
          positioning: `No seu mapa, ${ruler} está em ${rulerSign} na sua Casa ${rulerHouse}.`,
          influence: `Este posicionamento revela aspectos fundamentais sobre sua jornada de vida e como você expressa sua essência no mundo. O planeta regente atua como seu guia cósmico, influenciando sua abordagem à vida e suas prioridades naturais.`
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchInterpretation();
  }, [ascendant, ruler, rulerSign, rulerHouse]);

  if (isLoading || !interpretation) {
    return (
      <AstroCard className="border border-accent/30 shadow-lg shadow-accent/10">
        <div className="flex items-center justify-center gap-3 py-8">
          <UIIcons.Loader className="w-5 h-5 animate-spin text-accent" />
          <p className="text-secondary">Gerando interpretação do regente...</p>
        </div>
      </AstroCard>
    );
  }

  return (
    <AstroCard className="border border-accent/30 shadow-lg shadow-accent/10">
      <div className="space-y-6">
        {/* Título */}
        <div>
          <h2 className="text-accent mb-1" style={{ fontFamily: 'var(--font-serif)' }}>
            Seu Guia Pessoal: O Regente do Mapa
          </h2>
          <p className="text-sm text-muted-foreground">
            O planeta que guia sua jornada de vida
          </p>
        </div>

        {/* Conceito Principal */}
        <div className="relative overflow-hidden flex items-start gap-4 p-5 rounded-lg bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/30 shadow-lg shadow-accent/5">
          {/* Decorative glow */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-accent/5 rounded-full blur-3xl"></div>
          
          <div className="flex gap-3 items-center mt-1 relative z-10">
            {AscendantIcon && <AscendantIcon size={36} className="text-accent drop-shadow-lg" />}
            <span className="text-2xl text-muted-foreground">→</span>
            {RulerIcon && <RulerIcon size={36} className="text-accent drop-shadow-lg" />}
          </div>
          <div className="flex-1 relative z-10">
            <p className="text-foreground">{interpretation.concept}</p>
          </div>
        </div>

        {/* Posicionamento */}
        <div className="flex items-start gap-4 p-4 rounded-lg bg-card/50">
          <div className="flex gap-2 items-center mt-1">
            {RulerIcon && <RulerIcon size={28} className="text-accent" />}
            <span className="text-muted-foreground">em</span>
            {RulerSignIcon && <RulerSignIcon size={28} className="text-secondary" />}
          </div>
          <div className="flex-1">
            <h3 className="text-foreground mb-2">Posicionamento no Mapa</h3>
            <p className="text-secondary">{interpretation.positioning}</p>
          </div>
        </div>

        {/* Influência Prática */}
        <div className="space-y-3">
          <h3 className="text-foreground" style={{ fontFamily: 'var(--font-sans)' }}>
            A Influência Prática (O que isso significa):
          </h3>
          <p className="text-secondary leading-relaxed">
            {interpretation.influence}
          </p>
        </div>
      </div>
    </AstroCard>
  );
};
