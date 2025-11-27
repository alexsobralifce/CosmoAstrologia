import React from 'react';

export const ZodiacIcons = {
  Aries: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M6 12C6 8.686 8.686 6 12 6M12 6C15.314 6 18 8.686 18 12M12 6V2M6 12H2M18 12H22M9 18L12 22L15 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Taurus: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="14" r="5" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M7 9C7 5.686 9.239 3 12 3C14.761 3 17 5.686 17 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M5 9H19" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  
  Gemini: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M9 4V20M15 4V20M6 4H18M6 20H18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="9" cy="8" r="1.5" fill="currentColor"/>
      <circle cx="15" cy="16" r="1.5" fill="currentColor"/>
    </svg>
  ),
  
  Cancer: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="7" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/>
      <circle cx="17" cy="17" r="4" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M11 7H17M7 13V17" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  
  Leo: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="1.5"/>
      <path d="M12 7V3M17 12H21M12 17V21M7 12H3M15.5 8.5L18.5 5.5M15.5 15.5L18.5 18.5M8.5 15.5L5.5 18.5M8.5 8.5L5.5 5.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  
  Virgo: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M6 3V15M10 3V15M14 3V18C14 19.657 15.343 21 17 21C18.657 21 20 19.657 20 18V15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M4 15H8M8 15H12M8 15V18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  
  Libra: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M4 16H20M6 12C6 9.239 8.239 7 11 7H13C15.761 7 18 9.239 18 12V16M12 7V4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="6" cy="16" r="2" stroke="currentColor" strokeWidth="1.5"/>
      <circle cx="18" cy="16" r="2" stroke="currentColor" strokeWidth="1.5"/>
    </svg>
  ),
  
  Scorpio: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M5 4V14C5 15.657 6.343 17 8 17C9.657 17 11 15.657 11 14V4M11 14V17M15 4V17M15 17L19 21M15 17L19 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Sagittarius: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M4 20L20 4M20 4V12M20 4H12M13 15L15 17" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Capricorn: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M6 3V12C6 14.209 7.791 16 10 16H14M14 16C14 18.209 15.791 20 18 20C20.209 20 22 18.209 22 16C22 13.791 20.209 12 18 12M14 16V8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  ),
  
  Aquarius: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M3 9L6 12L9 9L12 12L15 9L18 12L21 9M3 15L6 18L9 15L12 18L15 15L18 18L21 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  
  Pisces: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M3 6C3 6 6 9 6 12C6 15 3 18 3 18M21 6C21 6 18 9 18 12C18 15 21 18 21 18M6 12H18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
};

export const zodiacSigns = [
  { name: "Áries", symbol: "♈", icon: ZodiacIcons.Aries },
  { name: "Touro", symbol: "♉", icon: ZodiacIcons.Taurus },
  { name: "Gêmeos", symbol: "♊", icon: ZodiacIcons.Gemini },
  { name: "Câncer", symbol: "♋", icon: ZodiacIcons.Cancer },
  { name: "Leão", symbol: "♌", icon: ZodiacIcons.Leo },
  { name: "Virgem", symbol: "♍", icon: ZodiacIcons.Virgo },
  { name: "Libra", symbol: "♎", icon: ZodiacIcons.Libra },
  { name: "Escorpião", symbol: "♏", icon: ZodiacIcons.Scorpio },
  { name: "Sagitário", symbol: "♐", icon: ZodiacIcons.Sagittarius },
  { name: "Capricórnio", symbol: "♑", icon: ZodiacIcons.Capricorn },
  { name: "Aquário", symbol: "♒", icon: ZodiacIcons.Aquarius },
  { name: "Peixes", symbol: "♓", icon: ZodiacIcons.Pisces },
];
