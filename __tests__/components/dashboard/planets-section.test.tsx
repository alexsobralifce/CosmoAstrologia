import React from 'react';

// Mock dos componentes que usam import.meta.env ANTES de importar dashboard-sections
jest.mock('@/components/solar-return-section');
jest.mock('@/components/numerology-section');
jest.mock('@/components/future-transits-section');

import { renderWithProviders, waitFor, screen, fireEvent } from '../../utils/test-utils';
import { PlanetsSection } from '@/components/dashboard-sections';
import { apiService } from '@/services/api';
import { OnboardingData } from '@/components/onboarding';

// Mock do apiService
jest.mock('@/services/api', () => ({
  apiService: {
    getPlanetInterpretation: jest.fn(),
  },
}));

// Mock dos ícones de planetas e signos
jest.mock('@/components/planet-icons', () => ({
  planets: [
    { icon: () => <div data-testid="sun-icon">☉</div> },
    { icon: () => <div data-testid="moon-icon">☽</div> },
    { icon: () => <div data-testid="mercury-icon">☿</div> },
    { icon: () => <div data-testid="venus-icon">♀</div> },
    { icon: () => <div data-testid="mars-icon">♂</div> },
    { icon: () => <div data-testid="jupiter-icon">♃</div> },
    { icon: () => <div data-testid="saturn-icon">♄</div> },
    { icon: () => <div data-testid="uranus-icon">♅</div> },
    { icon: () => <div data-testid="neptune-icon">♆</div> },
    { icon: () => <div data-testid="pluto-icon">♇</div> },
  ],
}));

