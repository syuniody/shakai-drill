# -*- coding: utf-8 -*-
# v43 日本の国土に「地図で答える」分野 kd17〜kd24 と日本全体の地図を追加
import io,sys,json
sys.path.insert(0,".")
import data_kokudo_map as d
P=sys.argv[1]; s=io.open(P,encoding="utf-8").read()
mp=json.load(open("kokudo_maps.json",encoding="utf-8"))
def rep(a,b):
    global s
    assert a in s,"見つからない: "+a[:60]
    s=s.replace(a,b,1)
S=d.build()
for x in S:
    assert '{id:"%s",'%x[0] not in s,"重複: "+x[0]
    assert x[4] in mp["OVER"],x[4]
    for q,a,l in x[5]: assert '"' not in q+a and "\\" not in q+a and l in "kh", q
end=s.rindex("\n]}\n]")+len("\n]}")
secs=['{id:"%s",from:"%s",title:"%s",page:"%s",figure:"%s",items:[\n%s\n]}'%(sid,frm,title,page,fig,
      ",\n".join('["%s","%s"]'%(q,a) for q,a,l in items)) for sid,frm,title,page,fig,items in S]
s=s[:end]+",\n"+",\n".join(secs)+s[end:]
rep('const LEVEL={','const LEVEL={'+",".join('"%s":"%s"'%(x[0],"".join(l for q,a,l in x[5])) for x in S)+',')
i=s.index("\n",s.index("\nconst OVER=")+1)
s=s[:i]+"\nObject.assign(REG,%s);Object.assign(OVER,%s);"%(json.dumps(mp["REG"],ensure_ascii=False),json.dumps(mp["OVER"],ensure_ascii=False))+s[i:]
assert 'OVER[key]&&OVER[key].cap||' in s
import re
s=re.sub(r'id="ver">v42 ・ [0-9/]+更新','id="ver">v43 ・ 11/13更新',s,count=1); assert "v43 ・" in s
io.open(P,"w",encoding="utf-8").write(s)
n=sum(len(x[5]) for x in S); k=sum(1 for x in S for q,a,l in x[5] if l=="k")
print("組み込み完了:",len(S),"分野",n,"問（基本",k,"／発展",n-k,"）")
