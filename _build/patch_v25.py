import io,os
dep=os.path.expanduser("~/Desktop/shakai-drill-deploy/jp9pyw1wu4/index.html")
s=io.open(dep,encoding="utf-8").read()
s=s[s.index("<title>"):]; s=s[:s.rindex("</body>")].rstrip()+"\n"
assert "v24" in s
def rep(a,b):
    global s
    assert s.count(a)==1,"COUNT %d: %s"%(s.count(a),a[:70])
    s=s.replace(a,b,1)

# ---------- CSS ----------
rep(".xfer .msg{",""".xfer .binfo{font-size:13px;color:var(--ink-2);margin:0}
.xfer .binfo b{font-family:var(--ff-m);font-variant-numeric:tabular-nums}
.xfer details{border-top:1px solid var(--rule);padding-top:8px;margin-top:2px}
.xfer summary{cursor:pointer;font-size:13px;color:var(--ink-3)}
.xfer details[open]>*:not(summary){margin-top:8px}
.nudge{display:flex;flex-wrap:wrap;align-items:center;gap:10px 12px;padding:12px 14px;border:1px solid color-mix(in srgb,var(--amber) 50%,transparent);background:var(--amber-soft);border-radius:12px}
.nudge .rt{font-size:14px;font-weight:500;color:var(--ink);flex:1 1 220px}
.xfer .msg{""")

# ---------- HTML：上部のお知らせ ----------
rep('''      <div class="resume" id="resume" hidden>''',
'''      <div class="nudge" id="undoBar" hidden>
        <span class="rt" id="undoText"></span>
        <button class="btn primary small" id="undoGo" type="button">元に戻す</button>
        <button class="btn small" id="undoClose" type="button">閉じる</button>
      </div>
      <div class="nudge" id="saveNudge" hidden>
        <span class="rt" id="nudgeText"></span>
        <button class="btn primary small" id="nudgeSave" type="button">ファイルに保存</button>
        <button class="btn small" id="nudgeLater" type="button">あとで</button>
      </div>
      <div class="resume" id="resume" hidden>''')
rep('>記録の引き継ぎ</button>','>記録の保存・読み込み</button>')

# ---------- HTML：保存パネル ----------
i=s.index('      <div class="xfer" id="xferPanel" hidden>'); j=s.index('      <p class="hint">◯できた',i)
s=s[:i]+'''      <div class="xfer" id="xferPanel" hidden>
        <h3>ファイルに保存</h3>
        <p>◯△の記録を、この端末にファイルとして保存します。ブラウザの記録が消えても、このファイルから元に戻せます。</p>
        <div class="row"><button class="btn primary small" id="fileSave" type="button">ファイルに保存</button><span class="msg" id="fileMsg"></span></div>
        <p class="binfo" id="backupInfo"></p>
        <h3>ファイルから読み込む</h3>
        <p>保存したファイルを選ぶと、いまの記録に合流します。いまの記録は消えません。</p>
        <div class="row"><button class="btn small" id="fileLoad" type="button">ファイルを選ぶ</button><input type="file" id="fileIn" accept=".json,application/json,text/plain" hidden><span class="msg" id="fileMsg2"></span></div>
        <div class="row" id="undoRow" hidden><button class="btn small" id="undoBtn2" type="button"></button></div>
        <p>iPhoneのSafariでは、7日以上開かないとブラウザの記録が消えることがあります。ホーム画面に追加して使うと消えにくくなります。</p>
        <details>
          <summary>ファイルが使えないとき（文字でコピー）</summary>
          <p>下の文字列をコピーして、メモなどに保存してください。</p>
          <textarea id="xferOut" readonly rows="3"></textarea>
          <div class="row"><button class="btn small" id="xferCopy" type="button">コピーする</button><span class="msg" id="xferMsg1"></span></div>
          <p>保存した文字列を貼り付けて読み込むと、いまの記録に合流します。</p>
          <textarea id="xferIn" rows="3" placeholder="ここに貼り付け"></textarea>
          <div class="row"><button class="btn small" id="xferLoad" type="button">読み込む</button><span class="msg" id="xferMsg2"></span></div>
        </details>
      </div>
'''+s[j:]

