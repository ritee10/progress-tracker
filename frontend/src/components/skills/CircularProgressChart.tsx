// ============================================================
// Component — CircularProgressChart
// ============================================================

interface CircularProgressProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
  animate?: boolean;
}

import { useEffect, useState } from 'react';
import { getProgressStrokeColor } from '@/lib/skillUtils';

export function CircularProgressChart({
  percentage,
  size = 120,
  strokeWidth = 10,
  showLabel = true,
  animate = true,
}: CircularProgressProps) {
  const [displayed, setDisplayed] = useState(animate ? 0 : percentage);

  useEffect(() => {
    if (!animate) {
      setDisplayed(percentage);
      return;
    }
    const start = 0;
    const end = Math.min(percentage, 100);
    const duration = 900;
    const startTime = performance.now();

    const step = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayed(Math.round(start + (end - start) * eased));
      if (progress < 1) requestAnimationFrame(step);
    };

    requestAnimationFrame(step);
  }, [percentage, animate]);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (displayed / 100) * circumference;
  const center = size / 2;
  const strokeColor = getProgressStrokeColor(percentage);
  const gradientId = `gradient-${Math.random().toString(36).slice(2)}`;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={strokeColor} stopOpacity="0.6" />
            <stop offset="100%" stopColor={strokeColor} stopOpacity="1" />
          </linearGradient>
        </defs>
        {/* Track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-muted/30"
        />
        {/* Progress */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: 'stroke-dashoffset 0.1s ease' }}
        />
      </svg>
      {showLabel && (
        <span className="absolute text-center">
          <span className="block text-lg font-bold leading-tight">{displayed}%</span>
        </span>
      )}
    </div>
  );
}
