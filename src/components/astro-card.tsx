import { HTMLAttributes, ReactNode } from 'react';
import { cn } from './ui/utils';

interface AstroCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: 'default' | 'glass' | 'solid';
}

export const AstroCard = ({ children, className, variant = 'glass', ...props }: AstroCardProps) => {
  const variants = {
    default: "bg-card backdrop-blur-md",
    glass: "bg-card backdrop-blur-md border border-border/50",
    solid: "bg-card/90 backdrop-blur-md"
  };
  
  return (
    <div
      className={cn(
        "rounded-lg p-6 shadow-xl",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
