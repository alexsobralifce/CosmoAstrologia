import React, { InputHTMLAttributes, forwardRef, useId } from 'react';
import { cn } from './ui/utils';

interface AstroInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const AstroInput = forwardRef<HTMLInputElement, AstroInputProps>(
  ({ className, label, error, type = 'text', id, ...props }, ref) => {
    // Associa o rótulo e a mensagem de erro ao campo (leitores de tela e clique no rótulo)
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const errorId = `${inputId}-error`;

    return (
      <div className="login-input-wrapper">
        {label && (
          <label className="login-input-label" htmlFor={inputId}>
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          type={type}
          className={cn(
            "login-input-figma",
            error && "error",
            className
          )}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? errorId : undefined}
          {...props}
        />
        {error && (
          <p id={errorId} className="login-input-error" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

AstroInput.displayName = 'AstroInput';
