import React from 'react';
import { UIIcons } from './ui-icons';

interface Aspect {
  planet1: string;
  planet2: string;
  type: string;
}

interface AspectsVisualProps {
  aspects: Aspect[];
  language: string;
}

// Informações sobre tipos de aspectos
const aspectInfo = {
  'CONJUNÇÃO': {
    color: '#8b5cf6', // purple-500
    bgColor: 'rgba(139, 92, 246, 0.1)',
    borderColor: 'rgba(139, 92, 246, 0.3)',
    icon: '☌',
    label: 'Conjunção',
    labelEn: 'Conjunction',
    description: 'Os planetas estão muito próximos, unindo suas energias de forma intensa.',
    descriptionEn: 'The planets are very close, uniting their energies intensely.',
    nature: 'Intensa',
    natureEn: 'Intense',
  },
  'SEXTIL': {
    color: '#06b6d4', // cyan-500
    bgColor: 'rgba(6, 182, 212, 0.1)',
    borderColor: 'rgba(6, 182, 212, 0.3)',
    icon: '⚹',
    label: 'Sextil',
    labelEn: 'Sextile',
    description: 'Aspecto harmonioso que facilita oportunidades e conexões criativas.',
    descriptionEn: 'Harmonious aspect that facilitates opportunities and creative connections.',
    nature: 'Harmonioso',
    natureEn: 'Harmonious',
  },
  'TRÍGONO': {
    color: '#10b981', // green-500
    bgColor: 'rgba(16, 185, 129, 0.1)',
    borderColor: 'rgba(16, 185, 129, 0.3)',
    icon: '△',
    label: 'Trígono',
    labelEn: 'Trine',
    description: 'Aspecto muito harmonioso que traz fluidez e facilidade natural.',
    descriptionEn: 'Very harmonious aspect that brings fluidity and natural ease.',
    nature: 'Muito Harmonioso',
    natureEn: 'Very Harmonious',
  },
  'QUADRATURA': {
    color: '#ef4444', // red-500
    bgColor: 'rgba(239, 68, 68, 0.1)',
    borderColor: 'rgba(239, 68, 68, 0.3)',
    icon: '□',
    label: 'Quadratura',
    labelEn: 'Square',
    description: 'Aspecto desafiador que cria tensão e necessidade de ação para crescimento.',
    descriptionEn: 'Challenging aspect that creates tension and need for action for growth.',
    nature: 'Desafiador',
    natureEn: 'Challenging',
  },
  'OPOSIÇÃO': {
    color: '#f59e0b', // amber-500
    bgColor: 'rgba(245, 158, 11, 0.1)',
    borderColor: 'rgba(245, 158, 11, 0.3)',
    icon: '☍',
    label: 'Oposição',
    labelEn: 'Opposition',
    description: 'Aspecto de polaridade que exige integração de forças opostas.',
    descriptionEn: 'Polarity aspect that requires integration of opposing forces.',
    nature: 'Polaridade',
    natureEn: 'Polarity',
  },
};

// Símbolos dos planetas
const planetSymbols: Record<string, string> = {
  'Sol': '☉',
  'Sun': '☉',
  'Lua': '☽',
  'Moon': '☽',
  'Mercúrio': '☿',
  'Mercury': '☿',
  'Vênus': '♀',
  'Venus': '♀',
  'Marte': '♂',
  'Mars': '♂',
  'Júpiter': '♃',
  'Jupiter': '♃',
  'Saturno': '♄',
  'Saturn': '♄',
  'Urano': '♅',
  'Uranus': '♅',
  'Netuno': '♆',
  'Neptune': '♆',
  'Plutão': '♇',
  'Pluto': '♇',
};

