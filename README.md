# Sahil Lab  -  data, dost list, aaj ki list, paper trading

Paper trading (kalpnik paisa) aur R&D ke liye software. **Asli paisa lagane ki salaah nahi.**
Result lagbhag random hain; 13 saal ke test me sirf chhota, ghat-ta hua "number kuch din me dobara aata hai" wala asar mila.

## Kya kya hai  (index)
| # | Hissa | Kahan |
|---|---|---|
| 1 | Data (2013 se, duplicate-free) + roz auto fetch | `data/results.csv`, `lab/fetcher.py`, `lab/update.py`, `.github/workflows/daily.yml` |
| 2 | Dost Khojo (3 samay: poora, pichle 3 mahine, is mahina; hara/peela/narangi; drift) | `lab/friends.py` |
| 3 | Aaj ki List (single jodi + 10 number ki list) | `lab/picks.py` |
| 4 | Paper Trading + Monitor | `lab/paper.py`, `lab/monitor.py` |
| - | Web app | `lab_server.py`, `lab_static/index.html` (andar "Guide" tab me poori samjhaayi) |

## Roz ka kaam kaise chalta hai
1. **Subah 7:00 IST** GitHub Action `daily-update` chalta hai: site se kal ki poori line (DS subah 5:30 ko khulta hai), paper bet settle, aaj ki nayi paper bet, dost-list ka drift, monitor. Badla hua `data/` commit ho jaata hai.
2. **Manual:** web app ke "Data" tab me *Abhi result fetch karo* (PIN), ya GitHub > Actions > daily-update > *Run workflow*, ya phone se `bash scripts/fetch_now.sh`.
3. **Backup:** phone me `/sdcard/SahilLab_Data/` (results.csv ki copy). Bhari ho to Drive me move.

## Data ka niyam
FD GB GL usi tarikh ke. DS = agli subah khula Desawar, usi tarikh ki line me. Mahine ka aakhri din chhuti (us din ki line nahi).
`00` ko `0` likha hai. Site ke chart me DS us tarikh par dikhta hai jis subah khula; isliye `line(d).DS = site DS (d+1)`.

## Chalana
```
pip install -r requirements.txt
python -m unittest discover -s tests          # 24 test
python -m lab.update                          # fetch + paper + monitor
PORT=5000 LAB_SYNC=0 python lab_server.py     # web app (local)
```
Render: `render.yaml` (Blueprint). Env: `GITHUB_TOKEN` (Contents: Read and write, sirf is repo par) aur `ADMIN_PIN`.
