import io
s=io.open("/tmp/v30.html",encoding="utf-8").read()
s=s[s.index("<title>"):]; s=s[:s.rindex("</body>")].rstrip()+"\n"
assert "v30" in s and "flashWrap" not in s and "startFlash" not in s
def rep(a,b):
    global s
    assert s.count(a)==1,"COUNT %d: %s"%(s.count(a),a[:80])
    s=s.replace(a,b,1)

# ---------- CSS ----------
rep(".result{max-width:720px;","""/* フラッシュ暗記 */
.fl-top{display:flex;align-items:center;gap:10px 12px;padding:14px 0 6px;font-size:14px;color:var(--ink-2);flex-wrap:wrap}
.fl-top .ctr{margin-left:auto;font-family:var(--ff-m);font-size:14px;color:var(--ink-3);font-variant-numeric:tabular-nums}
.fl-card{border:1px solid var(--rule-2);border-radius:18px;background:var(--paper-2);padding:26px 22px;max-width:720px;margin:0 auto;min-height:48vh;display:flex;flex-direction:column;justify-content:center;gap:18px}
.fl-tag{font-size:12.5px;color:var(--ink-3);letter-spacing:.04em;margin:0}
.fl-q{margin:0;font-size:clamp(20px,5.2vw,27px);line-height:1.75;font-weight:500;text-wrap:pretty}
.fl-a{margin:0;font-size:clamp(22px,6vw,32px);line-height:1.7;font-weight:700;color:var(--red-ink);min-height:1.7em;opacity:0;transition:opacity .12s linear}
.fl-a.show{opacity:1}
.fl-bar{height:5px;background:var(--paper-3);border-radius:999px;overflow:hidden;margin:2px 0 16px}
.fl-bar i{display:block;height:100%;width:0;background:var(--ink);transition:width .2s linear}
.fl-ctrl{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:10px;margin-top:16px;max-width:720px;margin-left:auto;margin-right:auto}
.fl-ctrl .btn{min-width:84px}
.fl-speed{display:flex;flex-wrap:wrap;align-items:center;gap:8px;justify-content:center;margin-top:12px}
.fl-note{text-align:center;font-size:12.5px;color:var(--ink-3);margin:12px auto 0;max-width:720px}
.fl-map{margin:0 auto;max-width:460px}
.fl-map .cmap,.fl-map .jpmap{max-height:34vh;width:auto;max-width:100%}
@media (max-width:720px){.fl-card{padding:20px 16px;min-height:44vh}}
.result{max-width:720px;""")

# ---------- HTML：ボタンを1つ足す ----------
rep('        <button class="btn primary big" id="start" type="button">はじめる</button>',
    '        <button class="btn primary big" id="start" type="button">はじめる</button>\n        <button class="btn big" id="flashStart" type="button">フラッシュ暗記</button>')

# ---------- JS ----------
rep('let mode="list", sess=null;','let mode="list", sess=null, fl=null, flTimer=null;')
# 速さの設定を保存に含める
rep('function savePrefs(){try{localStorage.setItem(PKEY,JSON.stringify({subject:subject,sources:sources,current:current,filter:filter,count:count}));}catch(e){}}',
    'let flSpeed=1;\nfunction savePrefs(){try{localStorage.setItem(PKEY,JSON.stringify({subject:subject,sources:sources,current:current,filter:filter,count:count,flSpeed:flSpeed}));}catch(e){}}')
rep('      if(COUNTS.indexOf(p.count)>=0)count=p.count;','      if(COUNTS.indexOf(p.count)>=0)count=p.count;\n      if([0,1,2,3].indexOf(p.flSpeed)>=0)flSpeed=p.flSpeed;')

