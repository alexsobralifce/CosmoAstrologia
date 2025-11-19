import { useEffect, useRef, useState } from 'react';
import { AstroInput } from './astro-input';
import { UIIcons } from './ui-icons';

export interface LocationSelection {
  displayName: string;
  lat: number;
  lon: number;
}

interface LocationAutocompleteProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  onSelect: (selection: LocationSelection) => void;
}

interface Suggestion {
  display_name: string;
  lat: string;
  lon: string;
}

export const LocationAutocomplete = ({
  label,
  placeholder,
  value,
  onChange,
  onSelect,
}: LocationAutocompleteProps) => {
  const [query, setQuery] = useState(value);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

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
    const selection = {
      displayName: suggestion.display_name,
      lat: Number(suggestion.lat),
      lon: Number(suggestion.lon),
    };
    onSelect(selection);
    setSuggestions([]);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={containerRef}>
      <AstroInput
        label={label}
        placeholder={placeholder}
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          onChange(e.target.value);
        }}
        autoComplete="off"
      />
      {isOpen && suggestions.length > 0 && (
        <div className="absolute z-20 w-full mt-2 bg-card border border-border rounded-xl shadow-lg overflow-hidden max-h-56 overflow-y-auto">
          {isLoading && (
            <div className="flex items-center gap-2 px-4 py-3 text-sm text-secondary">
              <UIIcons.Loader className="w-4 h-4 animate-spin" />
              Buscando lugares...
            </div>
          )}
          {suggestions.map((suggestion) => (
            <button
              key={`${suggestion.lat}-${suggestion.lon}-${suggestion.display_name}`}
              className="w-full text-left px-4 py-3 hover:bg-accent/10 focus:bg-accent/10 transition-colors"
              onClick={() => handleSelect(suggestion)}
              type="button"
            >
              <p className="text-foreground text-sm font-medium">{suggestion.display_name}</p>
            </button>
          ))}
        </div>
      )}
      {!isLoading && isOpen && suggestions.length === 0 && query.trim().length >= 3 && (
        <div className="absolute z-20 w-full mt-2 bg-card border border-border rounded-xl shadow-lg px-4 py-3 text-sm text-secondary">
          Nenhum resultado encontrado.
        </div>
      )}
    </div>
  );
};

