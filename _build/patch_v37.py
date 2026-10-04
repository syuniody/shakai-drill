# -*- coding: utf-8 -*-
import io,sys
P=sys.argv[1]
s=io.open(P,encoding="utf-8").read()

CSS = """
/* おうちの人へ */
.pv{margin:20px 0 70px}
.pv .pv-top{display:flex;align-items:center;gap:12px;margin-bottom:18px}
.pv h2{font-family:var(--ff-d);font-size:26px;margin:0}
.pv .note{color:var(--ink-3);font-size:12px;margin:0 0 22px;line-height:1.7}
.pv section{border-top:1px solid var(--rule);padding:20px 0 4px}
.pv h3{font-size:15px;margin:0 0 14px;letter-spacing:.04em}
.pv .kpis{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:4px}
.pv .kpi{flex:1 1 130px;background:var(--paper-2);border-radius:14px;padding:14px 16px}
.pv .kpi b{display:block;font-size:30px;line-height:1.1;font-family:var(--ff-m);font-variant-numeric:tabular-nums}
.pv .kpi span{font-size:12px;color:var(--ink-2)}
.pv .kpi.on b{color:var(--green)}
.pv .kpi.off b{color:var(--ink-3)}
.pv .days{display:flex;gap:3px;align-items:flex-end;height:76px}
.pv .days i{flex:1;background:var(--green);border-radius:3px 3px 0 0;min-height:3px;display:block}
.pv .days i.z{background:var(--rule)}
.pv .dlab{display:flex;gap:3px;margin-top:6px}
.pv .dlab span{flex:1;text-align:center;font-size:9px;color:var(--ink-3);line-height:1.3}
.pv table{width:100%;border-collapse:collapse;font-size:13px}
.pv td,.pv th{padding:7px 4px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:middle}
.pv th{font-size:11px;color:var(--ink-3);font-weight:600}
.pv .bcell{width:38%}
.pv .bar2{background:var(--rule);border-radius:4px;height:9px;overflow:hidden;display:flex}
.pv .bar2 i{display:block;height:100%}
.pv .bar2 i.ok{background:var(--green)}
.pv .bar2 i.ng{background:var(--amber)}
.pv .num{text-align:right;white-space:nowrap;color:var(--ink-2);font-family:var(--ff-m);font-variant-numeric:tabular-nums}
.pv .em{color:var(--ink);font-weight:700}
.pv .lead{font-size:14px;line-height:1.9;margin:0 0 14px;color:var(--ink-2)}
.pv .lead b{color:var(--ink)}
.pv .none{color:var(--ink-3);font-size:13px;margin:0}
"""
i=s.rindex("</style>")
s=s[:i]+CSS+"\n"+s[i:]

# ボタン
old='<button class="btn small" id="themeBtn" type="button">背景：白</button>'
assert old in s
s=s.replace(old, old+'\n        <button class="btn small" id="parentBtn" type="button">おうちの人へ</button>',1)

