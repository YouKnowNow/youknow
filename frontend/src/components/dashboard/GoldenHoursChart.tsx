import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface GoldenHoursChartProps {
  data: Record<string, number>;
}

export function GoldenHoursChart({ data }: GoldenHoursChartProps) {
  const hours = Object.keys(data).sort((a, b) => parseInt(a) - parseInt(b));
  const values = hours.map(hour => data[hour]);

  const chartData = {
    labels: hours.map(hour => `${hour}:00`),
    datasets: [
      {
        label: 'Minutes',
        data: values,
        backgroundColor: 'hsl(var(--chart-primary) / 0.8)',
        borderColor: 'hsl(var(--chart-primary))',
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'hsl(var(--popover))',
        borderColor: 'hsl(var(--border))',
        borderWidth: 1,
        titleColor: 'hsl(var(--popover-foreground))',
        bodyColor: 'hsl(var(--popover-foreground))',
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: 'hsl(var(--muted-foreground))',
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'hsl(var(--border))',
        },
        ticks: {
          color: 'hsl(var(--muted-foreground))',
        },
      },
    },
  };

  return (
    <div className="h-48">
      <Bar data={chartData} options={options} />
    </div>
  );
}