# ---------- JS：保存の多重化 ----------
rep('const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(marks))}catch(e){}};',
'''const MKEY="env-drill-backup-meta", TRKEY="env-drill-trash";
function getMeta(){try{return JSON.parse(localStorage.getItem(MKEY)||"{}")||{};}catch(e){return {};}}
function setMeta(p){const m=Object.assign(getMeta(),p);try{localStorage.setItem(MKEY,JSON.stringify(m));}catch(e){}return m;}
function idbOpen(){return new Promise(function(res,rej){try{const r=indexedDB.open("shakai-drill",1);r.onupgradeneeded=function(){r.result.createObjectStore("kv");};r.onsuccess=function(){res(r.result);};r.onerror=function(){rej(r.error);};}catch(e){rej(e);}});}
function idbPut(k,v){idbOpen().then(function(db){db.transaction("kv","readwrite").objectStore("kv").put(v,k);}).catch(function(){});}
function idbGet(k){return idbOpen().then(function(db){return new Promise(function(res){const q=db.transaction("kv","readonly").objectStore("kv").get(k);q.onsuccess=function(){res(q.result||null);};q.onerror=function(){res(null);};});}).catch(function(){return null;});}
let askedPersist=false;
function askPersist(){if(askedPersist)return;askedPersist=true;try{if(navigator.storage&&navigator.storage.persist)navigator.storage.persist().catch(function(){});}catch(e){}}
const save=()=>{
  const txt=JSON.stringify(marks);
  try{localStorage.setItem(KEY,txt)}catch(e){}
  idbPut("marks",txt);
  const m=getMeta();setMeta({changes:(m.changes||0)+1});
  if(Object.keys(marks).length)askPersist();
};''')

# ---------- JS：記録を消す→取り消せるように ----------
rep('$("resetYes").onclick=function(){marks={};save();askReset(false);draw();};',
'''$("resetYes").onclick=function(){
  const n=Object.keys(marks).length;
  if(n){const t={t:Date.now(),marks:marks,shown:true};try{localStorage.setItem(TRKEY,JSON.stringify(t));}catch(e){}idbPut("trash",JSON.stringify(t));}
  marks={};save();askReset(false);draw();
};''')

