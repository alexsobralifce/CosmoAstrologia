import React from 'react';

interface Transit {
  id: string;
  type: 'jupiter' | 'saturn-return' | 'uranus' | 'neptune' | 'pluto';
  title: string;
  planet: string;
  timeframe: string;
  description: string;
  isActive?: boolean;
  start_date?: string;
  end_date?: string;
  aspect_type?: string;
  aspect_type_display?: string;
  natal_point?: string;
}

interface FutureTransitsSectionProps {
  transits?: Transit[];
}

export const FutureTransitsSection = ({ transits }: FutureTransitsSectionProps) => {
  return (
    <div data-testid="future-transits-section">
      <div>Future Transits Section</div>
    </div>
  );
};
