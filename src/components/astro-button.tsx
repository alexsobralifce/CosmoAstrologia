import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from './ui/utils';

interface AstroButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'google';
  size?: 'sm' | 'md' | 'lg';
}

export const AstroButton = forwardRef<HTMLButtonElement, AstroButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center gap-2 rounded-lg transition-all duration-200 font-medium focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed";
    
    const variants = {
      primary: "bg-accent text-accent-foreground hover:bg-accent/90 shadow-lg shadow-accent/20",
      secondary: "bg-card text-card-foreground border border-border hover:bg-card/80 backdrop-blur-sm",
      google: "bg-white text-gray-900 border border-gray-300 hover:bg-gray-50 shadow-sm"
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