# ---------- JS：ファイル保存・読み込み・取り消し・お知らせ ----------
i=s.index('const xferBtn=$("xferBtn")'); j=s.index('const mapFab=$("mapfab")')
s=s[:i]+'''const xferBtn=$("xferBtn"),xferPanel=$("xferPanel"),xferOut=$("xferOut"),xferIn=$("xferIn");
function xferText(){return JSON.stringify({v:1,app:"shakai-drill",marks:marks});}
function flash(id,t,ms){const el=$(id);el.textContent=t;clearTimeout(el._t);el._t=setTimeout(function(){el.textContent="";},ms||4000);}
function pad(n){return String(n).padStart(2,"0");}
function jpTime(t){const d=new Date(t);return (d.getMonth()+1)+"月"+d.getDate()+"日 "+d.getHours()+":"+pad(d.getMinutes());}
function nOk(m){return Object.keys(m||{}).filter(k=>m[k]==="ok").length;}
function nNg(m){return Object.keys(m||{}).filter(k=>m[k]==="ng").length;}
function importMarks(d,msgId){
  if(!d||typeof d.marks!=="object"||d.marks===null){flash(msgId,"読み込めません。保存したファイルか確かめてください");return false;}
  let n=0;Object.keys(d.marks).forEach(function(k){const v=d.marks[k];if(v==="ok"||v==="ng"){marks[k]=v;n++;}});
  save();draw();xferOut.value=xferText();
  flash(msgId,n+"件を読み込みました",6000);return true;
}
function getTrash(){try{const t=JSON.parse(localStorage.getItem(TRKEY)||"null");if(t&&t.marks&&Date.now()-t.t<60*86400000)return t;}catch(e){}return null;}
function restoreTrash(){
  const t=getTrash();if(!t)return;
  let n=0;Object.keys(t.marks).forEach(function(k){if(!marks[k]){marks[k]=t.marks[k];n++;}});
  try{localStorage.removeItem(TRKEY);}catch(e){}idbPut("trash",null);
  save();draw();
}
function updateBackupInfo(){
  const m=getMeta();const n=Object.keys(marks).length;
  const bi=$("backupInfo");bi.replaceChildren();
  if(m.lastFile){
    bi.appendChild(document.createTextNode("最後にファイルに保存したのは "+jpTime(m.lastFile)+"（"));
    const b=document.createElement("b");b.textContent=(m.lastCount||0)+"件";bi.appendChild(b);
    bi.appendChild(document.createTextNode("）。いまの記録は "+n+"件です。"));
  }else bi.textContent="まだファイルに保存していません。いまの記録は "+n+"件です。";
  const t=getTrash(),ur=$("undoRow");
  if(t){ur.hidden=false;$("undoBtn2").textContent="消した記録を元に戻す（"+jpTime(t.t)+"に消した "+Object.keys(t.marks).length+"件）";}
  else ur.hidden=true;
}
function updateNotices(){
  const list=(mode==="list");
  const t=getTrash(),ub=$("undoBar");
  if(list&&t&&t.shown){ub.hidden=false;$("undoText").textContent="記録を消しました（◯"+nOk(t.marks)+"件・△"+nNg(t.marks)+"件）。まちがえた場合は元に戻せます。";}
  else ub.hidden=true;
  const m=getMeta(),n=Object.keys(marks).length,nb=$("saveNudge");
  const since=m.changes||0, snooze=m.snooze||0;
  const need=n>=10&&(!m.lastFile?since>=15:since>=30)&&Date.now()>snooze;
  if(list&&need&&ub.hidden){nb.hidden=false;$("nudgeText").textContent=m.lastFile?("前回ファイルに保存してから、記録が"+since+"回ふえました。念のため保存しておきましょう。"):("記録が"+n+"件たまりました。消えたときのために、ファイルに保存しておきましょう。");}
  else nb.hidden=true;
}
function saveFile(msgId){
  let prefs=null,sv=null;try{prefs=JSON.parse(localStorage.getItem(PKEY)||"null");sv=JSON.parse(localStorage.getItem(SKEY)||"null");}catch(e){}
  const n=Object.keys(marks).length;
  const obj={app:"shakai-drill",v:2,savedAt:new Date().toISOString(),count:n,ok:nOk(marks),ng:nNg(marks),marks:marks,prefs:prefs,session:sv};
  const d=new Date();const name="社会ドリル記録_"+d.getFullYear()+pad(d.getMonth()+1)+pad(d.getDate())+"_"+pad(d.getHours())+pad(d.getMinutes())+".json";
  try{
    const blob=new Blob([JSON.stringify(obj,null,1)],{type:"application/json"});
    const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;a.rel="noopener";
    document.body.appendChild(a);a.click();
    setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},2000);
  }catch(e){flash(msgId,"保存できませんでした。下の「文字でコピー」を使ってください",8000);return;}
  setMeta({lastFile:Date.now(),lastCount:n,changes:0,snooze:0});
  flash(msgId,"保存しました（"+n+"件）。ファイル名："+name,8000);
  updateBackupInfo();updateNotices();
}
xferBtn.onclick=function(){const on=xferPanel.hidden;xferPanel.hidden=!on;xferBtn.setAttribute("aria-expanded",String(on));if(on){xferOut.value=xferText();updateBackupInfo();}};
$("fileSave").onclick=function(){saveFile("fileMsg");};
$("fileLoad").onclick=function(){$("fileIn").click();};
$("fileIn").onchange=function(){
  const f=this.files&&this.files[0];if(!f)return;
  const r=new FileReader();
  r.onload=function(){let d=null;try{d=JSON.parse(String(r.result).trim());}catch(e){}if(importMarks(d,"fileMsg2"))updateBackupInfo();};
  r.onerror=function(){flash("fileMsg2","ファイルを読めませんでした");};
  r.readAsText(f);this.value="";
};
$("undoBtn2").onclick=function(){restoreTrash();updateBackupInfo();flash("fileMsg2","消した記録を元に戻しました",6000);};
$("undoGo").onclick=function(){restoreTrash();};
$("undoClose").onclick=function(){const t=getTrash();if(t){t.shown=false;try{localStorage.setItem(TRKEY,JSON.stringify(t));}catch(e){}}updateNotices();};
$("nudgeSave").onclick=function(){xferPanel.hidden=false;xferBtn.setAttribute("aria-expanded","true");xferOut.value=xferText();saveFile("fileMsg");xferPanel.scrollIntoView({behavior:"smooth",block:"center"});};
$("nudgeLater").onclick=function(){setMeta({snooze:Date.now()+3*86400000});updateNotices();};
$("xferCopy").onclick=function(){
  xferOut.value=xferText();xferOut.select();let ok=false;try{ok=document.execCommand("copy");}catch(e){}
  if(ok){flash("xferMsg1","コピーしました");return;}
  if(navigator.clipboard){navigator.clipboard.writeText(xferOut.value).then(function(){flash("xferMsg1","コピーしました");},function(){flash("xferMsg1","選択済みです。手動でコピーしてください");});}
  else flash("xferMsg1","選択済みです。手動でコピーしてください");
};
$("xferLoad").onclick=function(){let d=null;try{d=JSON.parse(xferIn.value.trim());}catch(e){}if(importMarks(d,"xferMsg2"))xferIn.value="";};

'''+s[j:]

# drawのたびにお知らせを更新
rep('  tally();updateFab();updateResume();\n}','  tally();updateFab();updateResume();updateNotices();\n}')
rep('if(mode==="card"){renderPlay();tally();updateFab();updateResume();return;}','if(mode==="card"){renderPlay();tally();updateFab();updateResume();updateNotices();return;}')

# 起動時：ブラウザの記録が空なら、予備の保管場所から戻す
rep('\ndraw();\n</script>','''
draw();
if(!Object.keys(marks).length){
  idbGet("marks").then(function(v){
    let d=null;try{d=JSON.parse(v||"null");}catch(e){}
    if(d&&typeof d==="object"&&Object.keys(d).length){
      marks=d;try{localStorage.setItem(KEY,JSON.stringify(marks));}catch(e){}
      draw();
    }
  });
}
</script>''')
rep("v24 ・ 9/19更新","v25 ・ 9/20更新")
io.open("kankyo-drill.html","w",encoding="utf-8").write(s); io.open("env-drill.html","w",encoding="utf-8").write(s)
i=s.rindex("<script>"); io.open("check.js","w",encoding="utf-8").write(s[i+8:s.rindex("</script>")])
print("built",len(s))
