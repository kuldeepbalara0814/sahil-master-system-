import { useState } from "react";
import { useAddRecord, useSavePendingEntry, useGetPending, useCheckPrediction, getGetPredictionsQueryKey, getGetStatsQueryKey } from "@workspace/api-client-react";
import { Layout } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { Save, Loader2, RefreshCw } from "lucide-react";

export default function Result() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { data: pendingEntries, refetch: refetchPending, isLoading: pendingLoading } = useGetPending();
  const addRecordMutation = useAddRecord();
  const savePendingMutation = useSavePendingEntry();
  const checkPredictionMutation = useCheckPrediction();

  const refreshTrackerAndStats = () => {
    queryClient.invalidateQueries({ queryKey: getGetPredictionsQueryKey() });
    queryClient.invalidateQueries({ queryKey: getGetStatsQueryKey() });
  };

  const [date, setDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [fd, setFd] = useState("");
  const [gb, setGb] = useState("");
  const [gl, setGl] = useState("");
  const [ds, setDs] = useState("");

  const handleSaveFull = () => {
    if (!fd || !gb || !gl || !ds) {
      toast({ title: "Error", description: "Sare numbers daalna zaroori hai full save ke liye", variant: "destructive" });
      return;
    }

    const fdN = Number(fd), gbN = Number(gb), glN = Number(gl), dsN = Number(ds);

    addRecordMutation.mutate(
      { data: { date, fd: fdN, gb: gbN, gl: glN, ds: dsN } },
      {
        onSuccess: () => {
          toast({ title: "Saved!", description: "Result save ho gaya — Pass/Fail check ho raha hai..." });
          setFd(""); setGb(""); setGl(""); setDs("");
          refetchPending();

          // Check prediction pass/fail and refresh tracker
          checkPredictionMutation.mutate(
            { data: { date, fd: fdN, gb: gbN, gl: glN, ds: dsN } },
            {
              onSuccess: (res) => {
                refreshTrackerAndStats();
                if (res.status === "PASS_L1") toast({ title: "PASS L1!", description: `Matched: ${res.matched?.join(", ")}` });
                else if (res.status === "PASS_L2") toast({ title: "PASS L2!", description: `Matched: ${res.matched?.join(", ")}` });
                else if (res.status === "PASS_L3") toast({ title: "PASS L3!", description: `Matched: ${res.matched?.join(", ")}` });
                else if (res.status === "FAIL") toast({ title: "FAIL", description: "Koi number match nahi hua.", variant: "destructive" });
                else refreshTrackerAndStats();
              },
              onError: () => refreshTrackerAndStats(),
            }
          );
        },
        onError: (err: any) => {
          toast({ title: "Error", description: err?.message || "Save nahi ho paya", variant: "destructive" });
        },
      }
    );
  };

  const handleSavePartial = (field: 'fd' | 'gb' | 'gl' | 'ds', valueStr: string) => {
    if (!valueStr) return;

    savePendingMutation.mutate(
      { data: { date, field, value: Number(valueStr) } },
      {
        onSuccess: (data) => {
          toast({ title: "Saved!", description: `${field.toUpperCase()} save ho gaya!` });
          refetchPending();

          if (data.complete && data.entry) {
            const e = data.entry;
            toast({ title: "Pura result aa gaya!", description: "Abhi record save karein." });

            // Auto-save full record and check prediction when all 4 arrive
            addRecordMutation.mutate(
              { data: { date, fd: e.fd ?? 0, gb: e.gb ?? 0, gl: e.gl ?? 0, ds: e.ds ?? 0 } },
              {
                onSuccess: () => {
                  checkPredictionMutation.mutate(
                    { data: { date, fd: e.fd ?? 0, gb: e.gb ?? 0, gl: e.gl ?? 0, ds: e.ds ?? 0 } },
                    {
                      onSuccess: (res) => {
                        refreshTrackerAndStats();
                        if (res.status?.startsWith("PASS")) toast({ title: `${res.status}!`, description: `Matched: ${res.matched?.join(", ")}` });
                        else if (res.status === "FAIL") toast({ title: "FAIL", description: "Koi match nahi.", variant: "destructive" });
                      },
                      onError: () => refreshTrackerAndStats(),
                    }
                  );
                },
                onError: () => {},
              }
            );
          }
        },
        onError: (err: any) => {
          toast({ title: "Error", description: err?.message || "Update nahi ho paya", variant: "destructive" });
        },
      }
    );
  };

  return (
    <Layout title="Result Save Karo">
      <div className="space-y-6">
        
        <Card className="bg-card">
          <CardHeader>
            <CardTitle>Aaj Ka Result</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Date</Label>
              <Input type="date" value={date} onChange={e => setDate(e.target.value)} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2 p-3 bg-secondary rounded-lg border border-border">
                <div className="flex justify-between items-center">
                  <Label>Faridabad (FD)</Label>
                  <Button size="sm" variant="ghost" className="h-6 px-2 text-xs" onClick={() => handleSavePartial('fd', fd)} disabled={!fd || savePendingMutation.isPending}>
                    Save
                  </Button>
                </div>
                <Input type="number" min="0" max="99" value={fd} onChange={e => setFd(e.target.value)} placeholder="00" className="text-center font-mono text-lg" />
              </div>

              <div className="space-y-2 p-3 bg-secondary rounded-lg border border-border">
                <div className="flex justify-between items-center">
                  <Label>Ghaziabad (GB)</Label>
                  <Button size="sm" variant="ghost" className="h-6 px-2 text-xs" onClick={() => handleSavePartial('gb', gb)} disabled={!gb || savePendingMutation.isPending}>
                    Save
                  </Button>
                </div>
                <Input type="number" min="0" max="99" value={gb} onChange={e => setGb(e.target.value)} placeholder="00" className="text-center font-mono text-lg" />
              </div>

              <div className="space-y-2 p-3 bg-secondary rounded-lg border border-border">
                <div className="flex justify-between items-center">
                  <Label>Gali (GL)</Label>
                  <Button size="sm" variant="ghost" className="h-6 px-2 text-xs" onClick={() => handleSavePartial('gl', gl)} disabled={!gl || savePendingMutation.isPending}>
                    Save
                  </Button>
                </div>
                <Input type="number" min="0" max="99" value={gl} onChange={e => setGl(e.target.value)} placeholder="00" className="text-center font-mono text-lg" />
              </div>

              <div className="space-y-2 p-3 bg-secondary rounded-lg border border-border">
                <div className="flex justify-between items-center">
                  <Label>Desawar (DS)</Label>
                  <Button size="sm" variant="ghost" className="h-6 px-2 text-xs" onClick={() => handleSavePartial('ds', ds)} disabled={!ds || savePendingMutation.isPending}>
                    Save
                  </Button>
                </div>
                <Input type="number" min="0" max="99" value={ds} onChange={e => setDs(e.target.value)} placeholder="00" className="text-center font-mono text-lg" />
              </div>
            </div>

            <Button className="w-full mt-4" onClick={handleSaveFull} disabled={addRecordMutation.isPending}>
              {addRecordMutation.isPending ? <Loader2 className="animate-spin mr-2" /> : <Save className="mr-2" />}
              Save Full Day Result
            </Button>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Pending Results</h2>
            <Button variant="outline" size="sm" onClick={() => refetchPending()} className="h-8">
              <RefreshCw className="w-4 h-4 mr-1" /> Refresh
            </Button>
          </div>

          {pendingLoading ? (
            <div className="flex justify-center p-4"><Loader2 className="animate-spin" /></div>
          ) : pendingEntries && pendingEntries.length > 0 ? (
            <div className="space-y-3">
              {pendingEntries.map(entry => (
                <Card key={entry.date} className="bg-card">
                  <CardContent className="p-4 flex items-center justify-between">
                    <span className="font-bold">{entry.date}</span>
                    <div className="flex gap-2 font-mono text-sm">
                      <span className={entry.fd !== null ? "text-primary" : "text-muted-foreground"}>FD:{entry.fd ?? '-'}</span>
                      <span className={entry.gb !== null ? "text-primary" : "text-muted-foreground"}>GB:{entry.gb ?? '-'}</span>
                      <span className={entry.gl !== null ? "text-primary" : "text-muted-foreground"}>GL:{entry.gl ?? '-'}</span>
                      <span className={entry.ds !== null ? "text-primary" : "text-muted-foreground"}>DS:{entry.ds ?? '-'}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground bg-card rounded-xl border border-border">
              Koi pending result nahi hai. Sab up to date hai!
            </div>
          )}
        </div>

      </div>
    </Layout>
  );
}
