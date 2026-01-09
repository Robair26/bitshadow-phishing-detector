# link_scanner.py
import requests

def check_links(urls):
    results = {}
    for url in urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code in [200, 301, 302]:
                results[url] = "✅ Active"
            else:
                results[url] = "🚨 Unsafe"
        except Exception:
            results[url] = "🚨 Unsafe"
    return results
