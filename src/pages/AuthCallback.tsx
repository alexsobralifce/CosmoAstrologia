import { useEffect } from 'react';
import { setAuthToken } from '../services/api';
import { UIIcons } from '../components/ui-icons';

export const AuthCallback = () => {
  useEffect(() => {
    // Get token from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
      // Save token
      setAuthToken(token);
      
      // Check if there's pending onboarding data
      const pendingData = localStorage.getItem('pending_onboarding');
      if (pendingData) {
        // Save to session storage for App.tsx to pick up
        sessionStorage.setItem('onboarding_data', pendingData);
        localStorage.removeItem('pending_onboarding');
      }
      
      // Redirect to main app
      window.location.href = '/';
    } else {
      // No token, redirect to home
      window.location.href = '/';
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background via-background to-[#1a1f4a]">
      <div className="text-center space-y-4">
        <div className="animate-spin">
          <UIIcons.Star size={48} className="text-accent" />
        </div>
        <p className="text-secondary">Finalizando login...</p>
      </div>
    </div>
  );
};