# 地方ごとの地図（下絵＋記号）を生成する共通部品
import json, math, sys
sys.setrecursionlimit(200000)
_GEO=json.load(open("japan.geojson",encoding="utf-8"))
def _dp(pts,eps):
    if len(pts)<3: return pts
    (x1,y1),(x2,y2)=pts[0],pts[-1]; dx,dy=x2-x1,y2-y1; n=math.hypot(dx,dy) or 1e-9
    im,dm=0,0
    for i in range(1,len(pts)-1):
        x,y=pts[i]; d=abs(dy*x-dx*y+x2*y1-y2*x1)/n
        if d>dm: im,dm=i,d
    if dm>eps: return _dp(pts[:im+1],eps)[:-1]+_dp(pts[im:],eps)
    return [pts[0],pts[-1]]
def _area(r): return abs(sum(r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1] for i in range(len(r)-1)))/2
def _cent(r):
    a=cx=cy=0
    for i in range(len(r)-1):
        c=r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1]; a+=c; cx+=(r[i][0]+r[i+1][0])*c; cy+=(r[i][1]+r[i+1][1])*c
    a=a/2 or 1e-9; return (cx/(6*a),cy/(6*a))
class Region:
    def __init__(s,name,lon0,lon1,lat0,lat1,S,main,nei,eps=0.55,amin=6,inset=None,pinr=10.5):
        s.name=name;s.lon0=lon0;s.lon1=lon1;s.lat0=lat0;s.lat1=lat1;s.S=S
        s.K=math.cos(math.radians((lat0+lat1)/2)); s.W=round((lon1-lon0)*s.K*S); s.H=round((lat1-lat0)*S)
        s.pinr=pinr; s.cent={}
        def rings(f,eps,amin,P,box):
            g=f["geometry"]; polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]; out=[]
            for poly in polys:
                lons=[p[0] for p in poly[0]]; lats=[p[1] for p in poly[0]]
                clo,cla=sum(lons)/len(lons),sum(lats)/len(lats)
                if not (box[0]<=clo<=box[1] and box[2]<=cla<=box[3]): continue
                r=[P(la,lo) for lo,la in poly[0]]
                if _area(r)<amin: continue
                m=len(r)//2; q=_dp(r[:m+1],eps)[:-1]+_dp(r[m:],eps)
                if len(q)>=4: out.append(q)
            return out
        dstr=lambda rs:"".join("M"+" ".join("%.1f,%.1f"%p for p in r)+"Z" for r in rs)
        box=(lon0-0.3,lon1+0.3,lat0-0.3,lat1+0.3)
        mains=[];neis=[]
        for f in _GEO["features"]:
            i=f["properties"]["id"]
            if i in main:
                rs=rings(f,eps,amin,s.P,box)
                if rs: mains.append(dstr(rs)); s.cent[i]=_cent(max(rs,key=_area))
            elif i in nei:
                rs=rings(f,eps*2.2,amin*5,s.P,box)
                if rs: neis.append(dstr(rs))
        extra=""
        if inset:
            # inset: dict(id, lon0,lon1,lat0,lat1,S,x,y,label)
            K2=math.cos(math.radians((inset["lat0"]+inset["lat1"])/2)); S2=inset["S"]
            w2=(inset["lon1"]-inset["lon0"])*K2*S2; h2=(inset["lat1"]-inset["lat0"])*S2
            P2=lambda la,lo:(inset["x"]+6+(lo-inset["lon0"])*K2*S2, inset["y"]+6+(inset["lat1"]-la)*S2)
            s.P2=P2
            for f in _GEO["features"]:
                if f["properties"]["id"]==inset["id"]:
                    rs=rings(f,0.5,4,P2,(inset["lon0"],inset["lon1"],inset["lat0"],inset["lat1"]))
                    s.cent[inset["id"]]=_cent(max(rs,key=_area))
                    extra='<rect class="inset" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6"/><g class="land"><path d="%s"/></g><text class="inset-t" x="%.1f" y="%.1f">%s</text>'%(inset["x"],inset["y"],w2+12,h2+12,dstr(rs),inset["x"]+6,inset["y"]+h2+8,inset["label"])
        s.base='<g class="nei">'+"".join('<path d="%s"/>'%d for d in neis)+'</g><g class="land">'+"".join('<path d="%s"/>'%d for d in mains)+'</g>'+extra
    def P(s,lat,lon): return ((lon-s.lon0)*s.K*s.S,(s.lat1-lat)*s.S)
    def pin(s,lat,lon,label,dx=0,dy=0,P=None):
        x,y=(P or s.P)(lat,lon); px,py=x+dx,y+dy; r=s.pinr; o=""
        if dx or dy: o+='<path class="lead" d="M%.1f,%.1f L%.1f,%.1f"/><circle class="dot" cx="%.1f" cy="%.1f" r="%.1f"/>'%(px,py,x,y,x,y,r*0.21)
        o+='<circle class="pin" cx="%.1f" cy="%.1f" r="%.1f"/><text class="pin-t" style="font-size:%.1fpx" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'%(px,py,r,r*1.19,px,py+r*0.42,label)
        return o
    def line(s,cls,pts): return '<polyline class="%s" points="%s"/>'%(cls," ".join("%.1f,%.1f"%s.P(a,b) for a,b in pts))
    def peak(s,lat,lon):
        x,y=s.P(lat,lon); k=s.pinr/10.5
        return '<path class="peak" d="M%.1f,%.1f l%.1f,%.1f l%.1f,0 Z"/>'%(x,y-6*k,6*k,10*k,-12*k)
    def zone(s,lat,lon,rx,ry,rot=0):
        x,y=s.P(lat,lon); return '<ellipse class="zone" cx="%.1f" cy="%.1f" rx="%s" ry="%s" transform="rotate(%s %.1f %.1f)"/>'%(x,y,rx,ry,rot,x,y)
    def prefmap(s,order,caps,adj={}):
        num="①②③④⑤⑥⑦⑧⑨⑩"; o=""; fs=17*s.pinr/10.5
        for n,k in enumerate(order):
            x,y=s.cent[k]; dx,dy=adj.get(k,(0,0))
            o+='<text class="pnum" style="font-size:%.1fpx" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'%(fs,x+dx,y+dy+fs*0.35,num[n])
        for k,(la,lo) in caps.items():
            x,y=(s.P2 if (k=="inset") else s.P)(la,lo); o+='<circle class="cap" cx="%.1f" cy="%.1f" r="%.1f"/>'%(x,y,3.2*s.pinr/10.5)
        return o
    def rivers(s,RIV,names,cls="river"): return "".join(s.line(cls,RIV[n]) for n in names)
