import React from 'react';
import { renderWithProviders, createMockUser, waitFor, screen, fireEvent } from '../../utils/test-utils';
import { CompleteBirthChartSection } from '@/components/complete-birth-chart-section';
import { apiService } from '@/services/api';
import { OnboardingData } from '@/components/onboarding';

// Mock do apiService
jest.mock('@/services/api', () => ({
  apiService: {
    getCompleteChart: jest.fn(),
    getPlanetInterpretation: jest.fn(),
  },
}));

// Mock do BirthChartWheel
jest.mock('@/components/birth-chart-wheel', () => ({
  BirthChartWheel: ({ userData }: { userData: any }) => (
    <div data-testid="birth-chart-wheel">Birth Chart Wheel</div>
  ),
}));

// Mock do generateBirthChartPDF
jest.mock('@/utils/generateBirthChartPDF', () => ({
  generateBirthChartPDF: jest.fn(),
}));

const mockUserData: OnboardingData = {
  name: 'Test User',
  birthDate: new Date('1990-01-01'),
  birthTime: '12:00',
  birthPlace: 'São Paulo, SP, Brasil',
  coordinates: {
    latitude: -23.5505,
    longitude: -46.6333,
  },
  sunSign: 'Capricorn',
  moonSign: 'Aries',
  ascendant: 'Leo',
};

const mockChartData = {
  birth_data: {
    date: '01/01/1990',
    time: '12:00',
    latitude: -23.5505,
    longitude: -46.6333,
  },
  planets_in_signs: [
    {
      planet: 'Sol',
      planet_key: 'sol',
      sign: 'Capricorn',
      degree: 10.5,
      degree_dms: '10°30\'',
      is_retrograde: false,
      house: 1,
    },
    {
      planet: 'Lua',
      planet_key: 'lua',
      sign: 'Aries',
      degree: 20.3,
      degree_dms: '20°18\'',
      is_retrograde: false,
      house: 4,
    },
  ],
  special_points: [
    {
      point: 'Ascendente',
      point_key: 'ascendente',
      sign: 'Leo',
      degree: 15.7,
      degree_dms: '15°42\'',
      house: 1,
    },
  ],
  planets_in_houses: [
    {
      house: 1,
      planets: [
        {
          planet: 'Sol',
          planet_key: 'sol',
          sign: 'Capricorn',
          degree: 10.5,
          degree_dms: '10°30\'',
          house: 1,
          is_retrograde: false,
        },
      ],
    },
  ],
};

const mockInterpretation = {
  interpretation: 'Esta é uma interpretação de teste para o planeta.',
  sources: [],
  query_used: 'test query',
  generated_by: 'groq',
};

