import React, { useState } from 'react';
import { UIIcons } from '../ui-icons';
import { zodiacSigns } from '../zodiac-icons';
import { apiService } from '../../services/api';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';
import { AstroButton } from '../astro-button';
import { InlineBold } from '../ui/inline-bold';
import { removeSupportAndTechnicalContent } from './text-cleaners';

// ===== SINASTRIA =====
interface SynastrySectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const SynastrySection = ({ userData, onBack }: SynastrySectionProps) => {
  const { language } = useLanguage();
  const [partnerSign, setPartnerSign] = useState<string>('');
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const userSunSign = userData.sunSign || 'Áries';

  // Função para formatar o texto da compatibilidade organizando por tópicos
  const formatCompatibilityText = (text: string): React.ReactNode => {
    if (!text || !text.trim()) {
      console.warn('[Sinastria] Texto vazio para formatar');
      return null;
    }

    // Remover conteúdo indesejado: tudo a partir de "### Astrologia Moderna" ou "## 📞 Suporte"
    let cleanedText = removeSupportAndTechnicalContent(text);
    const unwantedPatterns = [
      /###\s*Astrologia Moderna.*$/s,
      /##\s*📞\s*Suporte.*$/s,
      /###\s*Astrologia Moderna \(Psicológica\).*$/s,
      /##\s*Suporte.*$/s
    ];
    
    for (const pattern of unwantedPatterns) {
      const match = cleanedText.match(pattern);
      if (match) {
        cleanedText = cleanedText.substring(0, match.index).trim();
        break;
      }
    }

    // Dividir o texto em parágrafos (por quebras de linha duplas ou simples)
    const paragraphs = cleanedText.split(/\n\n|\n/).filter(p => p.trim());
    
    if (paragraphs.length === 0) {
      console.warn('[Sinastria] Nenhum parágrafo encontrado');
      return <p className="synastry-text-paragraph">{text}</p>;
    }
    
    // Identificar tópicos (números, bullets, títulos em negrito, etc.)
    const formattedParagraphs: React.ReactNode[] = [];
    
    // Detectar se estamos em uma seção de exemplos práticos
    let isExamplesSection = false;
    
    paragraphs.forEach((paragraph, index) => {
      const trimmed = paragraph.trim();
      if (!trimmed) return;

      // Verificar se é uma seção de exemplos práticos
      const isExamplesTitle = trimmed.toLowerCase().includes('exemplo') && 
                              (trimmed.toLowerCase().includes('prático') || trimmed.toLowerCase().includes('prática'));
      
      if (isExamplesTitle) {
        isExamplesSection = true;
        // Título da seção de exemplos
        const titleText = trimmed.replace(/\*\*/g, '').replace(/:/g, '');
        formattedParagraphs.push(
          <h4 key={index} className="synastry-examples-title">
            {titleText}
          </h4>
        );
        return;
      }

      // Se estamos na seção de exemplos, formatar como exemplo
      if (isExamplesSection) {
        // Remover bullet points se existirem
        const cleanLine = trimmed.replace(/^[•\-]\s*/, '');
        formattedParagraphs.push(
          <div key={index} className="synastry-example-item">
            <div className="synastry-example-box">
              <p className="synastry-example-text">{cleanLine}</p>
            </div>
          </div>
        );
        return;
      }

      // Verificar se é um tópico numerado (1., 2., etc.)
      const numberedMatch = trimmed.match(/^(\d+)[\.\)]\s*(.+)$/);
      // Verificar se é um bullet (-, •, etc.)
      const bulletMatch = trimmed.match(/^[-•*]\s*(.+)$/);
      // Verificar se contém texto em negrito (markdown **texto**)
      const boldMatch = trimmed.match(/\*\*(.+?)\*\*/);
      // Verificar se é um título (linha que termina com : e tem menos de 60 chars)
      const isTitle = trimmed.endsWith(':') && trimmed.length < 60 && !trimmed.includes('.');

      if (isTitle || (boldMatch && trimmed.length < 60)) {
        // Título ou texto em negrito como título
        const titleText = boldMatch ? boldMatch[1] : trimmed.replace(':', '');
        formattedParagraphs.push(
          <h4 key={index} className="synastry-text-title">
            {titleText}
          </h4>
        );
      } else if (numberedMatch) {
        // Tópico numerado
        formattedParagraphs.push(
          <div key={index} className="synastry-text-numbered">
            <span className="synastry-text-number">{numberedMatch[1]}.</span>
            <span className="synastry-text-content">{numberedMatch[2]}</span>
          </div>
        );
      } else if (bulletMatch) {
        // Tópico com bullet
        formattedParagraphs.push(
          <div key={index} className="synastry-text-bullet">
            <span className="synastry-text-bullet-marker">•</span>
            <span className="synastry-text-content">{bulletMatch[1]}</span>
          </div>
        );
      } else {
        // Parágrafo normal - processar markdown inline
        formattedParagraphs.push(
          <p key={index} className="synastry-text-paragraph"><InlineBold text={trimmed} /></p>
        );
      }
    });

