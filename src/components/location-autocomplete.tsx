'use client';

import React, { useEffect, useRef, useState } from 'react';
import { AstroInput } from './astro-input';
import { UIIcons } from './ui-icons';

export interface LocationSelection {
  displayName: string;
  shortName: string;
  city: string;
  state: string;
  country: string;
  lat: number;
  lon: number;
}

interface LocationAutocompleteProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  onSelect: (selection: LocationSelection) => void;
  error?: string;
}

interface AddressDetails {
  city?: string;
  town?: string;
  village?: string;
  municipality?: string;
  state?: string;
  region?: string;
  country?: string;
}

interface Suggestion {
  display_name: string;
  lat: string;
  lon: string;
  address?: AddressDetails;
}

// Função para extrair cidade, estado e país
const formatLocation = (suggestion: Suggestion): { shortName: string; city: string; state: string; country: string } => {
  const address = suggestion.address || {};
  
  // Cidade pode estar em diferentes campos
  const city = address.city || address.town || address.village || address.municipality || '';
  const state = address.state || address.region || '';
  const country = address.country || '';
  
  // Se não tiver address details, extrair do display_name
  if (!city && !state && !country) {
    const parts = suggestion.display_name.split(',').map(p => p.trim());
    if (parts.length >= 3) {
      return {
        shortName: `${parts[0]}, ${parts[parts.length - 2]}, ${parts[parts.length - 1]}`,
        city: parts[0],
        state: parts[parts.length - 2],
        country: parts[parts.length - 1]
      };
    }
    return {
      shortName: suggestion.display_name,
      city: parts[0] || '',
      state: '',
      country: parts[parts.length - 1] || ''
    };
  }
  
  // Formatar nome curto: Cidade, Estado, País
  const shortParts = [city, state, country].filter(Boolean);
  const shortName = shortParts.join(', ');
  
  return { shortName, city, state, country };
};

export const LocationAutocomplete = ({
  label,
  placeholder,
  value,
  onChange,
  onSelect,
  error,
}: LocationAutocompleteProps) => {
  const [query, setQuery] = useState(value);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setQuery(value);
  }, [value]);

  useEffect(() => {
    if (query.trim().length < 3) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    const controller = new AbortController();
    setIsLoading(true);

    const timeout = setTimeout(async () => {
      try {
        // Incluir addressdetails=1 para obter cidade, estado, país separadamente
        const url = `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&limit=5&q=${encodeURIComponent(query)}`;
        const response = await fetch(url, {
          headers: {
            'Accept-Language': 'pt-BR',
          },
          signal: controller.signal,
        });
        if (!response.ok) throw new Error('Erro ao buscar localizações');
        const data: Suggestion[] = await response.json();
        setSuggestions(data);
        setIsOpen(true);
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') return;
        console.error(error);
        setSuggestions([]);
        setIsOpen(false);
      } finally {
        setIsLoading(false);
      }
    }, 400);

    return () => {
      clearTimeout(timeout);
      controller.abort();
    };
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (suggestion: Suggestion) => {
    const { shortName, city, state, country } = formatLocation(suggestion);
    
    const selection: LocationSelection = {
      displayName: suggestion.display_name,
      shortName,
      city,
      state,
      country,
      lat: Number(suggestion.lat),
      lon: Number(suggestion.lon),
    };
    
    // Atualizar o campo com o nome curto
    setQuery(shortName);
    onChange(shortName);
    onSelect(selection);
    setSuggestions([]);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={containerRef}>
      <div ref={inputRef}>
        <AstroInput
          label={label}
          placeholder={placeholder}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            onChange(e.target.value);
          }}
          autoComplete="off"
          error={error}
        />
      </div>
      
      {/* Dropdown de sugestões - posicionado com z-index alto */}
      {isOpen && suggestions.length > 0 && (
        <div 
          className="absolute left-0 right-0 mt-1 bg-card border border-border rounded-xl shadow-2xl overflow-hidden max-h-48 overflow-y-auto"
          style={{ 
            zIndex: 9999,
            top: '100%',
          }}
        >
          {isLoading && (
            <div className="flex items-center gap-2 px-4 py-3 text-sm text-secondary">
              <UIIcons.Loader className="w-4 h-4 animate-spin" />
              Buscando lugares...
            </div>
          )}
          {suggestions.map((suggestion, index) => {
            const { shortName, city, state, country } = formatLocation(suggestion);
            return (
              <button
                key={`${suggestion.lat}-${suggestion.lon}-${index}`}
                className="w-full text-left px-4 py-3 hover:bg-primary/10 focus:bg-primary/10 transition-colors border-b border-border/50 last:border-b-0"
                onClick={() => handleSelect(suggestion)}
                type="button"
              >
                <div className="flex items-center gap-2">
                  <UIIcons.MapPin size={16} className="text-primary flex-shrink-0" />
                  <div>
                    <p className="text-foreground text-sm font-medium">{city || shortName.split(',')[0]}</p>
                    <p className="text-muted-foreground text-xs">
                      {[state, country].filter(Boolean).join(', ')}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
      
      {!isLoading && isOpen && suggestions.length === 0 && query.trim().length >= 3 && (
        <div 
          className="absolute left-0 right-0 mt-1 bg-card border border-border rounded-xl shadow-lg px-4 py-3 text-sm text-secondary"
          style={{ zIndex: 9999, top: '100%' }}
        >
          Nenhum resultado encontrado.
        </div>
      )}
    </div>
  );
};
