import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from './ui/utils';

interface AstroInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const AstroInput = forwardRef<HTMLInputElement, AstroInputProps>(
  ({ className, label, error, type = 'text', ...props }, ref) => {
    return (
      <div className="w-full space-y-2">
        {label && (
          <label className="block text-sm text-foreground/90">
            {label}
          </label>
        )}
        <input
          ref={ref}
          type={type}
          className={cn(
            "w-full px-4 py-3 rounded-lg bg-input-background border border-[var(--input-border)] text-foreground placeholder:text-secondary transition-all duration-200",
            "focus:outline-none focus:border-[var(--input-border-active)] focus:ring-2 focus:ring-accent/20",
            "backdrop-blur-sm",
            error && "border-destructive focus:border-destructive focus:ring-destructive/20",
            className
          )}
          {...props}
        />
        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}
      </div>
    );
  }
);

AstroInput.displayName = 'AstroInput';
