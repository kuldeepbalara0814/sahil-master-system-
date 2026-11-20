#!/data/data/com.termux/files/usr/bin/bash
# Phone se: abhi site se result laao -> data update -> GitHub par push -> phone ke folder me backup.
# Chalane ke liye:  bash fetch_now.sh        (pehli baar repo apne aap clone ho jayegi)
set -e
REPO_DIR="${SAHIL_LAB_DIR:-$HOME/sahil-lab}"
BACKUP="${SAHIL_BACKUP:-/sdcard/SahilLab_Data}"
REMOTE="${SAHIL_REMOTE:-git@github.com:kuldeepbalara0814/sahil-master-system-.git}"
BRANCH="${SAHIL_BRANCH:-main}"
[ -d "$REPO_DIR/.git" ] || git clone -b "$BRANCH" "$REMOTE" "$REPO_DIR"
cd "$REPO_DIR"
git pull --ff-only origin "$BRANCH"
python3 -m pip install -q -r requirements.txt
python3 -m lab.update
mkdir -p "$BACKUP"
cp data/results.csv "$BACKUP/results.csv"
cp data/paper_ledger.json data/monitor.json data/drift_log.json "$BACKUP/" 2>/dev/null || true
git add data
if git diff --cached --quiet; then echo "GitHub par kuch naya nahi"; else
  git commit -q -m "manual: fetch from phone $(date +%F)"
  git push origin "$BRANCH"
  echo "GitHub par push ho gaya"
fi
echo "Backup: $BACKUP/results.csv"
