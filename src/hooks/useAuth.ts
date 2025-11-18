/**
 * Custom hook for authentication
 */
import { useState, useEffect } from 'react';
import { apiService, setAuthToken, getAuthToken } from '../services/api';

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  created_at?: string;
}

export interface UserWithBirthData extends User {
  birthData?: {
    name: string;
    birth_date: string;
    birth_time: string;
    birth_place: string;
  };
}

export function useAuth() {
  const [user, setUser] = useState<UserWithBirthData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await apiService.getCurrentUser();
      
      // Try to get birth data
      let birthData = null;
      try {
        birthData = await apiService.getUserBirthData();
      } catch (error) {
        // Birth data not found - user needs to complete onboarding
        console.log('Birth data not found for user');
      }
      
      setUser({
        ...userData,
        birthData
      });
    } catch (error) {
      console.error('Auth check failed:', error);
      setAuthToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = () => {
    apiService.loginWithGoogle();
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setAuthToken(null);
    }
  };

  const updateUser = async (name: string) => {
    try {
      const updatedUser = await apiService.updateUser(name);
      setUser(prev => prev ? { ...prev, ...updatedUser } : null);
    } catch (error) {
      console.error('Update user error:', error);
      throw error;
    }
  };

  const saveBirthData = async (birthData: any) => {
    try {
      await apiService.saveUserBirthData({
        name: birthData.name,
        birth_date: birthData.birthDate.toISOString().split('T')[0],
        birth_time: birthData.birthTime,
        birth_place: birthData.birthPlace
      });
      
      // Update user with birth data
      setUser(prev => prev ? {
        ...prev,
        birthData: {
          name: birthData.name,
          birth_date: birthData.birthDate.toISOString().split('T')[0],
          birth_time: birthData.birthTime,
          birth_place: birthData.birthPlace
        }
      } : null);
    } catch (error) {
      console.error('Save birth data error:', error);
      throw error;
    }
  };

  return {
    user,
    loading,
    login,
    logout,
    updateUser,
    saveBirthData,
    isAuthenticated: !!user,
    hasBirthData: !!(user?.birthData),
  };
}

