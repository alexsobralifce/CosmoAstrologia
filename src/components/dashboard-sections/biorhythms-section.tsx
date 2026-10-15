import React from 'react';
import { useState, useEffect } from 'react';
import { UIIcons } from '../ui-icons';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';

// ===== BIORRITMOS =====
interface BiorhythmsSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const BiorhythmsSection = ({ userData, onBack }: BiorhythmsSectionProps) => {
  const { language } = useLanguage();
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Atualizar tempo atual a cada minuto para recalcular biorritmos dinamicamente
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Atualizar a cada minuto
    
    return () => clearInterval(interval);
  }, []);
  
  // Calcular biorritmos dinamicamente baseados na data de nascimento e tempo atual
  const birthDate = userData.birthDate ? new Date(userData.birthDate) : new Date('1990-01-01');

  // Calcular dias desde o nascimento com precisão (incluindo horas)
  const millisecondsSinceBirth = currentTime.getTime() - birthDate.getTime();
  const daysSinceBirth = millisecondsSinceBirth / (1000 * 60 * 60 * 24);

  // Calcular biorritmos usando fórmulas matemáticas precisas
  const physical = Math.sin((2 * Math.PI * daysSinceBirth) / 23) * 100;
  const emotional = Math.sin((2 * Math.PI * daysSinceBirth) / 28) * 100;
  const intellectual = Math.sin((2 * Math.PI * daysSinceBirth) / 33) * 100;

  // Calcular início, fim e próximo dia crítico de cada ciclo
  const calculateCycleInfo = (period: number, daysSinceBirth: number) => {
    // Fase atual do ciclo (0 a period)
    const currentPhase = daysSinceBirth % period;
    const currentCycleNumber = Math.floor(daysSinceBirth / period);
    
    // Data de início do ciclo atual
    const cycleStartDate = new Date(birthDate);
    cycleStartDate.setDate(cycleStartDate.getDate() + (currentCycleNumber * period));
    
    // Data de fim do ciclo atual
    const cycleEndDate = new Date(cycleStartDate);
    cycleEndDate.setDate(cycleEndDate.getDate() + period);
    
    // Próximo dia crítico (quando o ciclo cruza zero - fim do ciclo atual)
    const nextCriticalDate = new Date(cycleEndDate);
    
    // Dias restantes no ciclo atual
    const daysRemaining = period - currentPhase;
    
    // Progresso do ciclo atual (0 a 100%)
    const cycleProgress = (currentPhase / period) * 100;
    
    return {
      cycleStart: cycleStartDate,
      cycleEnd: cycleEndDate,
      nextCritical: nextCriticalDate,
      currentPhase: Math.floor(currentPhase),
      daysRemaining: Math.ceil(daysRemaining),
      cycleProgress: cycleProgress,
      cycleNumber: currentCycleNumber + 1
    };
  };

  const physicalCycle = calculateCycleInfo(23, daysSinceBirth);
  const emotionalCycle = calculateCycleInfo(28, daysSinceBirth);
  const intellectualCycle = calculateCycleInfo(33, daysSinceBirth);

  const biorhythms = [
    { 
      name: language === 'pt' ? 'Físico' : 'Physical', 
      value: physical, 
      color: 'rgb(239, 68, 68)', 
      period: 23,
      desc: language === 'pt' ? 'Energia, força, coordenação' : 'Energy, strength, coordination',
      cycleStart: physicalCycle.cycleStart,
      cycleEnd: physicalCycle.cycleEnd,
      nextCritical: physicalCycle.nextCritical,
      currentPhase: physicalCycle.currentPhase,
      daysRemaining: physicalCycle.daysRemaining,
      cycleProgress: physicalCycle.cycleProgress,
      cycleNumber: physicalCycle.cycleNumber,
      status: physical > 0 
        ? (language === 'pt' ? 'Alto' : 'High')
        : (language === 'pt' ? 'Baixo' : 'Low')
    },
    { 
      name: language === 'pt' ? 'Emocional' : 'Emotional', 
      value: emotional, 
      color: 'rgb(59, 130, 246)', 
      period: 28,
      desc: language === 'pt' ? 'Humor, sensibilidade, criatividade' : 'Mood, sensitivity, creativity',
      cycleStart: emotionalCycle.cycleStart,
      cycleEnd: emotionalCycle.cycleEnd,
      nextCritical: emotionalCycle.nextCritical,
      currentPhase: emotionalCycle.currentPhase,
      daysRemaining: emotionalCycle.daysRemaining,
      cycleProgress: emotionalCycle.cycleProgress,
      cycleNumber: emotionalCycle.cycleNumber,
      status: emotional > 0 
        ? (language === 'pt' ? 'Alto' : 'High')
        : (language === 'pt' ? 'Baixo' : 'Low')
    },
    { 
      name: language === 'pt' ? 'Intelectual' : 'Intellectual', 
      value: intellectual, 
      color: 'rgb(34, 197, 94)', 
      period: 33,
      desc: language === 'pt' ? 'Raciocínio, memória, comunicação' : 'Reasoning, memory, communication',
      cycleStart: intellectualCycle.cycleStart,
      cycleEnd: intellectualCycle.cycleEnd,
      nextCritical: intellectualCycle.nextCritical,
      currentPhase: intellectualCycle.currentPhase,
      daysRemaining: intellectualCycle.daysRemaining,
      cycleProgress: intellectualCycle.cycleProgress,
      cycleNumber: intellectualCycle.cycleNumber,
      status: intellectual > 0 
        ? (language === 'pt' ? 'Alto' : 'High')
        : (language === 'pt' ? 'Baixo' : 'Low')
    },
  ];

  return (
    <div className="biorhythms-section">
      {/* Header */}
      <div className="section-header">
        <div className="section-header-content">
          <h2 className="section-title">
            {language === 'pt' ? 'Seus Biorritmos' : 'Your Biorhythms'}
          </h2>
          <p className="section-subtitle">
            {language === 'pt' ? 'Ciclos naturais baseados na sua data de nascimento' : 'Natural cycles based on your birth date'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="section-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Importance Section */}
      <div className="biorhythms-importance-card">
        <div className="biorhythms-importance-header">
          <h3 className="biorhythms-importance-title">
            {language === 'pt' ? 'A Importância de Entender os Biorritmos' : 'The Importance of Understanding Biorhythms'}
          </h3>
        </div>
        <div className="biorhythms-importance-content">
          <p className="biorhythms-importance-intro">
            {language === 'pt' 
              ? 'A importância de entender os biorritmos é otimizar o bem-estar e a produtividade, ao alinhar as atividades do dia a dia com os picos naturais de energia e concentração do seu corpo. Conhecer e respeitar seu "relógio biológico" ajuda a evitar o cansaço e a irritabilidade, melhorando o humor, a autoestima e o rendimento em tarefas que exigem foco ou criatividade.'
              : 'The importance of understanding biorhythms is to optimize well-being and productivity by aligning daily activities with your body\'s natural peaks of energy and concentration. Knowing and respecting your "biological clock" helps avoid fatigue and irritability, improving mood, self-esteem and performance in tasks that require focus or creativity.'}
          </p>
          
          <h4 className="biorhythms-benefits-title">
            {language === 'pt' ? 'Principais benefícios de conhecer seus biorritmos' : 'Main benefits of knowing your biorhythms'}
          </h4>
          
          <div className="biorhythms-benefits-grid">
            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.TrendingUp size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Mais produtividade' : 'More productivity'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Adequar tarefas aos seus horários de pico de concentração baseados nos seus biorritmos atuais. Veja abaixo como descobrir seu perfil e horários ideais.'
                    : 'Adapt tasks to your peak concentration times based on your current biorhythms. See below how to discover your profile and ideal times.'}
                </p>
              </div>
            </div>

            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.Heart size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Melhor bem-estar' : 'Better well-being'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Evitar a sensação de "preguiça" ou frustração por não conseguir ser produtivo em certos horários, percebendo que é uma questão de ajuste e não de falta de vontade.'
                    : 'Avoid the feeling of "laziness" or frustration at not being able to be productive at certain times, realizing that it is a matter of adjustment and not lack of will.'}
                </p>
              </div>
            </div>

            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.Zap size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Gerenciamento de energia' : 'Energy management'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Planejar atividades físicas mais leves nos períodos de menor energia física, e aproveitar os momentos de alta criatividade para projetos inovadores.'
                    : 'Plan lighter physical activities during periods of lower physical energy, and take advantage of high creativity moments for innovative projects.'}
                </p>
              </div>
            </div>

            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.Shield size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Saúde física e mental' : 'Physical and mental health'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Respeitar os ciclos do corpo pode melhorar o humor e a autoestima, pois reduz a autocrítica pela falta de produtividade em determinados momentos.'
                    : 'Respecting the body\'s cycles can improve mood and self-esteem, as it reduces self-criticism for lack of productivity at certain times.'}
                </p>
              </div>
            </div>

            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.RefreshCw size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Adaptação a mudanças' : 'Adaptation to changes'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Entender os biorritmos ajuda a se adaptar melhor a mudanças como o jet lag, que é um desajuste natural do relógio biológico.'
                    : 'Understanding biorhythms helps you adapt better to changes such as jet lag, which is a natural disruption of the biological clock.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Biorhythm Cards */}
      <div className="biorhythms-cards-grid">
        {biorhythms.map((bio) => (
          <div key={bio.name} className="biorhythm-card">
            <div className="biorhythm-card-header">
              <h3 className="biorhythm-card-title">{bio.name}</h3>
              <span 
                className="biorhythm-card-value" 
                style={{ color: bio.color }}
              >
                {Math.round(Math.abs(bio.value))}%
              </span>
            </div>
            
            {/* Progress Bar */}
            <div className="biorhythm-progress-container">
              <div 
                className="biorhythm-progress-bar"
                style={{ 
                  width: `${Math.abs(bio.value)}%`,
                  backgroundColor: bio.color
                }}
              />
            </div>

            <p className="biorhythm-card-desc">{bio.desc}</p>
            <div className="biorhythm-card-cycle-info">
            <p className="biorhythm-card-period">
                {language === 'pt' 
                  ? `Ciclo ${bio.cycleNumber} de ${bio.period} dias • ${bio.status}`
                  : `Cycle ${bio.cycleNumber} of ${bio.period} days • ${bio.status}`
                }
              </p>
              <p className="biorhythm-card-cycle-dates">
                {language === 'pt' 
                  ? `Início: ${bio.cycleStart.toLocaleDateString('pt-BR')} • Fim: ${bio.cycleEnd.toLocaleDateString('pt-BR')}`
                  : `Start: ${bio.cycleStart.toLocaleDateString('en-US')} • End: ${bio.cycleEnd.toLocaleDateString('en-US')}`
                }
            </p>
              <p className="biorhythm-card-cycle-progress">
                {language === 'pt' 
                  ? `Dia ${bio.currentPhase} de ${bio.period} • ${Math.round(bio.cycleProgress)}% do ciclo • ${bio.daysRemaining} dias restantes`
                  : `Day ${bio.currentPhase} of ${bio.period} • ${Math.round(bio.cycleProgress)}% of cycle • ${bio.daysRemaining} days remaining`
                }
              </p>
              <p className="biorhythm-card-next-critical">
                {language === 'pt' 
                  ? `Próximo dia crítico: ${bio.nextCritical.toLocaleDateString('pt-BR')}`
                  : `Next critical day: ${bio.nextCritical.toLocaleDateString('en-US')}`
                }
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Discover Your Profile Section */}
      <div className="biorhythms-profile-card">
        <div className="biorhythms-profile-header">
          <UIIcons.User size={24} className="biorhythms-profile-icon" />
          <h3 className="biorhythms-profile-title">
            {language === 'pt' ? 'Descubra Seu Perfil de Produtividade' : 'Discover Your Productivity Profile'}
          </h3>
        </div>
        <div className="biorhythms-profile-content">
          <p className="biorhythms-profile-intro">
            {language === 'pt' 
              ? 'Seu perfil de produtividade é determinado pela combinação dos seus biorritmos e seus padrões naturais. Use as informações abaixo para identificar seus horários de pico e otimizar sua rotina.'
              : 'Your productivity profile is determined by the combination of your biorhythms and natural patterns. Use the information below to identify your peak times and optimize your routine.'}
          </p>
          
          {/* Análise dos Biorritmos Atuais */}
          <div className="biorhythms-profile-analysis">
            <h4 className="biorhythms-profile-analysis-title">
              {language === 'pt' ? 'Análise dos Seus Biorritmos Atuais' : 'Analysis of Your Current Biorhythms'}
            </h4>
            
            {/* Sugestões baseadas nos biorritmos */}
            <div className="biorhythms-profile-suggestions">
              {intellectual > 50 && (
                <div className="biorhythms-profile-suggestion biorhythms-profile-suggestion-high">
                  <UIIcons.Brain size={20} />
                  <div>
                    <strong>{language === 'pt' ? 'Energia Intelectual Alta:' : 'High Intellectual Energy:'}</strong>
                    <p>
                      {language === 'pt' 
                        ? 'Momento perfeito para estudos, leitura, tomada de decisões importantes, resolução de problemas e atividades que exigem concentração mental.'
                        : 'Perfect time for studies, reading, important decision-making, problem-solving and activities requiring mental concentration.'}
                    </p>
                  </div>
                </div>
              )}
              
              {physical > 50 && (
                <div className="biorhythms-profile-suggestion biorhythms-profile-suggestion-high">
                  <UIIcons.Zap size={20} />
                  <div>
                    <strong>{language === 'pt' ? 'Energia Física Alta:' : 'High Physical Energy:'}</strong>
                    <p>
                      {language === 'pt' 
                        ? 'Aproveite para atividades físicas, exercícios e tarefas que exigem força. Ideal para treinos, caminhadas e atividades ao ar livre.'
                        : 'Take advantage for physical activities, exercise and tasks that require strength. Ideal for workouts, walks and outdoor activities.'}
                    </p>
                  </div>
                </div>
              )}
              
              {emotional > 50 && (
                <div className="biorhythms-profile-suggestion biorhythms-profile-suggestion-high">
                  <UIIcons.Heart size={20} />
                  <div>
                    <strong>{language === 'pt' ? 'Energia Emocional Alta:' : 'High Emotional Energy:'}</strong>
                    <p>
                      {language === 'pt' 
                        ? 'Período ideal para criatividade, expressão artística, relacionamentos e atividades que envolvem sensibilidade e intuição.'
                        : 'Ideal period for creativity, artistic expression, relationships and activities involving sensitivity and intuition.'}
                    </p>
                  </div>
                </div>
              )}
              
              {(physical < -30 || emotional < -30 || intellectual < -30) && (
                <div className="biorhythms-profile-suggestion biorhythms-profile-suggestion-low">
                  <UIIcons.Moon size={20} />
                  <div>
                    <strong>{language === 'pt' ? 'Período de Recuperação:' : 'Recovery Period:'}</strong>
                    <p>
                      {language === 'pt' 
                        ? 'Alguns dos seus biorritmos estão em fase baixa. Priorize descanso, atividades leves e evite decisões importantes ou esforços excessivos.'
                        : 'Some of your biorhythms are in a low phase. Prioritize rest, light activities and avoid important decisions or excessive efforts.'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Guia para descobrir cronotipo */}
          <div className="biorhythms-profile-guide">
            <h4 className="biorhythms-profile-guide-title">
              {language === 'pt' ? 'Como Descobrir Seu Cronotipo (Matutino/Vespertino)' : 'How to Discover Your Chronotype (Morning/Evening)'}
            </h4>
            
            <div className="biorhythms-profile-guide-steps">
              <div className="biorhythms-profile-guide-step">
                <div className="biorhythms-profile-guide-step-number">1</div>
                <div className="biorhythms-profile-guide-step-content">
                  <h5>{language === 'pt' ? 'Observe seus padrões naturais' : 'Observe your natural patterns'}</h5>
                  <p>
                    {language === 'pt' 
                      ? 'Por uma semana, anote quando você naturalmente acorda sem despertador e quando se sente mais alerta e produtivo durante o dia.'
                      : 'For a week, note when you naturally wake up without an alarm and when you feel most alert and productive during the day.'}
                  </p>
                </div>
              </div>
              
              <div className="biorhythms-profile-guide-step">
                <div className="biorhythms-profile-guide-step-number">2</div>
                <div className="biorhythms-profile-guide-step-content">
                  <h5>{language === 'pt' ? 'Identifique seus picos de energia' : 'Identify your energy peaks'}</h5>
                  <p>
                    {language === 'pt' 
                      ? 'Matutinos: pico entre 6h-10h. Vespertinos: pico entre 14h-18h. Intermediários: pico entre 10h-14h.'
                      : 'Morning types: peak between 6am-10am. Evening types: peak between 2pm-6pm. Intermediate: peak between 10am-2pm.'}
                  </p>
                </div>
              </div>
              
              <div className="biorhythms-profile-guide-step">
                <div className="biorhythms-profile-guide-step-number">3</div>
                <div className="biorhythms-profile-guide-step-content">
                  <h5>{language === 'pt' ? 'Combine com seus biorritmos' : 'Combine with your biorhythms'}</h5>
                  <p>
                    {language === 'pt' 
                      ? 'Use os biorritmos acima para identificar quando sua energia física, emocional e intelectual estão altas. Planeje tarefas importantes nesses períodos.'
                      : 'Use the biorhythms above to identify when your physical, emotional and intellectual energy are high. Plan important tasks during these periods.'}
                  </p>
                </div>
              </div>
              
              <div className="biorhythms-profile-guide-step">
                <div className="biorhythms-profile-guide-step-number">4</div>
                <div className="biorhythms-profile-guide-step-content">
                  <h5>{language === 'pt' ? 'Ajuste sua rotina' : 'Adjust your routine'}</h5>
                  <p>
                    {language === 'pt' 
                      ? 'Baseado no seu cronotipo e biorritmos, agende tarefas que exigem foco nos seus horários de pico e atividades leves nos períodos de baixa energia.'
                      : 'Based on your chronotype and biorhythms, schedule tasks that require focus during your peak times and light activities during low energy periods.'}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Recomendações práticas */}
          <div className="biorhythms-profile-recommendations">
            <h4 className="biorhythms-profile-recommendations-title">
              {language === 'pt' ? 'Recomendações Práticas para Hoje' : 'Practical Recommendations for Today'}
            </h4>
            <div className="biorhythms-profile-recommendations-list">
              {intellectual > 50 && (
                <div className="biorhythms-profile-recommendation">
                  <UIIcons.CheckCircle size={18} />
                  <span>
                    {language === 'pt' 
                      ? 'Estude ou trabalhe em projetos que exigem concentração mental'
                      : 'Study or work on projects requiring mental concentration'}
                  </span>
                </div>
              )}
              {physical > 50 && (
                <div className="biorhythms-profile-recommendation">
                  <UIIcons.CheckCircle size={18} />
                  <span>
                    {language === 'pt' 
                      ? 'Faça exercícios físicos ou atividades que exigem força'
                      : 'Do physical exercise or activities requiring strength'}
                  </span>
                </div>
              )}
              {emotional > 50 && (
                <div className="biorhythms-profile-recommendation">
                  <UIIcons.CheckCircle size={18} />
                  <span>
                    {language === 'pt' 
                      ? 'Dedique tempo a atividades criativas ou relacionamentos'
                      : 'Dedicate time to creative activities or relationships'}
                  </span>
                </div>
              )}
              {(physical < -30 || emotional < -30 || intellectual < -30) && (
                <div className="biorhythms-profile-recommendation biorhythms-profile-recommendation-rest">
                  <UIIcons.Moon size={18} />
                  <span>
                    {language === 'pt' 
                      ? 'Priorize descanso e atividades leves - alguns ciclos estão baixos'
                      : 'Prioritize rest and light activities - some cycles are low'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="biorhythms-summary-card">
        <h3 className="biorhythms-summary-title">
          {language === 'pt' ? 'Resumo do Dia' : 'Daily Summary'}
        </h3>
        <p className="biorhythms-summary-text">
          {language === 'pt' 
            ? `Hoje você está no dia ${Math.floor(daysSinceBirth)} desde o seu nascimento (atualizado em tempo real). ${
                physical > 50 ? 'Sua energia física está alta, ótimo para exercícios e atividades físicas.' :
                physical < -50 ? 'Sua energia física está baixa, priorize o descanso.' :
                'Sua energia física está moderada, mantenha um ritmo equilibrado.'
              } ${
                emotional > 50 ? 'Emocionalmente você está receptivo e criativo.' :
                emotional < -50 ? 'Emocionalmente pode ser um dia mais introspectivo.' :
                'Suas emoções estão estáveis.'
              } ${
                intellectual > 50 ? 'Mentalmente é um ótimo dia para estudos e decisões importantes.' :
                intellectual < -50 ? 'Evite decisões complexas hoje, se possível.' :
                'Seu raciocínio está funcionando normalmente.'
              }`
            : `Today you are on day ${Math.floor(daysSinceBirth)} since your birth (updated in real time). ${
                physical > 50 ? 'Your physical energy is high, great for exercise and physical activities.' :
                physical < -50 ? 'Your physical energy is low, prioritize rest.' :
                'Your physical energy is moderate, maintain a balanced pace.'
              } ${
                emotional > 50 ? 'Emotionally you are receptive and creative.' :
                emotional < -50 ? 'Emotionally it may be a more introspective day.' :
                'Your emotions are stable.'
              } ${
                intellectual > 50 ? 'Mentally it is a great day for studies and important decisions.' :
                intellectual < -50 ? 'Avoid complex decisions today if possible.' :
                'Your reasoning is working normally.'
              }`
          }
        </p>
      </div>
    </div>
  );
};
