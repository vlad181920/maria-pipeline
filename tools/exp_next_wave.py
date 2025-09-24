import json,sys,os,datetime,argparse,uuid,glob
def read_json(p,default):
    try:
        with open(p,encoding="utf-8") as f: return json.load(f)
    except: return default
def write_json(p,data):
    tmp=p+".tmp"
    with open(tmp,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
    os.replace(tmp,p)
ap=argparse.ArgumentParser()
ap.add_argument("--exp",required=True)
ap.add_argument("--variant",choices=["A","B"],required=True)
ap.add_argument("--price",type=float,required=True)
args=ap.parse_args()
exp=os.path.abspath(args.exp)
os.makedirs(exp,exist_ok=True)
cfg_path=os.path.join(exp,"config.json")
cfg=read_json(cfg_path,{})
prev_wave=int(cfg.get("wave",0))
wave=prev_wave+1
ts=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
cfg.update({"wave":wave,"active_variant":args.variant,"price":args.price,"updated_at_utc":ts,"experiment_id":os.path.basename(exp)})
write_json(cfg_path,cfg)
waves_path=os.path.join(exp,"waves.jsonl")
rec={"ts_utc":ts,"wave":wave,"variant":args.variant,"price":args.price,"id":str(uuid.uuid4())}
with open(waves_path,"a",encoding="utf-8") as f:
    f.write(json.dumps(rec,ensure_ascii=False)+"\n")
print(json.dumps({"ok":True,"wave":wave,"variant":args.variant,"price":args.price},ensure_ascii=False))
