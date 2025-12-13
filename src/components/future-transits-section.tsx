import React, { useState, useEffect } from 'react';
import { AstroCard } from './astro-card';
import { planets } from './planet-icons';
import { UIIcons } from './ui-icons';
import { apiService } from '../services/api';
import '../styles/transits-section.css';

interface Transit {
  id: string;
  type: 'jupiter' | 'saturn-return' | 'uranus' | 'neptune' | 'pluto';
  title: string;
  planet: string;
  timeframe: string;
  description: string;
  isActive?: boolean;
  start_date?: string;
  end_date?: string;
  aspect_type?: string;
  aspect_type_display?: string;
  natal_point?: string;
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
  const [currentTransits, setCurrentTransits] = useState<any[]>([]);
  const [moonVoid, setMoonVoid] = useState<{
    is_void: boolean;
    void_end?: string;
    void_start?: string;
    next_aspect?: string;
    next_aspect_time?: string;
    current_moon_sign?: string;
    void_duration_hours?: number;
  } | null>(null);
  const [isLoadingCurrent, setIsLoadingCurrent] = useState(true);

  // Função para formatar data
  const formatDate = (dateString: string): string => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      const months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
      return `${date.getDate()} de ${months[date.getMonth()]} de ${date.getFullYear()}`;
    } catch {
      return dateString;
    }
  };

  // Função para formatar data apenas com números (usada na timeline horizontal)
  const formatDateShort = (dateString: string): string => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
    } catch {
      return dateString;
    }
  };

  // Função para formatar texto da descrição (markdown simples)
  const formatDescription = (text: string): React.ReactNode => {
    if (!text) return null;

    // Dividir por linhas duplas (parágrafos), mas manter estrutura
    const sections = text.split(/\n\n+/);
    
    return (
      <div className="transits-transit-description-container">
        {sections.map((section, index) => {
          const trimmed = section.trim();
          if (!trimmed) return null;

          // Remover todos os asteriscos do texto primeiro
          let cleanedText = trimmed
            .replace(/\*\*([^*]+?)\*\*/g, '$1') // Remove **texto**
            .replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '$1') // Remove *texto* (itálico)
            .replace(/^\*+\s*|\s*\*+$/g, '') // Remove asteriscos no início/fim
            .replace(/\*{2,}/g, '') // Remove asteriscos múltiplos
            .trim();

          // Verificar se começa com um título (primeira linha curta sem ponto)
          const lines = cleanedText.split('\n');
          const firstLine = lines[0]?.trim() || '';
          const isTitle = firstLine.length < 80 && 
                          !firstLine.includes('.') && 
                          !firstLine.match(/^[a-záàâãéêíóôõúç]/) &&
                          firstLine.length > 0 &&
                          lines.length > 1;

          if (isTitle) {
            const title = firstLine;
            let content = lines.slice(1).join('\n').trim();
            
            // Remover asteriscos do conteúdo também
            content = content
              .replace(/\*\*([^*]+?)\*\*/g, '$1')
              .replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '$1')
              .replace(/^\*+\s*|\s*\*+$/g, '')
              .replace(/\*{2,}/g, '')
              .trim();
              
            // Verificar se é seção de exemplos (case-insensitive)
            const isExamples = title.toLowerCase().includes('exemplo') || title.toLowerCase().includes('prático');
            
            return (
              <div key={index} className="transits-description-section">
                <h4 className={`transits-transit-description-title ${isExamples ? 'transits-examples-title' : ''}`}>
                  {title}
                </h4>
                {content && (
                  <div className={isExamples ? 'transits-examples-container' : ''}>
                    {content.split('\n').map((line, lineIndex) => {
                      const trimmedLine = line.trim();
                      if (!trimmedLine) return null;
                      
                      // Se é seção de exemplos, sempre renderizar como exemplo
                      if (isExamples) {
                        // Remover o bullet point se existir e asteriscos
                        const cleanLine = trimmedLine
                          .replace(/^[•\-]\s*/, '')
                          .replace(/\*\*([^*]+?)\*\*/g, '$1')
                          .replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '$1')
                          .replace(/^\*+\s*|\s*\*+$/g, '')
                          .replace(/\*{2,}/g, '')
                          .trim();
                        return (
                          <div key={lineIndex} className="transits-example-item">
                            <div className="transits-example-box">
                              <p className="transits-example-text">{cleanLine}</p>
                            </div>
                          </div>
                        );
                      }
                      
                      // Remover asteriscos da linha
                      const cleanLine = trimmedLine
                        .replace(/\*\*([^*]+?)\*\*/g, '$1')
                        .replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '$1')
                        .replace(/^\*+\s*|\s*\*+$/g, '')
                        .replace(/\*{2,}/g, '')
                        .trim();
                      
                      // Verificar se é um bullet point (para outras seções)
                      if (cleanLine.startsWith('•') || cleanLine.startsWith('-')) {
                        return (
                          <p key={lineIndex} className="transits-transit-description-list-item" style={{ marginLeft: '1rem' }}>
                            {cleanLine}
                          </p>
                        );
                      }

                      return (
                        <p key={lineIndex} className="transits-transit-description-paragraph">
                          {cleanLine}
                        </p>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          }

          // Parágrafo normal (sem título)
          return (
            <div key={index} className="transits-description-section">
              {trimmed.split('\n').map((line, lineIndex) => {
                const trimmedLine = line.trim();
                if (!trimmedLine) return null;
                
                // Remover asteriscos da linha
                const cleanLine = trimmedLine
                  .replace(/\*\*([^*]+?)\*\*/g, '$1')
                  .replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '$1')
                  .replace(/^\*+\s*|\s*\*+$/g, '')
                  .replace(/\*{2,}/g, '')
                  .trim();

                // Verificar se é um bullet point
                if (cleanLine.startsWith('•') || cleanLine.startsWith('-')) {
                  return (
                    <p key={lineIndex} className="transits-transit-description-list-item" style={{ marginLeft: '1rem' }}>
                      {cleanLine}
                    </p>
                  );
                }
                return (
                  <p key={lineIndex} className="transits-transit-description-paragraph">
                    {cleanLine}
                  </p>
                );
              })}
            </div>
          );
        })}
      </div>
    );
  };

  // Função para filtrar transitos passados (camada extra de segurança)
  const filterValidTransits = (transitsToFilter: Transit[]): Transit[] => {
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Resetar horas para comparar apenas datas
    
    return transitsToFilter.filter(transit => {
      try {
        // Verificar end_date primeiro (trânsito válido se ainda não terminou)
        if (transit.end_date) {
          const endDate = new Date(transit.end_date);
          endDate.setHours(0, 0, 0, 0);
          
          // Trânsito válido se end_date >= hoje
          if (endDate >= today) {
            return true;
          }
          // Trânsito passado, não incluir
          return false;
        }
        
        // Se não tem end_date, verificar start_date
        if (transit.start_date) {
          const startDate = new Date(transit.start_date);
          startDate.setHours(0, 0, 0, 0);
          
          // Trânsito válido se start_date >= hoje (futuro)
          if (startDate >= today) {
            return true;
          }
          // Trânsito passado, não incluir
          return false;
        }
        
        // Se não tem nenhuma data, não incluir (dados inválidos)
        return false;
      } catch (error) {
        // Em caso de erro ao parsear data, não incluir (segurança)
        console.warn('[Transits] Erro ao processar data do trânsito:', transit.title, error);
        return false;
      }
    });
  };

  useEffect(() => {
    // Se transits foram passados como prop, filtrar e usar eles
    if (propTransits && propTransits.length > 0) {
      const validTransits = filterValidTransits(propTransits);
      setTransits(validTransits);
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
          // Filtrar transitos passados (camada extra de segurança)
          const validTransits = filterValidTransits(response.transits);
          
          if (validTransits.length > 0) {
            setTransits(validTransits);
          } else {
            // Se após filtrar não houver trânsitos válidos, mostrar mensagem
            setError('Não há trânsitos futuros disponíveis no momento');
            setTransits([]);
          }
        } else {
          // Se não houver trânsitos, usar os padrão (apenas para desenvolvimento)
          // Em produção, não usar defaults
          if (process.env.NODE_ENV === 'development') {
            setTransits(defaultTransits);
          } else {
            setTransits([]);
          }
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
        // Log apenas se não for timeout (timeout é esperado em algumas situações)
        if (!errorMessage.includes('Tempo de espera esgotado')) {
          console.error('Erro ao buscar trânsitos:', err);
        }
        setError('Não foi possível carregar os trânsitos futuros');
        // Em produção, não usar defaults em caso de erro
        if (process.env.NODE_ENV === 'development') {
          setTransits(defaultTransits);
        } else {
          setTransits([]);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchTransits();
  }, [propTransits]);

  // Buscar trânsitos atuais em tempo real
  useEffect(() => {
    const fetchCurrentTransits = async () => {
      try {
        setIsLoadingCurrent(true);
        const response = await apiService.getCurrentPersonalTransits();
        
        if (response.active_transits && response.active_transits.length > 0) {
          setCurrentTransits(response.active_transits);
        }
        
        if (response.moon_void_of_course) {
          setMoonVoid(response.moon_void_of_course);
        }
      } catch (err) {
        console.error('Erro ao buscar trânsitos atuais:', err);
        // Não mostrar erro, apenas não exibir seção
      } finally {
        setIsLoadingCurrent(false);
      }
    };

    fetchCurrentTransits();
  }, []);

  // Função para determinar o tipo de aspecto e retornar classe CSS
  const getAspectTypeClass = (aspectType?: string): string => {
    if (!aspectType) return 'other';
    
    const aspectLower = aspectType.toLowerCase();
    
    // Aspectos harmoniosos (verde)
    if (aspectLower.includes('trígono') || aspectLower.includes('trigono') || 
        aspectLower.includes('sextil') || aspectLower.includes('sextile')) {
      return 'harmonious';
    }
    
    // Aspectos tensos (vermelho)
    if (aspectLower.includes('quadratura') || aspectLower.includes('square') ||
        aspectLower.includes('oposição') || aspectLower.includes('opposition')) {
      return 'tense';
    }
    
    // Conjunção (amarelo/dourado - neutro/transformação)
    if (aspectLower.includes('conjunção') || aspectLower.includes('conjunction')) {
      return 'conjunction';
    }
    
    return 'other';
  };

  // Função para obter cor do ícone baseada no tipo de planeta (mantida para compatibilidade)
  const getPlanetColor = (type: Transit['type']): string => {
    const colors: Record<string, string> = {
      'jupiter': '#E8B95A',
      'saturn-return': '#8B7355',
      'uranus': '#4ECDC4',
      'neptune': '#9B59B6',
      'pluto': '#E74C3C'
    };
    return colors[type] || 'hsl(var(--accent))';
  };

  return (
    <div className="transits-section-container">
      <div>
        <h2 className="transits-title" style={{ color: 'hsl(var(--accent))' }}>
          Horizontes Futuros
        </h2>
        <p className="transits-subtitle">
          Trânsitos de longo prazo que moldarão sua jornada
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="transits-loading-card">
          <div className="transits-loading-content">
            <UIIcons.Loader size={20} style={{ color: 'hsl(var(--accent))', animation: 'spin 1s linear infinite' }} />
            <p style={{ color: 'hsl(var(--muted-foreground))' }}>Calculando trânsitos futuros...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="transits-error-card" style={{ borderColor: 'hsl(var(--destructive) / 0.3)' }}>
          <div className="transits-error-content">
            <UIIcons.AlertCircle size={20} />
            <p style={{ fontSize: '0.875rem' }}>{error}</p>
          </div>
        </div>
      )}

      {/* Alerta de Lua Fora de Curso */}
      {!isLoadingCurrent && moonVoid && (
        <div className="transits-current-section">
          <div className={`transits-moon-void-card ${moonVoid.is_void ? 'transits-moon-void-active' : 'transits-moon-void-inactive'}`}>
              <div className="transits-moon-void-indicator">
                <div className={`transits-moon-void-light ${moonVoid.is_void ? 'transits-moon-void-red' : 'transits-moon-void-green'}`}></div>
                <div className="transits-moon-void-content">
                  <h4 className="transits-moon-void-title">
                    {moonVoid.is_void ? '⚠️ Lua Fora de Curso' : '✅ Lua em Aspecto'}
                  </h4>
                  <div className="transits-moon-void-description">
                    {moonVoid.is_void 
                      ? (
                        <p>
                          A Lua não está fazendo aspectos maiores com nenhum planeta até {moonVoid.void_end ? new Date(moonVoid.void_end).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : 'mudar de signo'}. Evite iniciar projetos importantes, reuniões decisivas ou tomar decisões significativas durante este período.
                        </p>
                      )
                      : (
                        <div>
                          <p>
                            <strong>O que isso significa:</strong> A Lua está formando aspectos ativos com outros planetas, o que significa que suas emoções e necessidades estão sendo influenciadas e ativadas. Este é um período de movimento emocional e ação.
                          </p>
                          <p>
                            <strong>Como isso influencia você:</strong>
                          </p>
                          <ul>
                            <li>Suas emoções estão mais receptivas e ativas</li>
                            <li>É um bom momento para tomar decisões baseadas em intuição</li>
                            <li>Comunicação emocional e relacionamentos podem fluir melhor</li>
                            <li>Iniciar projetos e ações tem maior probabilidade de sucesso</li>
                            <li>Reuniões importantes e negociações tendem a ser mais produtivas</li>
                          </ul>
                          {moonVoid.next_aspect && (
                            <p>
                              <strong>Próximo aspecto:</strong> {moonVoid.next_aspect}
                              <br />
                              <span style={{ fontSize: '0.875rem', color: 'hsl(var(--muted-foreground))' }}>
                                Este aspecto específico trará influências adicionais quando ocorrer.
                              </span>
                            </p>
                          )}
                        </div>
                      )
                    }
                  </div>
                  {moonVoid.is_void && moonVoid.void_duration_hours && (
                    <p className="transits-moon-void-duration">
                      Duração restante: {Math.round(moonVoid.void_duration_hours)} horas
                    </p>
                  )}
                </div>
              </div>
            </div>
        </div>
      )}

      {/* Timeline com cards */}
      {!isLoading && !error && (
        <div className="transits-timeline-wrapper">
          {/* Container com linha vertical e cards */}
          <div className="transits-timeline-container">
            {/* Linha vertical */}
            <div className="transits-timeline-line"></div>

            {transits.length === 0 ? (
            <div className="transits-loading-card">
              <p style={{ color: 'hsl(var(--muted-foreground))', textAlign: 'center', padding: '1rem 0' }}>
                Nenhum trânsito significativo encontrado no período calculado.
              </p>
            </div>
          ) : (
            transits.map((transit, index) => {
              const PlanetIcon = planets.find(p => p.name === transit.planet)?.icon;
              const aspectClass = getAspectTypeClass(transit.aspect_type);
              const planetColor = getPlanetColor(transit.type);
              
              return (
                <div 
                  key={transit.id} 
                  className="transits-timeline-item"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  {/* Ponto na timeline com cor baseada no aspecto */}
                  <div className={`transits-timeline-dot transits-timeline-dot-${aspectClass} ${
                    transit.isActive ? 'transits-timeline-dot-active' : ''
                  }`}>
                    {transit.isActive && (
                      <div className="transits-timeline-dot-inner"></div>
                    )}
                  </div>

                  <div className="transits-transit-card">
                    {/* Header */}
                    <div className="transits-transit-header">
                      <div className="transits-transit-header-left">
                        {PlanetIcon && (
                          <div className={`transits-transit-icon-container transits-transit-icon-container-${aspectClass}`}>
                            <PlanetIcon size={28} style={{ color: planetColor }} />
                          </div>
                        )}
                        <div className="transits-transit-content">
                          <h3 className="transits-transit-title">{transit.title}</h3>
                          <div className="transits-transit-badges">
                            {transit.aspect_type_display && (
                              <span className="transits-badge transits-badge-primary">
                                {transit.aspect_type_display}
                              </span>
                            )}
                            {transit.isActive && (
                              <span className="transits-badge transits-badge-accent">
                                ⚡ Em Progresso
                              </span>
                            )}
                          </div>
                          {transit.start_date && transit.end_date && (
                            <div className="transits-transit-dates">
                              <p className="transits-transit-date-item">
                                <span className="transits-transit-date-label">Início:</span> {formatDate(transit.start_date)}
                              </p>
                              <p className="transits-transit-date-item">
                                <span className="transits-transit-date-label">Término:</span> {formatDate(transit.end_date)}
                              </p>
                            </div>
                          )}
                          {!transit.start_date && transit.timeframe && (
                            <p className="transits-transit-timeframe">📅 {transit.timeframe}</p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Descrição formatada */}
                    <div className="transits-transit-description">
                      {formatDescription(transit.description)}
                    </div>

                    {/* Tags do Tipo de Trânsito */}
                    <div className="transits-transit-type-tags">
                      <span className="transits-transit-type-label">Tipo:</span>
                      <span className="transits-transit-type-badge" style={{ 
                        backgroundColor: `${planetColor}20`,
                        color: planetColor
                      }}>
                        {transit.type === 'jupiter' ? '🌟 Expansão' :
                         transit.type === 'saturn-return' ? '🏛️ Retorno de Saturno' :
                         transit.type === 'uranus' ? '⚡ Mudança Súbita' :
                         transit.type === 'neptune' ? '🌊 Espiritualidade' :
                         '🔥 Transformação'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
          </div>
        </div>
      )}

      {/* Footer informativo */}
      <div className="transits-info-card">
        <div className="transits-info-content">
          <UIIcons.Info size={20} className="transits-info-icon" />
          <p className="transits-info-text">
            <span className="transits-info-text-bold">Dica:</span> Os trânsitos de planetas lentos 
            (Júpiter, Saturno, Urano, Netuno e Plutão) criam os grandes temas e lições de vida. Use 
            este conhecimento para planejar estrategicamente e surfar as ondas cósmicas.
          </p>
        </div>
      </div>
    </div>
  );
};
