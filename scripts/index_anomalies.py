# .github/scripts/index_anomalies.py
import os, base64, json, datetime, requests, sys

ES_URL   = os.getenv("ES_URL", "https://localhost:9200").rstrip("/")
ES_INDEX = os.getenv("ES_INDEX", "anomalies-capstone")
API_ID   = os.getenv("ES_API_ID")
API_KEY  = os.getenv("ES_API_KEY")
JSONL    = os.getenv("ANOMALIES_JSONL", "")

if not (API_ID and API_KEY):
    print("ERROR: ES_API_ID and/or ES_API_KEY not set in env.")
    sys.exit(2)

auth_b64 = base64.b64encode(f"{API_ID}:{API_KEY}".encode()).decode()
HEADERS = {"Authorization": f"ApiKey {auth_b64}", "Content-Type": "application/json"}

def post(doc: dict):
    doc.setdefault("@timestamp", datetime.datetime.utcnow().isoformat() + "Z")
    r = requests.post(f"{ES_URL}/{ES_INDEX}/_doc", headers=HEADERS, json=doc,
                      timeout=10, verify=False)  # verify=False for self-signed TLS
    r.raise_for_status()

def main():
    sent = 0
    if JSONL and os.path.exists(JSONL):
        with open(JSONL, "r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    post(json.loads(line))
                    sent += 1
                except Exception as e:
                    print("WARN: skipping line:", e)
        print(f"Indexed {sent} docs from {JSONL}")
        return

    # Smoke test: one fake anomaly so you can see it in Discover
    doc = {
        "src_ip":"10.0.0.5","dst_ip":"54.66.123.1",
        "src_port":51512,"dst_port":443,"proto":"tcp",
        "score":0.97,"label":"malicious",
        "features":{"conn_state":"S0","duration":0.0}
    }
    post(doc)
    print("Indexed 1 smoke-test doc")

if __name__ == "__main__":
    main()
