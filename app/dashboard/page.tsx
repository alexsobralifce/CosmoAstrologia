'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CosmosDashboard } from '@/components/cosmos-dashboard';
import { useAuth } from '@/hooks/useAuth';
import { UIIcons } from '@/components/ui-icons';

export default function DashboardPage() {
  const router = useRouter();
  const {
    userData,
    isCheckingAuth,
    handleViewInterpretation,
    handleLogout,
    setUserData,
  } = useAuth();

  useEffect(() => {
    if (!isCheckingAuth && !userData) {
      router.push('/login');
    }
  }, [userData, isCheckingAuth, router]);

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
          <div className="loading-screen-icon">
            <UIIcons.Star size={32} style={{ color: 'hsl(var(--accent))' }} />
          </div>
          <p className="loading-screen-text">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  if (!userData) {
    return null;
  }

  return (
    <CosmosDashboard
      userData={userData}
      onViewInterpretation={handleViewInterpretation}
      onLogout={handleLogout}
      onUserUpdate={(updatedData) => {
        setUserData({
          ...updatedData,
          birthDate: new Date(updatedData.birthDate),
          coordinates: updatedData.coordinates ? {
            ...updatedData.coordinates
          } : undefined,
        });
      }}
    />
  );
}
