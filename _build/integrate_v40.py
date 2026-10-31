# -*- coding: utf-8 -*-
# v40 第1章 地図の見方（地形図・地図記号の図・地球儀と時差）を地理の先頭に追加
import io,sys,json
sys.path.insert(0,".")
import data_chizu as d
import chizu_symbols as cs
P=sys.argv[1]; s=io.open(P,encoding="utf-8").read()
def rep(a,b):
    global s
    assert a in s,"見つからない: "+a[:60]
    s=s.replace(a,b,1)
FIG={"mp4":"sym_land","mp5":"sym_b1","mp6":"sym_b2","mp7":"sym_b3"}
for a,b,c in d.SOURCES_ADD: assert 'id:"%s"'%a not in s,"出典が重複: "+a
for x in d.S: assert 'id:"%s"'%x[0] not in s,"セクションが重複: "+x[0]
for x in d.S:
    for q,a in x[4]: assert '"' not in q+a and "\\" not in q+a, q

# 出典：地理の先頭（単元31の前）
i=s.index('{subject:"地理",id:"u31"')
s=s[:i]+"".join('{subject:"地理",id:"%s",short:"%s",title:"%s"},\n'%x for x in d.SOURCES_ADD)+s[i:]
# 問題：DATAの末尾
end=s.rindex("\n]}\n]")+len("\n]}")
secs=['{id:"%s",from:"%s",title:"%s",page:"%s",%sitems:[\n%s\n]}'%(sid,frm,title,page,
      ('figure:"%s",'%FIG[sid]) if sid in FIG else "",
      ",\n".join('["%s","%s"]'%(q,a) for q,a in items)) for sid,frm,title,page,items in d.S]
s=s[:end]+",\n"+",\n".join(secs)+s[end:]
# ふりがな
k="const RUBY={\n"; i=s.index(k)+len(k)
s=s[:i]+"".join('"%s":"%s",'%(a,b) for a,b in d.RUBY_ADD.items())+"\n"+s[i:]
# 地図記号の図
reg,over=cs.build()
i=s.index("\n",s.index("\nconst OVER=")+1)
s=s[:i]+"\nObject.assign(REG,%s);Object.assign(OVER,%s);"%(json.dumps(reg,ensure_ascii=False),json.dumps(over,ensure_ascii=False))+s[i:]
rep('cap.textContent="出典：地球地図日本（国土地理院）をもとに作成";',
    'cap.textContent=OVER[key]&&OVER[key].cap||"出典：地球地図日本（国土地理院）をもとに作成";')
i=s.rindex("</style>")
s=s[:i]+(".cmap .cell{fill:var(--paper-2);stroke:var(--rule)}\n"
 ".cmap .sym{fill:none;stroke:var(--ink);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}\n"
 ".cmap .symf,.cmap .symt{fill:var(--ink)}\n.cmap .symt{font-family:var(--ff-b)}\n.cmap .symw{fill:var(--paper)}\n"
 ".cmap .snum{fill:var(--red);font-size:16px;font-weight:700}\n")+s[i:]
# テストのはんい（まとめて選ぶ）に地理の第1章
rep('const PRESETS={"歴史":[','const PRESETS={"地理":[\n  {name:"第1章 地図の見方（1・2）",ids:["map1","map2"]}\n],"歴史":[')
s=s.replace("v39 ・ 10/10更新","v40 ・ 10/31更新",1)
io.open(P,"w",encoding="utf-8").write(s)
print("組み込み完了:",len(d.S),"セクション",sum(len(x[4]) for x in d.S),"問")
# カードの図の注記（v40で追記。integrate後に実行した修正と同じもの）
# if(c)c.textContent="タップで拡大・"+(OVER[it.fig]&&OVER[it.fig].cap?"地図記号は形を簡単にして作図":"出典：…");
