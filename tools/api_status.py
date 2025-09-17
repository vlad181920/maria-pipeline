#!/usr/bin/env python3
import urllib.request, os
port = int((open("artifacts/logs/web_learn.port").read().strip()) if os.path.exists("artifacts/logs/web_learn.port") else 8765)
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
print(opener.open(f"http://127.0.0.1:{port}/status", timeout=5).read().decode())
