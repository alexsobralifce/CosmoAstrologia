import React, { useState, useEffect } from 'react';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { apiService } from '../services/api';
// import { useLanguage } from '../i18n'; // Não usado no momento
import '../styles/best-timing-section.css';

interface BestTimingSectionProps {
  userData: {
    birthDate: Date;
    birthTime: string;
    coordinates?: {
      latitude: number;
      longitude: number;
    };
  };
}

interface BestMoment {
  date: string;
  score: number;
  aspects: Array<{
    planet: string;
    house: number;
    aspect_type: string;
    is_primary: boolean;
  }>;
  reasons: string[];
  warnings?: string[];
  is_moon_void: boolean;
}

const ACTION_OPTIONS = [
  {
    id: 'pedir_aumento',
    label: 'Pedir Aumento',
    icon: '💰',
    description: 'Negociar aumento salarial'
  },
  {
    id: 'assinar_contrato',
    label: 'Assinar Contrato',
    icon: '📝',
    description: 'Firmar acordos e contratos'
  },
  {
    id: 'primeiro_encontro',
    label: 'Primeiro Encontro',
    icon: '💕',
    description: 'Encontro romântico'
  },
  {
    id: 'apresentacao_publica',
    label: 'Apresentação Pública',
    icon: '🎤',
    description: 'Apresentações e palestras'
  },
  {
    id: 'negociacao',
    label: 'Negociação',
    icon: '🤝',
    description: 'Negociações importantes'
  },
  {
    id: 'investimento',
    label: 'Investimento',
    icon: '📈',
    description: 'Decisões financeiras'
  },
  {
    id: 'mudanca_carreira',
    label: 'Mudança de Carreira',
    icon: '🔄',
    description: 'Transição profissional'
  },
  {
    id: 'iniciar_projeto',
    label: 'Iniciar Projeto',
    icon: '🚀',
    description: 'Lançar novos projetos'
  }
];

