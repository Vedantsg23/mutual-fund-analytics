import requests
import time

API_URL = "https://api.mfapi.in/mf/search"

SEARCH_TERMS = [
    "HDFC Top 100 Fund",
    "HDFC Top 100 Direct Growth",
    "HDFC Top 100 Plan Growth",
    "SBI Large Cap Fund",
    "SBI Large Cap Direct Growth",
    "SBI Bluechip Fund Direct Growth",
]
def main():
    with requests.Session() as session:
        for term in SEARCH_TERMS:
            print("\n" + "=" * 70)
            print("SEARCH:", term)
            print("=" * 70)

            try:
                response = session.get(
                    API_URL,
                    params={"q": term},
                    timeout=30
                )
                response.raise_for_status()
                results = response.json()

                if not isinstance(results, list) or not results:
                    print("No results found.")
                    continue

                preferred = [
                    item for item in results
                    if "direct" in item.get("schemeName", "").lower()
                    and "growth" in item.get("schemeName", "").lower()
                ]

                candidates = preferred if preferred else results

                for item in candidates[:15]:
                    print(
                        "Code:", item.get("schemeCode"),
                        "| Name:", item.get("schemeName")
                    )

            except (requests.RequestException, ValueError) as exc:
                print("Search failed:", exc)

            time.sleep(0.5)

    print("\nSearch complete.")

if __name__ == "__main__":
    main()