describe('CompleteBirthChartSection', () => {
  const mockOnBack = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (apiService.getCompleteChart as jest.Mock).mockResolvedValue(mockChartData);
    (apiService.getPlanetInterpretation as jest.Mock).mockResolvedValue(mockInterpretation);
  });

  it('should render initial state with generate button', () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    expect(screen.getByText(/Meu Mapa Astral Completo|My Complete Birth Chart/)).toBeInTheDocument();
    expect(screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/)).toBeInTheDocument();
    expect(screen.getByTestId('birth-chart-wheel')).toBeInTheDocument();
  });

  it('should display user information', () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText(/São Paulo, SP, Brasil/)).toBeInTheDocument();
  });

  it('should call getCompleteChart when generate button is clicked', async () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(apiService.getCompleteChart).toHaveBeenCalledWith({
        birthDate: expect.any(String),
        birthTime: '12:00',
        latitude: -23.5505,
        longitude: -46.6333,
        birthPlace: 'São Paulo, SP, Brasil',
        name: 'Test User',
      });
    });
  });

  it('should show loading state while fetching chart data', async () => {
    (apiService.getCompleteChart as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockChartData), 100))
    );

    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    expect(screen.getByText(/Calculando mapa completo|Calculating complete chart/)).toBeInTheDocument();
  });

  it('should display chart data after loading', async () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText(/Sol em Capricorn|Sun in Capricorn/)).toBeInTheDocument();
    });
  });

  it('should load interpretation when item is expanded', async () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText(/Sol em Capricorn|Sun in Capricorn/)).toBeInTheDocument();
    });

    const solItem = screen.getByText(/Sol em Capricorn|Sun in Capricorn/).closest('button');
    if (solItem) {
      fireEvent.click(solItem);
    }

    await waitFor(() => {
      expect(apiService.getPlanetInterpretation).toHaveBeenCalledWith({
        planet: 'Sol',
        sign: 'Capricorn',
        house: 1,
        sunSign: 'Capricorn',
        moonSign: 'Aries',
        ascendant: 'Leo',
        userName: 'Test User',
      });
    });
  });

  it('should display interpretation after loading', async () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText(/Sol em Capricorn|Sun in Capricorn/)).toBeInTheDocument();
    });

    const solItem = screen.getByText(/Sol em Capricorn|Sun in Capricorn/).closest('button');
    if (solItem) {
      fireEvent.click(solItem);
    }

    await waitFor(() => {
      expect(screen.getByText(/Esta é uma interpretação de teste/)).toBeInTheDocument();
    });
  });

  it('should handle chart loading error', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation();
    (apiService.getCompleteChart as jest.Mock).mockRejectedValue(new Error('API Error'));

    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(consoleError).toHaveBeenCalled();
    });

    consoleError.mockRestore();
  });

  it('should handle interpretation loading error', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation();
    (apiService.getPlanetInterpretation as jest.Mock).mockRejectedValue(new Error('API Error'));

    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText(/Sol em Capricorn|Sun in Capricorn/)).toBeInTheDocument();
    });

    const solItem = screen.getByText(/Sol em Capricorn|Sun in Capricorn/).closest('button');
    if (solItem) {
      fireEvent.click(solItem);
    }

    await waitFor(() => {
      expect(consoleError).toHaveBeenCalled();
    });

    consoleError.mockRestore();
  });

  it('should call onBack when back button is clicked', () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const backButton = screen.getByText(/Voltar|Back/);
    fireEvent.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('should display retrograde indicator when planet is retrograde', async () => {
    const retrogradeChartData = {
      ...mockChartData,
      planets_in_signs: [
        {
          ...mockChartData.planets_in_signs[0],
          is_retrograde: true,
        },
      ],
    };

    (apiService.getCompleteChart as jest.Mock).mockResolvedValue(retrogradeChartData);

    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText(/Rx/)).toBeInTheDocument();
    });
  });

  it('should display house information when available', async () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      const houseElements = screen.getAllByText(/Casa|House/);
      expect(houseElements.length).toBeGreaterThan(0);
    });
  });

  it('should toggle item expansion', async () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText(/Sol em Capricorn|Sun in Capricorn/)).toBeInTheDocument();
    });

    const solItem = screen.getByText(/Sol em Capricorn|Sun in Capricorn/).closest('button');
    if (solItem) {
      // Expandir
      fireEvent.click(solItem);

      await waitFor(() => {
        expect(apiService.getPlanetInterpretation).toHaveBeenCalled();
      });

      // Colapsar
      fireEvent.click(solItem);
    }
  });

  it('should not reload interpretation if already loaded', async () => {
    renderWithProviders(
      <CompleteBirthChartSection userData={mockUserData} onBack={mockOnBack} />
    );

    const generateButton = screen.getByText(/Gerar Análise Completa|Generate Complete Analysis/);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText(/Sol em Capricorn|Sun in Capricorn/)).toBeInTheDocument();
    });

    const solItem = screen.getByText(/Sol em Capricorn|Sun in Capricorn/).closest('button');
    if (solItem) {
      // Primeira expansão - deve carregar
      fireEvent.click(solItem);
      await waitFor(() => {
        expect(apiService.getPlanetInterpretation).toHaveBeenCalledTimes(1);
      });

      // Colapsar
      fireEvent.click(solItem);

      // Expandir novamente - não deve recarregar
      fireEvent.click(solItem);
      await waitFor(() => {
        expect(apiService.getPlanetInterpretation).toHaveBeenCalledTimes(1);
      });
    }
  });
});
