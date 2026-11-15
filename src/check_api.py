import os
import sys

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
KEY = os.environ.get("DOC_ASSISTANT_API_KEY", "")
QUESTION = "How many days of annual leave do I get?"

if not KEY:
    sys.exit("Set DOC_ASSISTANT_API_KEY first (the same key the server was started with).")


def post(question, key):
    headers = {"x-api-key": key} if key else {}
    return httpx.post(f"{BASE}/ask", json={"question": question}, headers=headers, timeout=180)


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"   ({detail})" if detail else ""))
    return ok


results = []

r = httpx.get(f"{BASE}/health", timeout=30)
results.append(check("health endpoint", r.status_code == 200, r.text))

r = post(QUESTION, "")
results.append(check("no key is rejected", r.status_code == 401, f"status {r.status_code}"))

r = post(QUESTION, "wrong-key")
results.append(check("wrong key is rejected", r.status_code == 401, f"status {r.status_code}"))

r = post(QUESTION, KEY)
data = r.json() if r.status_code == 200 else {}
results.append(check("valid key gets the right answer", r.status_code == 200 and "21" in data.get("answer", ""),
                     data.get("answer", f"status {r.status_code}")[:80]))

r = post("What is the company dress code?", KEY)
data = r.json() if r.status_code == 200 else {}
results.append(check("out-of-scope question is refused", r.status_code == 200 and data.get("refused") is True,
                     data.get("answer", f"status {r.status_code}")[:80]))

print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)