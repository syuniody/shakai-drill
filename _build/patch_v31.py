import io,os,re
dep=os.path.expanduser("~/Desktop/shakai-drill-deploy/jp9pyw1wu4/index.html")
s=io.open(dep,encoding="utf-8").read()
s=s[s.index("<title>"):]; s=s[:s.rindex("</body>")].rstrip()+"\n"
assert "v30" in s and "flashWrap" not in s
def rep(a,b):
    global s
    assert s.count(a)==1,"COUNT %d: %s"%(s.count(a),a[:80])
    s=s.replace(a,b,1)

# ---------- CSS ----------
rep("#hud{position:fixed;", """/* フラッシュ暗算 */
#flashWrap{max-width:720px;margin:0 auto}
.fset{display:flex;flex-direction:column;gap:12px;padding:18px 0 4px}
.frow{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px}
.frow .lab{min-width:3.6em}
.fstage{
  margin:18px auto 0;max-width:720px;min-height:46vh;border:1px solid var(--rule-2);border-radius:18px;
  background:var(--paper-2);display:grid;place-items:center;padding:20px;position:relative;
}
.fnum{font-family:var(--ff-m);font-weight:700;font-size:clamp(64px,22vw,140px);line-height:1;color:var(--ink);font-variant-numeric:tabular-nums;letter-spacing:.02em}
.fnum.minus{color:var(--red)}
.fcount{font-family:var(--ff-d);font-size:clamp(56px,18vw,120px);color:var(--ink-3)}
.fmsg{font-size:17px;color:var(--ink-2);text-align:center;line-height:1.9}
.fbadge{position:absolute;top:12px;right:16px;font-family:var(--ff-m);font-size:13px;color:var(--ink-3)}
.fans{display:flex;flex-direction:column;align-items:center;gap:14px;margin-top:18px}
.finput{
  font-family:var(--ff-m);font-size:40px;font-weight:700;text-align:center;letter-spacing:.06em;
  width:100%;max-width:340px;padding:10px 14px;border:2px solid var(--rule-2);border-radius:12px;
  background:var(--paper);color:var(--ink);font-variant-numeric:tabular-nums;min-height:66px;
}
.finput.ok{border-color:var(--green);color:var(--green)}
.finput.ng{border-color:var(--red);color:var(--red)}
.keypad{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;width:100%;max-width:340px}
.key{font:inherit;font-family:var(--ff-m);font-size:26px;font-weight:700;min-height:62px;border-radius:12px;border:1px solid var(--rule-2);background:var(--paper-2);color:var(--ink);cursor:pointer}
.key:active{background:var(--paper-3)}
.key.wide{grid-column:span 2}
.key.go{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.key.del{color:var(--red)}
.fhist{font-size:13px;color:var(--ink-3);margin:14px 0 0;line-height:1.9}
.freview{margin-top:14px;font-family:var(--ff-m);font-size:15px;color:var(--ink-2);line-height:2;word-break:break-all}
.freview b{color:var(--ink)}
#hud{position:fixed;""")

# ---------- HTML ----------
rep('  <main id="play" hidden></main>','''  <main id="play" hidden></main>
  <main id="flashWrap" hidden>
    <div class="fset" id="fset">
      <div class="frow">
        <span class="lab">レベル</span>
        <span class="chips" id="flevel"></span>
      </div>
      <div class="frow">
        <span class="lab">けた</span><span class="chips" id="fdigits"></span>
        <span class="lab">口数</span><span class="chips" id="fterms"></span>
      </div>
      <div class="frow">
        <span class="lab">はやさ</span><span class="chips" id="fspeed"></span>
      </div>
      <div class="frow">
        <span class="lab">何問</span><span class="chips" id="fcount"></span>
        <button class="btn small" id="fminus" type="button" aria-pressed="false">ひき算もまぜる</button>
      </div>
      <div class="frow">
        <button class="btn primary big" id="fstart" type="button">スタート</button>
        <span class="msg" id="fmsg"></span>
      </div>
      <p class="fhist" id="fhist"></p>
    </div>
    <div class="fstage" id="fstage" hidden>
      <span class="fbadge" id="fbadge"></span>
      <div id="fstageIn"></div>
    </div>
    <div class="fans" id="fans" hidden>
      <input class="finput" id="finput" type="text" inputmode="none" readonly placeholder="こたえ">
      <div class="keypad" id="fkeys"></div>
    </div>
  </main>''')

