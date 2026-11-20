# Sahil Master System

Lottery jodi prediction system — FD/GB/GL/DS games.

Python (Flask) service: `sahil_system/` engine + `sahil_system/static/index.html` web UI.
Purana React/Express code `artifacts/` me padha hai (adhura export, build nahi hota).

## Data kahan rehta hai
`sahil_system/lifetime_record.txt` (format `YYYY-MM-DD | FD GB GL DS`, DS = us date ke agle din subah ka Desawar),
`prediction_history.json`, `pending_result.json`. Site se likhne par ye GitHub me commit hote hain
(Render free par disk restart par mit jaata hai).

## Local chalana
```
pip install -r requirements.txt
cd sahil_system && python3 server.py        # http://localhost:5000, GITHUB_TOKEN nahi to local files
```

## Render par deploy
1. GitHub: Settings → Developer settings → Fine-grained token → sirf is repo, `Contents: Read and write`.
2. Render: New → Blueprint → is repo ko chuno (`render.yaml` apne aap padh lega).
3. Env vars: `GITHUB_TOKEN` (upar wala token), `ADMIN_PIN` (apna PIN). Token/PIN kabhi repo me mat likhna.
4. Site khulne par record dekhna sabko dikhta hai; likhne (result, prediction) ke liye PIN lagta hai.
