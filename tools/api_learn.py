#!/usr/bin/env python3
import sys, json, urllib.request, os
if len(sys.argv)<2:
    print("usage: tools/api_learn.py <url> [title]"); sys.exit(1)
url = sys.argv[1]; title = sys.argv[2] if len(sys.argv)>2 else url
port = int((open("artifacts/logs/web_learn.port").read().strip()) if os.path.exists("artifacts/logs/web_learn.port") else 8765)
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
data = json.dumps({"url": url, "title": title}).encode()
req = urllib.request.Request(f"http://127.0.0.1:{port}/learn", data=data, headers={"Content-Type":"application/json"})
print(opener.open(req, timeout=20).read().decode())
