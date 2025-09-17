import subprocess, json, os
home = os.environ["MARIA_HOME"]
out = subprocess.check_output(["bash","-lc", f'maria chat "де фіксувати зміни по маніфесту?"'], text=True)
ok = "Next step:" in out
print(json.dumps({"has_next_step": ok, "sample_reply": out.splitlines()[-1]}, ensure_ascii=False, indent=2))
