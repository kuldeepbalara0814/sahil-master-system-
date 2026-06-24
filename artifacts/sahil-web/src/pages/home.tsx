import { useGetStats, useGetPredictions } from "@workspace/api-client-react";
import { Layout } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Link } from "wouter";
import { Zap, FileEdit, Activity } from "lucide-react";

export default function Home() {
  const { data: stats, isLoading: statsLoading } = useGetStats();
  const { data: predictions, isLoading: predsLoading } = useGetPredictions();

  const recentPredictions = predictions?.slice(0, 3) || [];

  return (
    <Layout title="Sahil Master System">
      <div className="space-y-6">
        <section>
          <h2 className="text-lg font-semibold mb-3">Aaj ki Stats</h2>
          {statsLoading ? (
            <Skeleton className="h-32 w-full rounded-xl" />
          ) : stats ? (
            <div className="grid grid-cols-2 gap-3">
              <Card className="bg-primary text-primary-foreground border-primary">
                <CardHeader className="p-4 pb-2">
                  <CardTitle className="text-sm font-medium opacity-90">Success Rate</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="text-3xl font-bold">{Math.round(stats.successRate)}%</div>
                  <div className="text-xs mt-1 opacity-80">{stats.passed} Passed / {stats.total} Total</div>
                </CardContent>
              </Card>
              
              <Card className="bg-card">
                <CardHeader className="p-4 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Pending</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="text-3xl font-bold text-foreground">{stats.pending}</div>
                  <div className="text-xs mt-1 text-muted-foreground">Waiting for results</div>
                </CardContent>
              </Card>

              <Card className="bg-card col-span-2">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="text-center">
                    <div className="text-xl font-bold text-green-500">{stats.passL1}</div>
                    <div className="text-xs text-muted-foreground">L1 Pass</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-blue-500">{stats.passL2}</div>
                    <div className="text-xs text-muted-foreground">L2 Pass</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-yellow-500">{stats.passL3}</div>
                    <div className="text-xs text-muted-foreground">L3 Pass</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-red-500">{stats.failed}</div>
                    <div className="text-xs text-muted-foreground">Failed</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : null}
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-3">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            <Link href="/predict" className="flex flex-col items-center justify-center gap-2 bg-secondary hover:bg-secondary/80 p-4 rounded-xl transition-colors border border-border">
              <Zap className="w-6 h-6 text-primary" />
              <span className="text-sm font-medium">New Prediction</span>
            </Link>
            <Link href="/result" className="flex flex-col items-center justify-center gap-2 bg-secondary hover:bg-secondary/80 p-4 rounded-xl transition-colors border border-border">
              <FileEdit className="w-6 h-6 text-primary" />
              <span className="text-sm font-medium">Save Result</span>
            </Link>
          </div>
        </section>

        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Recent Predictions</h2>
            <Link href="/tracker" className="text-sm text-primary flex items-center gap-1">
              View All <Activity className="w-3 h-3" />
            </Link>
          </div>
          
          <div className="space-y-3">
            {predsLoading ? (
              [1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full rounded-xl" />)
            ) : recentPredictions.length > 0 ? (
              recentPredictions.map((pred, i) => (
                <Card key={i} className="bg-card">
                  <CardContent className="p-4 flex items-center justify-between">
                    <div>
                      <div className="font-medium">{pred.gameDate}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {pred.matched?.length ? `Matched: ${pred.matched.join(', ')}` : "No matches yet"}
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`inline-block px-2 py-1 rounded-md text-xs font-bold ${
                        pred.status === 'PASS_L1' ? 'bg-green-500/20 text-green-500' :
                        pred.status === 'PASS_L2' ? 'bg-blue-500/20 text-blue-500' :
                        pred.status === 'PASS_L3' ? 'bg-yellow-500/20 text-yellow-500' :
                        pred.status === 'FAIL' ? 'bg-red-500/20 text-red-500' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {pred.status.replace('_', ' ')}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="text-center py-6 text-muted-foreground text-sm bg-card rounded-xl border border-border">
                No recent predictions found.
              </div>
            )}
          </div>
        </section>
      </div>
    </Layout>
  );
}
