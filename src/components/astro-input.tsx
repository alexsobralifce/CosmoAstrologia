import React, { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from './ui/utils';

interface AstroInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const AstroInput = forwardRef<HTMLInputElement, AstroInputProps>(
  ({ className, label, error, type = 'text', ...props }, ref) => {
    return (
      <div className="login-input-wrapper">
        {label && (
          <label className="login-input-label">
            {label}
          </label>
        )}
        <input
          ref={ref}
          type={type}
          className={cn(
            "login-input-figma",
            error && "error",
            className
          )}
          {...props}
        />
        {error && (
          <p className="login-input-error">
            {error}
          </p>
        )}
      </div>
    );
  }
);

AstroInput.displayName = 'AstroInput';
