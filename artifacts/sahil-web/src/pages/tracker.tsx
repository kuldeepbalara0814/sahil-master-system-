import { useGetPredictions } from "@workspace/api-client-react";
import { Layout } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2 } from "lucide-react";

export default function Tracker() {
  const { data: predictions, isLoading } = useGetPredictions();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PASS_L1': return 'bg-green-500/20 text-green-500 border-green-500/30';
      case 'PASS_L2': return 'bg-blue-500/20 text-blue-500 border-blue-500/30';
      case 'PASS_L3': return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30';
      case 'FAIL': return 'bg-red-500/20 text-red-500 border-red-500/30';
      case 'PENDING': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <Layout title="Pass/Fail Tracker">
      <div className="space-y-4">
        {isLoading ? (
          <div className="flex justify-center p-8">
            <Loader2 className="animate-spin w-8 h-8 text-primary" />
          </div>
        ) : predictions && predictions.length > 0 ? (
          predictions.map((pred) => (
            <Card key={pred.gameDate} className={`bg-card border ${getStatusColor(pred.status).split(' ')[2]}`}>
              <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-base font-bold">{pred.gameDate}</CardTitle>
                <div className={`px-2 py-1 rounded text-xs font-bold ${getStatusColor(pred.status)}`}>
                  {pred.status.replace('_', ' ')}
                </div>
              </CardHeader>
              <CardContent className="p-4 pt-0 space-y-3">
                
                {pred.actualResult && pred.actualResult.length > 0 && (
                  <div className="bg-secondary/50 p-2 rounded-md flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">Actual Result:</span>
                    <span className="font-mono font-bold tracking-widest">{pred.actualResult.join(' - ')}</span>
                  </div>
                )}

                {pred.matched && pred.matched.length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">Matched:</span>
                    <div className="flex gap-1">
                      {pred.matched.map(m => (
                        <span key={m} className="bg-primary/20 text-primary font-mono text-xs px-1.5 py-0.5 rounded font-bold">
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="space-y-1">
                    <div className="text-green-500 font-semibold mb-1">L1</div>
                    <div className="flex flex-wrap gap-1">
                      {pred.L1.map(j => (
                        <span key={j} className={`font-mono ${pred.matched?.includes(j) ? 'text-green-500 font-bold bg-green-500/20 px-1 rounded' : 'text-muted-foreground'}`}>{j}</span>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-blue-500 font-semibold mb-1">L2</div>
                    <div className="flex flex-wrap gap-1">
                      {pred.L2.map(j => (
                        <span key={j} className={`font-mono ${pred.matched?.includes(j) ? 'text-blue-500 font-bold bg-blue-500/20 px-1 rounded' : 'text-muted-foreground'}`}>{j}</span>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-yellow-500 font-semibold mb-1">L3</div>
                    <div className="flex flex-wrap gap-1">
                      {pred.L3.map(j => (
                        <span key={j} className={`font-mono ${pred.matched?.includes(j) ? 'text-yellow-500 font-bold bg-yellow-500/20 px-1 rounded' : 'text-muted-foreground'}`}>{j}</span>
                      ))}
                    </div>
                  </div>
                </div>

              </CardContent>
            </Card>
          ))
        ) : (
          <div className="text-center py-12 text-muted-foreground bg-card rounded-xl border border-border">
            Koi prediction history nahi mili.
          </div>
        )}
      </div>
    </Layout>
  );
}
