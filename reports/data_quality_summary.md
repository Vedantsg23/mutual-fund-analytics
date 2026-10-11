# Day 1 Data Quality Summary

- CSVs found: 10
- CSVs read successfully: 10

## 1788499980509-304c1255-08_investor_transactions.csv
- Shape: 32778 rows × 13 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## 1788499982117-e3d6ab98-09_portfolio_holdings.csv
- Shape: 322 rows × 8 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## 1788499982615-f9647ab2-10_benchmark_indices.csv
- Shape: 8050 rows × 3 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## 1788499983024-b042c300-01_fund_master.csv
- Shape: 40 rows × 15 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## 1788499983331-4389156d-02_nav_history.csv
- Shape: 46000 rows × 3 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## 1788499984134-b0cbf625-03_aum_by_fund_house.csv
- Shape: 90 rows × 5 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## 1788499984405-d702a6c6-04_monthly_sip_inflows.csv
- Shape: 48 rows × 6 columns
- Duplicate rows: 0
- Missing values: 12
- Anomalies: missing values by column: {'yoy_growth_pct': 12}

## 1788499984721-4b860901-05_category_inflows.csv
- Shape: 144 rows × 3 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## 1788499985036-da4a0c4a-06_industry_folio_count.csv
- Shape: 21 rows × 6 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## 1788499985420-bb134abf-07_scheme_performance.csv
- Shape: 40 rows × 19 columns
- Duplicate rows: 0
- Missing values: 0
- Anomalies: No basic anomalies detected

## AMFI code validation

```json
{
  "status": "pass",
  "master_file": "1788499983024-b042c300-01_fund_master.csv",
  "nav_file": "1788499983331-4389156d-02_nav_history.csv",
  "master_unique_codes": 40,
  "nav_unique_codes": 40,
  "matched_codes": 40,
  "master_codes_missing_from_nav_history": [],
  "nav_codes_not_in_master": []
}
```

## Code structure note
AMFI scheme codes are identifiers assigned to schemes, typically numeric strings/integers. Treat them as identifiers, not quantities; do not infer AMC/category from the digits. One fund house may have many scheme codes, and regular/direct or growth/IDCW variants can have distinct codes.