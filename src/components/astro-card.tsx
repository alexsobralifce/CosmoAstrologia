import React, { HTMLAttributes, ReactNode } from 'react';
import '../styles/components.css';

interface AstroCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: 'default' | 'glass' | 'solid';
  className?: string;
}

export const AstroCard = ({ children, className = '', variant = 'glass', ...props }: AstroCardProps) => {
  const classes = [
    'astro-card',
    `astro-card-${variant}`,
    className
  ].filter(Boolean).join(' ');
  
  return (
    <div
      className={classes}
      {...props}
    >
      {children}
    </div>
  );
};
