import sys
import urllib.request
from prometheus_client.parser import text_string_to_metric_families

url, *required = sys.argv[1:]

try:
    with urllib.request.urlopen(url) as response:
        content = response.read().decode()
        metrics = {f.name for f in text_string_to_metric_families(content)}

    missing = set(required) - metrics
    if missing:
        print(f"Missing metrics: {missing}")
        print(f"Available: {metrics}")
        sys.exit(1)

except Exception:
    sys.exit(1)
