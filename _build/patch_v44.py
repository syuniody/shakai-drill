# -*- coding: utf-8 -*-
# v44 日本の国土（3・4）の「基本」を減らす。問題は消さず、レベルだけ k→h に付け替える（◯△の記録はそのまま）
# 方針：同じことを基本で2回聞かない。地図の分野（kd17〜24）は「地図中の○の名前」だけを基本に残し、
#       県名・特色などの付け足しは文章の分野（kd1〜16）の基本に任せる。文章の分野は、地図で覚える位置の言いかえ・
#       逆向き・2位3位の単独問題・ほかの問題と同じ答えのものを発展へ。
import io,re,sys
sys.path.insert(0,"_build")
import data_kokudo_map as dm
P=sys.argv[1]; s=io.open(P,encoding="utf-8").read()
TEXT={"kd1":[4],"kd2":[8,9,10,11,12],"kd3":[15],"kd7":[3,11,12,13,15,16,17,19,20,21,22,23,24],
      "kd12":[1,2,5,6,8,9,10],"kd13":[14],"kd14":[1]}
names={x[0]:len(x[5]) for x in dm.M} if False else {}
for sid,frm,title,page,fig,marks,kind,extra in dm.M:
    n=len(marks); names[sid]=(n,n+len(extra))
m=re.search(r"const LEVEL=\{",s); i=m.end(); j=s.index("};",i)
body=s[i:j]
def setlv(body,sid,idx):
    mm=re.search(r'"%s":"([kh]+)"'%sid,body); assert mm,sid
    l=list(mm.group(1))
    for k in idx:
        assert l[k]=="k",(sid,k,l[k]); l[k]="h"
    return body[:mm.start(1)]+"".join(l)+body[mm.end(1):]
for sid,idx in TEXT.items(): body=setlv(body,sid,idx)
for sid,(a,b) in names.items():
    mm=re.search(r'"%s":"([kh]+)"'%sid,body); l=mm.group(1)
    body=setlv(body,sid,[k for k in range(a,b) if l[k]=="k"])
s=s[:i]+body+s[j:]
s=re.sub(r"v43 ・ 11/1\d更新","v44 ・ 11/14更新",s,count=1)
io.open(P,"w",encoding="utf-8").write(s)
L=dict(re.findall(r'"(kd\d+)":"([kh]+)"',body))
k=sum(v.count("k") for v in L.values()); h=sum(v.count("h") for v in L.values())
print("日本の国土（3・4） 基本",k,"発展",h,"計",k+h)
