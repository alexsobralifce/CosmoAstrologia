import React from 'react';
import { OnboardingData } from '../onboarding';

interface SolarReturnSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const SolarReturnSection = ({ userData, onBack }: SolarReturnSectionProps) => {
  return (
    <div data-testid="solar-return-section">
      <button onClick={onBack}>Back</button>
      <div>Solar Return Section</div>
    </div>
  );
};
