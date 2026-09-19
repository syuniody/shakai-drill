import json, io
g=json.load(open("geo_base.json"))
W,H,S,LON0,LAT0,K=g["W"],g["H"],g["S"],g["LON0"],g["LAT0"],g["K"]
def P(lat,lon): return ((lon-LON0)*K*S,(LAT0-lat)*S)
def pt(lat,lon): x,y=P(lat,lon); return "%.1f,%.1f"%(x,y)

BASE='<g class="nei">'+"".join('<path d="%s"/>'%d for d in g["nei"])+'</g><g class="land">'+"".join('<path d="%s"/>'%g["main"][k] for k in sorted(g["main"],key=int))+'</g>'

def pin(lat,lon,label,dx=0,dy=0,r=10.5):
    x,y=P(lat,lon); px,py=x+dx,y+dy; s=""
    if dx or dy: s+='<path class="lead" d="M%.1f,%.1f L%.1f,%.1f"/><circle class="dot" cx="%.1f" cy="%.1f" r="2.2"/>'%(px,py,x,y,x,y)
    s+='<circle class="pin" cx="%.1f" cy="%.1f" r="%.1f"/><text class="pin-t" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'%(px,py,r,px,py+4.4,label)
    return s
def line(cls,pts): return '<polyline class="%s" points="%s"/>'%(cls," ".join(pt(a,b) for a,b in pts))
def peak(lat,lon): x,y=P(lat,lon); return '<path class="peak" d="M%.1f,%.1f l6,10 l-12,0 Z"/>'%(x,y-6)
def zone(lat,lon,rx,ry,rot=0): x,y=P(lat,lon); return '<ellipse class="zone" cx="%.1f" cy="%.1f" rx="%s" ry="%s" transform="rotate(%s %.1f %.1f)"/>'%(x,y,rx,ry,rot,x,y)

RIV={
"信濃川":[(35.91,138.73),(36.25,138.48),(36.40,138.25),(36.62,138.23),(36.85,138.37),(37.01,138.65),(37.13,138.76),(37.31,138.80),(37.45,138.84),(37.63,138.96),(37.95,139.06)],
"阿賀野川":[(37.60,139.62),(37.68,139.45),(37.80,139.22),(37.97,139.13)],
"神通川":[(36.15,137.25),(36.45,137.30),(36.70,137.21),(36.76,137.22)],
"黒部川":[(36.40,137.60),(36.566,137.662),(36.82,137.58),(36.93,137.43)],
"庄川":[(36.13,136.91),(36.26,136.90),(36.43,136.94),(36.62,136.97),(36.78,137.07)],
"九頭竜川":[(35.90,136.67),(35.98,136.49),(36.06,136.50),(36.10,136.22),(36.22,136.13)],
"天竜川":[(36.05,138.08),(35.83,137.95),(35.51,137.83),(35.10,137.79),(34.75,137.80),(34.65,137.79)],
"富士川":[(35.85,138.30),(35.60,138.47),(35.37,138.44),(35.13,138.62)],
"大井川":[(35.62,138.22),(35.22,138.23),(35.05,138.08),(34.83,138.17),(34.77,138.29)],
"木曽川":[(36.05,137.72),(35.84,137.69),(35.60,137.61),(35.49,137.50),(35.44,137.02),(35.39,136.94),(35.30,136.72),(35.04,136.74)],
"長良川":[(35.99,136.84),(35.75,136.96),(35.54,136.91),(35.43,136.76),(35.20,136.69),(35.05,136.71)],
"揖斐川":[(35.67,136.50),(35.49,136.57),(35.36,136.65),(35.18,136.66),(35.04,136.69)],
}
def rivers(names,cls="river"): return "".join(line(cls,RIV[n]) for n in names)
ALLR=list(RIV.keys())

