/**
 * Custom hook for managing birth chart data and API calls
 */
import { useState, useEffect } from 'react';
import { apiService, BirthChartResponse, BirthData, DailyTransit, FutureTransit } from '../services/api';
import { OnboardingData } from '../components/onboarding';

export function useChart(userData: OnboardingData | null) {
  const [chart, setChart] = useState<BirthChartResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dailyTransits, setDailyTransits] = useState<DailyTransit | null>(null);
  const [futureTransits, setFutureTransits] = useState<FutureTransit[]>([]);

  useEffect(() => {
    if (userData) {
      loadChart();
    }
  }, [userData]);

  const loadChart = async () => {
    if (!userData) return;

    setLoading(true);
    setError(null);

    try {
      // Convert OnboardingData to BirthData format
      const birthData = {
        name: userData.name,
        birth_date: userData.birthDate.toISOString().split('T')[0], // YYYY-MM-DD
        birth_time: userData.birthTime, // HH:MM
        birth_place: userData.birthPlace,
      };

      const chartData = await apiService.calculateChart(birthData);
      setChart(chartData);

      // Load transits
      try {
        const daily = await apiService.getDailyTransits(chartData);
        setDailyTransits(daily);

        const future = await apiService.getFutureTransits(chartData, 24);
        setFutureTransits(future);
      } catch (transitError) {
        console.warn('Error loading transits:', transitError);
        // Don't fail the whole chart if transits fail
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar mapa astral');
      console.error('Error loading chart:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshChart = () => {
    loadChart();
  };

  return {
    chart,
    loading,
    error,
    dailyTransits,
    futureTransits,
    refreshChart,
  };
}

