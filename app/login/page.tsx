'use client';

import { AuthPortal } from '@/components/auth-portal';
import { ThemeToggle } from '@/components/theme-toggle';
import { LanguageToggle } from '@/components/language-toggle';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  const {
    handleAuthSuccess,
    handleNeedsBirthData,
    handleGoogleNeedsOnboarding,
  } = useAuth();

  return (
    <>
      <div className="controls-container">
        <ThemeToggle />
        <div className="controls-divider"></div>
        <LanguageToggle />
      </div>
      <AuthPortal
        onAuthSuccess={handleAuthSuccess}
        onNeedsBirthData={handleNeedsBirthData}
        onGoogleNeedsOnboarding={handleGoogleNeedsOnboarding}
      />
    </>
  );
}
