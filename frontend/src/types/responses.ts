export interface ErrorResponse {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>;
}

export interface DashboardStats {
  totalSkills: number;
  totalTopics: number;
  completedTopics: number;
  progressPercentage: number;
  streakDays: number;
}

// Additional specific backend responses can be placed here
