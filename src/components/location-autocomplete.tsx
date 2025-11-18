import { useState, useEffect, useRef } from 'react';
import { AstroInput } from './astro-input';
import { UIIcons } from './ui-icons';

interface LocationSuggestion {
  display_name: string;
  city: string;
  state: string;
  country: string;
  lat: string;
  lon: string;
}

interface LocationAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect?: (location: LocationSuggestion) => void;
  label?: string;
  placeholder?: string;
  autoFocus?: boolean;
}

export const LocationAutocomplete = ({
  value,
  onChange,
  onSelect,
  label,
  placeholder = "Ex: São Paulo, SP",
  autoFocus = false
}: LocationAutocompleteProps) => {
  const [suggestions, setSuggestions] = useState<LocationSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceTimer = useRef<NodeJS.Timeout>();

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch suggestions from Nominatim (OpenStreetMap)
  const fetchSuggestions = async (query: string) => {
    if (query.length < 3) {
      setSuggestions([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?` +
        `q=${encodeURIComponent(query)}` +
        `&format=json` +
        `&addressdetails=1` +
        `&limit=5` +
        `&countrycodes=br,us,pt,es,mx,ar,cl,co,pe,uy,py,bo,ve,ec`, // Common countries
        {
          headers: {
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
          }
        }
      );

      if (!response.ok) throw new Error('Failed to fetch suggestions');

      const data = await response.json();
      
      const parsed: LocationSuggestion[] = data.map((item: any) => {
        const address = item.address || {};
        const city = address.city || address.town || address.village || address.municipality || '';
        const state = address.state || address.region || '';
        const country = address.country || '';
        
        let displayName = '';
        if (city) displayName += city;
        if (state) displayName += (displayName ? ', ' : '') + state;
        if (country) displayName += (displayName ? ', ' : '') + country;
        
        if (!displayName) displayName = item.display_name;

        return {
          display_name: displayName,
          city,
          state,
          country,
          lat: item.lat,
          lon: item.lon
        };
      });

      setSuggestions(parsed);
      setShowSuggestions(true);
    } catch (error) {
      console.error('Error fetching location suggestions:', error);
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    setSelectedIndex(-1);

    // Debounce API calls
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(() => {
      fetchSuggestions(newValue);
    }, 500);
  };

  const handleSelectSuggestion = (suggestion: LocationSuggestion) => {
    onChange(suggestion.display_name);
    setShowSuggestions(false);
    setSuggestions([]);
    if (onSelect) {
      onSelect(suggestion);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelectSuggestion(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        break;
    }
  };

  return (
    <div ref={wrapperRef} className="relative">
      <AstroInput
        label={label}
        placeholder={placeholder}
        value={value}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => {
          if (suggestions.length > 0) {
            setShowSuggestions(true);
          }
        }}
        autoFocus={autoFocus}
        autoComplete="off"
      />

      {/* Loading indicator */}
      {isLoading && (
        <div className="absolute right-3 top-[38px] animate-spin">
          <UIIcons.Search size={16} className="text-accent" />
        </div>
      )}

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-card border border-border/30 rounded-lg shadow-xl overflow-hidden animate-fadeIn">
          <div className="max-h-[300px] overflow-y-auto">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSelectSuggestion(suggestion)}
                onMouseEnter={() => setSelectedIndex(index)}
                className={`w-full px-4 py-3 text-left transition-colors border-b border-border/10 last:border-b-0 ${
                  index === selectedIndex
                    ? 'bg-accent/20'
                    : 'hover:bg-accent/10'
                }`}
              >
                <div className="flex items-start gap-3">
                  <UIIcons.MapPin size={16} className="text-accent mt-1 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {suggestion.city || 'Localização'}
                    </p>
                    <p className="text-xs text-secondary truncate">
                      {suggestion.state && `${suggestion.state}, `}
                      {suggestion.country}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
          
          {/* Footer with info */}
          <div className="px-4 py-2 bg-card/50 border-t border-border/20">
            <p className="text-xs text-secondary flex items-center gap-2">
              <UIIcons.Info size={12} />
              Use as setas ↑↓ para navegar e Enter para selecionar
            </p>
          </div>
        </div>
      )}

      {/* No results message */}
      {showSuggestions && !isLoading && value.length >= 3 && suggestions.length === 0 && (
        <div className="absolute z-50 w-full mt-2 bg-card border border-border/30 rounded-lg shadow-xl p-4 animate-fadeIn">
          <div className="flex items-center gap-3 text-secondary">
            <UIIcons.Search size={16} />
            <p className="text-sm">Nenhuma localização encontrada. Tente ser mais específico.</p>
          </div>
        </div>
      )}
    </div>
  );
};

