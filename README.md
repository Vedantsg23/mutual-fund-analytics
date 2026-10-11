# Mutual Fund Analytics — Day 1 Data Ingestion

## Project layout

```text
.
├── data/
│   ├── raw/          # 10 source CSVs and fetched MFAPI NAV snapshots
│   └── processed/   # reserved for validated/cleaned datasets
├── notebooks/
├── sql/
├── dashboard/
├── reports/          # generated data-quality reports
├── data_ingestion.py
├── live_nav_fetch.py
└── requirements.txt
```

## Setup and run

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python data_ingestion.py
python live_nav_fetch.py
python data_ingestion.py  # rerun if you want to profile the newly fetched files separately
```

The ingestion script reads each source CSV in `data/raw/`, prints shape, dtypes, head and basic anomaly checks, profiles fund-master dimensions, validates fund-master AMFI codes against `nav_history`, and writes Markdown/JSON reports under `reports/`.

The live fetcher requests the six scheme codes supplied for this task from `https://api.mfapi.in/mf/<scheme-code>` and saves NAV history as CSV files in `data/raw/`. Network access and the API must be available at runtime.

## AMFI scheme code notes

AMFI scheme codes are scheme identifiers. Treat them as identifiers rather than numeric measurements; do not infer fund house or category from the digits. Scheme variants (such as direct vs regular and growth vs IDCW) may have different codes. The `fund_master` dataset is the source of descriptive metadata; NAV history should be joined using the code field after normalizing both sides consistently.

## Git

The initial local commit is named `Day 1: Data ingestion complete`. To publish it, create an empty GitHub repository, then run:

```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY>.git
git push -u origin main
```

Do not put GitHub tokens/passwords in source files or commit history.
