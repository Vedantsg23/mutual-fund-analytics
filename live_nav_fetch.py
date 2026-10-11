from pathlib import Path
import time
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
API_BASE = "https://api.mfapi.in/mf/"

SCHEMES = {
    "hdfc_top_100_direct": ("119018", ["hdfc", "large cap"]),
    "sbi_bluechip": ("119598", ["sbi", "large cap"]),
    "icici_bluechip": ("120586", ["icici prudential", "large cap"]),
    "nippon_large_cap": ("118632", ["nippon india", "large cap"]),
    "axis_bluechip": ("120465", ["axis", "large cap"]),
    "kotak_bluechip": ("120152", ["kotak", "large cap"]),
}


def fetch_scheme(session, label, code, expected):
    response = session.get(API_BASE + code, timeout=30)
    response.raise_for_status()

    payload = response.json()
    meta = payload.get("meta") or {}
    records = payload.get("data") or []

    actual_code = str(meta.get("scheme_code", ""))
    actual_name = str(meta.get("scheme_name", ""))

    if actual_code != code:
        raise ValueError(f"Code mismatch: requested {code}, received {actual_code}")

    if not actual_name or not all(
        term.casefold() in actual_name.casefold()
        for term in expected
    ):
        raise ValueError(f"Scheme mismatch: {actual_name}")

    if not records:
        raise ValueError(f"No NAV records for {actual_name}")

    df = pd.DataFrame(records)

    if not {"date", "nav"}.issubset(df.columns):
        raise ValueError("Missing date or nav columns")

    df["date"] = pd.to_datetime(
        df["date"], format="%d-%m-%Y", errors="coerce"
    )
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    invalid_mask = (
        df["date"].isna()
        | df["nav"].isna()
        | (df["nav"] <= 0)
    )

    invalid_records = df.loc[invalid_mask].copy()
    df = df.loc[~invalid_mask].copy()

    if not invalid_records.empty:
        invalid_output = RAW_DIR / f"invalid_nav_{label}_{code}.csv"
        invalid_records.to_csv(invalid_output, index=False)
        print(
            f"WARNING: {len(invalid_records)} invalid record(s) "
            f"saved to {invalid_output.name}"
        )

    if df.empty:
        raise ValueError(f"No valid NAV records for {actual_name}")

    df.insert(0, "amfi_code", actual_code)
    df.insert(1, "scheme_name", actual_name)
    df["fetched_at_utc"] = pd.Timestamp.now(tz="UTC").isoformat()

    output = RAW_DIR / f"live_nav_{label}_{code}.csv"
    df.to_csv(output, index=False)

    print(
        f"VALIDATED: {label} | code={code} | "
        f"scheme={actual_name} | valid_rows={len(df):,} | "
        f"invalid_rows={len(invalid_records):,} | file={output.name}"
    )


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    failures = []

    with requests.Session() as session:
        for label, (code, expected) in SCHEMES.items():
            try:
                fetch_scheme(session, label, code, expected)
            except (requests.RequestException, ValueError, KeyError) as exc:
                failures.append(f"{label} [{code}]: {exc}")
                print(f"FAILED: {failures[-1]}")

            time.sleep(0.5)

    if failures:
        print("\nFailed schemes:")
        for failure in failures:
            print("-", failure)
        raise SystemExit("NAV ingestion incomplete.")

    print("\nSUCCESS: All six schemes passed validation.")


if __name__ == "__main__":
    main()
