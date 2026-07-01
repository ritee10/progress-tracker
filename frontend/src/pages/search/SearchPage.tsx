import { useState } from 'react';
import { useSearch } from '@/hooks/useSearch';
import { useDebounce } from '@/hooks/useDebounce';
import { Search as SearchIcon, SlidersHorizontal } from 'lucide-react';
import { LoadingOverlay } from '@/components/ui/api-status/LoadingOverlay';
import { ErrorBanner } from '@/components/ui/api-status/ErrorBanner';
import { cn } from '@/lib/utils';

type SearchType = 'global' | 'topic' | 'skill';

const TYPE_OPTIONS: { label: string; value: SearchType }[] = [
  { label: 'All', value: 'global' },
  { label: 'Skills', value: 'skill' },
  { label: 'Topics', value: 'topic' },
];

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [type, setType] = useState<SearchType>('global');
  const debouncedQuery = useDebounce(query, 500);

  const { data: results, isLoading, error } = useSearch(debouncedQuery, type);

  return (
    <div className="space-y-5 sm:space-y-6">
      {/* Page heading */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Search</h1>
        <p className="text-muted-foreground mt-1 text-sm sm:text-base">
          Find skills, topics, and notes instantly.
        </p>
      </div>

      {/* Search bar — full width */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <input
            type="search"
            inputMode="search"
            autoCapitalize="off"
            autoCorrect="off"
            className="w-full pl-10 pr-4 py-3 sm:py-2.5 border rounded-xl bg-background focus:outline-none focus:ring-2 focus:ring-ring text-sm min-h-[44px]"
            placeholder="Search skills, topics, notes..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        {/* Filter — pill buttons on mobile, select on desktop */}
        <div className="flex items-center gap-2 sm:hidden">
          <SlidersHorizontal className="h-4 w-4 text-muted-foreground shrink-0" />
          {TYPE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setType(opt.value)}
              className={cn(
                'rounded-full px-3.5 py-1.5 text-xs font-medium border transition-colors min-h-[36px]',
                type === opt.value
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-muted/50 text-muted-foreground border-transparent hover:bg-muted'
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Desktop select */}
        <select
          value={type}
          onChange={(e) => setType(e.target.value as SearchType)}
          className="hidden sm:block border rounded-xl px-3 py-2.5 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring min-h-[44px]"
        >
          {TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label === 'All' ? 'Global Search' : `${opt.label} Only`}
            </option>
          ))}
        </select>
      </div>

      {/* Results area */}
      <div className="min-h-[280px] border rounded-xl p-5 relative">
        {isLoading && <LoadingOverlay message="Searching..." />}
        {error && (
          <ErrorBanner title="Search Failed" message={(error as any).message} />
        )}

        {!isLoading && !error && debouncedQuery.length <= 2 && (
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-3">
            <SearchIcon className="h-10 w-10 opacity-20" />
            <p className="text-sm">Type at least 3 characters to search</p>
          </div>
        )}

        {!isLoading && !error && debouncedQuery.length > 2 && results?.data?.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-3">
            <SearchIcon className="h-10 w-10 opacity-20" />
            <p className="text-sm">
              Nothing matched &quot;{debouncedQuery}&quot;
            </p>
          </div>
        )}

        {!isLoading && !error && results?.data?.length > 0 && (
          <div className="space-y-3">
            {results.data.map((item: any, i: number) => (
              <div
                key={i}
                className="p-4 border rounded-xl hover:bg-muted/50 active:bg-muted transition-colors cursor-pointer"
              >
                <h3 className="font-semibold text-sm sm:text-base">
                  {item.title || item.name}
                </h3>
                {item.description && (
                  <p className="text-xs sm:text-sm text-muted-foreground mt-1 line-clamp-2">
                    {item.description}
                  </p>
                )}
                <div className="mt-2 text-xs bg-primary/10 text-primary px-2.5 py-0.5 rounded-full inline-block">
                  {item.type || type}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
