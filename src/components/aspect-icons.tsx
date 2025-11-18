export const AspectIcons = {
  Conjunction: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="2" fill="none" />
    </svg>
  ),
  
  Trine: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M12 4L19.5 17.5H4.5L12 4Z" stroke="currentColor" strokeWidth="2" fill="none" strokeLinejoin="round" />
    </svg>
  ),
  
  Sextile: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M12 4L15.5 9.5L21 10.5L16.5 14.5L17.5 20L12 17L6.5 20L7.5 14.5L3 10.5L8.5 9.5L12 4Z" stroke="currentColor" strokeWidth="2" fill="none" strokeLinejoin="round" />
    </svg>
  ),
  
  Square: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <rect x="6" y="6" width="12" height="12" stroke="currentColor" strokeWidth="2" fill="none" />
    </svg>
  ),
  
  Opposition: ({ className = "", size = 24 }: { className?: string; size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" strokeWidth="2" />
      <circle cx="4" cy="12" r="2" fill="currentColor" />
      <circle cx="20" cy="12" r="2" fill="currentColor" />
    </svg>
  ),
};

export type AspectType = 'conjunction' | 'trine' | 'sextile' | 'square' | 'opposition';

export const aspectData: Record<AspectType, { name: string; icon: any; type: 'harmonic' | 'dynamic' | 'neutral'; color: string }> = {
  conjunction: {
    name: 'Conjunção',
    icon: AspectIcons.Conjunction,
    type: 'neutral',
    color: 'text-accent',
  },
  trine: {
    name: 'Trígono',
    icon: AspectIcons.Trine,
    type: 'harmonic',
    color: 'text-green-400',
  },
  sextile: {
    name: 'Sextil',
    icon: AspectIcons.Sextile,
    type: 'harmonic',
    color: 'text-blue-400',
  },
  square: {
    name: 'Quadratura',
    icon: AspectIcons.Square,
    type: 'dynamic',
    color: 'text-red-400',
  },
  opposition: {
    name: 'Oposição',
    icon: AspectIcons.Opposition,
    type: 'dynamic',
    color: 'text-orange-400',
  },
};