    return <div className="synastry-text-container">{formattedParagraphs}</div>;
  };

  const fetchCompatibility = async () => {
    if (!partnerSign) {
      console.warn('[Sinastria] Nenhum signo do parceiro selecionado');
      return;
    }
    
    try {
      setIsLoading(true);
      setInterpretation(''); // Limpar interpretação anterior
      
      console.log(`[Sinastria] Buscando compatibilidade: ${userSunSign} + ${partnerSign}`);
      
      // Usar o novo endpoint específico de sinastria que busca características de cada signo
      const result = await apiService.getSynastryInterpretation({
        sign1: userSunSign,
        sign2: partnerSign,
        language: language,
      });
      
      console.log('[Sinastria] Resposta recebida:', {
        hasInterpretation: !!result?.interpretation,
        length: result?.interpretation?.length || 0,
        generatedBy: result?.generated_by,
        hasSign1Info: !!result?.sign1_info,
        hasSign2Info: !!result?.sign2_info
      });
      
      // Verificar se a interpretação foi gerada corretamente
      if (result && result.interpretation) {
        const interpretationText = result.interpretation.trim();
        
        if (interpretationText.length > 20) {
          // Se tiver conteúdo válido, usar
          setInterpretation(interpretationText);
          console.log('[Sinastria] Interpretação definida com sucesso');
        } else {
          console.warn('[Sinastria] Interpretação muito curta - pode ser que não houve informações suficientes no RAG');
          throw new Error(language === 'pt' 
            ? 'Interpretação muito curta. Pode não haver informações suficientes sobre estes signos na base de conhecimento.'
            : 'Interpretation too short. There may not be enough information about these signs in the knowledge base.');
        }
      } else {
        console.error('[Sinastria] Resposta sem interpretação válida');
        throw new Error('Resposta sem interpretação');
      }
    } catch (error: any) {
      console.error('[Sinastria] Erro ao buscar compatibilidade:', error);
      
      // Não usar fallback estático - mostrar erro real
      const errorMessage = language === 'pt'
        ? `**Erro ao gerar interpretação de sinastria**

Não foi possível gerar uma interpretação personalizada para ${userSunSign} e ${partnerSign} no momento.

**Possíveis causas:**
- Informações insuficientes na base de conhecimento sobre estes signos
- Problema temporário no serviço de interpretação
- Erro de conexão com o servidor

**O que fazer:**
- Tente novamente em alguns instantes
- Verifique sua conexão com a internet
- Se o problema persistir, entre em contato com o suporte

**Detalhes técnicos:**
${error?.message || 'Erro desconhecido'}`
        : `**Error generating synastry interpretation**

Unable to generate a personalized interpretation for ${userSunSign} and ${partnerSign} at this time.

**Possible causes:**
- Insufficient information in the knowledge base about these signs
- Temporary problem with the interpretation service
- Connection error with the server

**What to do:**
- Try again in a few moments
- Check your internet connection
- If the problem persists, contact support

**Technical details:**
${error?.message || 'Unknown error'}`;
      
      setInterpretation(errorMessage);
      console.error('[Sinastria] Erro capturado - sem fallback estático');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="section-header">
        <div className="section-header-content">
          <h2 className="section-title">
            {language === 'pt' ? 'Sinastria' : 'Synastry'}
          </h2>
          <p className="section-subtitle">
            {language === 'pt' ? 'Análise de compatibilidade entre mapas' : 'Compatibility analysis between charts'}
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

      {/* Information Card */}
      <div className="synastry-info-card">
        <h3 className="synastry-info-title">
          {language === 'pt' ? 'O que é Sinastria?' : 'What is Synastry?'}
        </h3>
        <p className="synastry-info-text">
          {language === 'pt' 
            ? 'A sinastria é uma técnica astrológica que analisa a compatibilidade entre dois mapas astrais, comparando as posições planetárias de duas pessoas para entender as dinâmicas do relacionamento. Ela revela pontos de conexão, desafios e potenciais de crescimento conjunto, ajudando a compreender melhor como as energias de cada pessoa interagem e se complementam.'
            : 'Synastry is an astrological technique that analyzes compatibility between two birth charts by comparing the planetary positions of two people to understand relationship dynamics. It reveals connection points, challenges, and potential for joint growth, helping to better understand how each person\'s energies interact and complement each other.'}
        </p>
      </div>

      {/* Your Sign */}
      <div className="synastry-user-sign-card">
        <div className="synastry-user-sign-content">
          <div className="synastry-sign-icon-container">
            {(() => {
              const SignIcon = zodiacSigns.find(z => z.name === userSunSign)?.icon;
              return SignIcon ? <SignIcon size={32} className="synastry-sign-icon" /> : null;
            })()}
          </div>
          <div>
            <p className="synastry-user-sign-label">{language === 'pt' ? 'Seu Signo Solar' : 'Your Sun Sign'}</p>
            <p className="synastry-user-sign-name">{userSunSign}</p>
          </div>
        </div>
      </div>

      {/* Partner Sign Selection */}
      <div className="synastry-partner-selection-card">
        <h3 className="synastry-partner-selection-title">
          {language === 'pt' ? 'Selecione o signo do parceiro(a)' : 'Select partner\'s sign'}
        </h3>
        <div className="synastry-signs-grid">
          {zodiacSigns.map((sign) => {
            const SignIcon = sign.icon;
            const isSelected = partnerSign === sign.name;
            return (
              <button
                key={sign.name}
                onClick={() => setPartnerSign(sign.name)}
                className={`synastry-sign-button ${isSelected ? 'synastry-sign-button-selected' : ''}`}
              >
                <div className="synastry-sign-button-icon-container">
                  <SignIcon size={24} className={`synastry-sign-button-icon ${isSelected ? 'synastry-sign-button-icon-selected' : ''}`} />
                </div>
                <p className="synastry-sign-button-name">{sign.name}</p>
              </button>
            );
          })}
        </div>
        
        {partnerSign && (
          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <AstroButton
              onClick={fetchCompatibility}
              disabled={isLoading}
              variant="primary"
              size="md"
            >
              {isLoading ? (
                <>
                  <UIIcons.Loader className="synastry-analyze-button-loader" />
                  {language === 'pt' ? 'Analisando...' : 'Analyzing...'}
                </>
              ) : (
                language === 'pt' ? 'Analisar Compatibilidade' : 'Analyze Compatibility'
              )}
            </AstroButton>
          </div>
        )}
      </div>

      {/* Interpretation */}
      {interpretation ? (
        <div className="synastry-interpretation-card">
          <h3 className="synastry-interpretation-title">
            {userSunSign} + {partnerSign}
          </h3>
          <div className="synastry-interpretation-content">
            {formatCompatibilityText(interpretation)}
          </div>
        </div>
      ) : isLoading ? (
        <div className="synastry-interpretation-card">
          <div className="synastry-loading-container">
            <UIIcons.Loader className="synastry-loading-spinner" />
            <p className="synastry-loading-text">
              {language === 'pt' ? 'Analisando compatibilidade...' : 'Analyzing compatibility...'}
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
};
