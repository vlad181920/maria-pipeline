#!/usr/bin/env bash
file="artifacts/todo_week_2025-09-02.md"
if [ -f "$file" ]; then
  sed -n '1,200p' "$file"
else
  echo "todo-файл не знайдено: $file"
fi
