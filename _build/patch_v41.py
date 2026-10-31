# -*- coding: utf-8 -*-
# v41 レベル（基本／発展）の絞り込み。まず第1章 地図の見方に付ける
# 基本＝テキストの赤線・知識の確認・標準問題で直接問われるもの（ここを全部取れば80点ライン）
# 発展＝逆引き・形の由来・テキスト外の補足・日付をまたぐ時差など
import io,sys
P=sys.argv[1]; s=io.open(P,encoding="utf-8").read()
def rep(a,b):
    global s
    assert a in s,"見つからない: "+a[:60]
    s=s.replace(a,b,1)
LEVEL={
 "mp1":"kkkkkkhhkkkkkkkk",
 "mp2":"kkkkkkkkkkhhhkk",
 "mp3":"kkkkkkkhkkhkkhhkkh",
 "mp4":"kkkkkkkk"+"hhhhh",
 "mp5":"kkkkkkkkkk"+"hhhhh",
 "mp6":"kkkkkkkkkh"+"hhhh",
 "mp7":"kkkkkhh"+"hh",
 "mp8":"".join("k" if i in (7,10,11,13,14,23,26) else "h" for i in range(29)),
 "mp9":"kkkkhkkkkhkhkk",
 "mp10":"hhhhhkkkk",
 "mp11":"kkkkkkkkkkkkhhhhkkhh",
 "mp12":"khhkkkkkkhkkkkh",
 "mp13":"kkkkkkkkkkhkkhhhh",
 "mp14":"kkkkkkkkkkkhkhhhhh",
 "mp15":"kkhhhhhhh",
}
# 長さが問題数と合っているか
import re
for sid,lv in LEVEL.items():
    m=re.search(r'\{id:"%s",from:"[^"]*",title:"[^"]*",page:"[^"]*",(?:figure:"[^"]*",)?items:\[\n(.*?)\n\]\}'%sid,s,re.S)
    n=m.group(1).count('\n')+1
    assert n==len(lv),(sid,n,len(lv))
lv_js="const LEVEL={"+",".join('"%s":"%s"'%kv for kv in LEVEL.items())+"};\n"
rep('DATA.forEach(s=>s.items.forEach((it,i)=>it.push(s.id+"-"+i)));',
    'DATA.forEach(s=>s.items.forEach((it,i)=>it.push(s.id+"-"+i)));\n'+lv_js+
    'const LV={};DATA.forEach(s=>{const l=LEVEL[s.id];if(l)s.items.forEach((it,i)=>{LV[it[2]]=l[i];});});\n'
    'function hasLevel(){return sections().some(s=>LEVEL[s.id]&&(current==="all"||s.id===current));}')
rep('function keep(k){const m=marks[k];',
    'function keep(k){if(level!=="all"&&LV[k]&&LV[k]!==level)return false;const m=marks[k];')
rep('let subject="地理", sources=[], current="all", filter="all", count=20;',
    'let subject="地理", sources=[], current="all", filter="all", count=20, level="all";')
rep('filter:filter,count:count,','filter:filter,level:level,count:count,')
rep('''          <option value="ok">◯ できた だけ</option>
        </select></span>''','''          <option value="ok">◯ できた だけ</option>
        </select></span>
        <span class="lvw" id="lvWrap" hidden><span class="lab">レベル</span>
        <span class="sel"><select id="level" aria-label="レベルを選ぶ">
          <option value="all">基本＋発展</option>
          <option value="k">基本だけ（80点ライン）</option>
          <option value="h">発展だけ</option>
        </select></span></span>''')
rep('filterSel.onchange=function(){filter=filterSel.value;refresh();};',
    'filterSel.onchange=function(){filter=filterSel.value;refresh();};\n$("level").onchange=function(){level=$("level").value;refresh();};')
rep('      if(["all","none","ng","ok"].indexOf(p.filter)>=0)filter=p.filter;',
    '      if(["all","none","ng","ok"].indexOf(p.filter)>=0)filter=p.filter;\n      if(["all","k","h"].indexOf(p.level)>=0)level=p.level;')
rep('  filterSel.value=filter;\n','  filterSel.value=filter;$("level").value=level;\n')
# レベル欄は、はんいに基本／発展つきの分野があるときだけ出す
rep('function draw(){\n  recount();','function draw(){\n  $("lvWrap").hidden=!hasLevel();$("level").value=level;\n  recount();')
# 一覧とカードに「発展」の目印
rep('  el.append(num,ask,box,mk);return el;',
    '  if(LV[it.key]==="h"){const t=document.createElement("span");t.className="lvtag";t.textContent="発展";ask.prepend(t);}\n  el.append(num,ask,box,mk);return el;')
rep('tag.className="tag";tag.textContent=(it.short?it.short+"　":"")+it.sec;',
    'tag.className="tag";tag.textContent=(it.short?it.short+"　":"")+it.sec+(LV[it.key]==="h"?"　［発展］":LV[it.key]==="k"?"　［基本］":"");')
i=s.rindex("</style>")
s=s[:i]+(".lvw{display:contents}\n"
 ".lvtag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.06em;color:var(--red);border:1px solid var(--red);border-radius:4px;padding:0 5px;margin-right:6px;line-height:1.6;vertical-align:2px}\n")+s[i:]
s=s.replace("v40 ・ 10/31更新","v41 ・ 10/31更新",1)
io.open(P,"w",encoding="utf-8").write(s)
k=sum(v.count("k") for v in LEVEL.values()); h=sum(v.count("h") for v in LEVEL.values())
print("ok 基本",k,"発展",h)