def preview(regs_overs,fn):
    css='''<style>body{margin:0;background:#FBF8F1;font-family:sans-serif}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:8px}
figure{margin:0}figcaption{font-size:12px}.nei path{fill:#F1ECE0;stroke:#DDD5C3;stroke-width:.8}.land path{fill:#E6DEC9;stroke:#9A927E;stroke-width:1.1;stroke-linejoin:round}
.pin{fill:#B93328;stroke:#FBF8F1;stroke-width:1.6}.pin-t{fill:#FBF8F1;font-weight:700}.lead{stroke:#B93328;stroke-width:1.2;fill:none}.dot{fill:#B93328}
.river{stroke:#2B5691;stroke-width:1.8;fill:none;stroke-linejoin:round;stroke-linecap:round}.river.faint{opacity:.35;stroke-width:1.3}.bridge{stroke:#B93328;stroke-width:3;fill:none;stroke-linecap:round}
.range{stroke:#8A5A1C;stroke-width:5;fill:none;stroke-linecap:round;stroke-linejoin:round;opacity:.75}.peak{fill:#5B3A10}.zone{fill:#3F7A3A;opacity:.32;stroke:#3F7A3A;stroke-width:1}
.pnum{font-weight:700;fill:#22211C}.cap{fill:#B93328;stroke:#FBF8F1;stroke-width:1}.inset{fill:#FBF8F1;stroke:#9A927E;stroke-width:1}.inset-t{font-size:10px;fill:#5D5A4F}</style>'''
    h='<meta charset=utf-8>'+css+'<div class=grid>'
    for R,overs in regs_overs:
        for k,v in overs.items(): h+='<figure><svg viewBox="0 0 %d %d" width="100%%">%s%s</svg><figcaption>%s (%dx%d)</figcaption></figure>'%(R.W,R.H,R.base,v,k,R.W,R.H)
    open(fn,"w",encoding="utf-8").write(h+'</div>')
