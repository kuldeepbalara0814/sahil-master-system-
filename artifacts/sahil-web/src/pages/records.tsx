import { useState } from "react";
import { useGetRecords, useUpdateRecord } from "@workspace/api-client-react";
import { Layout } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Edit2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

export default function Records() {
  const { data: records, isLoading, refetch } = useGetRecords();
  const updateRecordMutation = useUpdateRecord();
  const { toast } = useToast();

  const [editingRecord, setEditingRecord] = useState<any>(null);
  const [editForm, setEditForm] = useState({ fd: "", gb: "", gl: "", ds: "" });

  const handleEditClick = (record: any) => {
    setEditingRecord(record);
    setEditForm({
      fd: record.fd.toString(),
      gb: record.gb.toString(),
      gl: record.gl.toString(),
      ds: record.ds.toString(),
    });
  };

  const handleUpdate = () => {
    if (!editingRecord) return;

    updateRecordMutation.mutate({
      date: editingRecord.date,
      data: {
        date: editingRecord.date,
        fd: Number(editForm.fd),
        gb: Number(editForm.gb),
        gl: Number(editForm.gl),
        ds: Number(editForm.ds),
      }
    }, {
      onSuccess: () => {
        toast({ title: "Success", description: "Record update ho gaya!" });
        setEditingRecord(null);
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Error", description: err?.message || "Update nahi ho paya", variant: "destructive" });
      }
    });
  };

  return (
    <Layout title="Records History">
      <div className="space-y-4">
        {isLoading ? (
          <div className="flex justify-center p-8">
            <Loader2 className="animate-spin w-8 h-8 text-primary" />
          </div>
        ) : records && records.length > 0 ? (
          <div className="overflow-hidden rounded-xl border border-border bg-card">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs uppercase bg-secondary text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3 text-center">FD</th>
                    <th className="px-4 py-3 text-center">GB</th>
                    <th className="px-4 py-3 text-center">GL</th>
                    <th className="px-4 py-3 text-center">DS</th>
                    <th className="px-4 py-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((record) => (
                    <tr key={record.date} className="border-b border-border/50 hover:bg-secondary/50">
                      <td className="px-4 py-3 font-medium whitespace-nowrap">{record.date}</td>
                      <td className="px-4 py-3 text-center font-mono">{record.fd.toString().padStart(2, '0')}</td>
                      <td className="px-4 py-3 text-center font-mono">{record.gb.toString().padStart(2, '0')}</td>
                      <td className="px-4 py-3 text-center font-mono">{record.gl.toString().padStart(2, '0')}</td>
                      <td className="px-4 py-3 text-center font-mono">{record.ds.toString().padStart(2, '0')}</td>
                      <td className="px-4 py-3 text-center">
                        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => handleEditClick(record)}>
                          <Edit2 className="w-3 h-3" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground bg-card rounded-xl border border-border">
            Koi purana record nahi mila.
          </div>
        )}

        <Dialog open={!!editingRecord} onOpenChange={(open) => !open && setEditingRecord(null)}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Edit Record: {editingRecord?.date}</DialogTitle>
            </DialogHeader>
            <div className="grid grid-cols-4 gap-4 py-4">
              <div className="space-y-2">
                <Label>FD</Label>
                <Input type="number" value={editForm.fd} onChange={e => setEditForm({...editForm, fd: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>GB</Label>
                <Input type="number" value={editForm.gb} onChange={e => setEditForm({...editForm, gb: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>GL</Label>
                <Input type="number" value={editForm.gl} onChange={e => setEditForm({...editForm, gl: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label>DS</Label>
                <Input type="number" value={editForm.ds} onChange={e => setEditForm({...editForm, ds: e.target.value})} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setEditingRecord(null)}>Cancel</Button>
              <Button onClick={handleUpdate} disabled={updateRecordMutation.isPending}>
                {updateRecordMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Update
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
}
