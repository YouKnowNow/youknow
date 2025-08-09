import { useState, useEffect } from 'react';
import { DashboardCard } from './DashboardCard';
import { TrendCard } from './TrendCard';
import { GoldenHoursChart } from './GoldenHoursChart';
import { Badge } from '@/components/ui/badge-variants';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Clock, Calendar, Target, ChevronRight } from 'lucide-react';

interface DashboardData {
  top_domains: Array<{ domain: string; minutes: number }>;
  top_searches: Array<{ q: string; count: number }>;
  focus: { docs_min: number; social_min: number; score: number };
  golden_hours: Record<string, number>;
  sessions: Array<{
    start: string;
    duration_min: number;
    dominant: string;
    path: string[];
  }>;
  trends: {
    docs_min_delta_pct: number;
    social_min_delta_pct: number;
    search_count_delta_pct: number;
  };
  chains: string[][];
  interests: string[];
}

export function ProductivityDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // In development, use the proxy to Flask backend
        // In production, this will be served from the same domain
        const apiUrl = import.meta.env.DEV ? '/api/dashboard' : '/api/dashboard';
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const jsonData = await response.json();
        setData(jsonData);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        setError(error instanceof Error ? error.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-muted-foreground">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-destructive text-center">
          <div className="text-lg font-semibold mb-2">Failed to load dashboard data</div>
          <div className="text-sm text-muted-foreground">{error}</div>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-destructive">No data available</div>
      </div>
    );
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-background p-3">
      <div className="max-w-7xl mx-auto space-y-3">
        {/* Header */}
        <div className="border-b border-border pb-3">
          <h1 className="text-xl font-bold text-foreground">Productivity Dashboard</h1>
          <p className="text-muted-foreground mt-1 text-sm">Weekly insights into your browsing patterns and focus metrics</p>
        </div>

        {/* Focus Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <DashboardCard title="Focus vs. Distraction" className="md:col-span-1">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground">Focus Time</span>
                <span className="font-semibold text-focus text-sm">{data.focus.docs_min}m</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground">Social Time</span>
                <span className="font-semibold text-distraction text-sm">{data.focus.social_min}m</span>
              </div>
              <div className="pt-1 border-t border-border">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-medium">Focus Score</span>
                  <div className="flex items-center">
                    <Target className="w-3 h-3 mr-1 text-primary" />
                    <span className="font-bold text-sm">{Math.round(data.focus.score * 100)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </DashboardCard>

          {/* Trends */}
          <TrendCard
            title="Docs Minutes"
            value={data.focus.docs_min}
            change={data.trends.docs_min_delta_pct}
            unit="m"
          />
          <TrendCard
            title="Search Count"
            value={data.top_searches.reduce((acc, search) => acc + search.count, 0)}
            change={data.trends.search_count_delta_pct}
          />
        </div>

        {/* Golden Hours Chart */}
        <DashboardCard title="Golden Hours">
          <GoldenHoursChart data={data.golden_hours} />
        </DashboardCard>

        {/* Tables Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* Top Domains */}
          <DashboardCard title="Top Domains (Weekly)">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Domain</TableHead>
                  <TableHead className="text-right">Minutes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.top_domains.map((domain, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{domain.domain}</TableCell>
                    <TableCell className="text-right">{domain.minutes}m</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </DashboardCard>

          {/* Top Searches */}
          <DashboardCard title="Top Searches (Weekly)">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Query</TableHead>
                  <TableHead className="text-right">Count</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.top_searches.map((search, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{search.q}</TableCell>
                    <TableCell className="text-right">{search.count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </DashboardCard>
        </div>

        {/* Recent Sessions */}
        <DashboardCard title="Recent Sessions">
          <div className="space-y-2">
            {data.sessions.map((session, index) => (
              <div key={index} className="flex items-center justify-between p-2 border border-border rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3 mr-1" />
                    {formatTime(session.start)}
                  </div>
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Clock className="w-3 h-3 mr-1" />
                    {session.duration_min}m
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="interest" size="sm">{session.dominant}</Badge>
                  <div className="flex items-center text-xs text-muted-foreground">
                    {session.path.join(' → ')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </DashboardCard>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* Common Chains */}
          <DashboardCard title="Common Browsing Patterns">
            <div className="space-y-2">
              {data.chains.map((chain, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <span className="text-xs font-medium text-muted-foreground">#{index + 1}</span>
                  <div className="flex items-center space-x-1 text-xs">
                    {chain.map((site, siteIndex) => (
                      <div key={siteIndex} className="flex items-center">
                        <span className="font-medium">{site}</span>
                        {siteIndex < chain.length - 1 && (
                          <ChevronRight className="w-2 h-2 mx-1 text-muted-foreground" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </DashboardCard>

          {/* Interests */}
          <DashboardCard title="Current Interests">
            <div className="flex flex-wrap gap-1">
              {data.interests.map((interest, index) => (
                <Badge key={index} variant="interest" size="sm">{interest}</Badge>
              ))}
            </div>
          </DashboardCard>
        </div>
      </div>
    </div>
  );
}