# 本体
rep('function startSession(items){','''const FLSP=[{name:"ゆっくり",q:3200,a:2600},{name:"ふつう",q:2200,a:1800},{name:"はやい",q:1500,a:1200},{name:"とてもはやい",q:1000,a:900}];
function startFlash(items){
  if(!items.length){mode="list";draw();return;}
  fl={items:items,i:0,phase:"q",paused:false,range:rangeText()};
  mode="flash";
  try{if(!(history.state&&history.state.v==="card"))history.pushState({v:"card"},"");}catch(e){}
  draw();
  flTick();
  window.scrollTo({top:$("masthead").offsetHeight-8,behavior:"smooth"});
}
function flClear(){clearTimeout(flTimer);flTimer=null;}
function flTick(){
  flClear();
  if(!fl||fl.paused)return;
  const sp=FLSP[flSpeed];
  if(fl.phase==="q")flTimer=setTimeout(function(){fl.phase="a";renderFlash();flTick();},sp.q);
  else flTimer=setTimeout(function(){
    if(fl.i+1>=fl.items.length){fl.phase="end";renderFlash();return;}
    fl.i++;fl.phase="q";renderFlash();flTick();
  },sp.a);
}
function flGo(d){
  if(!fl)return;
  flClear();
  if(fl.phase==="end"&&d<0){fl.phase="a";renderFlash();return;}
  const ni=fl.i+d;
  if(ni<0||ni>=fl.items.length)return;
  fl.i=ni;fl.phase="q";renderFlash();flTick();
}
function flPause(on){
  if(!fl)return;
  fl.paused=on;
  if(on)flClear();else flTick();
  renderFlash();
}
function renderFlash(){
  playEl.replaceChildren();
  if(!fl)return;
  const n=fl.items.length;
  const top=document.createElement("div");top.className="fl-top";
  const back=document.createElement("button");back.className="link";back.type="button";back.textContent="← 設定にもどる";
  back.onclick=function(){flClear();fl=null;goList();};
  const range=document.createElement("span");range.className="range";range.textContent=fl.range;
  const ctr=document.createElement("span");ctr.className="ctr";ctr.textContent=(fl.phase==="end"?n:fl.i+1)+" / "+n;
  top.append(back,range,ctr);
  const bar=document.createElement("div");bar.className="fl-bar";
  const bi=document.createElement("i");bi.style.width=((fl.phase==="end"?n:fl.i)/n*100)+"%";bar.appendChild(bi);
  playEl.append(top,bar);

  if(fl.phase==="end"){
    const box=document.createElement("section");box.className="result";
    const h=document.createElement("h2");h.textContent=n+"問 おわり！";
    const p=fmsgFlash("同じはんいでもう一度見るか、設定にもどれます。");
    const acts=document.createElement("div");acts.className="actions";
    const again=document.createElement("button");again.className="btn primary big";again.type="button";again.textContent="同じ問題をもう一回";
    again.onclick=function(){fl.i=0;fl.phase="q";renderFlash();flTick();};
    const other=document.createElement("button");other.className="btn big";other.type="button";other.textContent="べつの問題で";
    other.onclick=function(){startFlash(pickItems());};
    const toCard=document.createElement("button");toCard.className="btn";toCard.type="button";toCard.textContent="1問ずつ答える";
    toCard.onclick=function(){const it=fl.items.slice();flClear();fl=null;startSession(it);};
    acts.append(again,other,toCard);
    box.append(h,p,acts);
    playEl.appendChild(box);
    return;
  }

  const it=fl.items[fl.i];
  const card=document.createElement("section");card.className="fl-card";
  const tag=document.createElement("p");tag.className="fl-tag";tag.textContent=(it.short?it.short+"　":"")+it.sec;
  const q=document.createElement("p");q.className="fl-q";q.appendChild(rubyFrag(it.q));
  card.append(tag,q);
  if(it.fig){const mb=mapNode(it.fig);mb.classList.add("fl-map");card.appendChild(mb);}
  const a=document.createElement("p");a.className="fl-a"+(fl.phase==="a"?" show":"");
  a.appendChild(rubyFrag(it.a));
  card.appendChild(a);
  playEl.appendChild(card);

  const ctrl=document.createElement("div");ctrl.className="fl-ctrl";
  const prev=document.createElement("button");prev.className="btn";prev.type="button";prev.textContent="← まえ";prev.disabled=(fl.i===0);
  prev.onclick=function(){flGo(-1);};
  const pause=document.createElement("button");pause.className="btn primary";pause.type="button";pause.textContent=fl.paused?"さいせい":"一時停止";
  pause.onclick=function(){flPause(!fl.paused);};
  const next=document.createElement("button");next.className="btn";next.type="button";next.textContent="つぎ →";
  next.onclick=function(){if(fl.phase==="q"){flClear();fl.phase="a";renderFlash();flTick();}else flGo(1);};
  ctrl.append(prev,pause,next);
  playEl.appendChild(ctrl);

  const sp=document.createElement("div");sp.className="fl-speed";
  const lab=document.createElement("span");lab.className="lab";lab.textContent="はやさ";sp.appendChild(lab);
  FLSP.forEach(function(x,i){
    const b=document.createElement("button");b.className="tab";b.type="button";
    b.setAttribute("aria-selected",String(i===flSpeed));b.textContent=x.name;
    b.onclick=function(){flSpeed=i;savePrefs();renderFlash();flTick();};
    sp.appendChild(b);
  });
  playEl.appendChild(sp);
  const note=document.createElement("p");note.className="fl-note";
  note.textContent="画面を見ているだけで、問題と答えが順に出ます。◯△の記録はつきません。";
  playEl.appendChild(note);
}
function fmsgFlash(t){const p=document.createElement("p");p.style.color="var(--ink-2)";p.style.margin="0 0 18px";p.textContent=t;return p;}
function startSession(items){''')

