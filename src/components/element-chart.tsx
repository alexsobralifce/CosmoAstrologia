import React from 'react';
import { AstroCard } from './astro-card';

interface ElementData {
  name: string;
  percentage: number;
  color: string;
}

interface ElementChartProps {
  data: ElementData[];
  title: string;
}

export const ElementChart = ({ data, title }: ElementChartProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-foreground">{title}</h3>
      <div className="space-y-3">
        {data.map((item) => (
          <div key={item.name} className="space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-secondary">{item.name}</span>
              <span className="text-accent">{item.percentage}%</span>
            </div>
            <div className="w-full h-3 bg-card rounded-full overflow-hidden border border-border/30">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${item.percentage}%`,
                  backgroundColor: item.color,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
