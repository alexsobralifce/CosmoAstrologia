'use client';

import { useRouter } from 'next/navigation';
import { LandingPage } from '@/components/landing-page';

export function LandingPageClient() {
  const router = useRouter();

  const handleEnter = () => {
    router.push('/login');
  };

  const handleGetStarted = () => {
    router.push('/login');
  };

  return (
    <LandingPage
      onEnter={handleEnter}
      onGetStarted={handleGetStarted}
    />
  );
}
