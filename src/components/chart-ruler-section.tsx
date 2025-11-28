import React, { useState, useEffect } from 'react';
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
  const [detailedInterpretation, setDetailedInterpretation] = useState<string>('');
  const [showDetailed, setShowDetailed] = useState(false);
  const [loadingDetailed, setLoadingDetailed] = useState(false);

  const AscendantIcon = zodiacSigns.find(z => z.name === ascendant)?.icon;
  const RulerIcon = planets.find(p => p.name === ruler)?.icon;
  const RulerSignIcon = zodiacSigns.find(z => z.name === rulerSign)?.icon;

  // Função para formatar o texto organizando por tópicos
  const formatTextByTopics = (text: string): React.ReactNode => {
    if (!text) return null;

    // Dividir o texto em parágrafos
    const paragraphs = text.split('\n').filter(p => p.trim());
    
    // Identificar tópicos (números, bullets, títulos em negrito, etc.)
    const formattedParagraphs: React.ReactNode[] = [];
    
    paragraphs.forEach((paragraph, index) => {
      const trimmed = paragraph.trim();
      if (!trimmed) return;

      // Verificar se é um tópico numerado (1., 2., etc.)
      const numberedMatch = trimmed.match(/^(\d+)[\.\)]\s*(.+)$/);
      // Verificar se é um bullet (-, •, etc.)
      const bulletMatch = trimmed.match(/^[-•*]\s*(.+)$/);
      // Verificar se é um título (texto em negrito ou em maiúsculas curtas)
      const titleMatch = trimmed.match(/^([A-ZÁÊÇ][A-ZÁÊÇ\s]{2,30}):?\s*$/);
      // Verificar se contém texto em negrito (markdown **texto**)
      const boldMatch = trimmed.match(/\*\*(.+?)\*\*/);

      if (numberedMatch) {
        // Tópico numerado
        formattedParagraphs.push(
          <div key={index} className="mb-4">
            <p className="text-foreground/90 leading-relaxed">
              <span className="font-semibold text-foreground">{numberedMatch[1]}.</span> {numberedMatch[2]}
            </p>
          </div>
        );
      } else if (bulletMatch) {
        // Tópico com bullet
        formattedParagraphs.push(
          <div key={index} className="mb-4 ml-4">
            <p className="text-foreground/90 leading-relaxed">
              <span className="text-accent mr-2">•</span> {bulletMatch[1]}
            </p>
          </div>
        );
      } else if (boldMatch || (titleMatch && trimmed.length < 50)) {
        // Título ou texto em negrito
        const content = boldMatch ? trimmed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') : trimmed;
        formattedParagraphs.push(
          <div key={index} className="mb-4">
            <p 
              className="font-semibold text-foreground mb-2" 
              dangerouslySetInnerHTML={{ __html: content }}
            />
          </div>
        );
      } else {
        // Parágrafo normal
        formattedParagraphs.push(
          <div key={index} className="mb-4">
            <p className="text-foreground/90 leading-relaxed">{trimmed}</p>
          </div>
        );
      }
    });

    return <div className="space-y-1">{formattedParagraphs}</div>;
  };

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
        const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
        // Log apenas se não for timeout (timeout é esperado em algumas situações)
        if (!errorMessage.includes('Tempo de espera esgotado')) {
          console.error('Erro ao buscar interpretação do regente:', error);
        }
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

  const loadDetailedInterpretation = async () => {
    if (loadingDetailed || detailedInterpretation) {
      setShowDetailed(true);
      return;
    }

    try {
      setLoadingDetailed(true);
      
      // Construir query específica sobre o regente
      const query = `regente do mapa ${ruler} em ${rulerSign} casa ${rulerHouse} significado interpretação orientação autoconhecimento características personalidade comportamento influência prática vida`;
      
      const result = await apiService.getInterpretation({
        custom_query: query,
        use_groq: true,
      });

      if (result.interpretation) {
        // Limpar a interpretação
        let cleanInterpretation = result.interpretation;
        
        // Remover referências a fontes e contexto
        cleanInterpretation = cleanInterpretation.replace(/\[Fonte:[^\]]+\]/g, '');
        cleanInterpretation = cleanInterpretation.replace(/--- Documento \d+[^-]+---/g, '');
        cleanInterpretation = cleanInterpretation.replace(/Fonte:[^\n]+/g, '');
        cleanInterpretation = cleanInterpretation.replace(/Página \d+/g, '');
        cleanInterpretation = cleanInterpretation.replace(/Contexto da consulta:[^\n]+/g, '');
        
        // Melhorar formatação
        cleanInterpretation = cleanInterpretation
          .replace(/\*\*(.*?)\*\*/g, '$1')
          .replace(/\n{3,}/g, '\n\n')
          .trim();

        if (cleanInterpretation && cleanInterpretation.length > 50) {
          setDetailedInterpretation(cleanInterpretation);
        } else {
          setDetailedInterpretation('Não foi possível carregar informações detalhadas sobre o regente no momento. Tente novamente mais tarde.');
        }
      } else {
        setDetailedInterpretation('Não foi possível carregar informações detalhadas sobre o regente no momento. Tente novamente mais tarde.');
      }
      
      setShowDetailed(true);
    } catch (error: any) {
      console.error('Erro ao carregar interpretação detalhada:', error);
      setDetailedInterpretation('Erro ao carregar informações detalhadas. Tente novamente mais tarde.');
      setShowDetailed(true);
    } finally {
      setLoadingDetailed(false);
    }
  };

  if (isLoading || !interpretation) {
    return (
      <AstroCard className="border border-accent/30 shadow-lg shadow-accent/10">
        <div className="flex items-center justify-center gap-3 py-8">
          <UIIcons.Loader className="w-5 h-5 animate-spin text-accent" />
          <p className="text-muted-foreground">Gerando interpretação do regente...</p>
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
        <div className="flex items-start gap-4 p-4 rounded-lg bg-card/50 border border-border/30">
          <div className="flex gap-2 items-center mt-1">
            {RulerIcon && <RulerIcon size={28} className="text-accent" />}
            <span className="text-muted-foreground">em</span>
            {RulerSignIcon && <RulerSignIcon size={28} className="text-primary" />}
          </div>
          <div className="flex-1">
            <h3 className="text-foreground mb-2">Posicionamento no Mapa</h3>
            <p className="text-foreground/90">{interpretation.positioning}</p>
          </div>
        </div>

        {/* Botão Leia mais */}
        <div className="pt-2">
          <button
            onClick={loadDetailedInterpretation}
            disabled={loadingDetailed}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-accent hover:text-accent/80 bg-accent/10 hover:bg-accent/20 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loadingDetailed ? (
              <>
                <UIIcons.Loader className="w-4 h-4 animate-spin" />
                Carregando...
              </>
            ) : (
              <>
                <UIIcons.BookOpen className="w-4 h-4" />
                Leia mais
              </>
            )}
          </button>
        </div>

        {/* Interpretação Detalhada */}
        {showDetailed && (
          <div className="space-y-4 p-4 rounded-lg bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/20">
            <div className="flex items-center justify-between">
              <h4 className="text-accent font-medium" style={{ fontFamily: 'var(--font-sans)' }}>
                A Influência Prática (O que isso significa):
              </h4>
              <button
                onClick={() => setShowDetailed(false)}
                className="p-1 text-muted-foreground hover:text-foreground transition-colors"
              >
                <UIIcons.X className="w-4 h-4" />
              </button>
            </div>
            <div className="prose prose-sm max-w-none text-foreground/90">
              {formatTextByTopics(detailedInterpretation)}
            </div>
          </div>
        )}
      </div>
    </AstroCard>
  );
};