export const BestTimingSection: React.FC<BestTimingSectionProps> = ({ userData }) => {
  // Language não usado no momento, mas mantido para futuras traduções
  // const { language } = useLanguage();
  const [selectedAction, setSelectedAction] = useState<string>('pedir_aumento');
  const [bestMoments, setBestMoments] = useState<BestMoment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Atualizar automaticamente quando a data muda (diariamente)
  useEffect(() => {
    if (selectedAction && userData.birthDate && userData.birthTime && userData.coordinates) {
      fetchBestTiming();
      
      // Atualizar a cada dia (verificar a cada hora se mudou o dia)
      const interval = setInterval(() => {
        const now = new Date();
        const lastUpdate = localStorage.getItem('best_timing_last_update');
        
        if (lastUpdate) {
          const lastDate = new Date(lastUpdate);
          // Se mudou o dia, atualizar
          if (now.getDate() !== lastDate.getDate() || 
              now.getMonth() !== lastDate.getMonth() || 
              now.getFullYear() !== lastDate.getFullYear()) {
            fetchBestTiming();
            localStorage.setItem('best_timing_last_update', now.toISOString());
          }
        } else {
          localStorage.setItem('best_timing_last_update', now.toISOString());
        }
      }, 3600000); // Verificar a cada hora
      
      return () => clearInterval(interval);
    }
  }, [selectedAction, userData.birthDate]);

  const fetchBestTiming = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      if (!userData.coordinates) {
        setError('Localização não encontrada. Por favor, complete seu perfil.');
        return;
      }
      
      const response = await apiService.getBestTiming({
        action_type: selectedAction,
        days_ahead: 30
      });
      
      // VALIDAÇÃO RIGOROSA: Verificar se a resposta é válida e vem da API
      if (!response || typeof response !== 'object') {
        console.error('[BestTiming] Resposta da API inválida:', response);
        setBestMoments([]);
        setError('Resposta inválida da API.');
        return;
      }
      
      // VALIDAÇÃO: Verificar se best_moments existe e é um array
      if (!response.best_moments) {
        console.warn('[BestTiming] Resposta da API não contém best_moments:', response);
        setBestMoments([]);
        setError('Nenhum momento favorável encontrado no período calculado.');
        return;
      }
      
      if (!Array.isArray(response.best_moments)) {
        console.error('[BestTiming] best_moments não é um array:', response.best_moments);
        setBestMoments([]);
        setError('Formato de dados inválido da API.');
        return;
      }
      
      // VALIDAÇÃO: Validar estrutura de cada momento antes de aceitar
      const validMoments = response.best_moments.filter((moment: any) => {
        // Verificar estrutura mínima obrigatória
        if (!moment || typeof moment !== 'object') {
          console.warn('[BestTiming] Momento inválido (não é objeto):', moment);
          return false;
        }
        
        if (!moment.date || typeof moment.date !== 'string') {
          console.warn('[BestTiming] Momento sem data válida:', moment);
          return false;
        }
        
        if (typeof moment.score !== 'number' || moment.score <= 0) {
          console.warn('[BestTiming] Momento sem score válido:', moment);
          return false;
        }
        
        if (!moment.aspects || !Array.isArray(moment.aspects) || moment.aspects.length === 0) {
          console.warn('[BestTiming] Momento sem aspectos válidos:', moment);
          return false;
        }
        
        // Validar estrutura de cada aspecto
        const validAspects = moment.aspects.filter((aspect: any) => {
          if (!aspect || typeof aspect !== 'object') return false;
          if (!aspect.planet || typeof aspect.planet !== 'string') return false;
          if (!aspect.aspect_type || typeof aspect.aspect_type !== 'string') return false;
          if (typeof aspect.house !== 'number') return false;
          return true;
        });
        
        if (validAspects.length === 0) {
          console.warn('[BestTiming] Momento sem aspectos válidos após validação:', moment);
          return false;
        }
        
        // Atualizar aspectos com apenas os válidos
        moment.aspects = validAspects;
        
        return true;
      });
      
      // Log para debug - ANTES de qualquer processamento
      console.log('[BestTiming] Resposta RAW da API (antes de validação):', {
        action: selectedAction,
        total_moments: response.best_moments.length,
        moments_raw: response.best_moments.slice(0, 5).map((m: any) => ({
          date: m.date,
          score: m.score,
          aspects_count: m.aspects?.length || 0,
          aspects_raw: m.aspects || [],
          aspects_str: m.aspects?.map((a: any) => `${a.planet} em ${a.aspect_type} com Casa ${a.house}`) || []
        }))
      });
      
      // Log para debug - DEPOIS da validação
      console.log('[BestTiming] Resposta da API validada:', {
        action: selectedAction,
        total_recebidos: response.best_moments.length,
        total_validos: validMoments.length,
        momentos_invalidos: response.best_moments.length - validMoments.length,
        moments: validMoments.slice(0, 5).map(m => ({
          date: m.date,
          score: m.score,
          aspects_count: m.aspects?.length || 0,
          aspects: m.aspects?.map((a: any) => `${a.planet} em ${a.aspect_type} com Casa ${a.house}`)
        }))
      });
      
      // CRÍTICO: Apenas definir momentos se houver dados válidos da API
      if (validMoments.length > 0) {
        setBestMoments(validMoments);
        setError(null);
      } else {
        setBestMoments([]);
        setError('Nenhum momento favorável encontrado no período calculado.');
      }
    } catch (err) {
      console.error('Erro ao buscar melhores momentos:', err);
      setError('Não foi possível calcular os melhores momentos.');
      setBestMoments([]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string): string => {
    // Extrair data de forma segura, usando UTC para evitar problemas de timezone
    try {
      // Se a data já está no formato YYYY-MM-DD, usar diretamente
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
        const [year, month, day] = dateString.split('-');
        const months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        return `${parseInt(day)} de ${months[parseInt(month) - 1]} de ${year}`;
      }
      
      // Se tem timestamp, parsear e usar UTC
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        console.error('[BestTiming] Data inválida em formatDate:', dateString);
        return dateString; // Retornar original se inválida
      }
      
      // Usar UTC para evitar problemas de timezone
      const months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
      return `${date.getUTCDate()} de ${months[date.getUTCMonth()]} de ${date.getUTCFullYear()}`;
    } catch (e) {
      console.error('[BestTiming] Erro ao formatar data:', dateString, e);
      return dateString; // Retornar original em caso de erro
    }
  };

  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const getScoreColor = (score: number): string => {
    if (score >= 15) return 'high';
    if (score >= 10) return 'medium';
    return 'low';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 15) return 'Excelente';
    if (score >= 10) return 'Bom';
    return 'Moderado';
  };

  return (
    <div className="best-timing-section">
      <div className="best-timing-header">
        <h3 className="best-timing-title">
          <UIIcons.Calendar size={20} style={{ marginRight: '0.5rem' }} />
          Agenda de Melhores Momentos
        </h3>
        <p className="best-timing-subtitle">
          Descubra os melhores momentos para ações importantes baseado nos astros
        </p>
      </div>

      {/* Seleção de Ação */}
      <div className="best-timing-actions">
        <label className="best-timing-actions-label">
          Selecione a ação:
        </label>
        <div className="best-timing-actions-grid">
          {ACTION_OPTIONS.map((action) => (
            <button
              key={action.id}
              className={`best-timing-action-button ${
                selectedAction === action.id ? 'best-timing-action-button-active' : ''
              }`}
              onClick={() => setSelectedAction(action.id)}
            >
              <span className="best-timing-action-icon">{action.icon}</span>
              <div className="best-timing-action-info">
                <span className="best-timing-action-label">{action.label}</span>
                <span className="best-timing-action-desc">{action.description}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Resultados */}
      {isLoading && (
        <div className="best-timing-loading">
          <UIIcons.Loader size={24} style={{ animation: 'spin 1s linear infinite' }} />
          <p>Calculando melhores momentos...</p>
        </div>
      )}

      {error && !isLoading && (
        <div className="best-timing-error">
          <UIIcons.AlertCircle size={20} />
          <p>{error}</p>
        </div>
      )}

      {/* CRÍTICO: Apenas exibir se houver dados válidos da API */}
      {!isLoading && !error && bestMoments && Array.isArray(bestMoments) && bestMoments.length > 0 && (
        <div className="best-timing-results">
          {(() => {
              // VALIDAÇÃO CRÍTICA: Verificar se bestMoments é um array válido da API
              if (!bestMoments || !Array.isArray(bestMoments) || bestMoments.length === 0) {
                console.warn('[BestTiming] bestMoments não é válido para processamento:', bestMoments);
                return null; // Não renderizar nada se não houver dados válidos
              }
              
              // FILTRAR momentos válidos ANTES de agrupar
              // IMPORTANTE: Apenas processar momentos com score > 0 e aspectos válidos
              const validMoments = bestMoments.filter(moment => {
                // Validar que o momento tem dados válidos
                if (moment.score <= 0) {
                  console.warn('[BestTiming] Ignorando momento com score <= 0:', {
                    date: moment.date,
                    score: moment.score
                  });
                  return false; // Ignorar momentos sem score
                }
                
                if (!moment.aspects || !Array.isArray(moment.aspects) || moment.aspects.length === 0) {
                  console.warn('[BestTiming] Ignorando momento sem aspectos válidos:', {
                    date: moment.date,
                    score: moment.score,
                    has_aspects: !!moment.aspects
                  });
                  return false; // Ignorar momentos sem aspectos
                }
                
                // Validar que a data é válida
                try {
                  const dateObj = new Date(moment.date);
                  if (isNaN(dateObj.getTime())) {
                    console.error('[BestTiming] Data inválida:', moment.date);
                    return false; // Ignorar momento com data inválida
                  }
                } catch (e) {
                  console.error('[BestTiming] Erro ao validar data:', {
                    date: moment.date,
                    error: e
                  });
                  return false;
                }
                
                return true; // Momento válido
              });
              
              console.log('[BestTiming] Momentos válidos após filtro:', {
                total_recebidos: bestMoments.length,
                total_validos: validMoments.length,
                momentos_filtrados: bestMoments.length - validMoments.length
              });
              
              // Agrupar momentos válidos por data
              // CRÍTICO: Usar APENAS split('T')[0] para evitar problemas de timezone
              const momentsByDate = new Map<string, BestMoment[]>();
              
              validMoments.forEach(moment => {
                // Extrair data de forma segura: usar APENAS split para evitar timezone
                let dateKey: string;
                
                // VALIDAÇÃO: Verificar formato da data
                if (!moment.date || typeof moment.date !== 'string') {
                  console.error('[BestTiming] Data inválida no momento:', moment);
                  return; // Ignorar momento sem data válida
                }
                
                // Usar split para extrair data (formato ISO: YYYY-MM-DDTHH:MM:SS)
                const dateMatch = moment.date.match(/^(\d{4}-\d{2}-\d{2})/);
                if (!dateMatch) {
                  console.error('[BestTiming] Formato de data inválido:', moment.date);
                  return; // Ignorar momento com formato inválido
                }
                
                dateKey = dateMatch[1]; // YYYY-MM-DD
                
                // VALIDAÇÃO ADICIONAL: Verificar se a data é válida
                const dateParts = dateKey.split('-');
                if (dateParts.length !== 3) {
                  console.error('[BestTiming] Data malformada:', dateKey);
                  return;
                }
                
                const year = parseInt(dateParts[0], 10);
                const month = parseInt(dateParts[1], 10);
                const day = parseInt(dateParts[2], 10);
                
                if (isNaN(year) || isNaN(month) || isNaN(day) || 
                    month < 1 || month > 12 || day < 1 || day > 31) {
                  console.error('[BestTiming] Valores de data inválidos:', { year, month, day });
                  return;
                }
                
                if (!momentsByDate.has(dateKey)) {
                  momentsByDate.set(dateKey, []);
                }
                momentsByDate.get(dateKey)!.push(moment);
              });
              
              // Log para debug: verificar agrupamento
              console.log('[BestTiming] Agrupamento por data:', {
                total_moments_validos: validMoments.length,
                dates: Array.from(momentsByDate.keys()).sort(),
                moments_per_date: Array.from(momentsByDate.entries()).map(([date, moments]) => ({
                  date,
                  count: moments.length,
                  scores: moments.map(m => m.score),
                  dates_raw: moments.map(m => m.date),
                  aspects_sample: moments[0]?.aspects?.slice(0, 2) || []
                }))
              });
              
              // Converter para array e ordenar por data
              const groupedMoments = Array.from(momentsByDate.entries())
                .map(([date, moments]) => ({
                  date,
                  moments: moments.sort((a, b) => b.score - a.score), // Ordenar por score dentro do dia
                  bestMoment: moments[0] // Melhor momento do dia
                }))
                .sort((a, b) => a.date.localeCompare(b.date)); // Ordenar por data
              
              return (
                <>
                  <h4 className="best-timing-results-title">
                    Melhores Dias ({groupedMoments.length})
                  </h4>
                  
                  <div className="best-timing-moments-list">
                    {groupedMoments.map((group, index) => {
                // CRÍTICO: Criar um novo Set para cada grupo para evitar vazamento de dados
                // bestMoment não usado, mas mantido para referência futura
                const allWarnings = new Set<string>();
                let hasMoonVoid = false;
                let maxScore = 0;
                
                // VALIDAÇÃO RIGOROSA: Apenas exibir aspectos que aparecem nos aspectos calculados
                // Usar APENAS os aspectos estruturados do backend (fonte única de verdade)
                // CRÍTICO: Criar novo Set para cada grupo (não reutilizar)
                const validReasons = new Set<string>();
                
                // Log para debug: verificar dados do grupo ANTES da validação
                console.log(`[BestTiming] Processando grupo ${index + 1}/${groupedMoments.length}:`, {
                  date: group.date,
                  action: selectedAction,
                  moments_count: group.moments.length,
                  validReasons_initial_size: validReasons.size, // Deve ser 0
                  moments: group.moments.map(m => {
                    const dateMatch = m.date?.match(/^(\d{4}-\d{2}-\d{2})/);
                    const extractedDate = dateMatch ? dateMatch[1] : 'INVÁLIDA';
                    return {
                      date: m.date,
                      extracted_date: extractedDate,
                      matches_group: extractedDate === group.date,
                      score: m.score,
                      aspects_count: m.aspects?.length || 0,
                      aspects: m.aspects?.map((a: any) => `${a.planet} em ${a.aspect_type} com Casa ${a.house}`) || []
                    };
                  })
                });
                
                // VALIDAÇÃO CRÍTICA: Verificar se todos os momentos pertencem à data do grupo
                const groupDateKey = group.date; // Data do grupo (YYYY-MM-DD)
                
                // VALIDAÇÃO ADICIONAL: Filtrar momentos ANTES de processar
                // Garantir que apenas momentos da data correta sejam processados
                const validMomentsForGroup = group.moments.filter(m => {
                  // Extrair data do momento usando APENAS regex/split (sem new Date para evitar timezone)
                  if (!m.date || typeof m.date !== 'string') {
                    console.error('[BestTiming] Momento sem data válida:', m);
                    return false;
                  }
                  
                  // Usar regex para extrair data (formato ISO: YYYY-MM-DDTHH:MM:SS)
                  const dateMatch = m.date.match(/^(\d{4}-\d{2}-\d{2})/);
                  if (!dateMatch) {
                    console.error('[BestTiming] Formato de data inválido no momento:', m.date);
                    return false;
                  }
                  
                  const momentDateKey = dateMatch[1]; // YYYY-MM-DD
                  
                  // VALIDAÇÃO CRÍTICA: Se a data do momento não corresponde à data do grupo, rejeitar
                  if (momentDateKey !== groupDateKey) {
                    console.error('[BestTiming] ERRO CRÍTICO: Momento não pertence à data do grupo!', {
                      group_date: groupDateKey,
                      moment_date: momentDateKey,
                      moment_full_date: m.date,
                      moment_score: m.score,
                      moment_aspects: m.aspects?.map((a: any) => `${a.planet} em ${a.aspect_type} com Casa ${a.house}`) || []
                    });
                    return false;
                  }
                  
                  return true;
                });
                
                // Se houver momentos inválidos, logar e usar apenas os válidos
                if (validMomentsForGroup.length !== group.moments.length) {
                  console.error('[BestTiming] Momentos inválidos filtrados:', {
                    group_date: groupDateKey,
                    total_moments: group.moments.length,
                    valid_moments: validMomentsForGroup.length,
                    invalid_count: group.moments.length - validMomentsForGroup.length
                  });
                }
                
                // Log detalhado ANTES de processar aspectos
                // CRÍTICO: Mostrar aspectos RAW do backend antes de qualquer processamento
                console.log(`[BestTiming] Processando ${validMomentsForGroup.length} momentos válidos para ${groupDateKey}:`, {
                  action: selectedAction,
                  group_date: groupDateKey,
                  moments: validMomentsForGroup.map(m => {
                    const dateMatch = m.date?.match(/^(\d{4}-\d{2}-\d{2})/);
                    const extractedDate = dateMatch ? dateMatch[1] : 'INVÁLIDA';
                    return {
                      date: m.date,
                      extracted_date: extractedDate,
                      score: m.score,
                      aspects_count: m.aspects?.length || 0,
                      aspects_raw: m.aspects || [], // Mostrar aspectos RAW do backend
                      aspects: m.aspects?.map((a: any) => ({
                        planet: a.planet,
                        aspect_type: a.aspect_type,
                        house: a.house,
                        is_primary: a.is_primary,
                        full_str: `${a.planet} em ${a.aspect_type} com Casa ${a.house}`
                      })) || []
                    };
                  })
                });
                
                // Coletar aspectos únicos APENAS dos momentos válidos que têm aspectos estruturados
                validMomentsForGroup.forEach(m => {
                  // VALIDAÇÃO ADICIONAL: Verificar novamente se o momento pertence à data do grupo
                  const dateMatch = m.date?.match(/^(\d{4}-\d{2}-\d{2})/);
                  const momentDateKey = dateMatch ? dateMatch[1] : null;
                  
                  if (momentDateKey !== groupDateKey) {
                    console.error('[BestTiming] ERRO CRÍTICO: Momento inválido detectado durante processamento!', {
                      group_date: groupDateKey,
                      moment_date: momentDateKey,
                      moment_full_date: m.date,
                      moment_score: m.score
                    });
                    return; // Ignorar momento inválido
                  }
                  
                  // Coletar avisos (warnings) de reasons
                  if (m.reasons && Array.isArray(m.reasons)) {
                    m.reasons.forEach((r: string) => {
                      if (r.startsWith('⚠️')) {
                        allWarnings.add(r);
                      }
                    });
                  }
                  
                  if (m.is_moon_void) hasMoonVoid = true;
                  if (m.score > maxScore) maxScore = m.score;
                  
                  // Verificar se o momento tem score válido E aspectos estruturados
                  if (m.score > 0 && m.aspects && Array.isArray(m.aspects) && m.aspects.length > 0) {
                    // VALIDAÇÃO FINAL: Definir casas e planetas permitidos baseado na ação selecionada
                    // Isso garante que apenas aspectos de casas e planetas corretos sejam exibidos
                    const allowedHouses: { [key: string]: number[] } = {
                      'pedir_aumento': [2, 10, 6, 11],
                      'assinar_contrato': [7, 10, 2, 9],
                      'primeiro_encontro': [5, 7, 1, 11],
                      'apresentacao_publica': [10, 1, 3, 9],
                      'negociacao': [7, 2, 3, 9],
                      'investimento': [2, 8, 5, 11],
                      'mudanca_carreira': [10, 1, 4, 9],
                      'iniciar_projeto': [1, 10, 5, 11]
                    };
                    
                    const allowedPlanets: { [key: string]: string[] } = {
                      'pedir_aumento': ['Júpiter', 'Sol', 'Vênus'],
                      'assinar_contrato': ['Júpiter', 'Mercúrio', 'Vênus'],
                      'primeiro_encontro': ['Vênus', 'Júpiter', 'Lua'],
                      'apresentacao_publica': ['Sol', 'Mercúrio', 'Júpiter'],
                      'negociacao': ['Mercúrio', 'Júpiter', 'Vênus'],
                      'investimento': ['Júpiter', 'Vênus'],
                      'mudanca_carreira': ['Júpiter', 'Urano', 'Sol'],
                      'iniciar_projeto': ['Sol', 'Júpiter', 'Mercúrio']
                    };
                    
                    const housesForAction = allowedHouses[selectedAction] || [];
                    const planetsForAction = allowedPlanets[selectedAction] || [];
                    
                    // Usar APENAS os aspectos estruturados do backend (fonte única de verdade)
                    m.aspects.forEach((aspect: any) => {
                      if (aspect && aspect.planet && aspect.aspect_type && aspect.house) {
                        // VALIDAÇÃO CRÍTICA 1: Verificar se o planeta está na lista permitida
                        if (planetsForAction.length > 0 && !planetsForAction.includes(aspect.planet)) {
                          console.error('[BestTiming] ERRO: Aspecto com planeta não permitido detectado!', {
                            aspect: `${aspect.planet} em ${aspect.aspect_type} com Casa ${aspect.house}`,
                            allowed_planets: planetsForAction,
                            action: selectedAction,
                            moment_date: m.date,
                            group_date: groupDateKey
                          });
                          return; // Ignorar aspecto com planeta não permitido
                        }
                        
                        // VALIDAÇÃO CRÍTICA 2: Verificar se a casa está na lista permitida
                        if (housesForAction.length > 0 && !housesForAction.includes(aspect.house)) {
                          console.error('[BestTiming] ERRO: Aspecto com casa não permitida detectado!', {
                            aspect: `${aspect.planet} em ${aspect.aspect_type} com Casa ${aspect.house}`,
                            allowed_houses: housesForAction,
                            action: selectedAction,
                            moment_date: m.date,
                            group_date: groupDateKey
                          });
                          return; // Ignorar aspecto com casa não permitida
                        }
                        
                        const reasonStr = `${aspect.planet} em ${aspect.aspect_type} com Casa ${aspect.house}`;
                        validReasons.add(reasonStr);
                        
                        // Log para debug: registrar cada aspecto adicionado
                        console.log(`[BestTiming] Aspecto adicionado para ${groupDateKey}:`, {
                          aspect: reasonStr,
                          moment_date: m.date,
                          moment_date_extracted: momentDateKey,
                          group_date: groupDateKey,
                          matches: momentDateKey === groupDateKey,
                          house_allowed: housesForAction.length === 0 || housesForAction.includes(aspect.house)
                        });
                      }
                    });
                  } else {
                    // Log para debug: momento sem aspectos válidos
                    if (m.score > 0) {
                      console.warn('[BestTiming] Momento com score > 0 mas sem aspectos válidos:', {
                        date: m.date,
                        score: m.score,
                        has_aspects: !!m.aspects,
                        aspects_length: m.aspects?.length || 0
                      });
                    }
                  }
                });
                
                // Se não houver momentos válidos, não exibir o grupo
                if (validMomentsForGroup.length === 0) {
                  console.error('[BestTiming] Grupo rejeitado: nenhum momento válido encontrado', {
                    group_date: groupDateKey,
                    total_moments: group.moments.length
                  });
                  return null; // Não renderizar o grupo
                }
                
                // NÃO usar reasons como fallback - apenas aspectos estruturados são válidos
                // Isso garante que apenas aspectos calculados e validados pelo backend sejam exibidos
                
                // Coletar horários favoráveis do dia (qualquer score > 0)
                // USAR APENAS MOMENTOS VÁLIDOS
                const favorableTimes = validMomentsForGroup
                  .filter(m => !m.is_moon_void && m.score > 0)
                  .map(m => formatTime(m.date))
                  .sort();
                
                // Log final do grupo processado
                console.log(`[BestTiming] Grupo ${group.date} processado:`, {
                  maxScore,
                  validReasonsCount: validReasons.size,
                  validReasons: Array.from(validReasons),
                  favorableTimesCount: favorableTimes.length,
                  favorableTimes
                });
                
                return (
                  <AstroCard key={index} className={`best-timing-moment-card best-timing-moment-${getScoreColor(maxScore)}`}>
                    <div className="best-timing-moment-header">
                      <div className="best-timing-moment-date">
                        <UIIcons.Calendar size={18} />
                        <div>
                          <strong>{formatDate(group.date)}</strong>
                          {favorableTimes.length > 0 && (
                            <span className="best-timing-moment-times">
                              Horários favoráveis: {favorableTimes.join(', ')}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className={`best-timing-moment-score best-timing-moment-score-${getScoreColor(maxScore)}`}>
                        <span className="best-timing-moment-score-value">{maxScore}</span>
                        <span className="best-timing-moment-score-label">{getScoreLabel(maxScore)}</span>
                        <span className="best-timing-moment-score-tooltip" title="Score máximo do dia: indica a qualidade astrológica do melhor momento deste dia. Quanto maior, mais favorável são os aspectos planetários para esta ação.">
                          <UIIcons.Info size={12} />
                        </span>
                      </div>
                    </div>
                    
                    <div className="best-timing-moment-score-explanation">
                      <p className="best-timing-moment-score-explanation-text">
                        <strong>O que significa este score?</strong> Este é o score máximo do dia, calculado baseado nos aspectos planetários favoráveis encontrados. 
                        Quanto maior o score, mais planetas benéficos estão formando aspectos harmoniosos (trígono, sextil, conjunção) com as casas astrológicas relevantes para esta ação.
                        {maxScore >= 15 && ' Este dia tem múltiplos aspectos favoráveis simultâneos, tornando-o especialmente propício.'}
                        {maxScore >= 10 && maxScore < 15 && ' Este dia tem aspectos favoráveis que indicam um bom momento para esta ação.'}
                        {maxScore < 10 && ' Este dia tem aspectos moderadamente favoráveis.'}
                      </p>
                      <details className="best-timing-moment-score-details">
                        <summary className="best-timing-moment-score-details-summary">
                          Como o score é calculado?
                        </summary>
                        <div className="best-timing-moment-score-details-content">
                          <p>O score é calculado somando pontos baseados em:</p>
                          <ul>
                            <li><strong>Trígono</strong> em casa primária: +10 pontos</li>
                            <li><strong>Sextil</strong> em casa primária: +7 pontos</li>
                            <li><strong>Conjunção</strong> em casa primária: +8 pontos</li>
                            <li>Aspectos em casas secundárias: pontos reduzidos (5, 3, 4 respectivamente)</li>
                            <li>Penalizações: aspectos tensos de planetas desfavoráveis (-5 pontos) e Lua Fora de Curso (-3 pontos)</li>
                          </ul>
                          <p>O score máximo do dia é o maior valor encontrado entre todos os horários verificados (a cada 6 horas).</p>
                        </div>
                      </details>
                    </div>

                    {hasMoonVoid && (
                      <div className="best-timing-moment-warning">
                        <UIIcons.Moon size={16} />
                        <span>Alguns horários têm Lua Fora de Curso - Verifique antes de agendar</span>
                      </div>
                    )}

                    {validReasons.size > 0 && (
                      <div className="best-timing-moment-aspects">
                        <strong>Aspectos Favoráveis do Dia:</strong>
                        <ul>
                          {Array.from(validReasons).map((reason, idx) => (
                            <li key={idx}>{reason}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Log para debug: mostrar se há inconsistências */}
                    {(() => {
                      if (maxScore > 0 && validReasons.size === 0) {
                        console.warn('[BestTiming] Inconsistência detectada:', {
                          date: group.date,
                          maxScore,
                          validReasonsCount: validReasons.size,
                          moments: group.moments.map(m => ({
                            date: m.date,
                            score: m.score,
                            aspects_count: m.aspects?.length || 0
                          }))
                        });
                      }
                      return null;
                    })()}

                    {allWarnings.size > 0 && (
                      <div className="best-timing-moment-warnings">
                        <strong>Atenções:</strong>
                        <ul>
                          {Array.from(allWarnings).map((reason, idx) => (
                            <li key={idx}>{reason}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </AstroCard>
                    );
                  })}
                  </div>
                </>
              );
            })()}
        </div>
      )}

      {/* CRÍTICO: Apenas exibir mensagem se não houver dados da API */}
      {!isLoading && !error && (!bestMoments || bestMoments.length === 0) && (
        <div className="best-timing-empty">
          <p>Nenhum momento favorável encontrado. Tente selecionar outra ação ou aumentar o período de busca.</p>
        </div>
      )}
    </div>
  );
};

