import os, json, sys
from kb import build_index
base=os.environ.get("MARIA_HOME", os.getcwd())
globs=[
    "insights/**/*.md",
    "insights/**/*.jsonl",
    "artifacts/reports/**/*.md",
    "artifacts/chat/*.jsonl",
    "artifacts/lessons.jsonl",
    "project_manifest.md"
]
out="artifacts/kb/index.json"
p=build_index(base, globs, out)
print(p)
