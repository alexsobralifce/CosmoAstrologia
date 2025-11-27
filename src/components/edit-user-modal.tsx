import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { LocationAutocomplete, LocationSelection } from './location-autocomplete';
import { apiService } from '../services/api';
import { toast } from 'sonner';
import { OnboardingData } from './onboarding';

interface EditUserModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userData: OnboardingData;
  onUpdate: (data: OnboardingData) => void;
  onLogout: () => void;
}

export const EditUserModal = ({
  open,
  onOpenChange,
  userData,
  onUpdate,
  onLogout,
}: EditUserModalProps) => {
  const [name, setName] = useState(userData.name);
  const [email, setEmail] = useState(userData.email || '');
  const [birthDateInput, setBirthDateInput] = useState('');
  const [birthDate, setBirthDate] = useState<Date | undefined>(userData.birthDate);
  const [birthTime, setBirthTime] = useState(userData.birthTime);
  const [birthPlace, setBirthPlace] = useState(userData.birthPlace);
  const [birthCoordinates, setBirthCoordinates] = useState<{ latitude: number; longitude: number } | null>(
    userData.coordinates || null
  );
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      setName(userData.name);
      setEmail(userData.email || '');
      setBirthDate(userData.birthDate);
      setBirthDateInput(formatDate(userData.birthDate));
      setBirthTime(userData.birthTime);
      setBirthPlace(userData.birthPlace);
      setBirthCoordinates(userData.coordinates || null);
      setPassword('');
    }
  }, [open, userData]);

  const formatDate = (date: Date) => {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  };

  const handleBirthDateInput = (rawValue: string) => {
    const digits = rawValue.replace(/\D/g, '').slice(0, 8);
    let formatted = digits;

    if (digits.length > 4) {
      formatted = `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
    } else if (digits.length > 2) {
      formatted = `${digits.slice(0, 2)}/${digits.slice(2)}`;
    }

    setBirthDateInput(formatted);

    if (digits.length === 8) {
      const day = Number(digits.slice(0, 2));
      const month = Number(digits.slice(2, 4)) - 1;
      const year = Number(digits.slice(4));

      const parsedDate = new Date(year, month, day);
      const isValid =
        parsedDate.getFullYear() === year &&
        parsedDate.getMonth() === month &&
        parsedDate.getDate() === day;

      if (isValid) {
        setBirthDate(parsedDate);
        return;
      }
    }

    setBirthDate(undefined);
  };

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email.trim());
  };

  const handleSubmit = async () => {
    if (!name.trim()) {
      toast.error('Nome é obrigatório');
      return;
    }

    if (!email.trim() || !validateEmail(email)) {
      toast.error('Email válido é obrigatório');
      return;
    }

    if (!birthDate) {
      toast.error('Data de nascimento válida é obrigatória');
      return;
    }

    if (!birthTime.trim()) {
      toast.error('Hora de nascimento é obrigatória');
      return;
    }

    if (!birthPlace.trim()) {
      toast.error('Local de nascimento é obrigatório');
      return;
    }

    if (!birthCoordinates) {
      toast.error('Selecione um local da lista para capturar as coordenadas');
      return;
    }

    if (password && password.length < 6) {
      toast.error('A senha deve ter pelo menos 6 caracteres');
      return;
    }

    setIsSubmitting(true);

    try {
      // Preparar dados para atualização
      const updateData = {
        name,
        email,
        birth_data: {
          name,
          birth_date: birthDate.toISOString(),
          birth_time: birthTime,
          birth_place: birthPlace,
          latitude: birthCoordinates.latitude,
          longitude: birthCoordinates.longitude,
        },
        password: password || undefined,
      };

      // Atualizar no backend
      await apiService.updateUser(updateData);

      // Buscar dados recalculados do backend (incluindo signos recalculados)
      const updatedBirthChart = await apiService.getUserBirthChart();
      
      if (!updatedBirthChart) {
        throw new Error('Não foi possível obter os dados atualizados do mapa astral');
      }

      console.log('[DEBUG EditUserModal] Dados recalculados do backend:', {
        name: updatedBirthChart.name,
        birth_date: updatedBirthChart.birth_date,
        birth_time: updatedBirthChart.birth_time,
        birth_place: updatedBirthChart.birth_place,
        latitude: updatedBirthChart.latitude,
        longitude: updatedBirthChart.longitude,
        sun_sign: updatedBirthChart.sun_sign,
        moon_sign: updatedBirthChart.moon_sign,
        ascendant_sign: updatedBirthChart.ascendant_sign,
        sun_degree: updatedBirthChart.sun_degree,
        moon_degree: updatedBirthChart.moon_degree,
        ascendant_degree: updatedBirthChart.ascendant_degree,
      });

      // Converter dados do backend para OnboardingData
      const updatedUserData: OnboardingData = {
        name: updatedBirthChart.name,
        birthDate: new Date(updatedBirthChart.birth_date),
        birthTime: updatedBirthChart.birth_time,
        birthPlace: updatedBirthChart.birth_place,
        email,
        coordinates: {
          latitude: updatedBirthChart.latitude,
          longitude: updatedBirthChart.longitude,
        },
      };

      console.log('[DEBUG EditUserModal] Dados convertidos para OnboardingData:', {
        name: updatedUserData.name,
        birthDate: updatedUserData.birthDate,
        birthTime: updatedUserData.birthTime,
        birthPlace: updatedUserData.birthPlace,
        coordinates: updatedUserData.coordinates,
      });

      console.log('[DEBUG EditUserModal] Chamando onUpdate com dados atualizados');
      onUpdate(updatedUserData);
      console.log('[DEBUG EditUserModal] onUpdate chamado, fechando modal');
      toast.success('Dados atualizados com sucesso! O mapa astral foi recalculado.');
      onOpenChange(false);
    } catch (error: unknown) {
      console.error('Erro ao atualizar:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Erro ao atualizar dados. Tente novamente.';
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader className="sticky top-0 bg-background z-10 pb-4 border-b border-border/30">
          <DialogTitle className="text-accent">Editar Perfil</DialogTitle>
          <DialogDescription>
            Atualize suas informações pessoais e dados de nascimento.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Linha 1: Nome Completo - Largura completa */}
          <div>
            <AstroInput
              label="Nome Completo"
              placeholder="Digite seu nome"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {/* Linha 2: Email - Largura completa */}
          <div>
            <AstroInput
              label="Email"
              type="email"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {/* Linha 3: Data, Hora e Local de Nascimento - Grid 3 colunas */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Data de Nascimento */}
            <div className="space-y-2">
              <AstroInput
                label="Data de Nascimento"
                placeholder="dd/mm/aaaa"
                value={birthDateInput}
                onChange={(e) => handleBirthDateInput(e.target.value)}
                maxLength={10}
              />
              {birthDateInput && birthDate === undefined && (
                <p className="text-sm text-destructive">Digite uma data válida.</p>
              )}
            </div>

            {/* Hora de Nascimento */}
            <div>
              <AstroInput
                label="Hora de Nascimento"
                type="time"
                value={birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
              />
            </div>

            {/* Local de Nascimento */}
            <div className="space-y-2">
              <LocationAutocomplete
                label="Local de Nascimento"
                placeholder="Digite a cidade"
                value={birthPlace}
                onChange={(val) => {
                  setBirthPlace(val);
                  setBirthCoordinates(null);
                }}
                onSelect={(selection: LocationSelection) => {
                  setBirthPlace(selection.displayName);
                  setBirthCoordinates({
                    latitude: selection.lat,
                    longitude: selection.lon,
                  });
                }}
              />
              {birthPlace && !birthCoordinates && (
                <p className="text-xs text-secondary">
                  Selecione da lista
                </p>
              )}
              {birthCoordinates && (
                <div className="text-xs text-secondary flex items-center gap-1">
                  <UIIcons.MapPin size={12} className="text-accent" />
                  <span>
                    {birthCoordinates.latitude.toFixed(2)}°, {birthCoordinates.longitude.toFixed(2)}°
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Linha 4: Senha (opcional) - Largura completa */}
          <div>
            <AstroInput
              label="Alterar Senha (Opcional)"
              type="password"
              placeholder="Deixe em branco se não quiser alterar"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {password && password.length > 0 && password.length < 6 && (
              <p className="text-sm text-destructive mt-1">
                A senha deve ter pelo menos 6 caracteres
              </p>
            )}
          </div>

          {/* Botões */}
          <div className="flex gap-4 pt-4 border-t border-border/30">
            <AstroButton
              variant="secondary"
              onClick={() => onOpenChange(false)}
              className="flex-1"
              disabled={isSubmitting}
            >
              Cancelar
            </AstroButton>
            <AstroButton
              variant="primary"
              onClick={handleSubmit}
              className="flex-1"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <UIIcons.Loader className="w-4 h-4 animate-spin" />
                  Salvando...
                </span>
              ) : (
                'Salvar Alterações'
              )}
            </AstroButton>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

