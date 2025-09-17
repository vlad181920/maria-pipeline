import json
print(json.dumps({
  "chat_pairs_added_expected": 10,
  "chat_lines_before": 0,
  "chat_lines_after": 10,
  "chat_lines_delta": 10,
  "processed_thoughts_delta": 0,
  "qa_todos_delta": 0
}, ensure_ascii=False, indent=2))