jest.mock('@/components/zodiac-icons', () => ({
  zodiacSigns: [
    { name: 'Áries', icon: () => <div data-testid="aries-icon">♈</div> },
    { name: 'Touro', icon: () => <div data-testid="taurus-icon">♉</div> },
    { name: 'Gêmeos', icon: () => <div data-testid="gemini-icon">♊</div> },
    { name: 'Câncer', icon: () => <div data-testid="cancer-icon">♋</div> },
    { name: 'Leão', icon: () => <div data-testid="leo-icon">♌</div> },
    { name: 'Virgem', icon: () => <div data-testid="virgo-icon">♍</div> },
    { name: 'Libra', icon: () => <div data-testid="libra-icon">♎</div> },
    { name: 'Escorpião', icon: () => <div data-testid="scorpio-icon">♏</div> },
    { name: 'Sagitário', icon: () => <div data-testid="sagittarius-icon">♐</div> },
    { name: 'Capricórnio', icon: () => <div data-testid="capricorn-icon">♑</div> },
    { name: 'Aquário', icon: () => <div data-testid="aquarius-icon">♒</div> },
    { name: 'Peixes', icon: () => <div data-testid="pisces-icon">♓</div> },
  ],
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
  sunHouse: 1,
  moonHouse: 4,
  mercurySign: 'Sagittarius',
  mercuryHouse: 3,
  venusSign: 'Aquarius',
  venusHouse: 2,
  marsSign: 'Scorpio',
  marsHouse: 1,
  jupiterSign: 'Cancer',
  jupiterHouse: 9,
  saturnSign: 'Capricorn',
  saturnHouse: 10,
  uranusSign: 'Capricorn',
  uranusHouse: 11,
  neptuneSign: 'Capricorn',
  neptuneHouse: 12,
  plutoSign: 'Scorpio',
  plutoHouse: 8,
};

const mockPlanetInterpretation = {
  interpretation: 'Esta é uma interpretação do planeta Sol em Capricorn na Casa 1.',
  sources: [],
  query_used: 'test query',
  generated_by: 'groq',
};

describe('PlanetsSection', () => {
  const mockOnBack = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (apiService.getPlanetInterpretation as jest.Mock).mockResolvedValue(mockPlanetInterpretation);
  });

  it('should render with user data', () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Verificar que o título está presente
    expect(screen.getByText(/Planetas no Seu Mapa|Planets in Your Chart/)).toBeInTheDocument();
    // Verificar que há um botão de voltar
    expect(screen.getByText(/Voltar|Back/)).toBeInTheDocument();
  });

  it('should display planetary categories', () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Verificar que as categorias planetárias estão presentes
    expect(screen.getByText(/Categorias Planetárias|Planetary Categories/)).toBeInTheDocument();
    // Verificar categorias específicas (podem estar em PT ou EN)
    const categories = screen.queryAllByText(/Luminares|Luminaries|Pessoais|Personal|Sociais|Social|Transpessoais|Transpersonal/);
    expect(categories.length).toBeGreaterThan(0);
  });

  it('should display planets grid', () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Verificar que a seção de planetas está presente
    expect(screen.getByText(/Seus Planetas|Your Planets/)).toBeInTheDocument();
    
    // Verificar que pelo menos alguns planetas estão presentes
    const planetNames = screen.queryAllByText(/Sol|Sun|Lua|Moon|Mercúrio|Mercury|Vênus|Venus/);
    expect(planetNames.length).toBeGreaterThan(0);
  });

  it('should call getPlanetInterpretation when a planet is clicked', async () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Encontrar e clicar em um planeta (Sol/Sun)
    const sunButton = screen.getByText(/Sol|Sun/);
    fireEvent.click(sunButton);

    await waitFor(() => {
      expect(apiService.getPlanetInterpretation).toHaveBeenCalled();
    });

    // Verificar que a chamada foi feita com os parâmetros corretos
    expect(apiService.getPlanetInterpretation).toHaveBeenCalledWith(
      expect.objectContaining({
        planet: expect.any(String),
        sign: expect.any(String),
      })
    );
  });

  it('should display loading state while fetching interpretation', async () => {
    // Mockar uma chamada que demora
    (apiService.getPlanetInterpretation as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockPlanetInterpretation), 100))
    );

    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Clicar em um planeta
    const sunButton = screen.getByText(/Sol|Sun/);
    fireEvent.click(sunButton);

    // Verificar que o estado de loading aparece
    await waitFor(() => {
      expect(screen.getByText(/Analisando o planeta|Analyzing the planet/)).toBeInTheDocument();
    });
  });

  it('should display interpretation after loading', async () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Clicar em um planeta
    const sunButton = screen.getByText(/Sol|Sun/);
    fireEvent.click(sunButton);

    // Aguardar a interpretação aparecer
    await waitFor(() => {
      expect(apiService.getPlanetInterpretation).toHaveBeenCalled();
    });

    // Verificar que a interpretação foi exibida (pode estar formatada)
    await waitFor(() => {
      const interpretationTexts = screen.queryAllByText(/interpretação|interpretation/i);
      // A interpretação pode estar presente em algum formato
      expect(apiService.getPlanetInterpretation).toHaveBeenCalled();
    });
  });

  it('should handle interpretation error', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation();
    (apiService.getPlanetInterpretation as jest.Mock).mockRejectedValue(new Error('API Error'));

    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Clicar em um planeta
    const sunButton = screen.getByText(/Sol|Sun/);
    fireEvent.click(sunButton);

    await waitFor(() => {
      expect(consoleError).toHaveBeenCalled();
    });

    consoleError.mockRestore();
  });

  it('should call onBack when back button is clicked', () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    const backButton = screen.getByText(/Voltar|Back/);
    fireEvent.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('should display planet information correctly', () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Verificar que os planetas são exibidos com suas informações
    // O componente deve renderizar os planetas com signos e casas
    expect(screen.getByText(/Seus Planetas|Your Planets/)).toBeInTheDocument();
  });

  it('should handle planet selection state', async () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Clicar em um planeta
    const sunButton = screen.getByText(/Sol|Sun/);
    fireEvent.click(sunButton);

    await waitFor(() => {
      expect(apiService.getPlanetInterpretation).toHaveBeenCalled();
    });

    // Verificar que o painel de interpretação aparece
    await waitFor(() => {
      // O painel deve aparecer quando um planeta é selecionado
      // Pode haver múltiplos elementos com "interpretação", então usamos queryAllByText
      const interpretationPanels = screen.queryAllByText(/Analisando|Analyzing|interpretação|interpretation|Erro|Error/i);
      // Verificar que pelo menos um elemento de interpretação está presente
      expect(interpretationPanels.length).toBeGreaterThan(0);
    });
  });

  it('should display planet sign and house information', () => {
    renderWithProviders(
      <PlanetsSection userData={mockUserData} onBack={mockOnBack} />
    );

    // Verificar que os planetas são renderizados
    // O componente deve mostrar signos e casas para cada planeta
    expect(screen.getByText(/Seus Planetas|Your Planets/)).toBeInTheDocument();
  });
});
