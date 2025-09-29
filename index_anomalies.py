import os, base64, json, datetime, requests

ES_URL   = os.getenv("ES_URL", "https://localhost:9200").rstrip("/")
ES_INDEX = os.getenv("ES_INDEX", "anomalies-capstone")
API_ID   = os.getenv("ES_API_ID")
API_KEY  = os.getenv("ES_API_KEY")
AUTH_HDR = {
    "Authorization": "ApiKey " + base64.b64encode(f"{API_ID}:{API_KEY}".encode()).decode(),
    "Content-Type": "application/json"
}

def post(doc: dict):
    doc.setdefault("@timestamp", datetime.datetime.utcnow().isoformat() + "Z")
    r = requests.post(f"{ES_URL}/{ES_INDEX}/_doc", headers=AUTH_HDR, json=doc, timeout=5, verify=False)
    r.raise_for_status()

def main():
    #Option B - index many from a JSONL file if you produce one in your build
    path = os.getenv("ANOMALIES_JSONL", "")
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    post(json.loads(line))
                except Exception as e:
                    print("skip bad line:", e)

if __name__ == "__main__":
    main()