# 画面の出し分け
rep('''  document.body.classList.toggle("playing",mode==="card");
  barEl.hidden=(mode==="card");
  listEl.hidden=(mode==="card");
  playEl.hidden=(mode!=="card");
  if(mode==="card"){renderPlay();tally();updateFab();updateResume();updateNotices();return;}''',
'''  const playing=(mode==="card"||mode==="flash");
  document.body.classList.toggle("playing",playing);
  barEl.hidden=playing;
  listEl.hidden=playing;
  playEl.hidden=!playing;
  if(mode==="flash"){renderFlash();tally();updateFab();updateResume();updateNotices();return;}
  if(mode==="card"){renderPlay();tally();updateFab();updateResume();updateNotices();return;}''')
rep('function refresh(){savePrefs();if(mode==="card"){mode="list";}draw();}',
    'function refresh(){savePrefs();if(mode==="card"||mode==="flash"){flClear();fl=null;mode="list";}draw();}')
rep('''window.addEventListener("popstate",function(e){
  if(e.state&&e.state.v==="card"){''','''window.addEventListener("popstate",function(e){
  if(mode==="flash"&&!(e.state&&e.state.v==="card")){flClear();fl=null;mode="list";draw();return;}
  if(e.state&&e.state.v==="card"){''')
rep('$("start").onclick=function(){startSession(pickItems());};',
'''$("start").onclick=function(){startSession(pickItems());};
$("flashStart").onclick=function(){startFlash(pickItems());};''')
# キー操作：フラッシュ中はスペースで一時停止、矢印で前後
rep('''document.addEventListener("keydown",function(e){
  if(mode!=="card"||!sess||sess.i>=sess.items.length)return;''','''document.addEventListener("keydown",function(e){
  if(mode==="flash"&&fl){
    const tag=(e.target&&e.target.tagName)||"";if(tag==="TEXTAREA"||tag==="INPUT"||tag==="SELECT")return;
    if(e.key===" "){e.preventDefault();flPause(!fl.paused);}
    else if(e.key==="ArrowRight"){e.preventDefault();flGo(1);}
    else if(e.key==="ArrowLeft"){e.preventDefault();flGo(-1);}
    return;
  }
  if(mode!=="card"||!sess||sess.i>=sess.items.length)return;''')
# 一覧へ戻る各所でタイマーを止める
rep('$("showList").onclick=function(){mode="list";draw();listEl.scrollIntoView({behavior:"smooth",block:"start"});};',
    '$("showList").onclick=function(){flClear();fl=null;mode="list";draw();listEl.scrollIntoView({behavior:"smooth",block:"start"});};')
rep("v30 ・ 10/2更新","v32 ・ 10/2更新")
io.open("kankyo-drill.html","w",encoding="utf-8").write(s); io.open("env-drill.html","w",encoding="utf-8").write(s)
i=s.rindex("<script>"); io.open("check.js","w",encoding="utf-8").write(s[i+8:s.rindex("</script>")])
print("built",len(s))
