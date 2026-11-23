import sys,csv,datetime as dt,time; sys.path.insert(0,'../../../scripts')
import importlib.util
sp=importlib.util.spec_from_file_location('f','../../../scripts/fetch_ds_history.py'); f=importlib.util.module_from_spec(sp); sp.loader.exec_module(f)
rows={}
for y in range(2013,2027):
    g=f.parse(f.fetch(y),y); rows.update(g); print(y,len(g),flush=True); time.sleep(1.2)
with open('../out/ds_site2_2013_2026.csv','w') as o:
    w=csv.writer(o); w.writerow(['line_date','ds'])
    for d in sorted(rows): w.writerow([(d-dt.timedelta(days=1)).isoformat(),rows[d]])
