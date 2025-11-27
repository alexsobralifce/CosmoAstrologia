import React from 'react';

export const PlanetIcons = {
  Sun: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="4" fill="currentColor"/>
      <path d="M12 2V4M12 20V22M22 12H20M4 12H2M19.07 4.93L17.66 6.34M6.34 17.66L4.93 19.07M19.07 19.07L17.66 17.66M6.34 6.34L4.93 4.93" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  
  Moon: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="currentColor" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Mercury: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="11" r="4" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M12 7V3M9 3H15M12 15V21M9 18H15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Venus: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="8" r="5" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M12 13V22M9 19H15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Mars: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="10" cy="14" r="6" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M15 9L21 3M21 3H16M21 3V8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Jupiter: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M7 3V21M14 10H7M14 10C16.209 10 18 11.791 18 14C18 16.209 16.209 18 14 18H11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M3 7H11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  
  Saturn: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M6 3V21M13 10H6M13 10C15.209 10 17 11.791 17 14C17 16.209 15.209 18 13 18H9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M3 10H21" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  
  Uranus: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="14" r="3" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M12 11V4M12 17V22M7 7V12M17 7V12M5 12H9M15 12H19" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Neptune: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M12 3V21M12 21L8 17M12 21L16 17M5 8L12 12L19 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="12" cy="8" r="2" stroke="currentColor" strokeWidth="1.5"/>
    </svg>
  ),
  
  Pluto: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="13" r="4" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M12 9V3M7 6H17M12 17V22M9 19H15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
};

export const planets = [
  { name: "Sol", symbol: "☉", icon: PlanetIcons.Sun },
  { name: "Lua", symbol: "☽", icon: PlanetIcons.Moon },
  { name: "Mercúrio", symbol: "☿", icon: PlanetIcons.Mercury },
  { name: "Vênus", symbol: "♀", icon: PlanetIcons.Venus },
  { name: "Marte", symbol: "♂", icon: PlanetIcons.Mars },
  { name: "Júpiter", symbol: "♃", icon: PlanetIcons.Jupiter },
  { name: "Saturno", symbol: "♄", icon: PlanetIcons.Saturn },
  { name: "Urano", symbol: "♅", icon: PlanetIcons.Uranus },
  { name: "Netuno", symbol: "♆", icon: PlanetIcons.Neptune },
  { name: "Plutão", symbol: "♇", icon: PlanetIcons.Pluto },
];
