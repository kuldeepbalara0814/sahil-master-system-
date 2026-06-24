import { useState, useRef } from "react";
import { useRunPrediction } from "@workspace/api-client-react";
import { Layout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Zap, Loader2 } from "lucide-react";
import { format } from "date-fns";

const FORMULAS = [
  { id: "2", label: "2 - Evergreen" },
  { id: "3", label: "3 - Universal" },
  { id: "4", label: "4 - Magic" },
  { id: "5", label: "5 - Day Fix" },
  { id: "6", label: "6 - Murda" },
  { id: "7", label: "7 - Haruf" },
  { id: "8", label: "8 - Baki" },
  { id: "9", label: "9 - Month Trend" },
];

export default function Predict() {
  const { toast } = useToast();
  const runPredictionMutation = useRunPrediction();

  const [date, setDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [fd, setFd] = useState("");
  const [gb, setGb] = useState("");
  const [gl, setGl] = useState("");
  const [ds, setDs] = useState("");
  
  const [selectedFormulas, setSelectedFormulas] = useState<string[]>(FORMULAS.map(f => f.id));
  const [result, setResult] = useState<any>(null);

  const toggleFormula = (id: string) => {
    setSelectedFormulas(prev => 
      prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]
    );
  };

  const handlePredict = () => {
    if (!fd || !gb || !gl || !ds) {
      toast({ title: "Error", description: "Sare numbers daalna zaroori hai (0-99)", variant: "destructive" });
      return;
    }

    if (selectedFormulas.length === 0) {
      toast({ title: "Error", description: "Kam se kam ek formula select karein", variant: "destructive" });
      return;
    }

    runPredictionMutation.mutate(
      {
        data: {
          gameDate: date,
          fd: Number(fd),
          gb: Number(gb),
          gl: Number(gl),
          ds: Number(ds),
          formula: selectedFormulas
        }
      },
      {
        onSuccess: (data) => {
          setResult(data);
          toast({ title: "Success", description: "Prediction tayar hai!" });
        },
        onError: (err: any) => {
          toast({ title: "Error", description: err?.message || "Kuch galat hua", variant: "destructive" });
        }
      }
    );
  };

  return (
    <Layout title="Aaj ki Prediction">
      <div className="space-y-6">
        
        <Card className="bg-card">
          <CardHeader>
            <CardTitle>Numbers Input Karo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Date</Label>
              <Input type="date" value={date} onChange={e => setDate(e.target.value)} />
            </div>
            
            <div className="grid grid-cols-4 gap-2">
              <div className="space-y-2">
                <Label className="text-xs text-center block">FD</Label>
                <Input type="number" min="0" max="99" value={fd} onChange={e => setFd(e.target.value)} className="text-center px-1" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs text-center block">GB</Label>
                <Input type="number" min="0" max="99" value={gb} onChange={e => setGb(e.target.value)} className="text-center px-1" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs text-center block">GL</Label>
                <Input type="number" min="0" max="99" value={gl} onChange={e => setGl(e.target.value)} className="text-center px-1" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs text-center block">DS</Label>
                <Input type="number" min="0" max="99" value={ds} onChange={e => setDs(e.target.value)} className="text-center px-1" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardHeader>
            <CardTitle>Formulas Select Karo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {FORMULAS.map((f) => (
                <div key={f.id} className="flex items-center space-x-2">
                  <Checkbox 
                    id={`formula-${f.id}`} 
                    checked={selectedFormulas.includes(f.id)}
                    onCheckedChange={() => toggleFormula(f.id)}
                  />
                  <Label htmlFor={`formula-${f.id}`} className="text-sm font-medium cursor-pointer">
                    {f.label}
                  </Label>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Button 
          className="w-full h-12 text-lg font-bold" 
          onClick={handlePredict}
          disabled={runPredictionMutation.isPending}
        >
          {runPredictionMutation.isPending ? <Loader2 className="animate-spin mr-2" /> : <Zap className="mr-2" />}
          Predict Numbers
        </Button>

        {result && (
          <div className="space-y-6 pt-4 pb-8 animate-in fade-in slide-in-from-bottom-4">
            <h2 className="text-2xl font-bold text-center text-primary">Prediction Result</h2>
            
            <Card className="bg-card border-green-500/50 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
              <CardHeader className="bg-green-500/10 pb-2">
                <CardTitle className="text-green-500">L1 - Super VIP (4 Jodis)</CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="flex flex-wrap gap-2">
                  {result.L1.map((jodi: string) => (
                    <span key={jodi} className="bg-green-500/20 text-green-400 font-mono text-lg px-3 py-1 rounded-md font-bold">
                      {jodi}
                    </span>
                  ))}
                  {result.L1.length === 0 && <span className="text-muted-foreground text-sm">Koi number nahi</span>}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
              <CardHeader className="bg-blue-500/10 pb-2">
                <CardTitle className="text-blue-500">L2 - Main (10 Jodis)</CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="flex flex-wrap gap-2">
                  {result.L2.map((jodi: string) => (
                    <span key={jodi} className="bg-blue-500/20 text-blue-400 font-mono px-3 py-1 rounded-md font-medium">
                      {jodi}
                    </span>
                  ))}
                  {result.L2.length === 0 && <span className="text-muted-foreground text-sm">Koi number nahi</span>}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-yellow-500/50 shadow-[0_0_15px_rgba(234,179,8,0.1)]">
              <CardHeader className="bg-yellow-500/10 pb-2">
                <CardTitle className="text-yellow-500">L3 - Support (16 Jodis)</CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="flex flex-wrap gap-2">
                  {result.L3.map((jodi: string) => (
                    <span key={jodi} className="bg-yellow-500/20 text-yellow-500 font-mono px-2 py-1 rounded text-sm">
                      {jodi}
                    </span>
                  ))}
                  {result.L3.length === 0 && <span className="text-muted-foreground text-sm">Koi number nahi</span>}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card">
              <CardHeader>
                <CardTitle className="text-sm">Tokari Counts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-5 sm:grid-cols-8 gap-2">
                  {result.tokari.map((item: any) => (
                    <div key={item.jodi} className="flex flex-col items-center bg-secondary p-1 rounded">
                      <span className="font-mono font-bold">{item.jodi}</span>
                      <span className="text-[10px] text-muted-foreground">{item.count}x</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

          </div>
        )}

      </div>
    </Layout>
  );
}