MAPS={}
# 1 県の位置
c=g["cent"]; order=[15,16,17,18,20,21,19,22,23]; num="①②③④⑤⑥⑦⑧⑨"
adj={15:(-14,18),17:(-13,34),22:(0,-6),23:(4,-6),18:(6,-4),16:(0,2)}
caps={15:(37.90,139.02),16:(36.70,137.21),17:(36.59,136.63),18:(36.07,136.22),20:(36.65,138.18),21:(35.39,136.72),19:(35.66,138.57),22:(34.98,138.38),23:(35.18,136.91)}
s=""
for i,k in enumerate(order):
    x,y=c[str(k)]; dx,dy=adj.get(k,(0,0))
    s+='<text class="pnum" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'%(x+dx,y+dy+6,num[i])
for k,(la,lo) in caps.items():
    x,y=P(la,lo); s+='<circle class="cap" cx="%.1f" cy="%.1f" r="3.2"/>'%(x,y)
MAPS["chubu_pref"]=s
# 2 山地・山
s=line("range",[(36.95,137.77),(36.76,137.76),(36.575,137.64),(36.34,137.65),(36.11,137.55)])
s+=line("range",[(35.95,137.86),(35.79,137.80),(35.62,137.78),(35.44,137.62)])
s+=line("range",[(35.78,138.24),(35.67,138.24),(35.46,138.16),(35.30,138.08),(35.15,138.04)])
s+=line("range",[(37.62,139.50),(37.30,139.25),(37.12,139.08),(36.92,138.97),(36.84,138.82)])
for la,lo in [(35.36,138.73),(36.41,138.52),(35.89,137.48),(36.155,136.77),(35.97,138.37),(36.575,137.62)]: s+=peak(la,lo)
s+=pin(36.60,137.70,"A",22,-12)+pin(35.70,137.79,"B",-22,6)+pin(35.46,138.16,"C",22,14)+pin(37.25,139.20,"D",22,4)
s+=pin(35.36,138.73,"E",20,8)+pin(36.41,138.52,"F",20,-8)+pin(35.89,137.48,"G",-20,-4)+pin(36.155,136.77,"H",-20,6)+pin(35.97,138.37,"I",20,-6)+pin(36.575,137.62,"J",-24,-6)
MAPS["chubu_mount"]=s
# 3 川
s=rivers([n for n in ALLR if n!="庄川"])
s+=pin(37.20,138.78,"A",20,4)+pin(37.74,139.33,"B",16,14)+pin(36.45,137.30,"C",-18,-6)+pin(36.82,137.58,"D",20,-6)+pin(36.06,136.50,"E",-4,22)
s+=pin(35.45,137.82,"F",20,4)+pin(35.45,138.45,"G",20,-4)+pin(35.10,138.12,"H",20,12)+pin(35.60,137.61,"I",-20,4)+pin(35.70,136.95,"J",4,-22)+pin(35.49,136.57,"K",-20,4)
MAPS["chubu_river"]=s
# 4 平野・盆地・台地
s=rivers(ALLR,"river faint")
Z=[(37.75,139.02,20,11,-35,"A",24,-10),(36.68,137.12,15,8,0,"B",0,-22),(36.52,136.58,10,6,-50,"C",-22,0),(36.12,136.22,9,7,0,"D",-22,0),(35.22,136.78,17,14,0,"E",-26,8),
   (35.64,138.58,11,7,0,"F",22,-8),(36.64,138.22,8,10,0,"G",22,-4),(36.26,137.96,6,11,0,"H",-22,0),(36.03,138.10,6,5,0,"I",22,8),(34.79,138.18,9,7,0,"J",18,16),(34.92,137.10,10,7,0,"K",8,24)]
