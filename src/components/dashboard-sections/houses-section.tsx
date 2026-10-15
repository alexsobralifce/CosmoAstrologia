import React from 'react';
import { useState } from 'react';
import { UIIcons } from '../ui-icons';
import { apiService } from '../../services/api';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';

// ===== CASAS =====
interface HousesSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const HousesSection = ({ userData, onBack }: HousesSectionProps) => {
  const { language } = useLanguage();
  const [selectedHouse, setSelectedHouse] = useState<number | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const houseMeanings = {
    pt: [
      { house: 1, title: 'Identidade', desc: 'Aparência física, personalidade e primeira impressão' },
      { house: 2, title: 'Recursos', desc: 'Finanças pessoais, valores e posses materiais' },
      { house: 3, title: 'Comunicação', desc: 'Irmãos, vizinhos, estudos e aprendizado' },
      { house: 4, title: 'Lar', desc: 'Família, raízes, lar e vida doméstica' },
      { house: 5, title: 'Criatividade', desc: 'Romance, filhos, diversão e hobbies' },
      { house: 6, title: 'Rotina', desc: 'Saúde, trabalho diário e prestação de serviço' },
      { house: 7, title: 'Parcerias', desc: 'Casamento, sociedades e contratos' },
      { house: 8, title: 'Transformação', desc: 'Crises, heranças, sexualidade e recursos compartilhados' },
      { house: 9, title: 'Expansão', desc: 'Viagens longas, filosofia e ensino superior' },
      { house: 10, title: 'Carreira', desc: 'Profissão, vocação, status e reputação pública' },
      { house: 11, title: 'Amizades', desc: 'Grupos, redes sociais, sonhos e causas coletivas' },
      { house: 12, title: 'Espiritualidade', desc: 'Inconsciente, karma, isolamento e transcendência' },
    ],
    en: [
      { house: 1, title: 'Identity', desc: 'Physical appearance, personality and first impression' },
      { house: 2, title: 'Resources', desc: 'Personal finances, values and material possessions' },
      { house: 3, title: 'Communication', desc: 'Siblings, neighbors, studies and learning' },
      { house: 4, title: 'Home', desc: 'Family, roots, home and domestic life' },
      { house: 5, title: 'Creativity', desc: 'Romance, children, fun and hobbies' },
      { house: 6, title: 'Routine', desc: 'Health, daily work and service provision' },
      { house: 7, title: 'Partnerships', desc: 'Marriage, partnerships and contracts' },
      { house: 8, title: 'Transformation', desc: 'Crises, inheritance, sexuality and shared resources' },
      { house: 9, title: 'Expansion', desc: 'Long travels, philosophy and higher education' },
      { house: 10, title: 'Career', desc: 'Profession, vocation, status and public reputation' },
      { house: 11, title: 'Friendships', desc: 'Groups, social networks, dreams and collective causes' },
      { house: 12, title: 'Spirituality', desc: 'Unconscious, karma, isolation and transcendence' },
    ],
  };

  const houses = houseMeanings[language === 'pt' ? 'pt' : 'en'];

