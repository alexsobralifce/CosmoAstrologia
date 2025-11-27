import React, { useState, useEffect } from 'react';
import { AstroCard } from './astro-card';
import { planets } from './planet-icons';
import { Badge } from './ui/badge';
import { UIIcons } from './ui-icons';
import { apiService } from '../services/api';

interface Transit {
  id: string;
  type: 'jupiter' | 'saturn-return' | 'uranus' | 'neptune' | 'pluto';
  title: string;
  planet: string;
  timeframe: string;
  description: string;
  isActive?: boolean;
}

interface FutureTransitsSectionProps {
  transits?: Transit[];
}

const defaultTransits: Transit[] = [
  {
    id: '1',
    type: 'jupiter',
    title: 'Expansão e Sorte: Júpiter entra em Touro',
    planet: 'Júpiter',
    timeframe: 'Próximos 3-6 meses',
    description: 'Júpiter transitará sua Casa 9, trazendo oportunidades de crescimento através de viagens, educação superior e filosofia. É o melhor momento para se matricular em um curso ou planejar uma grande viagem.',
    isActive: false
  },
  {
    id: '2',
    type: 'saturn-return',
    title: 'Marco de Amadurecimento: Seu Retorno de Saturno',
    planet: 'Saturno',
    timeframe: 'Próximos 1-2 anos',
    description: 'Saturno está retornando à sua posição de nascimento em Capricórnio na Casa 5. Este é um período de grandes lições de vida sobre criatividade, autoexpressão e romance. Você será recompensado por estruturar seus hobbies e levar sua alegria a sério.',
    isActive: true
  },
  {
    id: '3',
    type: 'uranus',
    title: 'Mudança e Inovação: Urano em quadratura com seu Sol',
    planet: 'Urano',
    timeframe: 'Próximo Ano',
    description: 'Prepare-se para eventos inesperados e mudanças súbitas que desafiam seu senso de identidade (Sol). Sua necessidade de liberdade e independência será alta. Não resista à mudança; use-a para inovar.',
    isActive: false
  }
];

