'use client';

import React from 'react';
import { useTheme } from './theme-provider';
import { UIIcons } from './ui-icons';
import '../styles/controls.css';

export const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle-button"
      aria-label="Alternar tema"
    >
      <UIIcons.Sun
        size={20}
        className="theme-toggle-icon"
      />
    </button>
  );
};
