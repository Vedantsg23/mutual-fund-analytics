# Mutual Fund Analytics

A Python-based data ingestion project for exploring mutual fund datasets and retrieving live Net Asset Value (NAV) history using the MFAPI API.

## Project Objectives

* Load and inspect mutual fund datasets using Pandas.
* Examine fund houses, categories, subcategories, and risk classifications.
* Validate scheme codes between the fund master and NAV history datasets.
* Fetch and validate live NAV history for six large-cap mutual fund schemes.
* Generate data-quality reports.

## Tech Stack

* Python
* Pandas
* NumPy
* Requests
* Matplotlib
* Seaborn
* Plotly
* SQLAlchemy
* SciPy
* Jupyter Notebook

## Project Structure

```text
mf_ingestion/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── sql/
├── dashboard/
├── reports/
├── data_ingestion.py
├── live_nav_fetch.py
├── find_scheme_codes.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Ingestion

Run the main dataset inspection script:

```bash
python data_ingestion.py
```

The script loads the supplied CSV datasets, inspects their structures, and generates data-quality reports.

## Live NAV Ingestion

Run:

```bash
python live_nav_fetch.py
```

The script retrieves NAV history for six mutual fund schemes, validates the returned scheme codes and names, and saves valid records as CSV files.

Invalid NAV records are preserved separately for auditing.

## Installation

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Data Quality

The project includes checks for missing values, invalid NAV values, scheme-name mismatches, and consistency between fund master and NAV history codes.

## Disclaimer

This project is for educational and analytical purposes only. It does not provide investment advice.