  const fetchHouseInterpretation = async (house: number) => {
    try {
      setIsLoading(true);
      setSelectedHouse(house);
      const result = await apiService.getInterpretation({
        house: house,
        custom_query: `Casa ${house} no mapa astral significado interpretação áreas da vida`,
        use_groq: true,
      });
      setInterpretation(result.interpretation);
    } catch (error) {
      console.error('Erro ao buscar interpretação:', error);
      const houseData = houses.find(h => h.house === house);
      setInterpretation(
        language === 'pt'
          ? `A Casa ${house} rege ${houseData?.desc}. Esta área do mapa revela como você lida com esses temas na sua vida.`
          : `House ${house} rules ${houseData?.desc}. This area of the chart reveals how you handle these themes in your life.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard-section-container">
      {/* Header */}
      <div className="section-header">
        <div className="section-header-content">
          <h2 className="section-title">
            {language === 'pt' ? 'As 12 Casas Astrológicas' : 'The 12 Astrological Houses'}
          </h2>
          <p className="section-subtitle">
            {language === 'pt' ? 'Cada casa representa uma área da sua vida' : 'Each house represents an area of your life'}
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

      {/* Explicação */}
      <div className="houses-info-container">
        <div className="houses-info-content">
          <div className="houses-info-icon">
            <UIIcons.Info size={20} className="text-primary" />
          </div>
          <div className="houses-info-text">
            <h3 className="houses-info-title">
              {language === 'pt' ? 'Como usar esta seção' : 'How to use this section'}
            </h3>
            <p className="houses-info-description">
              {language === 'pt' 
                ? 'As 12 casas astrológicas dividem o mapa natal em áreas específicas da vida, cada uma representando diferentes aspectos da sua experiência humana. Clique em qualquer uma das casas abaixo para ver uma análise personalizada baseada no seu mapa natal.'
                : 'The 12 astrological houses divide the birth chart into specific life areas, each representing different aspects of your human experience. Click on any house below to see a personalized analysis based on your birth chart.'}
            </p>
            <div className="houses-info-categories">
              <div className="houses-info-category">
                <span className="houses-info-category-bullet">•</span>
                <span className="houses-info-category-text">
                  {language === 'pt' ? 'Casas 1-4: Identidade e Fundamentos' : 'Houses 1-4: Identity and Foundations'}
                </span>
              </div>
              <div className="houses-info-category">
                <span className="houses-info-category-bullet">•</span>
                <span className="houses-info-category-text">
                  {language === 'pt' ? 'Casas 5-8: Criatividade e Relações' : 'Houses 5-8: Creativity and Relationships'}
                </span>
              </div>
              <div className="houses-info-category">
                <span className="houses-info-category-bullet">•</span>
                <span className="houses-info-category-text">
                  {language === 'pt' ? 'Casas 9-12: Expansão e Transcendência' : 'Houses 9-12: Expansion and Transcendence'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Houses Grid */}
      <div className="houses-list-container">
        <h3 className="houses-list-title">
          <UIIcons.Home size={18} className="text-primary" />
          {language === 'pt' ? 'Selecione uma Casa para Ver a Análise' : 'Select a House to See the Analysis'}
        </h3>
        <div className="houses-grid">
          {houses.map((house) => {
            const isSelected = selectedHouse === house.house;
            return (
              <button
                key={house.house}
                onClick={() => fetchHouseInterpretation(house.house)}
                className={`house-card ${isSelected ? 'selected' : ''}`}
              >
                <div className="house-card-number">
                  {house.house}
                </div>
                <p className="house-card-title">{house.title}</p>
                <p className="house-card-desc">{house.desc}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Interpretation Panel */}
      {selectedHouse && (
        <div className="house-interpretation-panel">
          <div className="house-interpretation-header">
            <div className="house-interpretation-number">
              {selectedHouse}
            </div>
            <div className="house-interpretation-title-container">
              <h3 className="house-interpretation-title">
                Casa {selectedHouse}: {houses.find(h => h.house === selectedHouse)?.title}
              </h3>
              <div className="house-interpretation-meta">
                <UIIcons.Home size={14} />
                <span>{houses.find(h => h.house === selectedHouse)?.desc}</span>
              </div>
            </div>
          </div>

          {isLoading ? (
            <div className="house-loading-container">
              <UIIcons.Loader className="house-loading-spinner" />
              <p className="house-loading-text">
                {language === 'pt' ? 'Buscando interpretação personalizada...' : 'Fetching personalized interpretation...'}
              </p>
            </div>
          ) : (
            <div className="house-interpretation-content">
              <div className="house-interpretation-divider"></div>
              <div className="house-interpretation-text">
                {interpretation.split('\n\n').map((paragraph, idx) => {
                  // Detecta se é um título/tópico (linhas que começam com maiúscula e terminam com :)
                  const isHeading = paragraph.match(/^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.!?]*:$/);
                  // Detecta listas com marcadores
                  const isList = paragraph.includes('\n-') || paragraph.includes('\n•') || paragraph.includes('\n*');
                  
                  if (isHeading) {
                    return (
                      <h4 key={idx} className="house-interpretation-heading">
                        <span className="house-interpretation-heading-bullet"></span>
                        {paragraph.replace(':', '')}
                      </h4>
                    );
                  } else if (isList) {
                    const items = paragraph.split('\n').filter(line => line.trim());
                    return (
                      <ul key={idx} className="house-interpretation-list">
                        {items.map((item, i) => {
                          const cleanItem = item.replace(/^[-•*]\s*/, '').trim();
                          if (!cleanItem) return null;
                          return (
                            <li key={i} className="house-interpretation-list-item">
                              <span className="house-interpretation-list-bullet">•</span>
                              <span>{cleanItem}</span>
                            </li>
                          );
                        })}
                      </ul>
                    );
                  } else if (paragraph.trim()) {
                    return (
                      <p key={idx} className="house-interpretation-text">
                        {paragraph}
                      </p>
                    );
                  }
                  return null;
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
