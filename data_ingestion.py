"""Day 1 ingestion and profiling for the mutual-fund analytics project."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports"
EXPECTED_DATASETS = 10


def read_csv_safely(path: Path) -> pd.DataFrame:
    """Read CSV while preserving AMFI codes as numeric-friendly values."""
    return pd.read_csv(path, low_memory=False)


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    return None


def profile_dataset(path: Path, df: pd.DataFrame) -> dict:
    print(f"\n{'=' * 90}\nFILE: {path.name}\nSHAPE: {df.shape}\nDTYPES:\n{df.dtypes}\nHEAD:\n{df.head().to_string(index=False)}")
    missing = df.isna().sum()
    duplicate_rows = int(df.duplicated().sum())
    anomalies = []
    if duplicate_rows:
        anomalies.append(f"{duplicate_rows} duplicate row(s)")
    missing_cols = {str(k): int(v) for k, v in missing.items() if v}
    if missing_cols:
        anomalies.append(f"missing values by column: {missing_cols}")
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if (df[col].dropna() < 0).any() and any(t in str(col).lower() for t in ["nav", "amount", "aum", "inflow", "weight", "folio", "price"]):
                anomalies.append(f"negative values in numeric field '{col}'")
    print("ANOMALIES:", "; ".join(anomalies) if anomalies else "No basic anomalies detected")
    return {
        "file": path.name, "rows": int(df.shape[0]), "columns": int(df.shape[1]),
        "duplicate_rows": duplicate_rows, "missing_values": int(df.isna().sum().sum()),
        "missing_by_column": missing_cols, "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "anomalies": anomalies,
    }


def inspect_fund_master(master: pd.DataFrame) -> dict:
    print("\nFUND MASTER ANALYSIS")
    results = {}
    for col in ["fund_house", "category", "sub_category", "risk_category", "risk_grade"]:
        actual = find_column(master, [col])
        if actual:
            vals = sorted(master[actual].dropna().astype(str).unique().tolist())
            results[actual] = vals
            print(f"Unique {actual} ({len(vals)}): {vals}")
    code_col = find_column(master, ["amfi_code", "scheme_code", "scheme code", "code"])
    if code_col:
        codes = pd.to_numeric(master[code_col], errors="coerce")
        invalid = int(codes.isna().sum())
        duplicates = int(codes.dropna().duplicated().sum())
        print(f"AMFI code column: {code_col}; unique numeric codes: {codes.nunique()}; invalid values: {invalid}; duplicate codes: {duplicates}")
        results["amfi_code_quality"] = {"column": code_col, "unique_numeric_codes": int(codes.nunique()), "invalid_values": invalid, "duplicate_codes": duplicates}
    return results


def validate_codes(frames: dict[str, pd.DataFrame]) -> dict:
    master_key = next((k for k in frames if "fund_master" in k.lower()), None)
    nav_key = next((k for k in frames if "nav_history" in k.lower()), None)
    if not master_key or not nav_key:
        return {"status": "not_run", "reason": "fund_master or nav_history CSV not found"}
    master, nav = frames[master_key], frames[nav_key]
    mc = find_column(master, ["amfi_code", "scheme_code", "scheme code", "code"])
    nc = find_column(nav, ["amfi_code", "scheme_code", "scheme code", "code"])
    if not mc or not nc:
        return {"status": "not_run", "reason": "AMFI code column not found", "master_file": master_key, "nav_file": nav_key}
    master_codes = set(pd.to_numeric(master[mc], errors="coerce").dropna().astype("int64"))
    nav_codes = set(pd.to_numeric(nav[nc], errors="coerce").dropna().astype("int64"))
    missing = sorted(master_codes - nav_codes)
    extra = sorted(nav_codes - master_codes)
    result = {"status": "pass" if not missing else "fail", "master_file": master_key, "nav_file": nav_key,
              "master_unique_codes": len(master_codes), "nav_unique_codes": len(nav_codes),
              "matched_codes": len(master_codes & nav_codes), "master_codes_missing_from_nav_history": missing,
              "nav_codes_not_in_master": extra}
    print("\nAMFI CODE VALIDATION\n" + json.dumps(result, indent=2))
    return result


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(p for p in RAW_DIR.glob("*.csv") if not p.name.startswith("live_nav_"))
    if not paths:
        raise FileNotFoundError(f"No input CSVs found in {RAW_DIR}. Put the 10 provided CSV datasets there.")
    if len(paths) != EXPECTED_DATASETS:
        print(f"WARNING: expected {EXPECTED_DATASETS} provided CSVs; found {len(paths)} CSV(s) in {RAW_DIR}.")
    frames, profiles = {}, []
    for path in paths:
        try:
            df = read_csv_safely(path)
            frames[path.name] = df
            profiles.append(profile_dataset(path, df))
        except Exception as exc:
            profiles.append({"file": path.name, "read_error": repr(exc)})
            print(f"ERROR reading {path.name}: {exc}")
    master_key = next((k for k in frames if "fund_master" in k.lower()), None)
    fund_analysis = inspect_fund_master(frames[master_key]) if master_key else {"warning": "fund_master file not found"}
    validation = validate_codes(frames)
    summary = {
        "datasets_found": len(paths), "datasets_read_successfully": len(frames),
        "dataset_profiles": profiles, "fund_master_analysis": fund_analysis,
        "amfi_code_validation": validation,
        "amfi_code_note": "AMFI scheme codes are identifiers assigned to schemes, typically numeric strings/integers. Treat them as identifiers, not quantities; do not infer AMC/category from the digits. One fund house may have many scheme codes, and regular/direct or growth/IDCW variants can have distinct codes.",
    }
    out = REPORT_DIR / "data_quality_summary.json"
    out.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    # Compact human-readable report for submission.
    lines = ["# Day 1 Data Quality Summary", "", f"- CSVs found: {len(paths)}", f"- CSVs read successfully: {len(frames)}", ""]
    for p in profiles:
        lines.append(f"## {p['file']}")
        if "read_error" in p:
            lines.append(f"- Read error: {p['read_error']}")
        else:
            lines += [f"- Shape: {p['rows']} rows × {p['columns']} columns", f"- Duplicate rows: {p['duplicate_rows']}", f"- Missing values: {p['missing_values']}", f"- Anomalies: {'; '.join(p['anomalies']) if p['anomalies'] else 'No basic anomalies detected'}"]
        lines.append("")
    lines += ["## AMFI code validation", "", "```json", json.dumps(validation, indent=2), "```", "", "## Code structure note", summary["amfi_code_note"]]
    (REPORT_DIR / "data_quality_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved reports: {REPORT_DIR / 'data_quality_summary.md'} and {out}")

if __name__ == "__main__":
    main()
