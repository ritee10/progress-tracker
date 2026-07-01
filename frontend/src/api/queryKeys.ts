export const QUERY_KEYS = {
  skills: ['skills'],
  skill: (id: string | number) => ['skill', id],

  topics: ['topics'],
  topic: (id: string | number) => ['topic', id],
  overdueTopics: ['topics', 'overdue'],

  dashboard: ['dashboard'],
  streak: ['streak'],
  longestStreak: ['streak', 'longest'],
  heatmap: ['streak', 'heatmap'],
  
  search: (query: string) => ['search', query],
  recentActivity: ['activity', 'recent'],
  
  progress: ['progress'],
} as const;
