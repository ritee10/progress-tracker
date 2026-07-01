// ============================================================
// Component — ProgressBar
// ============================================================

import { cn } from '@/lib/utils';
import { getProgressBarColor } from '@/lib/skillUtils';
import { useEffect, useRef, useState } from 'react';

interface ProgressBarProps {
  value: number;      // 0-100
  className?: string;
  showLabel?: boolean;
  label?: string;
  animate?: boolean;
  size?: 'sm' | 'md' | 'lg';
  colorOverride?: string;
}

export function ProgressBar({
  value,
  className,
  showLabel = true,
  label,
  animate = true,
  size = 'md',
  colorOverride,
}: ProgressBarProps) {
  const [width, setWidth] = useState(animate ? 0 : value);
  const mounted = useRef(false);

  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true;
      if (animate) {
        const timeout = setTimeout(() => setWidth(Math.min(value, 100)), 50);
        return () => clearTimeout(timeout);
      }
    }
    setWidth(Math.min(value, 100));
  }, [value, animate]);

  const heightClass = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  }[size];

  const barColor = colorOverride ?? getProgressBarColor(value);

  return (
    <div className={cn('w-full', className)}>
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-1">
          {label && <span className="text-xs font-medium text-muted-foreground">{label}</span>}
          {showLabel && <span className="text-xs font-semibold">{Math.round(value)}%</span>}
        </div>
      )}
      <div className={cn('w-full rounded-full bg-muted/50 overflow-hidden', heightClass)}>
        <div
          className={cn('h-full rounded-full transition-all duration-700 ease-out', barColor)}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}
