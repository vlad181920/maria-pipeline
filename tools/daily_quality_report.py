#!/usr/bin/env python3
import os, json, datetime, re, glob
HOME=os.environ.get("MARIA_HOME", os.path.expanduser("~/Desktop/Марія"))
LOG=os.path.join(HOME,"artifacts","logs","brain_core.log")
today=datetime.date.today().isoformat()
events=[]
if os.path.exists(LOG):
    for line in open(LOG,"r",encoding="utf-8"):
        line=line.strip()
        if not line.startswith("{"): continue
        try:
            ev=json.loads(line)
            if ev.get("ts","").startswith(today):
                events.append(ev)
        except: pass

quality=[e for e in events if e.get("event")=="quality"]
kb_used=[e for e in events if e.get("event")=="kb_used"]
kb_empty=[e for e in events if e.get("event")=="kb_empty"]

report={
  "date": today,
  "answers": sum(1 for e in events if e.get("event")=="chat_out"),
  "quality_events": len(quality),
  "ratio_has_kb": round(sum("has_kb" in e.get("tags",[]) for e in quality)/max(1,len(quality)),2),
  "kb_used": len(kb_used),
  "kb_empty": len(kb_empty),
  "kb_empty_stubs": [e.get("stub") for e in kb_empty if e.get("stub")]
}
path=os.path.join(HOME,"artifacts","insights",f"quality_report_{today}.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
open(path,"w",encoding="utf-8").write(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
