import React from 'react';
import { OnboardingData } from '../onboarding';

interface NumerologySectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const NumerologySection = ({ userData, onBack }: NumerologySectionProps) => {
  return (
    <div data-testid="numerology-section">
      <button onClick={onBack}>Back</button>
      <div>Numerology Section</div>
    </div>
  );
};