export const AspectsVisual: React.FC<AspectsVisualProps> = ({ 
  aspects, 
  language 
}) => {
  if (!aspects || aspects.length === 0) return null;

  const isPt = language === 'pt';

  // Agrupar aspectos por tipo
  const groupedByType = aspects.reduce((acc, aspect) => {
    const key = aspect.type.toUpperCase();
    if (!acc[key]) acc[key] = [];
    acc[key].push(aspect);
    return acc;
  }, {} as Record<string, Aspect[]>);

  // Ordenar tipos de aspectos por importância (tensos primeiro, depois harmoniosos)
  const aspectTypeOrder = ['QUADRATURA', 'OPOSIÇÃO', 'CONJUNÇÃO', 'TRÍGONO', 'SEXTIL'];
  const sortedTypes = Object.keys(groupedByType).sort((a, b) => {
    const indexA = aspectTypeOrder.indexOf(a) !== -1 ? aspectTypeOrder.indexOf(a) : 999;
    const indexB = aspectTypeOrder.indexOf(b) !== -1 ? aspectTypeOrder.indexOf(b) : 999;
    return indexA - indexB;
  });

  return (
    <div style={{ 
      margin: '2rem 0',
      padding: '1.5rem',
      borderRadius: '0.75rem',
      backgroundColor: 'hsl(var(--card))',
      border: '1px solid hsl(var(--border))',
    }}>
      {/* Título */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ 
          fontSize: '1.25rem', 
          fontWeight: 600, 
          marginBottom: '0.5rem',
          color: 'hsl(var(--foreground))',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}>
          <UIIcons.Sparkles size={20} className="text-primary" />
          {isPt ? 'Aspectos Planetários' : 'Planetary Aspects'}
        </h3>
        <p style={{ 
          fontSize: '0.875rem', 
          color: 'hsl(var(--muted-foreground))',
          lineHeight: '1.6',
        }}>
          {isPt 
            ? 'Os aspectos mostram como os planetas se relacionam entre si no seu mapa. Aspectos harmoniosos trazem facilidade, enquanto aspectos tensos trazem desafios e oportunidades de crescimento.'
            : 'Aspects show how planets relate to each other in your chart. Harmonious aspects bring ease, while challenging aspects bring growth opportunities.'}
        </p>
      </div>

      {/* Aspectos agrupados por tipo */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
        marginBottom: '2rem',
      }}>
        {sortedTypes.map((type) => {
          const info = aspectInfo[type as keyof typeof aspectInfo];
          if (!info) return null;

          const typeAspects = groupedByType[type];

          return (
            <div
              key={type}
              style={{
                padding: '1rem',
                borderRadius: '0.5rem',
                backgroundColor: info.bgColor,
                border: `2px solid ${info.borderColor}`,
              }}
            >
              {/* Cabeçalho do tipo */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '1rem',
              }}>
                <span style={{ fontSize: '1.5rem' }}>{info.icon}</span>
                <span style={{
                  fontSize: '1rem',
                  fontWeight: 600,
                  color: info.color,
                }}>
                  {isPt ? info.label : info.labelEn}
                </span>
                <span style={{
                  fontSize: '0.75rem',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '0.25rem',
                  backgroundColor: info.color,
                  color: 'white',
                  fontWeight: 600,
                }}>
                  {typeAspects.length}
                </span>
                <span style={{
                  fontSize: '0.75rem',
                  color: 'hsl(var(--muted-foreground))',
                  marginLeft: 'auto',
                }}>
                  {isPt ? info.nature : info.natureEn}
                </span>
              </div>

              {/* Grid de aspectos */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
                gap: '0.75rem',
              }}>
                {typeAspects.map((aspect, index) => {
                  const symbol1 = planetSymbols[aspect.planet1] || '○';
                  const symbol2 = planetSymbols[aspect.planet2] || '○';

                  return (
                    <div
                      key={index}
                      style={{
                        padding: '0.75rem',
                        borderRadius: '0.375rem',
                        backgroundColor: 'hsl(var(--background))',
                        border: `1px solid ${info.borderColor}`,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        fontSize: '0.875rem',
                      }}
                    >
                      <span style={{ fontSize: '1.25rem' }}>{symbol1}</span>
                      <span style={{ 
                        color: 'hsl(var(--foreground))',
                        fontWeight: 500,
                      }}>
                        {aspect.planet1}
                      </span>
                      <span style={{ 
                        color: info.color,
                        fontSize: '1rem',
                        fontWeight: 600,
                      }}>
                        {info.icon}
                      </span>
                      <span style={{ 
                        color: 'hsl(var(--foreground))',
                        fontWeight: 500,
                      }}>
                        {aspect.planet2}
                      </span>
                      <span style={{ fontSize: '1.25rem' }}>{symbol2}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legenda Explicativa */}
      <div style={{
        padding: '1.25rem',
        borderRadius: '0.5rem',
        backgroundColor: 'hsl(var(--muted) / 0.3)',
        border: '1px solid hsl(var(--border))',
      }}>
        <h4 style={{ 
          fontSize: '1rem', 
          fontWeight: 600, 
          marginBottom: '1rem',
          color: 'hsl(var(--foreground))',
        }}>
          {isPt ? '📚 O que significa cada aspecto?' : '📚 What does each aspect mean?'}
        </h4>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem',
        }}>
          {Object.entries(aspectInfo).map(([key, info]) => {
            const hasThisAspect = groupedByType[key] && groupedByType[key].length > 0;
            
            return (
              <div
                key={key}
                style={{
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  backgroundColor: hasThisAspect ? info.bgColor : 'transparent',
                  border: `1px solid ${hasThisAspect ? info.borderColor : 'hsl(var(--border))'}`,
                  opacity: hasThisAspect ? 1 : 0.6,
                }}
              >
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.5rem',
                  marginBottom: '0.5rem',
                }}>
                  <span style={{ fontSize: '1.25rem' }}>{info.icon}</span>
                  <span style={{ 
                    fontSize: '0.875rem', 
                    fontWeight: 600,
                    color: info.color,
                  }}>
                    {isPt ? info.label : info.labelEn}
                  </span>
                  {hasThisAspect && (
                    <span style={{
                      fontSize: '0.75rem',
                      padding: '0.125rem 0.375rem',
                      borderRadius: '0.25rem',
                      backgroundColor: info.color,
                      color: 'white',
                      fontWeight: 600,
                    }}>
                      {groupedByType[key].length}
                    </span>
                  )}
                </div>
                <p style={{ 
                  fontSize: '0.75rem', 
                  lineHeight: '1.5',
                  color: 'hsl(var(--muted-foreground))',
                  margin: 0,
                }}>
                  {isPt ? info.description : info.descriptionEn}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Dica Final */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        borderRadius: '0.5rem',
        backgroundColor: 'hsl(var(--primary) / 0.1)',
        border: '1px solid hsl(var(--primary) / 0.2)',
      }}>
        <p style={{ 
          margin: 0,
          fontSize: '0.875rem',
          lineHeight: '1.6',
          color: 'hsl(var(--foreground))',
        }}>
          <strong>💡 {isPt ? 'Dica:' : 'Tip:'}</strong>{' '}
          {isPt 
            ? 'Aspectos harmoniosos (Trígono, Sextil) trazem facilidade natural. Aspectos tensos (Quadratura, Oposição) trazem desafios que, quando trabalhados conscientemente, resultam em crescimento significativo.'
            : 'Harmonious aspects (Trine, Sextile) bring natural ease. Challenging aspects (Square, Opposition) bring challenges that, when worked consciously, result in significant growth.'}
        </p>
      </div>
    </div>
  );
};

// Função helper para extrair aspectos do texto
export function extractAspectsFromText(text: string): Aspect[] {
  const aspects: Aspect[] = [];
  const seen = new Set<string>();
  
  // Lista de planetas conhecidos
  const planets = [
    'Sol', 'Sun', 'Lua', 'Moon', 'Mercúrio', 'Mercury', 
    'Vênus', 'Venus', 'Marte', 'Mars', 'Júpiter', 'Jupiter',
    'Saturno', 'Saturn', 'Urano', 'Uranus', 'Netuno', 'Neptune',
    'Plutão', 'Pluto'
  ];
  
  // Padrões para detectar aspectos no texto
  const patterns = [
    // "* Sextil Sol-Lua" ou "* Conjunção Sol-Mercúrio"
    /^\s*[-*]\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+([A-ZÁÊÔÇa-záêôç]+)-([A-ZÁÊÔÇa-záêôç]+)\s*$/gmi,
    // "Sextil Sol-Lua" (sem marcador)
    /^\s*(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+([A-ZÁÊÔÇa-záêôç]+)-([A-ZÁÊÔÇa-záêôç]+)\s*$/gmi,
  ];

  patterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const type = match[1];
      const planet1 = match[2];
      const planet2 = match[3];
      
      // Validar que são planetas conhecidos
      const isPlanet1 = planets.some(p => p.toLowerCase() === planet1.trim().toLowerCase());
      const isPlanet2 = planets.some(p => p.toLowerCase() === planet2.trim().toLowerCase());
      
      if (type && planet1 && planet2 && isPlanet1 && isPlanet2) {
        const key = `${planet1.trim()}-${planet2.trim()}-${type.trim().toUpperCase()}`;
        const reverseKey = `${planet2.trim()}-${planet1.trim()}-${type.trim().toUpperCase()}`;
        
        // Evitar duplicatas (Sol-Lua é o mesmo que Lua-Sol)
        if (!seen.has(key) && !seen.has(reverseKey)) {
          seen.add(key);
          seen.add(reverseKey);
          aspects.push({
            planet1: planet1.trim(),
            planet2: planet2.trim(),
            type: type.trim().toUpperCase(),
          });
        }
      }
    }
  });

  return aspects;
}

