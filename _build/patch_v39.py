# -*- coding: utf-8 -*-
import io,sys
P=sys.argv[1]; s=io.open(P,encoding="utf-8").read()
def rep(a,b):
    global s
    assert a in s,"見つからない: "+a[:60]
    s=s.replace(a,b,1)

# テストのはんいをまとめて選ぶプリセット
rep('function drawSources(){','''const PRESETS={"歴史":[
  {name:"原始時代（旧石器・縄文・弥生）",ids:["hi34","hi35","hi36"]},
  {name:"古墳時代",ids:["hi37"]},
  {name:"飛鳥時代",ids:["hi38","hi39","hi40"]},
  {name:"奈良時代",ids:["hi41","hi42"]},
  {name:"平安時代",ids:["hi43","hi44","hi45"]},
  {name:"鎌倉時代",ids:["hi46"]}
]};
function headRow(t){const d=document.createElement("div");d.className="opt head";d.textContent=t;return d;}
function presetRows(){
  const ps=PRESETS[subject]||[];
  if(!ps.length)return [];
  const out=[headRow("テストのはんい（まとめて選ぶ）")];
  ps.forEach(function(p){
    const n=p.ids.reduce(function(a,id){return a+DATA.filter(d=>d.from===id).reduce((b,d)=>b+d.items.length,0);},0);
    const on=p.ids.length===sources.length&&p.ids.every(function(id){return sources.indexOf(id)>=0;});
    out.push(optRow(p.name,n,on,function(){sources=on?[]:p.ids.slice();current="all";refresh();}));
  });
  out.push(headRow("単元ごとに選ぶ"));
  return out;
}
function drawSources(){''')
rep('''  srcPop.replaceChildren(
    optRow("すべて",total,!sources.length,function(){sources=[];current="all";refresh();}),''',
'''  srcPop.replaceChildren(
    optRow("すべて",total,!sources.length,function(){sources=[];current="all";refresh();}),
    ...presetRows(),''')
i=s.rindex("</style>")
s=s[:i]+".opt.head{display:block;font-size:11px;letter-spacing:.08em;color:var(--ink-3);padding:12px 12px 4px;min-height:0;font-weight:700;cursor:default}\n.opt.head:hover{background:transparent}\n"+s[i:]
s=s.replace("v38 ・ 10/4更新","v39 ・ 10/10更新",1)
io.open(P,"w",encoding="utf-8").write(s); print("ok")
