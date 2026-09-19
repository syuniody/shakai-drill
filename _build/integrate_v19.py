import io,json,os,re
import chubu_data as C
dep=os.path.expanduser("~/Desktop/shakai-drill-deploy/jp9pyw1wu4/index.html")
s=io.open(dep,encoding="utf-8").read()
s=s[s.index("<title>"):]
s=s[:s.rindex("</body>")].rstrip()+"\n"
assert "v18" in s and "chubu" not in s
def rep(a,b,cnt=1):
    global s
    assert a in s,"MISS: "+a[:60]
    s=s.replace(a,b,cnt)

# 1) はんいを追加
i=s.index("const SOURCES=["); j=s.index("];",i)
s=s[:j].rstrip()+',\n{id:"chubu",short:"中部地方",title:"中部地方（新潟・富山・石川・福井・山梨・長野・岐阜・静岡・愛知）"}\n'+s[j:]

# 2) 問題データを末尾に追加（既存セクションには触れない）
fix={"浜松市で楽器やオートバイの生産がさかんな。ピアノの生産が全国1位の県は。":"ピアノの生産が全国1位の県は。"}
secs=[]
for sid,title,fig,items in C.SECTIONS:
    its=",\n".join("["+json.dumps(fix.get(q,q),ensure_ascii=False)+","+json.dumps(a,ensure_ascii=False)+"]" for q,a in items)
    f=(',figure:"%s"'%fig) if fig else ""
    secs.append('{id:"%s",from:"chubu",title:%s,page:"受験頻出"%s,items:[\n%s\n]}'%(sid,json.dumps(title,ensure_ascii=False),f,its))
k=s.index("DATA.forEach(s=>s.items.forEach(")
e=s.rindex("];",0,k)
s=s[:e].rstrip()+",\n"+",\n".join(secs)+"\n"+s[e:]

# 3) 地図
maps=io.open("chubu_maps.js",encoding="utf-8").read()
old=s[s.index("function mapNode(){"):s.index("function head(title,src){")]
new=maps+'''function mapNode(key){
  const box=document.createElement("div");box.className="mapbox";
  const cap=document.createElement("p");cap.className="mapcap";
  if(key==="map"){box.innerHTML=MAP_SVG;cap.textContent="略地図。実際の形や縮尺とは異なります。";}
  else{
    box.innerHTML='<svg class="cmap" viewBox="0 0 '+CHUBU_W+' '+CHUBU_H+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="中部地方の地図">'+CHUBU_BASE+(CHUBU_OVER[key]||"")+'</svg>';
    cap.textContent="出典：地球地図日本（国土地理院）をもとに作成";
  }
  box.appendChild(cap);return box;
}
'''
s=s.replace(old,new,1)
rep('if(s.figure==="map")sec.appendChild(mapNode());','if(s.figure)sec.appendChild(mapNode(s.figure));')
rep('if(it.fig==="map"){const mb=mapNode();','if(it.fig){const mb=mapNode(it.fig);')

# 4) CSS
rep(".mapcap{font-size:12px;color:var(--ink-3)}",
""".mapcap{font-size:12px;color:var(--ink-3)}
.cmap{width:100%;max-width:460px;height:auto;display:block}
.cmap .nei path{fill:color-mix(in srgb,var(--paper-3) 40%,var(--paper));stroke:var(--rule);stroke-width:.8}
.cmap .land path{fill:var(--paper-3);stroke:var(--ink-3);stroke-width:1.1;stroke-linejoin:round}
.cmap .pin{fill:var(--red);stroke:var(--paper);stroke-width:1.6}
.cmap .pin-t{fill:var(--paper);font-family:var(--ff-b);font-size:12.5px;font-weight:700}
.cmap .lead{stroke:var(--red);stroke-width:1.2;fill:none}
.cmap .dot{fill:var(--red)}
.cmap .river{stroke:var(--blue);stroke-width:1.9;fill:none;stroke-linejoin:round;stroke-linecap:round}
.cmap .river.faint{opacity:.38;stroke-width:1.3}
.cmap .range{stroke:var(--amber);stroke-width:5.5;fill:none;stroke-linecap:round;stroke-linejoin:round;opacity:.8}
.cmap .peak{fill:var(--ink)}
.cmap .zone{fill:var(--green);fill-opacity:.3;stroke:var(--green);stroke-width:1}
.cmap .pnum{font-family:var(--ff-b);font-size:17px;font-weight:700;fill:var(--ink)}
.cmap .cap{fill:var(--red);stroke:var(--paper);stroke-width:1}
.card-map{align-items:center;margin-left:auto;margin-right:auto}
.card-map .cmap{max-height:54vh;width:auto;max-width:100%}""")

# 5) ふりがな追加
RB=json.load(io.open("rb.json",encoding="utf-8"))
add=",".join(json.dumps(k,ensure_ascii=False)+":"+json.dumps(v,ensure_ascii=False) for k,v in RB.items() if ('"'+k+'":') not in s)
rep('"飛鳥":"あすか"\n};','"飛鳥":"あすか",\n'+add+'\n};')

rep("v18 ・ 9/13更新","v19 ・ 9/19更新")
io.open("kankyo-drill.html","w",encoding="utf-8").write(s)
io.open("env-drill.html","w",encoding="utf-8").write(s)
io.open("check.js","w",encoding="utf-8").write(s[s.index("<script>")+8:s.index("</script>")])
print("built",len(s))
