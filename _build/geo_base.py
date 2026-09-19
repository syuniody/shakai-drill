import json, math, io
d=json.load(open("japan.geojson",encoding="utf-8"))
MAIN={15:"新潟",16:"富山",17:"石川",18:"福井",19:"山梨",20:"長野",21:"岐阜",22:"静岡",23:"愛知"}
NEI=[6,7,10,11,13,14,24,25,26,9,29,27]
S=110.0; LON0=135.4; LAT0=38.72; K=math.cos(math.radians(36.5))
W=round((140.0-LON0)*K*S); H=round((LAT0-34.22)*S)
def P(lat,lon): return ((lon-LON0)*K*S,(LAT0-lat)*S)
def dp(pts,eps):
    if len(pts)<3: return pts
    (x1,y1),(x2,y2)=pts[0],pts[-1]
    dx,dy=x2-x1,y2-y1; n=math.hypot(dx,dy) or 1e-9
    imax,dmax=0,0
    for i in range(1,len(pts)-1):
        x,y=pts[i]; dist=abs(dy*x-dx*y+x2*y1-y2*x1)/n
        if dist>dmax: imax,dmax=i,dist
    if dmax>eps: return dp(pts[:imax+1],eps)[:-1]+dp(pts[imax:],eps)
    return [pts[0],pts[-1]]
def area(r): return abs(sum(r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1] for i in range(len(r)-1)))/2
def centroid(r):
    a=cx=cy=0
    for i in range(len(r)-1):
        c=r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1]; a+=c; cx+=(r[i][0]+r[i+1][0])*c; cy+=(r[i][1]+r[i+1][1])*c
    a=a/2 or 1e-9; return (cx/(6*a),cy/(6*a))
import sys; sys.setrecursionlimit(100000)
def rings(f,eps,amin):
    g=f["geometry"]; polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    out=[]
    for poly in polys:
        r=[P(lat,lon) for lon,lat in poly[0]]
        if area(r)<amin: continue
        # 半分に割ってから簡略化（閉じた輪の対策）
        m=len(r)//2; s=dp(r[:m+1],eps)[:-1]+dp(r[m:],eps)
        if len(s)>=4: out.append(s)
    return out
def dstr(rs): return "".join("M"+" ".join("%.1f,%.1f"%p for p in r)+"Z" for r in rs)
main={}; cent={}; nei=[]
for f in d["features"]:
    i=f["properties"]["id"]
    if i in MAIN:
        rs=rings(f,0.55,5); main[i]=dstr(rs)
        big=max(rs,key=area); cent[i]=centroid(big)
    elif i in NEI:
        rs=rings(f,1.3,30)
        rs=[r for r in rs if any(-20<x<W+20 and -20<y<H+20 for x,y in r)]
        if rs: nei.append(dstr(rs))
json.dump({"W":W,"H":H,"main":main,"cent":cent,"nei":nei,"S":S,"LON0":LON0,"LAT0":LAT0,"K":K},open("geo_base.json","w"))
print("W,H=",W,H," main bytes=",sum(len(v) for v in main.values())," nei bytes=",sum(len(v) for v in nei))
for i,c in cent.items(): print(MAIN[i],"%.0f,%.0f"%c)
