import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from './ui/utils';

interface AstroButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'google';
  size?: 'sm' | 'md' | 'lg';
}

export const AstroButton = forwardRef<HTMLButtonElement, AstroButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center gap-2 rounded-lg transition-all duration-200 font-medium focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed";
    
    const variants = {
      primary: "bg-accent text-accent-foreground hover:bg-accent/90 hover:scale-105 hover:shadow-xl hover:shadow-accent/30 shadow-lg shadow-accent/20 transition-all duration-200",
      secondary: "bg-card text-card-foreground border border-border hover:bg-card/80 hover:scale-105 hover:border-accent/40 hover:shadow-lg backdrop-blur-sm transition-all duration-200",
      google: "bg-white dark:bg-card text-gray-900 dark:text-foreground border border-gray-300 dark:border-border hover:bg-gray-50 dark:hover:bg-card/80 hover:scale-105 hover:shadow-md shadow-sm transition-all duration-200"
    };
    
    const sizes = {
      sm: "px-4 py-2",
      md: "px-6 py-3",
      lg: "px-8 py-4"
    };
    
    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

AstroButton.displayName = 'AstroButton';