# ---------- JS ----------
rep("const toTop=$(\"totop\");","""/* ================= フラッシュ暗算 ================= */
const FKEY2="env-drill-flash";
const FLEVELS=[
 {name:"1",d:1,t:3,ms:900},{name:"2",d:1,t:5,ms:750},{name:"3",d:1,t:8,ms:600},
 {name:"4",d:2,t:5,ms:750},{name:"5",d:2,t:8,ms:600},{name:"6",d:2,t:10,ms:450},
 {name:"7",d:3,t:5,ms:700},{name:"8",d:3,t:10,ms:500}
];
const FSPEEDS=[{name:"ゆっくり",ms:900},{name:"ふつう",ms:700},{name:"はやい",ms:500},{name:"とてもはやい",ms:350}];
let fset={d:1,t:5,ms:750,n:10,minus:false},fsess=null,ftimer=null;
function fload(){try{const o=JSON.parse(localStorage.getItem(FKEY2)||"null");if(o&&o.set)fset=Object.assign(fset,o.set);return o||{};}catch(e){return {};}}
function fsave(extra){try{const o=fload();localStorage.setItem(FKEY2,JSON.stringify(Object.assign(o,{set:fset},extra||{})));}catch(e){}}
function chip(label,on,fn){
  const b=document.createElement("button");b.className="tab";b.type="button";
  b.setAttribute("aria-selected",String(on));b.textContent=label;b.onclick=fn;return b;
}
function drawFset(){
  $("flevel").replaceChildren(...FLEVELS.map(function(L){
    const on=(fset.d===L.d&&fset.t===L.t&&fset.ms===L.ms);
    return chip("レベル"+L.name,on,function(){fset.d=L.d;fset.t=L.t;fset.ms=L.ms;fsave();drawFset();});
  }));
  $("fdigits").replaceChildren(...[1,2,3].map(d=>chip(d+"けた",fset.d===d,function(){fset.d=d;fsave();drawFset();})));
  $("fterms").replaceChildren(...[3,5,8,10,15].map(t=>chip(t+"口",fset.t===t,function(){fset.t=t;fsave();drawFset();})));
  $("fspeed").replaceChildren(...FSPEEDS.map(sp=>chip(sp.name,fset.ms===sp.ms,function(){fset.ms=sp.ms;fsave();drawFset();})));
  $("fcount").replaceChildren(...[5,10,20].map(n=>chip(n+"問",fset.n===n,function(){fset.n=n;fsave();drawFset();})));
  const mb=$("fminus");mb.setAttribute("aria-pressed",String(fset.minus));mb.classList.toggle("on",fset.minus);
  const h=fload().hist||[];
  $("fhist").textContent=h.length?("前回までの記録：　"+h.slice(0,3).map(r=>r.d+"けた"+r.t+"口　"+r.correct+"／"+r.n+"問").join("　／　")):"まだ記録はありません。レベルをえらんで「スタート」を押してください。";
}
function makeQ(){
  const lo=fset.d===1?1:(fset.d===2?10:100), hi=fset.d===1?9:(fset.d===2?99:999);
  const ns=[];let sum=0;
  for(let i=0;i<fset.t;i++){
    let v=lo+Math.floor(Math.random()*(hi-lo+1));
    if(fset.minus&&i>0&&Math.random()<0.4&&sum-v>=0)v=-v;
    ns.push(v);sum+=v;
  }
  return {ns:ns,sum:sum};
}
function fshow(el){const st=$("fstageIn");st.replaceChildren(el);}
function fbig(txt,cls){const d=document.createElement("div");d.className=cls||"fnum";d.textContent=txt;return d;}
function fmsgNode(txt){const d=document.createElement("div");d.className="fmsg";txt.split("\\n").forEach(function(t,i){if(i)d.appendChild(document.createElement("br"));d.appendChild(document.createTextNode(t));});return d;}
function startFlash(){
  fsess={qs:[],i:0,correct:0,t0:Date.now()};
  for(let i=0;i<fset.n;i++)fsess.qs.push(makeQ());
  $("fset").hidden=true;$("fstage").hidden=false;$("fans").hidden=true;
  runQ();
}
function runQ(){
  if(!fsess)return;
  if(fsess.i>=fsess.qs.length)return finishFlash();
  const q=fsess.qs[fsess.i];
  $("fbadge").textContent=(fsess.i+1)+" / "+fsess.qs.length;
  let k=3;
  fshow(fbig(String(k),"fcount"));
  ftimer=setInterval(function(){
    k--;
    if(k>0){fshow(fbig(String(k),"fcount"));return;}
    clearInterval(ftimer);flashNums(q);
  },600);
}
function flashNums(q){
  let i=0;
  const on=fset.ms,off=Math.max(90,Math.round(fset.ms*0.3));
  (function step(){
    if(!fsess)return;
    if(i>=q.ns.length){askAnswer();return;}
    const v=q.ns[i++];
    fshow(fbig((v<0?"−":"")+Math.abs(v),"fnum"+(v<0?" minus":"")));
    ftimer=setTimeout(function(){fshow(document.createTextNode(""));ftimer=setTimeout(step,off);},on);
  })();
}
function askAnswer(){
  fshow(fmsgNode("こたえは？"));
  const inp=$("finput");inp.value="";inp.className="finput";
  $("fans").hidden=false;
}
function keyIn(ch){
  const inp=$("finput");
  if(ch==="del")inp.value=inp.value.slice(0,-1);
  else if(inp.value.length<7)inp.value+=ch;
}
function submitAnswer(){
  if(!fsess||$("fans").hidden)return;
  const inp=$("finput");if(inp.value==="")return;
  const q=fsess.qs[fsess.i],got=Number(inp.value),right=(got===q.sum);
  if(right)fsess.correct++;
  q.got=got;q.right=right;
  inp.className="finput "+(right?"ok":"ng");
  $("fans").hidden=true;
  fshow(fmsgNode(right?"せいかい！":("ざんねん　こたえは "+q.sum)));
  ftimer=setTimeout(function(){fsess.i++;runQ();},right?700:1600);
}
function finishFlash(){
  const sec=Math.round((Date.now()-fsess.t0)/1000);
  const rec={t:Date.now(),d:fset.d,t2:fset.t,t:fset.t,ms:fset.ms,n:fset.qs?0:fset.n,correct:fsess.correct};
  rec.n=fsess.qs.length;
  const o=fload();const hist=[rec].concat(o.hist||[]).slice(0,30);fsave({hist:hist});
  const box=document.createElement("div");
  const h=document.createElement("div");h.className="fnum";h.textContent=fsess.correct+" / "+fsess.qs.length;
  const m=fmsgNode(fset.d+"けた "+fset.t+"口　"+sec+"びょう\\nもう一度やるか、下の「もどる」で設定にもどれます。");
  box.append(h,m);
  const rev=document.createElement("div");rev.className="freview";
  fsess.qs.forEach(function(q,i){
    const line=document.createElement("div");
    const ok=q.right?"◯":"×";
    line.appendChild(document.createTextNode(ok+" "+(i+1)+"　"+q.ns.map(v=>(v<0?"−":"+")+Math.abs(v)).join(" ").replace(/^\\+/,"")+" ＝ "));
    const b=document.createElement("b");b.textContent=String(q.sum);line.appendChild(b);
    if(!q.right&&q.got!==undefined)line.appendChild(document.createTextNode("（こたえた数："+q.got+"）"));
    rev.appendChild(line);
  });
  box.appendChild(rev);
  const row=document.createElement("div");row.className="frow";row.style.justifyContent="center";row.style.marginTop="14px";
  const again=document.createElement("button");again.className="btn primary";again.type="button";again.textContent="もう一回";
  again.onclick=function(){startFlash();};
  const back=document.createElement("button");back.className="btn";back.type="button";back.textContent="もどる";
  back.onclick=function(){stopFlash();};
  row.append(again,back);box.appendChild(row);
  fshow(box);
  $("fbadge").textContent="おわり";
  fsess=null;drawFset();
}
function stopFlash(){
  clearInterval(ftimer);clearTimeout(ftimer);fsess=null;
  $("fstage").hidden=true;$("fans").hidden=true;$("fset").hidden=false;drawFset();
}
$("fstart").onclick=function(){startFlash();};
$("fminus").onclick=function(){fset.minus=!fset.minus;fsave();drawFset();};
$("fkeys").replaceChildren(...["7","8","9","4","5","6","1","2","3"].map(function(c){
  return (function(){const b=document.createElement("button");b.className="key";b.type="button";b.textContent=c;b.onclick=function(){keyIn(c);};return b;})();
}));
(function(){
  const k=$("fkeys");
  const z=document.createElement("button");z.className="key";z.type="button";z.textContent="0";z.onclick=function(){keyIn("0");};
  const d=document.createElement("button");d.className="key del";d.type="button";d.textContent="けす";d.onclick=function(){keyIn("del");};
  const g=document.createElement("button");g.className="key go wide";g.type="button";g.textContent="こたえる";g.onclick=submitAnswer;
  k.append(z,d,g);
})();
document.addEventListener("keydown",function(e){
  if(subject!=="暗算"||$("fans").hidden)return;
  if(/^[0-9]$/.test(e.key)){keyIn(e.key);e.preventDefault();}
  else if(e.key==="Backspace"){keyIn("del");e.preventDefault();}
  else if(e.key==="Enter"){submitAnswer();e.preventDefault();}
});
fload();

const toTop=$("totop");""")

