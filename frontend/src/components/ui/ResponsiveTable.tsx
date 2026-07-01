import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { useMobile } from '@/hooks/useMobile';

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  /** If true, this column is hidden on mobile card view */
  mobileHide?: boolean;
  /** If true, render this as the card title on mobile */
  mobileTitle?: boolean;
}

interface ResponsiveTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: (row: T) => string;
  className?: string;
  emptyMessage?: string;
}

/**
 * ResponsiveTable
 * - Desktop: standard HTML table
 * - Mobile: stacked cards per row
 */
export function ResponsiveTable<T>({
  columns,
  data,
  rowKey,
  className,
  emptyMessage = 'No data available.',
}: ResponsiveTableProps<T>) {
  const isMobile = useMobile();

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
        {emptyMessage}
      </div>
    );
  }

  if (isMobile) {
    return (
      <div className={cn('space-y-3', className)}>
        {data.map((row) => {
          const titleCol = columns.find((c) => c.mobileTitle);
          const visibleCols = columns.filter((c) => !c.mobileHide && !c.mobileTitle);

          return (
            <div
              key={rowKey(row)}
              className="bg-card border rounded-xl p-4 space-y-2 shadow-sm"
            >
              {/* Card title */}
              {titleCol && (
                <div className="font-semibold text-sm">{titleCol.render(row)}</div>
              )}
              {/* Other fields */}
              {visibleCols.map((col) => (
                <div key={col.key} className="flex items-center justify-between gap-2">
                  <span className="text-xs text-muted-foreground">{col.header}</span>
                  <span className="text-sm font-medium text-right">{col.render(row)}</span>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className={cn('w-full overflow-x-auto rounded-xl border', className)}>
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-muted/40 border-b">
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.map((row) => (
            <tr
              key={rowKey(row)}
              className="hover:bg-muted/30 transition-colors"
            >
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3 whitespace-nowrap">
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
