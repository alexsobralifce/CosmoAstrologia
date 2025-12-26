'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleOnboarding } from '@/components/google-onboarding';
import { ThemeToggle } from '@/components/theme-toggle';
import { useAuth } from '@/hooks/useAuth';

export default function GoogleOnboardingPage() {
  const router = useRouter();
  const {
    googleData,
    handleGoogleOnboardingComplete,
    isCheckingAuth,
  } = useAuth();

  useEffect(() => {
    if (!isCheckingAuth && !googleData) {
      router.push('/login');
    }
  }, [googleData, isCheckingAuth, router]);

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

  if (!googleData) {
    return null;
  }

  return (
    <>
      <div style={{ position: 'absolute', top: '1rem', right: '1rem', zIndex: 50 }}>
        <ThemeToggle />
      </div>
      <GoogleOnboarding
        email={googleData.email}
        name={googleData.name}
        onComplete={handleGoogleOnboardingComplete}
        onBack={() => {
          router.push('/login');
        }}
      />
    </>
  );
}
