import io,json,os,re
import data_th,data_kanto,data_kinki,data_cs,data_kyushu
dep=os.path.expanduser("~/Desktop/shakai-drill-deploy/jp9pyw1wu4/index.html")
s=io.open(dep,encoding="utf-8").read()
s=s[s.index("<title>"):]; s=s[:s.rindex("</body>")].rstrip()+"\n"
assert "v21" in s and "kyushu" not in s
def rep(a,b,n=1):
    global s
    assert s.count(a)>=n,"MISS: "+a[:70]
    s=s.replace(a,b,n)
MODS=[data_th,data_kanto,data_kinki,data_cs,data_kyushu]

# 1) はんい：北から南の順に並べ直す（idは変えない）
i=s.index("const SOURCES=["); j=s.index("];",i)
old=s[i:j]
ents=re.findall(r'\{id:"([^"]+)".*?\}',old)
lines={m.group(1):m.group(0) for m in re.finditer(r'\{id:"([^"]+)".*?\}',old)}
new=dict(lines)
for M in MODS:
    sid,short,title=M.SRC
    new[sid]='{id:%s,short:%s,title:%s}'%(json.dumps(sid),json.dumps(short+"地方",ensure_ascii=False),json.dumps(title,ensure_ascii=False))
order=["u31","u32","tohoku","kanto","chubu","kinki","chushikoku","kyushu"]
assert set(order)==set(new),set(new)
s=s[:i]+"const SOURCES=[\n"+",\n".join(new[k] for k in order)+"\n"+s[j:]

# 2) 問題データを末尾に追加
secs=[]
for M in MODS:
    for sid,title,fig,items in M.SECTIONS:
        its=",\n".join("["+json.dumps(q,ensure_ascii=False)+","+json.dumps(a,ensure_ascii=False)+"]" for q,a in items)
        f=(',figure:"%s"'%fig) if fig else ""
        secs.append('{id:"%s",from:"%s",title:%s,page:"受験頻出"%s,items:[\n%s\n]}'%(sid,M.SRC[0],json.dumps(title,ensure_ascii=False),f,its))
k=s.index("DATA.forEach(s=>s.items.forEach(")
e=s.rindex("];",0,k)
s=s[:e].rstrip()+",\n"+",\n".join(secs)+"\n"+s[e:]

# 3) 地図
maps=io.open("region_maps.js",encoding="utf-8").read()
rep("function mapNode(key){", maps+"function mapNode(key){")
rep('''    box.innerHTML='<svg class="cmap" viewBox="0 0 '+CHUBU_W+' '+CHUBU_H+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="中部地方の地図">'+CHUBU_BASE+(CHUBU_OVER[key]||"")+'</svg>';''',
'''    let W=CHUBU_W,Hh=CHUBU_H,inner=CHUBU_BASE+(CHUBU_OVER[key]||"");
    if(OVER[key]){const R=REG[OVER[key].r];W=R.w;Hh=R.h;inner=R.base+OVER[key].svg;}
    box.innerHTML='<svg class="cmap" viewBox="0 0 '+W+' '+Hh+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="地図">'+inner+'</svg>';
    if(Hh/W>1.3)box.classList.add("tall");''')

# 4) CSS
rep(".cmap .cap{fill:var(--red);stroke:var(--paper);stroke-width:1}",
""".cmap .cap{fill:var(--red);stroke:var(--paper);stroke-width:1}
.cmap .bridge{stroke:var(--red);stroke-width:3.2;fill:none;stroke-linecap:round;stroke-linejoin:round}
.cmap .inset{fill:var(--paper);stroke:var(--ink-3);stroke-width:1}
.cmap .inset-t{font-family:var(--ff-b);font-size:11px;fill:var(--ink-2)}""")
rep("  .card.has-map>.card-map.big{position:static;box-shadow:none}",
    "  .card.has-map>.card-map.tall .cmap{max-height:54vh}\n  .card.has-map>.card-map.big{position:static;box-shadow:none}\n  .card.has-map>.card-map.big .cmap{max-height:none}")

# 5) ふりがな
RB=json.load(io.open("rb2.json",encoding="utf-8"))
add=",".join(json.dumps(k,ensure_ascii=False)+":"+json.dumps(v,ensure_ascii=False) for k,v in RB.items() if ('"'+k+'":') not in s)
m=re.search(r'\n\};\nconst RUBY_KEYS=',s); assert m
s=s[:m.start()]+",\n"+add+s[m.start():]

rep("v21 ・ 9/19更新","v22 ・ 9/19更新")
io.open("kankyo-drill.html","w",encoding="utf-8").write(s)
io.open("env-drill.html","w",encoding="utf-8").write(s)
io.open("check.js","w",encoding="utf-8").write(s[s.index("<script>")+8:s.index("</script>")])
print("built",len(s))