JS = """
/* ---------- 学習ログ（おうちの人へ） ---------- */
const LKEY="env-drill-log";
let plog=[];try{plog=JSON.parse(localStorage.getItem(LKEY)||"[]")||[];}catch(e){plog=[];}
if(!Array.isArray(plog))plog=[];
function saveLog(){try{localStorage.setItem(LKEY,JSON.stringify(plog));}catch(e){}idbPut("log",JSON.stringify(plog));}
function dstr(t){const d=new Date(t);return d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2);}
function addLog(e){plog.push(e);if(plog.length>900)plog=plog.slice(-900);saveLog();}
function logSession(o,kind){
  let ok=0,ng=0,sk=0;
  if(kind==="card")o.items.forEach(function(it){const r=o.res[it.key];if(r==="ok")ok++;else if(r==="ng")ng++;else sk++;});
  addLog({t:Date.now(),d:dstr(Date.now()),sub:subject,range:o.range||"",n:o.items.length,ok:ok,ng:ng,sk:sk,k:kind});
}
function byDay(){
  const m={};
  plog.forEach(function(e){
    const d=e.d||dstr(e.t);
    if(!m[d])m[d]={n:0,ok:0,ng:0,s:0};
    m[d].n+=e.n||0;m[d].ok+=e.ok||0;m[d].ng+=e.ng||0;m[d].s++;
  });
  return m;
}
function streakDays(m){
  let c=0;const d=new Date();
  if(!m[dstr(d.getTime())])d.setDate(d.getDate()-1);
  while(m[dstr(d.getTime())]){c++;d.setDate(d.getDate()-1);}
  return c;
}
function progBySource(){
  const out=[];
  SOURCES.forEach(function(sc){
    let n=0,ok=0,ng=0;
    DATA.forEach(function(x){if(x.from!==sc.id)return;x.items.forEach(function(it){n++;const v=marks[it[2]];if(v==="ok")ok++;else if(v==="ng")ng++;});});
    if(n)out.push({sub:sc.subject,short:sc.short,n:n,ok:ok,ng:ng});
  });
  return out;
}
function progBySection(){
  return DATA.map(function(x){
    let ok=0,ng=0;
    x.items.forEach(function(it){const v=marks[it[2]];if(v==="ok")ok++;else if(v==="ng")ng++;});
    const sc=SRC[x.from]||{};
    return {sub:sc.subject||"",src:sc.short||"",title:x.title,n:x.items.length,ok:ok,ng:ng};
  }).filter(function(x){return x.n;});
}
function barCell(ok,ng,n){
  const td=document.createElement("td");td.className="bcell";
  const b=document.createElement("div");b.className="bar2";
  const i1=document.createElement("i");i1.className="ok";i1.style.width=(n?ok/n*100:0)+"%";
  const i2=document.createElement("i");i2.className="ng";i2.style.width=(n?ng/n*100:0)+"%";
  b.append(i1,i2);td.appendChild(b);return td;
}
function pvSection(title){
  const se=document.createElement("section");
  const h=document.createElement("h3");h.textContent=title;se.appendChild(h);return se;
}
function renderParent(){
  const wrap=document.createElement("div");wrap.className="pv";
  const top=document.createElement("div");top.className="pv-top";
  const back=document.createElement("button");back.className="btn small";back.type="button";back.textContent="← ドリルにもどる";
  back.onclick=function(){mode="list";draw();window.scrollTo({top:0});};
  const h2=document.createElement("h2");h2.textContent="おうちの人へ";
  top.append(back,h2);wrap.appendChild(top);
  const note=document.createElement("p");note.className="note";
  note.textContent="この画面は、いまお使いの端末に残っている記録だけを表示します。お子さんが別の端末で解いた分は出ません。「できた◯」「まだ△」は本人がつけたものです。";
  wrap.appendChild(note);

  const m=byDay(),today=dstr(Date.now()),td=m[today]||{n:0,ok:0,ng:0,s:0};
  // 今日
  const s1=pvSection("きょうのようす");
  const k=document.createElement("div");k.className="kpis";
  function kpi(v,lab,cls){const d=document.createElement("div");d.className="kpi"+(cls?" "+cls:"");
    const b=document.createElement("b");b.textContent=v;const sp=document.createElement("span");sp.textContent=lab;d.append(b,sp);return d;}
  k.appendChild(kpi(td.n?td.n+"問":"まだ","きょう解いた問題",td.n?"on":"off"));
  k.appendChild(kpi(td.n?Math.round(td.ok/Math.max(1,td.ok+td.ng)*100)+"%":"—","きょうの正かい率"));
  k.appendChild(kpi(streakDays(m)+"日","つづいている日数"));
  s1.appendChild(k);
  const lead=document.createElement("p");lead.className="lead";
  const last=plog.length?plog[plog.length-1]:null;
  if(!plog.length){lead.innerHTML="まだ記録がありません。1回でも最後まで解くと、ここに出ます。";}
  else if(td.n){lead.innerHTML="きょうは <b>"+td.s+"回</b>（"+td.n+"問）解いています。できた◯が <b>"+td.ok+"</b>、まだ△が <b>"+td.ng+"</b> です。";}
  else{const dd=Math.floor((Date.now()-last.t)/86400000);
    lead.innerHTML="きょうはまだ解いていません。最後に解いたのは <b>"+(dd===0?"きょう":dd===1?"きのう":dd+"日前")+"</b>（"+last.range+"）です。";}
  s1.appendChild(lead);wrap.appendChild(s1);

  // 14日
  const s2=pvSection("この2週間");
  const days=[];for(let i=13;i>=0;i--){const d=new Date();d.setDate(d.getDate()-i);days.push(dstr(d.getTime()));}
  const mx=Math.max(1,...days.map(function(d){return (m[d]||{}).n||0;}));
  const row=document.createElement("div");row.className="days";
  days.forEach(function(d){const i=document.createElement("i");const v=(m[d]||{}).n||0;
    i.style.height=Math.round(v/mx*100)+"%";if(!v)i.className="z";i.title=d+"　"+v+"問";row.appendChild(i);});
  const lab=document.createElement("div");lab.className="dlab";
  days.forEach(function(d,ix){const sp=document.createElement("span");sp.textContent=(ix%2===0||ix===13)?(+d.slice(8,10))+"":"";lab.appendChild(sp);});
  const tot=days.reduce(function(a,d){return a+((m[d]||{}).n||0);},0);
  const dn=days.filter(function(d){return m[d];}).length;
  const l2=document.createElement("p");l2.className="lead";
  l2.innerHTML="2週間で <b>"+dn+"日</b>・<b>"+tot+"問</b> 解いています。";
  s2.append(row,lab,l2);wrap.appendChild(s2);

  // 教科ごと
  const s3=pvSection("教科ごとの進みぐあい");
  const byS={};progBySource().forEach(function(p){const o=byS[p.sub]=byS[p.sub]||{n:0,ok:0,ng:0};o.n+=p.n;o.ok+=p.ok;o.ng+=p.ng;});
  const t3=document.createElement("table");
  Object.keys(byS).forEach(function(sb){
    const p=byS[sb],tr=document.createElement("tr");
    const c1=document.createElement("td");c1.className="em";c1.textContent=sb;
    tr.append(c1,barCell(p.ok,p.ng,p.n));
    const c3=document.createElement("td");c3.className="num";c3.textContent=p.ok+" / "+p.n+"　("+Math.round(p.ok/p.n*100)+"%)";
    tr.appendChild(c3);t3.appendChild(tr);
  });
  const lg=document.createElement("p");lg.className="note";lg.style.margin="12px 0 0";
  lg.textContent="緑＝できた◯、オレンジ＝まだ△、灰色＝まだ解いていない問題です。";
  s3.append(t3,lg);wrap.appendChild(s3);

  // はんいごと
  const s4=pvSection("はんい（出典）ごとの進みぐあい");
  const ps=progBySource().filter(function(p){return p.ok+p.ng>0;}).sort(function(a,b){return (b.ok+b.ng)/b.n-(a.ok+a.ng)/a.n;});
  if(!ps.length){const p=document.createElement("p");p.className="none";p.textContent="まだ手をつけたはんいがありません。";s4.appendChild(p);}
  else{
    const t4=document.createElement("table");
    const hr=document.createElement("tr");["はんい","進みぐあい","できた"].forEach(function(x){const th=document.createElement("th");th.textContent=x;hr.appendChild(th);});
    t4.appendChild(hr);
    ps.forEach(function(p){
      const tr=document.createElement("tr");
      const c1=document.createElement("td");c1.textContent=p.short;
      tr.append(c1,barCell(p.ok,p.ng,p.n));
      const c3=document.createElement("td");c3.className="num";c3.textContent=p.ok+" / "+p.n;
      tr.appendChild(c3);t4.appendChild(tr);
    });
    s4.appendChild(t4);
  }
  wrap.appendChild(s4);

  // 苦手
  const s5=pvSection("つまずいているところ（△が多い順）");
  const ng=progBySection().filter(function(x){return x.ng>0;}).sort(function(a,b){return b.ng-a.ng;}).slice(0,10);
  if(!ng.length){const p=document.createElement("p");p.className="none";p.textContent="△のついた問題はまだありません。";s5.appendChild(p);}
  else{
    const t5=document.createElement("table");
    const hr=document.createElement("tr");["分野","","△の数"].forEach(function(x){const th=document.createElement("th");th.textContent=x;hr.appendChild(th);});
    t5.appendChild(hr);
    ng.forEach(function(x){
      const tr=document.createElement("tr");
      const c1=document.createElement("td");c1.textContent=x.title;
      tr.append(c1,barCell(x.ok,x.ng,x.n));
      const c3=document.createElement("td");c3.className="num";c3.textContent=x.ng+"問";
      tr.appendChild(c3);t5.appendChild(tr);
    });
    const tip=document.createElement("p");tip.className="note";tip.style.margin="12px 0 0";
    tip.textContent="「しぼりこみ」を『△ まだ だけ』にすると、ここだけを出題できます。";
    s5.append(t5,tip);
  }
  wrap.appendChild(s5);

  // 最近
  const s6=pvSection("さいきん解いたもの");
  if(!plog.length){const p=document.createElement("p");p.className="none";p.textContent="まだありません。";s6.appendChild(p);}
  else{
    const t6=document.createElement("table");
    const hr=document.createElement("tr");["いつ","はんい","問題数","できた"].forEach(function(x){const th=document.createElement("th");th.textContent=x;hr.appendChild(th);});
    t6.appendChild(hr);
    plog.slice(-12).reverse().forEach(function(e){
      const tr=document.createElement("tr");
      const dt=new Date(e.t);
      const c1=document.createElement("td");c1.textContent=(dt.getMonth()+1)+"/"+dt.getDate()+" "+dt.getHours()+":"+("0"+dt.getMinutes()).slice(-2);
      const c2=document.createElement("td");c2.textContent=(e.k==="flash"?"［フラッシュ］":"")+(e.range||e.sub||"");
      const c3=document.createElement("td");c3.className="num";c3.textContent=(e.n||0)+"問";
      const c4=document.createElement("td");c4.className="num";c4.textContent=e.k==="flash"?"—":(e.ok+" / "+(e.ok+e.ng));
      tr.append(c1,c2,c3,c4);t6.appendChild(tr);
    });
    s6.appendChild(t6);
  }
  wrap.appendChild(s6);

  // 合計
  const s7=pvSection("これまでの合計");
  const all=plog.reduce(function(a,e){a.n+=e.n||0;a.ok+=e.ok||0;a.ng+=e.ng||0;return a;},{n:0,ok:0,ng:0});
  const k7=document.createElement("div");k7.className="kpis";
  k7.appendChild(kpi(all.n+"問","これまでに解いた"));
  k7.appendChild(kpi(Object.keys(m).length+"日","解いた日数"));
  const pr=progBySource().reduce(function(a,p){a.n+=p.n;a.ok+=p.ok;return a;},{n:0,ok:0});
  k7.appendChild(kpi(pr.ok+"問","いま「できた◯」の数"));
  s7.appendChild(k7);wrap.appendChild(s7);

  listEl.appendChild(wrap);
}
"""
k="function draw(){"
i=s.index(k)
s=s[:i]+JS+"\n"+s[i:]

