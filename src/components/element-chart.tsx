import React from 'react';

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
    <div className="element-chart-container">
      {title && <h3 className="element-chart-title">{title}</h3>}
      <div className="element-chart-bars">
        {data.map((item) => (
          <div key={item.name} className="element-chart-item">
            <div className="element-chart-item-header">
              <span className="element-chart-item-name">{item.name}</span>
            </div>
            <div className="element-chart-bar-container">
              <div
                className="element-chart-bar"
                style={{
                  width: `${item.percentage}%`,
                  backgroundColor: item.color,
                }}
              >
                <span className="element-chart-bar-label">{item.percentage}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
