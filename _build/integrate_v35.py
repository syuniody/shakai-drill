# -*- coding: utf-8 -*-
import io,sys
sys.path.insert(0,".")
import data_rekishi1 as d
P=sys.argv[1]
s=io.open(P,encoding="utf-8").read()

# 1) 教科名を 社会→地理 に（歴史を別教科として並べるため）
assert s.count('{subject:"社会",id:')==9, s.count('{subject:"社会",id:')
s=s.replace('{subject:"社会",id:','{subject:"地理",id:')
assert 'let subject="社会"' in s
s=s.replace('let subject="社会"','let subject="地理"',1)
assert s.count('<p class="eyebrow">社会　赤シート式</p>')+s.count('<p class="eyebrow">社会・理科　赤シート式</p>')>0
s=s.replace('<p class="eyebrow">社会・理科　赤シート式</p>','<p class="eyebrow">地理・歴史・理科　赤シート式</p>')

# 2) SOURCES に歴史の出典を追加（理科の直前＝社会のあと）
anchor='{subject:"理科",id:"rika"'
i=s.index(anchor)
add="".join('{subject:"歴史",id:"%s",short:"%s",title:"%s"},\n'%(a,b,c) for a,b,c in d.SOURCES_ADD)
s=s[:i]+add+s[i:]

# 3) DATA にセクションを追加（末尾）
end=s.rindex("\n]}\n]")+len("\n]}")
secs=[]
for sid,frm,title,page,items in d.S:
    body=",\n".join('["%s","%s"]'%(q,a) for q,a in items)
    secs.append('{id:"%s",from:"%s",title:"%s",page:"%s",items:[\n%s\n]}'%(sid,frm,title,page,body))
s=s[:end]+",\n"+",\n".join(secs)+s[end:]

# 4) ふりがな辞書に追加
k="const RUBY={\n"
i=s.index(k)+len(k)
s=s[:i]+"".join('"%s":"%s",'%(a,b) for a,b in d.RUBY_ADD.items())+"\n"+s[i:]

io.open(P,"w",encoding="utf-8").write(s)
print("ok")
