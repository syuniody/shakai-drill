# -*- coding: utf-8 -*-
import io,sys
P=sys.argv[1]
s=io.open(P,encoding="utf-8").read()
def rep(a,b,n=1):
    global s
    assert a in s, "見つからない: "+a[:60]
    s=s.replace(a,b,n)

# --- CSS ---
CSS = """
.pv .sync{background:var(--paper-2);border-radius:14px;padding:16px 18px}
.pv .sync p{margin:0 0 12px;font-size:13px;line-height:1.9;color:var(--ink-2)}
.pv .sync .urlrow{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
.pv .sync input{flex:1 1 220px;min-width:0;font-family:var(--ff-m);font-size:12px;padding:9px 10px;border:1px solid var(--rule-2);border-radius:9px;background:var(--paper);color:var(--ink)}
.pv .sync .st{font-size:12px;color:var(--ink-3);margin:10px 0 0}
.pv .remote{background:var(--green-soft);border-radius:12px;padding:12px 14px;font-size:13px;line-height:1.8;margin:0 0 20px;color:var(--ink)}
.pv .err{background:var(--amber-soft);border-radius:12px;padding:12px 14px;font-size:13px;margin:0 0 20px}
"""
i=s.rindex("</style>"); s=s[:i]+CSS+"\n"+s[i:]

# --- 同期のしくみ ---
JS = """
/* ---------- 同期（おうちの人のスマホで見る） ---------- */
const SYNC_URL="https://drill-sync.oda-9b7.workers.dev";
const SYKEY="env-drill-sync";
const PIDRE=/^[a-z0-9]{16,40}$/;
let pvData=null, pvLoading=false, pvErr=null, pvPushing=false;
function syncCfg(){try{return JSON.parse(localStorage.getItem(SYKEY)||"null");}catch(e){return null;}}
function setSyncCfg(c){try{c?localStorage.setItem(SYKEY,JSON.stringify(c)):localStorage.removeItem(SYKEY);}catch(e){}}
function newId(){
  let a=new Uint8Array(16);
  try{crypto.getRandomValues(a);}catch(e){for(let i=0;i<16;i++)a[i]=Math.floor(Math.random()*256);}
  let o="";for(let i=0;i<16;i++)o+=("0"+a[i].toString(16)).slice(-2);
  return o.slice(0,20);
}
function secCounts(){
  const o={};
  DATA.forEach(function(x){let ok=0,ng=0;x.items.forEach(function(it){const v=marks[it[2]];if(v==="ok")ok++;else if(v==="ng")ng++;});if(ok||ng)o[x.id]=[ok,ng];});
  return o;
}
function pvSec(){return pvData?(pvData.sec||{}):secCounts();}
function pvLog(){return pvData?(pvData.log||[]):plog;}
function parentUrl(id){return location.origin+location.pathname+"?p="+id;}
function pushSync(){
  const c=syncCfg();
  if(!c||!c.id||pvData||pvPushing)return Promise.resolve(false);
  pvPushing=true;
  const body=JSON.stringify({v:1,t:Date.now(),sec:secCounts(),log:plog.slice(-300)});
  return fetch(SYNC_URL+"/p?k="+encodeURIComponent(c.id),{method:"POST",headers:{"Content-Type":"text/plain"},body:body})
    .then(function(r){pvPushing=false;if(r.ok){c.last=Date.now();setSyncCfg(c);if(mode==="parent")draw();}return r.ok;})
    .catch(function(){pvPushing=false;return false;});
}
function whenStr(t){
  if(!t)return "まだ送っていません";
  const d=new Date(t),n=new Date();
  const same=d.toDateString()===n.toDateString();
  return (same?"きょう ":(d.getMonth()+1)+"/"+d.getDate()+" ")+d.getHours()+":"+("0"+d.getMinutes()).slice(-2);
}
function syncNode(){
  const se=pvSection("おうちの人のスマホで見る");
  const box=document.createElement("div");box.className="sync";
  const c=syncCfg();
  if(!c||!c.id){
    const p=document.createElement("p");
    p.textContent="この端末の記録を、おうちの人のスマホからも見られるようにできます。ボタンを押すと専用のURLができます。送るのは「分野ごとにいくつ◯△がついたか」と「いつ何問解いたか」だけで、名前などは送りません。";
    const b=document.createElement("button");b.className="btn primary small";b.type="button";b.textContent="専用URLをつくる";
    b.onclick=function(){
      const cc={id:newId(),last:0};setSyncCfg(cc);
      b.disabled=true;b.textContent="送信中…";
      pushSync().then(function(){draw();});
    };
    box.append(p,b);
  }else{
    const p=document.createElement("p");
    p.textContent="このURLをおうちの人のスマホで開くと、いまの状況が見られます。解き終わるたびに自動で送られます。";
    const row=document.createElement("div");row.className="urlrow";
    const inp=document.createElement("input");inp.type="text";inp.readOnly=true;inp.value=parentUrl(c.id);
    inp.onclick=function(){inp.select();};
    const cp=document.createElement("button");cp.className="btn primary small";cp.type="button";cp.textContent="URLをコピー";
    cp.onclick=function(){
      const done=function(){cp.textContent="コピーしました";setTimeout(function(){cp.textContent="URLをコピー";},1800);};
      if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(inp.value).then(done,function(){inp.select();document.execCommand("copy");done();});
      else{inp.select();document.execCommand("copy");done();}
    };
    row.append(inp,cp);
    const row2=document.createElement("div");row2.className="urlrow";
    const now=document.createElement("button");now.className="btn small";now.type="button";now.textContent="いますぐ送る";
    now.onclick=function(){now.disabled=true;now.textContent="送信中…";pushSync().then(function(ok){now.disabled=false;now.textContent=ok?"送りました":"送れませんでした";setTimeout(function(){now.textContent="いますぐ送る";},1800);draw();});};
    const off=document.createElement("button");off.className="btn small";off.type="button";off.textContent="同期をやめる";
    const cf=document.createElement("span");cf.className="confirm";cf.hidden=true;
    const ask=document.createElement("span");ask.className="ask-del";ask.textContent="やめていいですか。";
    const yes=document.createElement("button");yes.className="btn small danger";yes.type="button";yes.textContent="はい";
    const no=document.createElement("button");no.className="btn small";no.type="button";no.textContent="やめる";
    yes.onclick=function(){setSyncCfg(null);draw();};
    no.onclick=function(){cf.hidden=true;off.hidden=false;};
    off.onclick=function(){off.hidden=true;cf.hidden=false;};
    cf.append(ask,yes,no);
    row2.append(now,off,cf);
    const st=document.createElement("p");st.className="st";
    st.textContent="最後に送ったのは "+whenStr(c.last)+"　／　URLを知っている人だけが見られます。人に渡さないでください。";
    box.append(p,row,row2,st);
  }
  se.appendChild(box);return se;
}
"""
rep("function renderParent(){", JS+"\nfunction renderParent(){")

