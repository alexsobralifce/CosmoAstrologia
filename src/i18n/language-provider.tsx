import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { translations, Language } from './translations';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  t: (category: string, key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    // Check localStorage first
    const savedLang = localStorage.getItem('astro-language') as Language;
    if (savedLang && (savedLang === 'pt' || savedLang === 'en')) {
      return savedLang;
    }
    
    // Check browser language
    const browserLang = navigator.language.toLowerCase();
    if (browserLang.startsWith('pt')) {
      return 'pt';
    }
    
    return 'pt'; // Default to Portuguese
  });

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('astro-language', lang);
  }, []);

  const toggleLanguage = useCallback(() => {
    setLanguageState((prev) => {
      const newLang = prev === 'pt' ? 'en' : 'pt';
      localStorage.setItem('astro-language', newLang);
      return newLang;
    });
  }, []);

  // Translation function
  const t = useCallback((category: string, key: string): string => {
    try {
      // Handle nested paths like "calendar.months.january"
      const parts = key.split('.');
      let result: any = (translations as any)[category];
      
      if (!result) {
        console.warn(`Translation category not found: ${category}`);
        return key;
      }

      for (const part of parts) {
        result = result?.[part];
        if (result === undefined) {
          console.warn(`Translation key not found: ${category}.${key}`);
          return key;
        }
      }

      // If result is an object with pt/en keys
      if (result && typeof result === 'object' && language in result) {
        return result[language];
      }

      // If it's a direct string (shouldn't happen with current structure)
      if (typeof result === 'string') {
        return result;
      }

      return key;
    } catch (error) {
      console.warn(`Translation error for ${category}.${key}:`, error);
      return key;
    }
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Hook helper for direct translation access
export const useTranslation = () => {
  const { t, language } = useLanguage();
  return { t, language };
};

