import React, { useMemo } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';

interface PullRequest {
    number: number;
    title: string;
    author: string;
    labels: string[];
    created_at: string;
}

interface StatsDashboardProps {
    prs: PullRequest[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

export function StatsDashboard({ prs }: StatsDashboardProps) {
    // 1. Label Distribution
    const labelData = useMemo(() => {
        const counts: Record<string, number> = {};
        prs.forEach(pr => {
            if (pr.labels.length === 0) {
                counts['(no label)'] = (counts['(no label)'] || 0) + 1;
            } else {
                pr.labels.forEach(label => {
                    counts[label] = (counts[label] || 0) + 1;
                });
            }
        });
        return Object.entries(counts)
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value)
            .slice(0, 5); // Top 5 labels
    }, [prs]);

    // 2. Top Authors
    const authorData = useMemo(() => {
        const counts: Record<string, number> = {};
        prs.forEach(pr => {
            counts[pr.author] = (counts[pr.author] || 0) + 1;
        });
        return Object.entries(counts)
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value)
            .slice(0, 5); // Top 5 authors
    }, [prs]);

    if (prs.length === 0) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-6">
            {/* Label Distribution */}
            <div className="bg-neutral-900/50 border border-neutral-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-neutral-500 mb-6">
                    Top Labels
                </h3>
                <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={labelData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                            >
                                {labelData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="transparent" />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#171717', borderColor: '#404040', borderRadius: '8px' }}
                                itemStyle={{ color: '#e5e5e5' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Top Authors */}
            <div className="bg-neutral-900/50 border border-neutral-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-neutral-500 mb-6">
                    Top Contributors
                </h3>
                <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={authorData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#404040" vertical={false} />
                            <XAxis dataKey="name" stroke="#737373" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#737373" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                            <Tooltip
                                cursor={{ fill: '#262626' }}
                                contentStyle={{ backgroundColor: '#171717', borderColor: '#404040', borderRadius: '8px' }}
                                itemStyle={{ color: '#e5e5e5' }}
                            />
                            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
