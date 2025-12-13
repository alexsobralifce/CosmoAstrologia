'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import type { OnboardingData } from '@/components/onboarding';
import type { GoogleOnboardingData } from '@/components/google-onboarding';
import type { AuthUserData } from '@/components/auth-portal';

interface GoogleUserData {
  email: string;
  name: string;
  googleId: string;
}

export function useAuth() {
  const router = useRouter();
  const [userData, setUserData] = useState<OnboardingData | null>(null);
  const [authData, setAuthData] = useState<AuthUserData | null>(null);
  const [googleData, setGoogleData] = useState<GoogleUserData | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [tempPassword, setTempPassword] = useState<string | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  // Verificar autenticação ao carregar
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
        if (!token) {
          setIsCheckingAuth(false);
          return;
        }

        const userInfo = await apiService.getCurrentUser();
        if (!userInfo) {
          apiService.logout();
          setIsCheckingAuth(false);
          return;
        }

        const birthChart = await apiService.getUserBirthChart();

        if (birthChart && userInfo) {
          setUserData({
            name: birthChart.name,
            birthDate: new Date(birthChart.birth_date),
            birthTime: birthChart.birth_time,
            birthPlace: birthChart.birth_place,
            email: userInfo.email || '',
            coordinates: {
              latitude: birthChart.latitude,
              longitude: birthChart.longitude,
            },
            sunSign: birthChart.sun_sign,
            sunDegree: birthChart.sun_degree,
            moonSign: birthChart.moon_sign,
            moonDegree: birthChart.moon_degree,
            ascendant: birthChart.ascendant_sign,
            ascendantDegree: birthChart.ascendant_degree,
            mercurySign: birthChart.mercury_sign,
            mercuryDegree: birthChart.mercury_degree,
            venusSign: birthChart.venus_sign,
            venusDegree: birthChart.venus_degree,
            marsSign: birthChart.mars_sign,
            marsDegree: birthChart.mars_degree,
            jupiterSign: birthChart.jupiter_sign,
            jupiterDegree: birthChart.jupiter_degree,
            saturnSign: birthChart.saturn_sign,
            saturnDegree: birthChart.saturn_degree,
            uranusSign: birthChart.uranus_sign,
            uranusDegree: birthChart.uranus_degree,
            neptuneSign: birthChart.neptune_sign,
            neptuneDegree: birthChart.neptune_degree,
            plutoSign: birthChart.pluto_sign,
            plutoDegree: birthChart.pluto_degree,
            midheavenSign: birthChart.midheaven_sign,
            midheavenDegree: birthChart.midheaven_degree,
            northNodeSign: birthChart.north_node_sign,
            northNodeDegree: birthChart.north_node_degree,
            southNodeSign: birthChart.south_node_sign,
            southNodeDegree: birthChart.south_node_degree,
            chironSign: birthChart.chiron_sign,
            chironDegree: birthChart.chiron_degree,
          });
          setAuthData({
            email: userInfo.email || '',
            name: userInfo.name,
            hasCompletedOnboarding: true,
          });
        } else if (userInfo) {
          setAuthData({
            email: userInfo.email || '',
            name: userInfo.name,
            hasCompletedOnboarding: false,
          });
        }
      } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        apiService.logout();
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuth();
  }, []);

  const handleAuthSuccess = (data: AuthUserData) => {
    setAuthData(data);
    if (data.hasCompletedOnboarding) {
      router.push('/dashboard');
    } else {
      router.push('/onboarding');
    }
  };

  const handleNeedsBirthData = (email: string, name?: string, password?: string) => {
    setAuthData({
      email,
      name: name || '',
      hasCompletedOnboarding: false,
    });
    if (password) {
      setTempPassword(password);
    }
    router.push('/onboarding');
  };

  const handleGoogleNeedsOnboarding = (email: string, name: string, googleId: string) => {
    setGoogleData({ email, name, googleId });
    router.push('/onboarding/google');
  };

  const handleGoogleOnboardingComplete = async (data: GoogleOnboardingData) => {
    try {
      const response = await apiService.registerUser({
        email: googleData!.email,
        name: data.name,
        birth_data: {
          name: data.name,
          birth_date: data.birthDate.toISOString().split('T')[0],
          birth_time: data.birthTime,
          birth_place: data.birthPlace,
          latitude: data.coordinates.latitude,
          longitude: data.coordinates.longitude,
        },
      });

      if ('access_token' in response && response.access_token) {
        const userInfo = await apiService.getCurrentUser();
        const birthChart = await apiService.getUserBirthChart();

        if (birthChart && userInfo) {
          setUserData({
            name: birthChart.name,
            birthDate: new Date(birthChart.birth_date),
            birthTime: birthChart.birth_time,
            birthPlace: birthChart.birth_place,
            email: userInfo.email || '',
            coordinates: {
              latitude: birthChart.latitude,
              longitude: birthChart.longitude,
            },
            sunSign: birthChart.sun_sign,
            sunDegree: birthChart.sun_degree,
            moonSign: birthChart.moon_sign,
            moonDegree: birthChart.moon_degree,
            ascendant: birthChart.ascendant_sign,
            ascendantDegree: birthChart.ascendant_degree,
            mercurySign: birthChart.mercury_sign,
            mercuryDegree: birthChart.mercury_degree,
            venusSign: birthChart.venus_sign,
            venusDegree: birthChart.venus_degree,
            marsSign: birthChart.mars_sign,
            marsDegree: birthChart.mars_degree,
            jupiterSign: birthChart.jupiter_sign,
            jupiterDegree: birthChart.jupiter_degree,
            saturnSign: birthChart.saturn_sign,
            saturnDegree: birthChart.saturn_degree,
            uranusSign: birthChart.uranus_sign,
            uranusDegree: birthChart.uranus_degree,
            neptuneSign: birthChart.neptune_sign,
            neptuneDegree: birthChart.neptune_degree,
            plutoSign: birthChart.pluto_sign,
            plutoDegree: birthChart.pluto_degree,
            midheavenSign: birthChart.midheaven_sign,
            midheavenDegree: birthChart.midheaven_degree,
            northNodeSign: birthChart.north_node_sign,
            northNodeDegree: birthChart.north_node_degree,
            southNodeSign: birthChart.south_node_sign,
            southNodeDegree: birthChart.south_node_degree,
            chironSign: birthChart.chiron_sign,
            chironDegree: birthChart.chiron_degree,
          });
          setAuthData({
            email: userInfo.email || '',
            name: userInfo.name,
            hasCompletedOnboarding: true,
          });
          setGoogleData(null);
          router.push('/dashboard');
        }
      }
    } catch (error) {
      console.error('Erro ao completar onboarding Google:', error);
      throw error;
    }
  };

  const handleOnboardingComplete = async (data: OnboardingData) => {
    try {
      const response = await apiService.registerUser({
        email: authData?.email || '',
        password: tempPassword || undefined,
        name: data.name,
        birth_data: {
          name: data.name,
          birth_date: data.birthDate.toISOString().split('T')[0],
          birth_time: data.birthTime,
          birth_place: data.birthPlace,
          latitude: data.coordinates.latitude,
          longitude: data.coordinates.longitude,
        },
      });

      if ('access_token' in response && response.access_token) {
        setUserData(data);
        setAuthData({
          email: authData?.email || '',
          name: data.name,
          hasCompletedOnboarding: true,
        });
        setTempPassword(null);
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Erro ao completar onboarding:', error);
      throw error;
    }
  };

  const handleViewInterpretation = (topicId: string) => {
    setSelectedTopic(topicId);
    router.push(`/interpretation/${topicId}`);
  };

  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  const handleLogout = () => {
    apiService.logout();
    setUserData(null);
    setAuthData(null);
    setGoogleData(null);
    setTempPassword(null);
    router.push('/');
  };

  return {
    userData,
    authData,
    googleData,
    tempPassword,
    selectedTopic,
    isCheckingAuth,
    handleAuthSuccess,
    handleNeedsBirthData,
    handleGoogleNeedsOnboarding,
    handleGoogleOnboardingComplete,
    handleOnboardingComplete,
    handleViewInterpretation,
    handleBackToDashboard,
    handleLogout,
    setUserData,
  };
}
