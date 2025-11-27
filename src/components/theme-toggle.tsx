import React from 'react';
import { useTheme } from './theme-provider';
import { UIIcons } from './ui-icons';

export const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-lg hover:bg-accent/10 hover:scale-110 transition-all duration-300 group"
      aria-label="Alternar tema"
    >
      <div className="relative w-6 h-6">
        {/* Sun Icon */}
        <UIIcons.Sun
          size={20}
          className={`absolute inset-0 m-auto text-accent transition-all duration-300 group-hover:scale-110 ${
            theme === 'light'
              ? 'opacity-100 rotate-0 scale-100'
              : 'opacity-0 rotate-90 scale-0'
          }`}
        />
        {/* Moon Icon */}
        <UIIcons.Moon
          size={20}
          className={`absolute inset-0 m-auto text-accent transition-all duration-300 group-hover:scale-110 ${
            theme === 'dark'
              ? 'opacity-100 rotate-0 scale-100'
              : 'opacity-0 -rotate-90 scale-0'
          }`}
        />
      </div>
    </button>
  );
};