# --- 集計を「ローカル or 同期データ」で切りかえる ---
rep('  plog.forEach(function(e){\n    const d=e.d||dstr(e.t);','  pvLog().forEach(function(e){\n    const d=e.d||dstr(e.t);')
rep("""function progBySource(){
  const out=[];
  SOURCES.forEach(function(sc){
    let n=0,ok=0,ng=0;
    DATA.forEach(function(x){if(x.from!==sc.id)return;x.items.forEach(function(it){n++;const v=marks[it[2]];if(v==="ok")ok++;else if(v==="ng")ng++;});});
    if(n)out.push({sub:sc.subject,short:sc.short,n:n,ok:ok,ng:ng});
  });
  return out;
}""","""function progBySource(){
  const C=pvSec(),out=[];
  SOURCES.forEach(function(sc){
    let n=0,ok=0,ng=0;
    DATA.forEach(function(x){if(x.from!==sc.id)return;const c=C[x.id]||[0,0];n+=x.items.length;ok+=c[0];ng+=c[1];});
    if(n)out.push({sub:sc.subject,short:sc.short,n:n,ok:ok,ng:ng});
  });
  return out;
}""")
rep("""function progBySection(){
  return DATA.map(function(x){
    let ok=0,ng=0;
    x.items.forEach(function(it){const v=marks[it[2]];if(v==="ok")ok++;else if(v==="ng")ng++;});
    const sc=SRC[x.from]||{};
    return {sub:sc.subject||"",src:sc.short||"",title:x.title,n:x.items.length,ok:ok,ng:ng};
  }).filter(function(x){return x.n;});
}""","""function progBySection(){
  const C=pvSec();
  return DATA.map(function(x){
    const c=C[x.id]||[0,0],sc=SRC[x.from]||{};
    return {sub:sc.subject||"",src:sc.short||"",title:x.title,n:x.items.length,ok:c[0],ng:c[1]};
  }).filter(function(x){return x.n;});
}""")

