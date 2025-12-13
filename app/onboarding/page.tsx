'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Onboarding } from '@/components/onboarding';
import { ThemeToggle } from '@/components/theme-toggle';
import { useAuth } from '@/hooks/useAuth';

export default function OnboardingPage() {
  const router = useRouter();
  const {
    authData,
    tempPassword,
    handleOnboardingComplete,
    isCheckingAuth,
  } = useAuth();

  useEffect(() => {
    if (!isCheckingAuth && !authData) {
      router.push('/login');
    }
  }, [authData, isCheckingAuth, router]);

  if (isCheckingAuth) {
    return (
      <div className="loading-screen">
        <div className="loading-screen-particles">
          {Array.from({ length: 50 }).map((_, i) => (
            <div
              key={i}
              className="loading-screen-particle"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                opacity: Math.random() * 0.5 + 0.3,
              }}
            />
          ))}
        </div>
        <div className="loading-screen-content">
          <p className="loading-screen-text">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  if (!authData) {
    return null;
  }

  return (
    <>
      <div style={{ position: 'absolute', top: '1rem', right: '1rem', zIndex: 50 }}>
        <ThemeToggle />
      </div>
      <Onboarding
        onComplete={handleOnboardingComplete}
        initialEmail={authData?.email}
        initialName={authData?.name}
        initialPassword={tempPassword || undefined}
        onBackToLogin={() => {
          router.push('/');
        }}
      />
    </>
  );
}