for la,lo,rx,ry,rot,lab,dx,dy in Z: s+=zone(la,lo,rx,ry,rot)
for la,lo,rx,ry,rot,lab,dx,dy in Z: s+=pin(la,lo,lab,dx,dy)
MAPS["chubu_plain"]=s
# 5 半島・湾・湖・島
s=pin(37.25,136.95,"A",-24,-6)+pin(34.85,138.93,"B",20,10)+pin(34.80,136.88,"C",-26,-12)+pin(34.64,137.20,"D",2,24)+pin(38.03,138.40,"E",-24,0)
s+=pin(36.98,137.28,"F",8,-20)+pin(35.78,135.78,"G",-6,-20)+pin(34.80,138.58,"H",2,26)+pin(34.72,136.70,"I",-20,22)+pin(34.74,137.10,"J",-4,-22)
s+=pin(34.75,137.58,"K",14,24)+pin(36.05,138.085,"L",20,-6)
MAPS["chubu_coast"]=s
# 6 ダム・発電所
s=rivers(ALLR,"river faint")
s+=pin(36.566,137.662,"A",20,-8)+pin(35.10,137.79,"B",20,4)+pin(36.13,136.91,"C",-20,8)+pin(35.665,136.50,"D",-20,0)+pin(37.15,139.25,"E",18,10)
s+=pin(37.43,138.60,"F",-20,-6)+pin(35.66,135.85,"G",-4,-22)+pin(34.62,138.14,"H",16,22)+pin(37.06,136.73,"I",-22,0)
MAPS["chubu_dam"]=s
# 7 工業・都市
s=pin(35.08,137.16,"A",20,4)+pin(35.02,136.90,"B",-6,24)+pin(35.27,137.10,"C",22,-10)+pin(35.30,136.80,"D",-22,-8)+pin(34.97,136.62,"E",-22,6)
s+=pin(34.71,137.73,"F",-2,26)+pin(35.16,138.68,"G",20,-6)+pin(34.87,138.32,"H",14,20)+pin(36.06,138.05,"I",20,-8)
s+=pin(35.95,136.18,"J",-22,0)+pin(37.39,136.90,"K",18,-10)+pin(36.75,137.02,"L",-6,-22)+pin(36.70,137.21,"M",20,8)+pin(37.65,138.92,"N",-22,-4)
MAPS["chubu_ind"]=s

js="const CHUBU_W=%d,CHUBU_H=%d;\nconst CHUBU_BASE='%s';\nconst CHUBU_OVER={\n"%(W,H,BASE)
js+=",\n".join('"%s":\'%s\''%(k,v) for k,v in MAPS.items())+"\n};\n"
io.open("chubu_maps.js","w",encoding="utf-8").write(js)

css='''<style>body{margin:0;background:#FBF8F1;font-family:sans-serif}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:8px}
figure{margin:0}figcaption{font-size:12px}
.nei path{fill:#F1ECE0;stroke:#DDD5C3;stroke-width:.8}.land path{fill:#E6DEC9;stroke:#9A927E;stroke-width:1.1;stroke-linejoin:round}
.pin{fill:#B93328;stroke:#FBF8F1;stroke-width:1.6}.pin-t{fill:#FBF8F1;font-size:11.5px;font-weight:700}.lead{stroke:#B93328;stroke-width:1.2;fill:none}.dot{fill:#B93328}
.river{stroke:#2B5691;stroke-width:1.8;fill:none;stroke-linejoin:round;stroke-linecap:round}.river.faint{opacity:.35;stroke-width:1.3}
.range{stroke:#8A5A1C;stroke-width:5;fill:none;stroke-linecap:round;stroke-linejoin:round;opacity:.75}.peak{fill:#5B3A10}
.zone{fill:#3F7A3A;opacity:.32;stroke:#3F7A3A;stroke-width:1}.pnum{font-size:19px;font-weight:700;fill:#22211C}.cap{fill:#B93328;stroke:#FBF8F1;stroke-width:1}</style>'''
html='<meta charset=utf-8>'+css+'<div class=grid>'+"".join('<figure><svg viewBox="0 0 %d %d" width="100%%">%s%s</svg><figcaption>%s</figcaption></figure>'%(W,H,BASE,v,k) for k,v in MAPS.items())+'</div>'
io.open("maps_preview.html","w",encoding="utf-8").write(html)
print("js bytes",len(js))
