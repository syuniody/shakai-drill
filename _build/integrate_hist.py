# -*- coding: utf-8 -*-
import io,sys,importlib
sys.path.insert(0,".")
mod,P=sys.argv[1],sys.argv[2]
d=importlib.import_module(mod)
s=io.open(P,encoding="utf-8").read()
for a,b,c in d.SOURCES_ADD:
    assert 'id:"%s"'%a not in s, "出典が重複: "+a
for sid,frm,title,page,items in d.S:
    assert 'id:"%s"'%sid not in s, "セクションが重複: "+sid
i=s.index('{subject:"理科",id:"rika"')
s=s[:i]+"".join('{subject:"歴史",id:"%s",short:"%s",title:"%s"},\n'%(a,b,c) for a,b,c in d.SOURCES_ADD)+s[i:]
end=s.rindex("\n]}\n]")+len("\n]}")
secs=['{id:"%s",from:"%s",title:"%s",page:"%s",items:[\n%s\n]}'%(sid,frm,title,page,
      ",\n".join('["%s","%s"]'%(q,a) for q,a in items)) for sid,frm,title,page,items in d.S]
s=s[:end]+",\n"+",\n".join(secs)+s[end:]
k="const RUBY={\n"; i=s.index(k)+len(k)
s=s[:i]+"".join('"%s":"%s",'%(a,b) for a,b in d.RUBY_ADD.items())+"\n"+s[i:]
io.open(P,"w",encoding="utf-8").write(s)
print("組み込み完了:",mod,len(d.S),"セクション",sum(len(x[4]) for x in d.S),"問")
