import React from 'react';
import { UIIcons } from './ui-icons';
import { GlossaryTooltip } from './glossary-tooltip';

interface PlanetaryDignity {
  planet: string;
  sign: string;
  dignity: string;
}

interface PlanetaryDignitiesVisualProps {
  dignities: PlanetaryDignity[];
  language: string;
}

// Mapeamento de dignidades para cores e ícones
const dignityInfo = {
  'DOMICÍLIO': {
    color: '#10b981', // green-500
    bgColor: 'rgba(16, 185, 129, 0.1)',
    borderColor: 'rgba(16, 185, 129, 0.3)',
    icon: '⭐',
    label: 'Domicílio',
    labelEn: 'Domicile',
    description: 'O planeta está em seu próprio signo, agindo com máxima força e naturalidade.',
    descriptionEn: 'The planet is in its own sign, acting with maximum strength and naturalness.',
    strength: 5,
  },
  'EXALTAÇÃO': {
    color: '#3b82f6', // blue-500
    bgColor: 'rgba(59, 130, 246, 0.1)',
    borderColor: 'rgba(59, 130, 246, 0.3)',
    icon: '✨',
    label: 'Exaltação',
    labelEn: 'Exaltation',
    description: 'O planeta está em um signo onde suas melhores qualidades são exaltadas. Energia elevada e expressão refinada.',
    descriptionEn: 'The planet is in a sign where its best qualities are exalted. Elevated energy and refined expression.',
    strength: 4,
  },
  'PEREGRINO': {
    color: '#6b7280', // gray-500
    bgColor: 'rgba(107, 114, 128, 0.1)',
    borderColor: 'rgba(107, 114, 128, 0.3)',
    icon: '○',
    label: 'Peregrino',
    labelEn: 'Peregrine',
    description: 'O planeta não está em nenhuma dignidade especial. Sua expressão depende dos aspectos que recebe de outros planetas.',
    descriptionEn: 'The planet is not in any special dignity. Its expression depends on the aspects it receives from other planets.',
    strength: 2,
  },
  'QUEDA': {
    color: '#ef4444', // red-500
    bgColor: 'rgba(239, 68, 68, 0.1)',
    borderColor: 'rgba(239, 68, 68, 0.3)',
    icon: '⚠️',
    label: 'Queda',
    labelEn: 'Fall',
    description: 'O planeta está em um signo onde sua energia é inadequada. Precisa de muito esforço para expressar suas qualidades.',
    descriptionEn: 'The planet is in a sign where its energy is inadequate. Needs much effort to express its qualities.',
    strength: 1,
  },
  'DETRIMENTO': {
    color: '#f59e0b', // amber-500
    bgColor: 'rgba(245, 158, 11, 0.1)',
    borderColor: 'rgba(245, 158, 11, 0.3)',
    icon: '⚡',
    label: 'Detrimento',
    labelEn: 'Detriment',
    description: 'O planeta está no signo oposto ao seu domicílio. Precisa de mais esforço para funcionar bem.',
    descriptionEn: 'The planet is in the sign opposite to its domicile. Needs more effort to function well.',
    strength: 1,
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

export const PlanetaryDignitiesVisual: React.FC<PlanetaryDignitiesVisualProps> = ({ 
  dignities, 
  language 
}) => {
  if (!dignities || dignities.length === 0) return null;

  const isPt = language === 'pt';

  // Agrupar por tipo de dignidade para a legenda
  const groupedByDignity = dignities.reduce((acc, d) => {
    const key = d.dignity.toUpperCase();
    if (!acc[key]) acc[key] = [];
    acc[key].push(d);
    return acc;
  }, {} as Record<string, PlanetaryDignity[]>);

  // Ordenar dignidades por força (mais forte primeiro)
  const sortedDignities = [...dignities].sort((a, b) => {
    const strengthA = dignityInfo[a.dignity.toUpperCase() as keyof typeof dignityInfo]?.strength || 0;
    const strengthB = dignityInfo[b.dignity.toUpperCase() as keyof typeof dignityInfo]?.strength || 0;
    return strengthB - strengthA;
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
          <UIIcons.Star size={20} className="text-primary" />
          {isPt ? 'Dignidades Planetárias' : 'Planetary Dignities'}
        </h3>
        <p style={{ 
          fontSize: '0.875rem', 
          color: 'hsl(var(--muted-foreground))',
          lineHeight: '1.6',
        }}>
          {isPt 
            ? 'As dignidades mostram como cada planeta expressa sua energia no seu mapa. Quanto mais forte a dignidade, mais natural é a expressão do planeta.'
            : 'Dignities show how each planet expresses its energy in your chart. The stronger the dignity, the more natural the planet\'s expression.'}
        </p>
      </div>

      {/* Grid de Planetas */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem',
      }}>
        {sortedDignities.map((dignity, index) => {
          const info = dignityInfo[dignity.dignity.toUpperCase() as keyof typeof dignityInfo];
          if (!info) return null;

          const planetSymbol = planetSymbols[dignity.planet] || '○';

          return (
            <div
              key={index}
              style={{
                padding: '1rem',
                borderRadius: '0.5rem',
                backgroundColor: info.bgColor,
                border: `2px solid ${info.borderColor}`,
                transition: 'all 0.2s ease',
                cursor: 'pointer',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = `0 4px 12px ${info.borderColor}`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              {/* Cabeçalho do Card */}
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem',
                marginBottom: '0.75rem',
              }}>
                <span style={{ fontSize: '1.5rem' }}>{planetSymbol}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    fontSize: '0.875rem', 
                    fontWeight: 600,
                    color: 'hsl(var(--foreground))',
                  }}>
                    {dignity.planet}
                  </div>
                  <div style={{ 
                    fontSize: '0.75rem', 
                    color: 'hsl(var(--muted-foreground))',
                  }}>
                    {dignity.sign}
                  </div>
                </div>
              </div>

              {/* Badge de Dignidade */}
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.375rem 0.75rem',
                borderRadius: '0.375rem',
                backgroundColor: info.bgColor,
                border: `1px solid ${info.borderColor}`,
                fontSize: '0.75rem',
                fontWeight: 600,
                color: info.color,
              }}>
                <span>{info.icon}</span>
                <span>{isPt ? info.label : info.labelEn}</span>
              </div>

              {/* Barra de Força */}
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '0.25rem',
                  fontSize: '0.75rem',
                  color: 'hsl(var(--muted-foreground))',
                }}>
                  <span>{isPt ? 'Força' : 'Strength'}</span>
                  <span>{info.strength}/5</span>
                </div>
                <div style={{
                  width: '100%',
                  height: '6px',
                  borderRadius: '3px',
                  backgroundColor: 'hsl(var(--muted))',
                  overflow: 'hidden',
                }}>
                  <div style={{
                    width: `${(info.strength / 5) * 100}%`,
                    height: '100%',
                    backgroundColor: info.color,
                    transition: 'width 0.3s ease',
                  }} />
                </div>
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
          {isPt ? '📚 O que significa cada dignidade?' : '📚 What does each dignity mean?'}
        </h4>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem',
        }}>
          {Object.entries(dignityInfo).map(([key, info]) => {
            const hasThisDignity = groupedByDignity[key] && groupedByDignity[key].length > 0;
            
            return (
              <div
                key={key}
                style={{
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  backgroundColor: hasThisDignity ? info.bgColor : 'transparent',
                  border: `1px solid ${hasThisDignity ? info.borderColor : 'hsl(var(--border))'}`,
                  opacity: hasThisDignity ? 1 : 0.6,
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
                  {hasThisDignity && (
                    <span style={{
                      fontSize: '0.75rem',
                      padding: '0.125rem 0.375rem',
                      borderRadius: '0.25rem',
                      backgroundColor: info.color,
                      color: 'white',
                      fontWeight: 600,
                    }}>
                      {groupedByDignity[key].length}
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
                {hasThisDignity && (
                  <div style={{ 
                    marginTop: '0.5rem',
                    fontSize: '0.75rem',
                    color: info.color,
                    fontWeight: 500,
                  }}>
                    {isPt 
                      ? `No seu mapa: ${groupedByDignity[key].map(d => d.planet).join(', ')}`
                      : `In your chart: ${groupedByDignity[key].map(d => d.planet).join(', ')}`}
                  </div>
                )}
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
            ? 'Planetas em Domicílio ou Exaltação são seus pontos fortes naturais. Planetas em Queda ou Detrimento precisam de mais atenção e esforço consciente para se desenvolverem plenamente.'
            : 'Planets in Domicile or Exaltation are your natural strengths. Planets in Fall or Detriment need more attention and conscious effort to develop fully.'}
        </p>
      </div>
    </div>
  );
};

// Função helper para extrair dignidades do texto
export function extractDignitiesFromText(text: string): PlanetaryDignity[] {
  const dignities: PlanetaryDignity[] = [];
  const seen = new Set<string>();
  
  // Lista de planetas conhecidos (em português e inglês)
  const planets = [
    'Sol', 'Sun', 'Lua', 'Moon', 'Mercúrio', 'Mercury', 
    'Vênus', 'Venus', 'Marte', 'Mars', 'Júpiter', 'Jupiter',
    'Saturno', 'Saturn', 'Urano', 'Uranus', 'Netuno', 'Neptune',
    'Plutão', 'Pluto'
  ];
  
  // Lista de signos conhecidos
  const signs = [
    'Áries', 'Aries', 'Touro', 'Taurus', 'Gêmeos', 'Gemini',
    'Câncer', 'Cancer', 'Leão', 'Leo', 'Virgem', 'Virgo',
    'Libra', 'Escorpião', 'Scorpio', 'Sagitário', 'Sagittarius',
    'Capricórnio', 'Capricorn', 'Aquário', 'Aquarius', 'Peixes', 'Pisces'
  ];
  
  // Padrões para detectar dignidades no texto
  const patterns = [
    // "* Lua em Leão: PEREGRINO" (com asterisco no início da linha)
    /^\s*\*\s*(\w+)\s+em\s+(\w+):\s*(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi,
    // "- Lua em Leão: PEREGRINO" (com hífen no início da linha)
    /^\s*[-]\s*(\w+)\s+em\s+(\w+):\s*(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi,
    // "Lua em Leão: PEREGRINO" (sem marcador)
    /^\s*(\w+)\s+em\s+(\w+):\s*(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi,
  ];

  patterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const planet = match[1];
      const sign = match[2];
      const dignity = match[3];
      
      // Validar que é realmente um planeta e signo conhecidos
      const isPlanet = planets.some(p => p.toLowerCase() === planet.trim().toLowerCase());
      const isSign = signs.some(s => s.toLowerCase() === sign.trim().toLowerCase());
      
      if (planet && sign && dignity && isPlanet && isSign) {
        const key = `${planet.trim()}-${sign.trim()}-${dignity.trim().toUpperCase()}`;
        if (!seen.has(key)) {
          seen.add(key);
          dignities.push({
            planet: planet.trim(),
            sign: sign.trim(),
            dignity: dignity.trim().toUpperCase(),
          });
        }
      }
    }
  });

  return dignities;
}

