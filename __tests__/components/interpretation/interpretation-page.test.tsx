import React from 'react';
import { renderWithProviders, waitFor, screen, fireEvent } from '../../utils/test-utils';
import { InterpretationPage } from '@/components/interpretation-page';

// Mock do ThemeToggle
jest.mock('@/components/theme-toggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme Toggle</div>,
}));

describe('InterpretationPage', () => {
  const mockOnBack = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render with valid topicId', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    expect(screen.getByText('Amor e Relacionamentos')).toBeInTheDocument();
    expect(screen.getByText(/Posição Natal • Conexões e Harmonia/)).toBeInTheDocument();
  });

  it('should render default content for invalid topicId', () => {
    renderWithProviders(
      <InterpretationPage topicId="invalid-topic" onBack={mockOnBack} />
    );

    expect(screen.getByText('Interpretação Astrológica')).toBeInTheDocument();
  });

  it('should display all sections for amor topic', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    expect(screen.getByText('Visão Geral')).toBeInTheDocument();
    expect(screen.getByText(/Vênus e a Expressão do Amor/)).toBeInTheDocument();
    expect(screen.getByText(/Casa 7 e Parcerias/)).toBeInTheDocument();
    expect(screen.getByText(/Desafios e Crescimento/)).toBeInTheDocument();
  });

  it('should display all sections for carreira topic', () => {
    renderWithProviders(
      <InterpretationPage topicId="carreira" onBack={mockOnBack} />
    );

    expect(screen.getByText('Carreira e Finanças')).toBeInTheDocument();
    expect(screen.getByText(/Casa 10 e Profissão/)).toBeInTheDocument();
    expect(screen.getByText(/Saturno e Responsabilidade/)).toBeInTheDocument();
  });

  it('should display all sections for saude topic', () => {
    renderWithProviders(
      <InterpretationPage topicId="saude" onBack={mockOnBack} />
    );

    expect(screen.getByText('Saúde e Bem-Estar')).toBeInTheDocument();
    expect(screen.getByText(/Casa 6 e Saúde/)).toBeInTheDocument();
    expect(screen.getByText(/Marte e Energia/)).toBeInTheDocument();
  });

  it('should display all sections for familia topic', () => {
    renderWithProviders(
      <InterpretationPage topicId="familia" onBack={mockOnBack} />
    );

    expect(screen.getByText('Família e Amigos')).toBeInTheDocument();
    expect(screen.getByText(/Casa 4 e Família/)).toBeInTheDocument();
    expect(screen.getByText(/Casa 11 e Amizades/)).toBeInTheDocument();
  });

  it('should call onBack when back button is clicked', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    const backButton = screen.getByText(/Voltar/);
    fireEvent.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('should display header with title', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    expect(screen.getByText('Interpretação Detalhada')).toBeInTheDocument();
  });

  it('should display theme toggle in header', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
  });

  it('should display related topics section', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    expect(screen.getByText('Tópicos Relacionados')).toBeInTheDocument();
  });

  it('should display section numbers', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    // Verificar se há números de seção (1, 2, 3, 4)
    const sectionNumbers = screen.getAllByText(/^[1-4]$/);
    expect(sectionNumbers.length).toBeGreaterThan(0);
  });

  it('should render content paragraphs correctly', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    // Verificar se o conteúdo das seções está presente
    expect(screen.getByText(/Os relacionamentos amorosos são uma área fundamental/)).toBeInTheDocument();
    expect(screen.getByText(/Vênus rege o amor, a beleza e os valores/)).toBeInTheDocument();
  });

  it('should handle different topicIds correctly', () => {
    const { rerender } = renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    expect(screen.getByText('Amor e Relacionamentos')).toBeInTheDocument();

    rerender(
      <InterpretationPage topicId="carreira" onBack={mockOnBack} />
    );

    expect(screen.getByText('Carreira e Finanças')).toBeInTheDocument();
  });

  it('should display bookmark and share buttons', () => {
    renderWithProviders(
      <InterpretationPage topicId="amor" onBack={mockOnBack} />
    );

    // Verificar se os botões estão presentes (por título)
    const bookmarkButton = screen.getByTitle('Favoritar');
    const shareButton = screen.getByTitle('Compartilhar');

    expect(bookmarkButton).toBeInTheDocument();
    expect(shareButton).toBeInTheDocument();
  });
});
