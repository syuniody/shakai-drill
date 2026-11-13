# -*- coding: utf-8 -*-
# v42 地理に「3 日本の国土①」「4 川・平野・海岸と湖」を追加（レベル付き）
import io,sys,json,re
sys.path.insert(0,".")
import data_kokudo as d
P=sys.argv[1]; s=io.open(P,encoding="utf-8").read()
def rep(a,b):
    global s
    assert a in s,"見つからない: "+a[:60]
    s=s.replace(a,b,1)
for a,b,c in d.SOURCES_ADD: assert 'id:"%s"'%a not in s,"出典が重複: "+a
for x in d.S: assert '{id:"%s",'%x[0] not in s,"セクションが重複: "+x[0]
for x in d.S:
    for q,a,l in x[4]:
        assert '"' not in q+a and "\\" not in q+a, q
        assert l in "kh",q
# 出典：map2 の次
i=s.index('{subject:"地理",id:"u31"')
s=s[:i]+"".join('{subject:"地理",id:"%s",short:"%s",title:"%s"},\n'%x for x in d.SOURCES_ADD)+s[i:]
# 問題：DATAの末尾
end=s.rindex("\n]}\n]")+len("\n]}")
secs=['{id:"%s",from:"%s",title:"%s",page:"%s",items:[\n%s\n]}'%(sid,frm,title,page,
      ",\n".join('["%s","%s"]'%(q,a) for q,a,l in items)) for sid,frm,title,page,items in d.S]
s=s[:end]+",\n"+",\n".join(secs)+s[end:]
# レベル
lv=",".join('"%s":"%s"'%(sid,"".join(l for q,a,l in items)) for sid,frm,title,page,items in d.S)
rep('const LEVEL={','const LEVEL={'+lv+',')
# ふりがな（既にある語は足さない）
k="const RUBY={\n"; i=s.index(k)+len(k); j=s.index("\n};",i)
have=set(re.findall(r'"([^"]+)":"',s[i:j]))
add={a:b for a,b in d.RUBY_ADD.items() if a not in have}
s=s[:i]+"".join('"%s":"%s",'%(a,b) for a,b in add.items())+"\n"+s[i:]
# テストのはんい
rep('  {name:"第1章 地図の見方（1・2）",ids:["map1","map2"]}\n',
    '  {name:"第1章 地図の見方（1・2）",ids:["map1","map2"]},\n  {name:"日本の国土（3・4）",ids:["kd3","kd4"]}\n')
s=re.sub(r'id="ver">v41 ・ [0-9/]+更新','id="ver">v42 ・ 11/13更新',s,count=1)
assert 'v42 ・ 11/13更新' in s
io.open(P,"w",encoding="utf-8").write(s)
n=sum(len(x[4]) for x in d.S); k=sum(1 for x in d.S for q,a,l in x[4] if l=="k")
print("組み込み完了:",len(d.S),"分野",n,"問（基本",k,"／発展",n-k,"）ふりがな追加",len(add))
