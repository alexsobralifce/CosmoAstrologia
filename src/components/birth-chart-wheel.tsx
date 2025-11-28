import React, { useState } from 'react';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';

interface PlanetPosition {
  planet: string;
  sign: string;
  degree: number;
  house: number;
  icon: any;
}

interface BirthChartWheelProps {
  userData?: any;
  size?: number;
}

export const BirthChartWheel = ({ userData, size = 400 }: BirthChartWheelProps) => {
  const [hoveredPlanet, setHoveredPlanet] = useState<string | null>(null);

  // Mock data - Em produção, isso viria de um cálculo astrológico real
  const planetPositions: PlanetPosition[] = [
    { planet: 'Sol', sign: 'Leão', degree: 15, house: 5, icon: planets[0].icon },
    { planet: 'Lua', sign: 'Touro', degree: 22, house: 2, icon: planets[1].icon },
    { planet: 'Mercúrio', sign: 'Câncer', degree: 8, house: 4, icon: planets[2].icon },
    { planet: 'Vênus', sign: 'Gêmeos', degree: 28, house: 3, icon: planets[3].icon },
    { planet: 'Marte', sign: 'Áries', degree: 12, house: 1, icon: planets[4].icon },
    { planet: 'Júpiter', sign: 'Sagitário', degree: 5, house: 9, icon: planets[5].icon },
    { planet: 'Saturno', sign: 'Capricórnio', degree: 18, house: 10, icon: planets[6].icon },
    { planet: 'Urano', sign: 'Aquário', degree: 25, house: 11, icon: planets[7].icon },
    { planet: 'Netuno', sign: 'Peixes', degree: 3, house: 12, icon: planets[8].icon },
    { planet: 'Plutão', sign: 'Escorpião', degree: 20, house: 8, icon: planets[9].icon },
  ];

  return (
    <div style={{ width: '100%', maxWidth: `${size}px`, aspectRatio: '1', margin: '0 auto' }}>
      <svg viewBox="0 0 400 400" style={{ width: '100%', height: '100%' }}>
        {/* Background circles - múltiplos círculos concêntricos */}
        <circle cx="200" cy="200" r="190" fill="none" stroke="hsl(var(--border))" strokeWidth="1" opacity="0.3" />
        <circle cx="200" cy="200" r="170" fill="none" stroke="hsl(var(--border))" strokeWidth="1" opacity="0.3" />
        <circle cx="200" cy="200" r="150" fill="none" stroke="hsl(var(--border))" strokeWidth="1" opacity="0.3" />
        <circle cx="200" cy="200" r="130" fill="none" stroke="hsl(var(--border))" strokeWidth="1" opacity="0.3" />
        <circle cx="200" cy="200" r="110" fill="none" stroke="hsl(var(--border))" strokeWidth="1" opacity="0.3" />
        <circle cx="200" cy="200" r="90" fill="none" stroke="hsl(var(--border))" strokeWidth="1" opacity="0.3" />
        
        {/* House divisions (12 houses) - linhas radiais */}
        {Array.from({ length: 12 }).map((_, i) => {
          const angle = (i * 30 - 90) * (Math.PI / 180);
          const x1 = 200 + 90 * Math.cos(angle);
          const y1 = 200 + 90 * Math.sin(angle);
          const x2 = 200 + 190 * Math.cos(angle);
          const y2 = 200 + 190 * Math.sin(angle);
          return (
            <line
              key={i}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="hsl(var(--border))"
              strokeWidth="1"
              opacity="0.4"
            />
          );
        })}

        {/* Zodiac sign symbols around the outer ring - roxo/escuro */}
        {zodiacSigns.map((sign, i) => {
          const angle = (i * 30 + 15 - 90) * (Math.PI / 180);
          const x = 200 + 180 * Math.cos(angle);
          const y = 200 + 180 * Math.sin(angle);
          return (
            <g key={sign.name}>
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="hsl(var(--primary))"
                fontSize="20"
                fontWeight="500"
                style={{ fontFamily: 'var(--font-serif)' }}
              >
                {sign.symbol}
              </text>
            </g>
          );
        })}

        {/* House numbers - laranja (accent) */}
        {Array.from({ length: 12 }).map((_, i) => {
          const angle = (i * 30 + 15 - 90) * (Math.PI / 180);
          const x = 200 + 120 * Math.cos(angle);
          const y = 200 + 120 * Math.sin(angle);
          return (
            <text
              key={i}
              x={x}
              y={y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="hsl(var(--accent))"
              fontSize="14"
              fontWeight="600"
            >
              {i + 1}
            </text>
          );
        })}

        {/* Planet positions - roxo/rosa escuro com contornos laranja */}
        {planetPositions.map((planet, i) => {
          // Calculate position based on degree (simplified)
          const totalDegree = (zodiacSigns.findIndex(z => z.name === planet.sign) * 30) + planet.degree;
          const angle = (totalDegree - 90) * (Math.PI / 180);
          const radius = 140;
          const x = 200 + radius * Math.cos(angle);
          const y = 200 + radius * Math.sin(angle);

          return (
            <g
              key={planet.planet}
              onMouseEnter={() => setHoveredPlanet(planet.planet)}
              onMouseLeave={() => setHoveredPlanet(null)}
              className="cursor-pointer transition-all"
            >
              {/* Círculo de fundo com contorno laranja */}
              <circle
                cx={x}
                cy={y}
                r={hoveredPlanet === planet.planet ? 14 : 12}
                fill="hsl(var(--card))"
                stroke="hsl(var(--accent))"
                strokeWidth="2"
              />
              {/* Símbolo do planeta em roxo/primary */}
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="hsl(var(--primary))"
                fontSize={hoveredPlanet === planet.planet ? "16" : "14"}
                fontWeight="500"
              >
                {planets.find(p => p.name === planet.planet)?.symbol}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Hover tooltip */}
      {hoveredPlanet && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-card backdrop-blur-md border border-border rounded-lg px-4 py-2 shadow-lg">
          <p className="text-foreground whitespace-nowrap">
            <span className="text-accent">{hoveredPlanet}</span>
            {' em '}
            <span className="text-accent">
              {planetPositions.find(p => p.planet === hoveredPlanet)?.sign}
            </span>
            {' ('}
            {planetPositions.find(p => p.planet === hoveredPlanet)?.degree}°
            {')'}
          </p>
        </div>
      )}
    </div>
  );
};
