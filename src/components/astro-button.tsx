import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import '../styles/components.css';

interface AstroButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'google';
  size?: 'sm' | 'md' | 'lg';
}

export const AstroButton = forwardRef<HTMLButtonElement, AstroButtonProps>(
  ({ className = '', variant = 'primary', size = 'md', children, ...props }, ref) => {
    const classes = [
      'astro-button',
      `astro-button-${variant}`,
      `astro-button-${size}`,
      className
    ].filter(Boolean).join(' ');
    
    return (
      <button
        ref={ref}
        className={classes}
        {...props}
      >
        {children}
      </button>
    );
  }
);

AstroButton.displayName = 'AstroButton';
