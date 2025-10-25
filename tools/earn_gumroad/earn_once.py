import os, sys
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, BASE)
from tools.earn_gumroad.earn_daemon import cycle, log
log("earn_once start")
cycle()
log("earn_once done")
