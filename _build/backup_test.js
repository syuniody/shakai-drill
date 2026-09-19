const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9341;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const prof=fs.mkdtempSync("/tmp/cdp-");
  const ch=spawn(CH,["--headless=new","--disable-gpu","--remote-debugging-port="+PORT,"--user-data-dir="+prof,"--allow-file-access-from-files","about:blank"],{stdio:"ignore"});
  let tabs=null;for(let i=0;i<40;i++){try{tabs=await (await fetch("http://127.0.0.1:"+PORT+"/json")).json();if(tabs.length)break;}catch(e){}await sleep(250);}
  const ws=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener("open",r));
  let id=0;const pend={};ws.addEventListener("message",ev=>{const m=JSON.parse(ev.data);if(m.id&&pend[m.id]){pend[m.id](m.result||m);delete pend[m.id];}});
  const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}));});
  const ev=async(x)=>{const r=await send("Runtime.evaluate",{expression:x,awaitPromise:true,returnByValue:true});return r.result?r.result.value:r;};
  const url="file://"+path.resolve("t.html");const dl=path.resolve("dl");
  await send("Page.enable");await send("DOM.enable");
  await send("Browser.setDownloadBehavior",{behavior:"allow",downloadPath:dl});
  await send("Emulation.setDeviceMetricsOverride",{width:390,height:760,deviceScaleFactor:1.5,mobile:true});
  const go=async()=>{await send("Page.navigate",{url});await sleep(1500);};
  const cnt='Object.keys(marks).length';
  const out=[];const ok=(name,cond,detail)=>{out.push((cond?"OK   ":"FAIL ")+name+(detail!==undefined?"  ("+detail+")":""));};

  await go(); await ev('localStorage.clear();new Promise(r=>{const q=indexedDB.deleteDatabase("shakai-drill");q.onsuccess=q.onerror=q.onblocked=()=>r(1);})'); await go();
  await ev('sources=["chubu"];current="c1";count=10;draw();$("start").click();for(let i=0;i<10;i++)judge(i<6?"ok":"ng");1');
  await sleep(600);
  ok("10問に◯△をつける", await ev(cnt)===10, await ev(cnt));
  const idbN=await ev('idbGet("marks").then(v=>Object.keys(JSON.parse(v||"{}")).length)');
  ok("予備の保管場所（IndexedDB）にも同じ記録", idbN===10, idbN);

  await ev('goList();1'); await sleep(500);
  await ev('$("xferBtn").click();$("fileSave").click();1'); await sleep(2500);
  const files=fs.readdirSync(dl).filter(f=>f.endsWith(".json"));
  ok("ファイルに保存（ダウンロード）", files.length===1, files[0]);
  let saved=null; if(files[0]) saved=JSON.parse(fs.readFileSync(path.join(dl,files[0]),"utf8"));
  ok("保存ファイルの中身", saved&&saved.count===10&&saved.ok===6&&saved.ng===4, saved&&("count="+saved.count+" ok="+saved.ok+" ng="+saved.ng));
  ok("最後に保存した日時の表示", /最後にファイルに保存/.test(await ev('$("backupInfo").textContent')), await ev('$("backupInfo").textContent'));

  await ev('$("reset").click();$("resetYes").click();1'); await sleep(400);
  ok("記録を消す→0件", await ev(cnt)===0);
  ok("「元に戻す」のお知らせが出る", await ev('!$("undoBar").hidden'), await ev('$("undoText").textContent'));
  await send("Page.captureScreenshot",{format:"png"}).then(r=>fs.writeFileSync("b1_undo.png",Buffer.from(r.data,"base64")));
  await ev('$("undoGo").click();1'); await sleep(400);
  ok("元に戻す→10件に復帰", await ev(cnt)===10, await ev(cnt));

  await ev('localStorage.removeItem("env-drill-v1");1'); await go(); await sleep(800);
  ok("ブラウザの記録だけ消えた→予備から自動復元", await ev(cnt)===10, await ev(cnt));

  await ev('localStorage.clear();new Promise(r=>{const q=indexedDB.deleteDatabase("shakai-drill");q.onsuccess=q.onerror=q.onblocked=()=>r(1);})'); await go(); await sleep(600);
  ok("すべて消えた状態", await ev(cnt)===0);
  await ev('$("xferBtn").click();1');
  const doc=await send("DOM.getDocument",{depth:-1});const q=await send("DOM.querySelector",{nodeId:doc.root.nodeId,selector:"#fileIn"});
  await send("DOM.setFileInputFiles",{nodeId:q.nodeId,files:[path.join(dl,files[0])]});
  await ev('$("fileIn").dispatchEvent(new Event("change"));1'); await sleep(900);
  ok("保存ファイルから読み込み→10件に復帰", await ev(cnt)===10, await ev(cnt)+"件 / "+await ev('$("fileMsg2").textContent'));
  await send("Page.captureScreenshot",{format:"png"}).then(r=>fs.writeFileSync("b2_panel.png",Buffer.from(r.data,"base64")));

  await ev('setMeta({lastFile:Date.now()-5*86400000,lastCount:10,changes:35,snooze:0});$("xferBtn").click();draw();window.scrollTo(0,0);1'); await sleep(400);
  ok("保存をすすめるお知らせ", await ev('!$("saveNudge").hidden'), await ev('$("nudgeText").textContent'));
  await send("Page.captureScreenshot",{format:"png"}).then(r=>fs.writeFileSync("b3_nudge.png",Buffer.from(r.data,"base64")));
  console.log(out.join("\n"));
  ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
