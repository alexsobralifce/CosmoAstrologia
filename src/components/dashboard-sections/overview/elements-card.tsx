import React from 'react';
import { UIIcons } from '../../ui-icons';
import { planets } from '../../planet-icons';
import { ElementChart } from '../../element-chart';
import { useLanguage } from '../../../i18n';
import { computeElementDistribution } from './element-distribution';

type ElementDistribution = ReturnType<typeof computeElementDistribution>;

interface ElementsCardProps extends ElementDistribution {
  language: string;
  t: ReturnType<typeof useLanguage>['t'];
}

/** Cartão "Distribuição dos Elementos": gráfico, elemento dominante/ausente e orientações. */
export const ElementsCard = ({ language, t, elementData, dominantElement, missingElement }: ElementsCardProps) => {
  return (
    <div className="overview-detail-card">
      <h3 className="overview-detail-card-title">
        <UIIcons.Sparkles size={20} className="text-primary" />
        {language === 'pt' ? 'Distribuição dos Elementos' : 'Elements Distribution'}
      </h3>
      <div className="overview-elements-container">
        <ElementChart 
          data={elementData} 
          title="" 
        />
        
        {/* Explicação dos Elementos */}
        <div className="overview-elements-explanation" style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid hsl(var(--border))' }}>
          <h4 className="overview-elements-explanation-title" style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', color: 'hsl(var(--foreground))' }}>
            {language === 'pt' ? 'O que significam os elementos no seu mapa?' : 'What do the elements mean in your chart?'}
          </h4>
          
          <div className="overview-elements-meanings" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
            <div className="overview-element-meaning" style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--muted) / 0.5)' }}>
              <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.5' }}>
                <strong style={{ color: '#F97316' }}>{language === 'pt' ? '🔥 Fogo' : '🔥 Fire'}</strong>: {language === 'pt' ? 'Energia, ação, entusiasmo e liderança. Você é alguém que age, toma iniciativa e busca expressar sua criatividade no mundo.' : 'Energy, action, enthusiasm and leadership. You are someone who acts, takes initiative and seeks to express your creativity in the world.'}
              </p>
            </div>
            <div className="overview-element-meaning" style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--muted) / 0.5)' }}>
              <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.5' }}>
                <strong style={{ color: '#22C55E' }}>{language === 'pt' ? '🌍 Terra' : '🌍 Earth'}</strong>: {language === 'pt' ? 'Praticidade, estabilidade e realização material. Você valoriza segurança, estrutura e construir coisas concretas na vida.' : 'Practicality, stability and material realization. You value security, structure and building concrete things in life.'}
              </p>
            </div>
            <div className="overview-element-meaning" style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--muted) / 0.5)' }}>
              <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.5' }}>
                <strong style={{ color: '#3B82F6' }}>{language === 'pt' ? '💨 Ar' : '💨 Air'}</strong>: {language === 'pt' ? 'Comunicação, intelecto e conexões sociais. Você precisa de troca de ideias, aprendizado constante e relacionar-se com pessoas.' : 'Communication, intellect and social connections. You need exchange of ideas, constant learning and relating to people.'}
              </p>
            </div>
            <div className="overview-element-meaning" style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--muted) / 0.5)' }}>
              <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.5' }}>
                <strong style={{ color: '#8B5CF6' }}>{language === 'pt' ? '💧 Água' : '💧 Water'}</strong>: {language === 'pt' ? 'Emoções, intuição e profundidade emocional. Você sente tudo intensamente e busca conexões profundas e autênticas.' : 'Emotions, intuition and emotional depth. You feel everything intensely and seek deep and authentic connections.'}
              </p>
            </div>
          </div>

          {/* Explicação do desequilíbrio */}
          <div className="overview-elements-balance" style={{ marginBottom: '1.5rem' }}>
            <h5 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem', color: 'hsl(var(--foreground))' }}>
              {language === 'pt' ? 'Por que você tem mais de alguns elementos?' : 'Why do you have more of some elements?'}
            </h5>
            <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))', marginBottom: '0.5rem' }}>
              {language === 'pt' 
                ? `Ter mais ${dominantElement.name.toLowerCase()} no seu mapa (${dominantElement.percentage}%) mostra que essa energia é muito presente na sua personalidade. Isso não é bom nem ruim - é simplesmente quem você é. Os elementos aparecem de forma desigual porque seus planetas estão distribuídos entre signos diferentes, cada um com seu próprio elemento.`
                : `Having more ${dominantElement.name.toLowerCase()} in your chart (${dominantElement.percentage}%) shows that this energy is very present in your personality. This is neither good nor bad - it's simply who you are. Elements appear unevenly because your planets are distributed among different signs, each with its own element.`}
            </p>
          </div>

          {/* Como isso influencia */}
          <div className="overview-elements-influence" style={{ marginBottom: '1.5rem' }}>
            <h5 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem', color: 'hsl(var(--foreground))' }}>
              {language === 'pt' ? 'Como isso influencia sua vida?' : 'How does this influence your life?'}
            </h5>
            <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))', marginBottom: '0.75rem' }}>
              {language === 'pt'
                ? `Com mais ${dominantElement.name.toLowerCase()}, você tem essa energia como sua força natural. Mas elementos em falta ou pouco presentes mostram áreas que você pode precisar desenvolver mais conscientemente.`
                : `With more ${dominantElement.name.toLowerCase()}, you have this energy as your natural strength. But missing or low elements show areas you may need to develop more consciously.`}
            </p>
            {missingElement && (
              <div style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--primary) / 0.1)', border: '1px solid hsl(var(--primary) / 0.2)' }}>
                <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.6' }}>
                  {language === 'pt'
                    ? `💡 Você não tem planetas em signos de ${missingElement.name}, o que significa que essa energia pode ser menos natural para você. Isso não é um problema - apenas indica uma área para desenvolver ao longo da vida.`
                    : `💡 You don't have planets in ${missingElement.name} signs, which means this energy may be less natural for you. This is not a problem - it just indicates an area to develop throughout life.`}
                </p>
              </div>
            )}
          </div>

          {/* Dicas práticas para evoluir */}
          <div className="overview-elements-tips">
            <h5 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem', color: 'hsl(var(--foreground))' }}>
              {language === 'pt' ? '💫 Como você pode evoluir?' : '💫 How can you evolve?'}
            </h5>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {language === 'pt' ? (
                <>
                  <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                    <strong>• Use sua força natural:</strong> O elemento que você tem mais ({dominantElement.name.toLowerCase()}) é sua energia dominante. Use isso a seu favor - é onde você brilha naturalmente.
                  </p>
                  <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                    <strong>• Desenvolva o que falta:</strong> {missingElement 
                      ? `O elemento ${missingElement.name.toLowerCase()} está ausente no seu mapa. Pratique atividades que desenvolvam essa energia: ${missingElement.name === 'Fogo' ? 'exercícios físicos, esportes, atividades criativas e liderança' : missingElement.name === 'Terra' ? 'organização, planejamento, atividades práticas e conexão com a natureza' : missingElement.name === 'Ar' ? 'leitura, estudos, conversas profundas e networking' : 'meditação, arte, terapia e conexão emocional profunda'}.`
                      : 'Procure equilibrar todos os elementos na sua vida para uma experiência mais completa.'}
                  </p>
                  <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                    <strong>• Equilibre os extremos:</strong> Se você tem muito de um elemento (acima de 40%), pode estar exagerando nessa energia. Pratique o oposto: se tem muito Fogo, desacelere e reflita mais; se tem muita Terra, experimente mais; se tem muito Ar, conecte-se com suas emoções; se tem muita Água, aterre-se e seja mais prático.
                  </p>
                </>
              ) : (
                <>
                  <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                    <strong>• Use your natural strength:</strong> The element you have most ({dominantElement.name.toLowerCase()}) is your dominant energy. Use this to your advantage - it's where you naturally shine.
                  </p>
                  <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                    <strong>• Develop what's missing:</strong> {missingElement
                      ? `The ${missingElement.name.toLowerCase()} element is missing in your chart. Practice activities that develop this energy.`
                      : 'Seek to balance all elements in your life for a more complete experience.'}
                  </p>
                  <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                    <strong>• Balance extremes:</strong> If you have too much of one element (above 40%), you may be overdoing this energy. Practice the opposite.
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