export const FutureTransitsSection = ({ transits: propTransits }: FutureTransitsSectionProps) => {
  const [transits, setTransits] = useState<Transit[]>(defaultTransits);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Se transits foram passados como prop, usar eles
    if (propTransits && propTransits.length > 0) {
      setTransits(propTransits);
      setIsLoading(false);
      return;
    }

    // Caso contrário, buscar do backend
    const fetchTransits = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await apiService.getFutureTransits({
          months_ahead: 24,
          max_transits: 10
        });
        
        if (response.transits && response.transits.length > 0) {
          setTransits(response.transits);
        } else {
          // Se não houver trânsitos, usar os padrão
          setTransits(defaultTransits);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
        // Log apenas se não for timeout (timeout é esperado em algumas situações)
        if (!errorMessage.includes('Tempo de espera esgotado')) {
          console.error('Erro ao buscar trânsitos:', err);
        }
        setError('Não foi possível carregar os trânsitos futuros');
        // Usar transits padrão em caso de erro
        setTransits(defaultTransits);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTransits();
  }, [propTransits]);
  const getTypeColor = (type: Transit['type']) => {
    const colors = {
      'jupiter': 'text-[#E8B95A]',
      'saturn-return': 'text-[#8B7355]',
      'uranus': 'text-[#4ECDC4]',
      'neptune': 'text-[#9B59B6]',
      'pluto': 'text-[#E74C3C]'
    };
    return colors[type] || 'text-accent';
  };

  const getTypeBadgeStyle = (type: Transit['type']) => {
    const styles = {
      'jupiter': 'bg-[#E8B95A]/10 text-[#E8B95A] border-[#E8B95A]/30',
      'saturn-return': 'bg-[#8B7355]/10 text-[#8B7355] border-[#8B7355]/30',
      'uranus': 'bg-[#4ECDC4]/10 text-[#4ECDC4] border-[#4ECDC4]/30',
      'neptune': 'bg-[#9B59B6]/10 text-[#9B59B6] border-[#9B59B6]/30',
      'pluto': 'bg-[#E74C3C]/10 text-[#E74C3C] border-[#E74C3C]/30'
    };
    return styles[type] || 'bg-accent/10 text-accent border-accent/30';
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-accent mb-1" style={{ fontFamily: 'var(--font-serif)' }}>
          Horizontes Futuros
        </h2>
        <p className="text-sm text-muted-foreground">
          Trânsitos de longo prazo que moldarão sua jornada
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <AstroCard>
          <div className="flex items-center justify-center gap-3 py-8">
            <UIIcons.Loader className="w-5 h-5 animate-spin text-accent" />
            <p className="text-secondary">Calculando trânsitos futuros...</p>
          </div>
        </AstroCard>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <AstroCard className="border-destructive/30">
          <div className="flex items-center gap-3 text-destructive">
            <UIIcons.AlertCircle size={20} />
            <p className="text-sm">{error}</p>
          </div>
        </AstroCard>
      )}

      {/* Timeline Vertical com scrollbar */}
      {!isLoading && !error && (
        <div className="relative pl-8 space-y-6 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
          {/* Linha vertical */}
          <div className="absolute left-3 top-2 bottom-2 w-0.5 bg-gradient-to-b from-accent via-accent/50 to-accent/10"></div>

          {transits.length === 0 ? (
            <AstroCard>
              <p className="text-secondary text-center py-4">
                Nenhum trânsito significativo encontrado no período calculado.
              </p>
            </AstroCard>
          ) : (
            transits.map((transit, index) => {
              const PlanetIcon = planets.find(p => p.name === transit.planet)?.icon;
              
              return (
                <div 
                  key={transit.id} 
                  className="relative animate-fadeIn"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  {/* Ponto na timeline */}
                  <div className={`absolute -left-[29px] top-6 w-5 h-5 rounded-full border-2 border-accent ${
                    transit.isActive ? 'bg-accent' : 'bg-background'
                  } flex items-center justify-center`}>
                    {transit.isActive && (
                      <div className="w-2 h-2 rounded-full bg-background animate-pulse"></div>
                    )}
                  </div>

                  <AstroCard className="hover:border-accent/40 transition-all duration-300 hover:shadow-lg hover:shadow-accent/10 animate-fadeIn">
                    <div className="space-y-4">
                      {/* Header */}
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3 flex-1">
                          {PlanetIcon && (
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                              transit.type === 'jupiter' ? 'bg-[#E8B95A]/20' :
                              transit.type === 'saturn-return' ? 'bg-[#8B7355]/20' :
                              transit.type === 'uranus' ? 'bg-[#4ECDC4]/20' :
                              transit.type === 'neptune' ? 'bg-[#9B59B6]/20' :
                              'bg-[#E74C3C]/20'
                            }`}>
                              <PlanetIcon size={28} className={getTypeColor(transit.type)} />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <h3 className="text-foreground font-semibold text-base mb-2">{transit.title}</h3>
                            <div className="flex flex-wrap items-center gap-2">
                              <Badge variant="outline" className={getTypeBadgeStyle(transit.type)}>
                                📅 {transit.timeframe}
                              </Badge>
                              {transit.isActive && (
                                <Badge variant="outline" className="bg-accent/20 text-accent border-accent/40">
                                  ⚡ Em Progresso
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Descrição - cor preta/foreground para melhor legibilidade */}
                      <div className="border-l-2 border-accent/30 pl-4 py-2 bg-muted/30 rounded-r-lg">
                        <p className="text-sm text-foreground leading-relaxed">
                          {transit.description}
                        </p>
                      </div>

                      {/* Tags do Tipo de Trânsito */}
                      <div className="flex items-center gap-2 pt-2">
                        <span className="text-xs text-muted-foreground">Tipo:</span>
                        <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                          transit.type === 'jupiter' ? 'bg-[#E8B95A]/10 text-[#E8B95A]' :
                          transit.type === 'saturn-return' ? 'bg-[#8B7355]/10 text-[#8B7355]' :
                          transit.type === 'uranus' ? 'bg-[#4ECDC4]/10 text-[#4ECDC4]' :
                          transit.type === 'neptune' ? 'bg-[#9B59B6]/10 text-[#9B59B6]' :
                          'bg-[#E74C3C]/10 text-[#E74C3C]'
                        }`}>
                          {transit.type === 'jupiter' ? '🌟 Expansão' :
                           transit.type === 'saturn-return' ? '🏛️ Retorno de Saturno' :
                           transit.type === 'uranus' ? '⚡ Mudança Súbita' :
                           transit.type === 'neptune' ? '🌊 Espiritualidade' :
                           '🔥 Transformação'}
                        </span>
                      </div>
                    </div>
                  </AstroCard>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Footer informativo */}
      <AstroCard className="bg-muted/20 border-muted-foreground/20">
        <div className="flex items-start gap-3">
          <UIIcons.Info size={20} className="text-muted-foreground mt-0.5 flex-shrink-0" />
          <p className="text-sm text-muted-foreground">
            <span className="font-medium text-foreground">Dica:</span> Os trânsitos de planetas lentos 
            (Júpiter, Saturno, Urano, Netuno e Plutão) criam os grandes temas e lições de vida. Use 
            este conhecimento para planejar estrategicamente e surfar as ondas cósmicas.
          </p>
        </div>
      </AstroCard>
    </div>
  );
};