# 教科に「暗算」を足す
rep('''function drawSubjects(){
  $("subjects").replaceChildren(...SUBJECTS.map(function(sb){''','''function drawSubjects(){
  $("subjects").replaceChildren(...SUBJECTS.concat(["暗算"]).map(function(sb){''')
rep('''    const n=DATA.filter(d=>(SRC[d.from]||{}).subject===sb).reduce((a,d)=>a+d.items.length,0);
    b.appendChild(document.createTextNode(sb));
    const sp=document.createElement("span");sp.className="n";sp.textContent=n;b.appendChild(sp);
    b.onclick=function(){if(sb===subject)return;subject=sb;sources=[];current="all";recount();refresh();};''',
'''    const n=DATA.filter(d=>(SRC[d.from]||{}).subject===sb).reduce((a,d)=>a+d.items.length,0);
    b.appendChild(document.createTextNode(sb==="暗算"?"フラッシュ暗算":sb));
    if(sb!=="暗算"){const sp=document.createElement("span");sp.className="n";sp.textContent=n;b.appendChild(sp);}
    b.onclick=function(){if(sb===subject)return;if(subject==="暗算")stopFlash();subject=sb;sources=[];current="all";savePrefs();recount();refresh();};''')

# 画面の出し分け
rep('''  barEl.hidden=(mode==="card");''','''  const fl=(subject==="暗算");
  $("flashWrap").hidden=!fl;
  if(fl){
    document.body.classList.remove("playing");
    barEl.hidden=false;listEl.hidden=true;playEl.hidden=true;
    $("resume").hidden=true;$("undoBar").hidden=true;$("saveNudge").hidden=true;
    document.querySelectorAll(".bar .row2, .bar .hint, .bar .xfer").forEach(function(el,i){el.hidden=(i!==2);});
    drawSubjects();drawFset();return;
  }
  document.querySelectorAll(".bar .row2, .bar .hint").forEach(function(el){el.hidden=false;});
  barEl.hidden=(mode==="card");''')
rep('  recount();drawSubjects();drawSources();drawUnits();drawCounts();','  if(subject!=="暗算")recount();\n  drawSubjects();\n  if(subject==="暗算"){}else{drawSources();drawUnits();drawCounts();}')
# 教科の復元で「暗算」も許可
rep('if(p.subject&&SUBJECTS.indexOf(p.subject)>=0)subject=p.subject;','if(p.subject&&(SUBJECTS.indexOf(p.subject)>=0||p.subject==="暗算"))subject=p.subject;')
rep("v30 ・ 10/2更新","v31 ・ 10/2更新")
io.open("kankyo-drill.html","w",encoding="utf-8").write(s); io.open("env-drill.html","w",encoding="utf-8").write(s)
i=s.rindex("<script>"); io.open("check.js","w",encoding="utf-8").write(s[i+8:s.rindex("</script>")])
print("built",len(s))
