// ============================================================
// Component — SkillAnalytics (Charts)
// ============================================================

import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { SkillStats } from '@/types/skill';

interface SkillAnalyticsProps {
  stats: SkillStats;
}

const COLORS = ['#22c55e', '#f97316'];

export function SkillAnalytics({ stats }: SkillAnalyticsProps) {
  const pieData = [
    { name: 'Completed', value: stats.completedTopics },
    { name: 'Pending', value: stats.pendingTopics },
  ];

  const studyData = [
    { name: 'Completion %', value: stats.completionPercentage },
    { name: 'Remaining %', value: 100 - stats.completionPercentage },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
      {/* Topic Distribution Pie */}
      <div className="bg-card border rounded-2xl p-5 shadow-sm">
        <h3 className="font-semibold mb-4">Topic Distribution</h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={3}
              dataKey="value"
            >
              {pieData.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Completion Bar Chart */}
      <div className="bg-card border rounded-2xl p-5 shadow-sm">
        <h3 className="font-semibold mb-4">Completion Rate</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={studyData} barSize={40}>
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} unit="%" />
            <Tooltip
              formatter={(v: unknown) => [`${Number(v)}%`]}
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              <Cell fill="#22c55e" />
              <Cell fill="#f97316" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