# draw() に parent を足す
o1="  barEl.hidden=playing;\n  listEl.hidden=playing;"
assert o1 in s
s=s.replace(o1,'  barEl.hidden=playing||mode==="parent";\n  listEl.hidden=playing;',1)
o2='  listEl.replaceChildren();\n'
i=s.index("function draw(){"); j=s.index(o2,i)
s=s[:j+len(o2)]+'  if(mode==="parent"){renderParent();updateFab();updateResume();updateNotices();return;}\n'+s[j+len(o2):]

# セッション終了でログ
o3='  sess.i++;saveSess();renderPlay();tally();\n}'
assert o3 in s
s=s.replace(o3,'  sess.i++;\n  if(sess.i>=sess.items.length&&!sess.logged){sess.logged=1;logSession(sess,"card");}\n  saveSess();renderPlay();tally();\n}',1)

# フラッシュ終了でログ
o4='  if(fl.phase==="end"){\n'
assert o4 in s
s=s.replace(o4,'  if(fl.phase==="end"){\n    if(!fl.logged){fl.logged=1;logSession(fl,"flash");}\n',1)

# ボタン
o5='draw();\nif(!Object.keys(marks).length){'
assert o5 in s
s=s.replace(o5,'$("parentBtn").onclick=function(){mode="parent";draw();window.scrollTo({top:0});};\n'+o5,1)

# IndexedDB からログを復元
o6='      draw();\n    }\n  });\n}\n</script>'
assert o6 in s
s=s.replace(o6,'      draw();\n    }\n  });\n}\nif(!plog.length){\n  idbGet("log").then(function(v){\n    let d=null;try{d=JSON.parse(v||"null");}catch(e){}\n    if(Array.isArray(d)&&d.length){plog=d;try{localStorage.setItem(LKEY,JSON.stringify(plog));}catch(e){}if(mode==="parent")draw();}\n  });\n}\n</script>',1)

io.open(P,"w",encoding="utf-8").write(s)
print("ok")
