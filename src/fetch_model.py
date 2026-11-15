import hashlib
import sys
import time
import urllib.request
from pathlib import Path

URL = "https://chroma-onnx-models.s3.amazonaws.com/all-MiniLM-L6-v2/onnx.tar.gz"
SHA256 = "913d7300ceae3b2dbc2c50d1de4baacab4be7b9380491c27fab7418616a16ec3"
DEST = Path.home() / ".cache" / "chroma" / "onnx_models" / "all-MiniLM-L6-v2" / "onnx.tar.gz"


def is_ready():
    return DEST.exists() and hashlib.sha256(DEST.read_bytes()).hexdigest() == SHA256


DEST.parent.mkdir(parents=True, exist_ok=True)
for attempt in range(1, 8):
    if is_ready():
        print("embedding model archive is ready")
        sys.exit(0)
    try:
        print(f"download attempt {attempt}")
        with urllib.request.urlopen(URL, timeout=120) as response, open(DEST, "wb") as out:
            while chunk := response.read(1 << 20):
                out.write(chunk)
    except Exception as exc:
        print("attempt failed:", exc)
        time.sleep(5)

if not is_ready():
    sys.exit("could not download the embedding model")
print("embedding model archive is ready")