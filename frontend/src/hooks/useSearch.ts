import { useQuery } from '@tanstack/react-query';
import { searchApi } from '../api/search.api';
import { QUERY_KEYS } from '../api/queryKeys';

export function useSearch(query: string, type: 'global' | 'topic' | 'skill' = 'global') {
  return useQuery({
    queryKey: QUERY_KEYS.search(query),
    queryFn: () => {
      if (!query) return [];
      switch (type) {
        case 'topic':
          return searchApi.topicSearch(query);
        case 'skill':
          return searchApi.skillSearch(query);
        case 'global':
        default:
          return searchApi.globalSearch(query);
      }
    },
    enabled: !!query && query.length > 2, // Only search if query is at least 3 chars
    staleTime: 1000 * 60, // 1 minute cache for search
  });
}