# --- renderParent 内の plog 参照を切りかえ、同期の見出しを足す ---
rep('''  const h2=document.createElement("h2");h2.textContent="おうちの人へ";
  top.append(back,h2);wrap.appendChild(top);
  const note=document.createElement("p");note.className="note";
  note.textContent="この画面は、いまお使いの端末に残っている記録だけを表示します。お子さんが別の端末で解いた分は出ません。「できた◯」「まだ△」は本人がつけたものです。";
  wrap.appendChild(note);
''','''  const h2=document.createElement("h2");h2.textContent="おうちの人へ";
  if(pvData||pvLoading||pvErr)back.textContent="← このドリルを開く";
  top.append(back,h2);wrap.appendChild(top);
  if(pvLoading){const l=document.createElement("p");l.className="remote";l.textContent="記録を読み込んでいます…";wrap.appendChild(l);listEl.appendChild(wrap);return;}
  if(pvErr){const e=document.createElement("p");e.className="err";e.textContent=pvErr;wrap.appendChild(e);listEl.appendChild(wrap);return;}
  const note=document.createElement("p");note.className="note";
  if(pvData){
    const r=document.createElement("p");r.className="remote";
    r.textContent="お子さんの端末から送られてきた記録です。最終更新："+whenStr(pvData.t||pvData.srv);
    wrap.appendChild(r);
    note.textContent="「できた◯」「まだ△」は本人がつけたものです。この画面は読むだけで、記録は変わりません。";
  }else{
    note.textContent="この画面は、いまお使いの端末に残っている記録だけを表示します。「できた◯」「まだ△」は本人がつけたものです。";
  }
  wrap.appendChild(note);
  const L=pvLog();
''')
rep('  const last=plog.length?plog[plog.length-1]:null;\n  if(!plog.length){','  const last=L.length?L[L.length-1]:null;\n  if(!L.length){')
rep('  if(!plog.length){const p=document.createElement("p");p.className="none";p.textContent="まだありません。";s6.appendChild(p);}',
    '  if(!L.length){const p=document.createElement("p");p.className="none";p.textContent="まだありません。";s6.appendChild(p);}')
rep('    plog.slice(-12).reverse().forEach(function(e){','    L.slice(-12).reverse().forEach(function(e){')
rep('  const all=plog.reduce(','  const all=L.reduce(')
# 同期セクションを「これまでの合計」の前に
rep('  // 合計\n  const s7=pvSection("これまでの合計");','  if(!pvData)wrap.appendChild(syncNode());\n\n  // 合計\n  const s7=pvSection("これまでの合計");')

# --- 解き終わったら送る ---
rep('function addLog(e){plog.push(e);if(plog.length>900)plog=plog.slice(-900);saveLog();}',
    'function addLog(e){plog.push(e);if(plog.length>900)plog=plog.slice(-900);saveLog();try{pushSync();}catch(x){}}')

# --- 起動時：?p= があれば同期データを読む／なければ古ければ送る ---
rep('$("parentBtn").onclick=function(){mode="parent";draw();window.scrollTo({top:0});};',
'''$("parentBtn").onclick=function(){mode="parent";draw();window.scrollTo({top:0});};
(function(){
  let p="";try{p=(new URLSearchParams(location.search).get("p")||"").toLowerCase();}catch(e){}
  if(PIDRE.test(p)){
    mode="parent";pvLoading=true;draw();
    fetch(SYNC_URL+"/g?k="+encodeURIComponent(p)).then(function(r){return r.ok?r.json():null;}).then(function(d){
      pvLoading=false;
      if(d&&d.sec){pvData=d;}else{pvErr="まだ記録が届いていません。お子さんの端末で1回解き終わると届きます。";}
      draw();
    }).catch(function(){pvLoading=false;pvErr="記録を読み込めませんでした。通信の状態をご確認ください。";draw();});
    return;
  }
  const c=syncCfg();
  if(c&&c.id&&Date.now()-(c.last||0)>2*3600*1000)setTimeout(function(){pushSync();},1500);
})();''')
io.open(P,"w",encoding="utf-8").write(s)
print("ok")
