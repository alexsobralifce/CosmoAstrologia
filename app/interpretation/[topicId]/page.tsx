'use client';

import { useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { InterpretationPage } from '@/components/interpretation-page';
import { useAuth } from '@/hooks/useAuth';

export default function InterpretationRoutePage() {
  const router = useRouter();
  const params = useParams();
  const topicId = params?.topicId as string;
  const { userData, isCheckingAuth } = useAuth();

  useEffect(() => {
    if (!isCheckingAuth && !userData) {
      router.push('/login');
    }
  }, [userData, isCheckingAuth, router]);

  if (isCheckingAuth || !userData) {
    return null;
  }

  return (
    <InterpretationPage
      topicId={topicId || ''}
      onBack={() => router.push('/dashboard')}
    />
  );
}
