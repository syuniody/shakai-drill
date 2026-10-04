const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9397;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const prof=fs.mkdtempSync("/tmp/cdp-");
 const ch=spawn(CH,["--headless=new","--disable-gpu","--remote-debugging-port="+PORT,"--user-data-dir="+prof,"about:blank"],{stdio:"ignore"});
 let tabs=null;for(let i=0;i<40;i++){try{tabs=await (await fetch("http://127.0.0.1:"+PORT+"/json")).json();if(tabs.length)break;}catch(e){}await sleep(250);}
 const ws=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener("open",r));
 let id=0;const pend={};const errs=[];
 ws.addEventListener("message",ev=>{const m=JSON.parse(ev.data);
   if(m.method==="Runtime.exceptionThrown")errs.push(m.params.exceptionDetails.text+" "+((m.params.exceptionDetails.exception||{}).description||""));
   if(m.id&&pend[m.id]){pend[m.id](m.result||m);delete pend[m.id];}});
 const send=(m,p={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method:m,params:p}));});
 const ev=async x=>{const r=await send("Runtime.evaluate",{expression:x,awaitPromise:true,returnByValue:true});
   if(r.exceptionDetails)errs.push("eval:"+JSON.stringify(r.exceptionDetails.exception||r.exceptionDetails.text));return r.result?r.result.value:r;};
 const shot=async n=>{const r=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:true});fs.writeFileSync(n,Buffer.from(r.data,"base64"));};
 await send("Page.enable");await send("Runtime.enable");
 await send("Emulation.setDeviceMetricsOverride",{width:390,height:900,deviceScaleFactor:1.5,mobile:true});
 await send("Page.navigate",{url:"file://"+path.resolve("t.html")});await sleep(1800);
 const out=[];const ok=(n,c,dd)=>out.push((c?"OK   ":"FAIL ")+n+(dd!==undefined?"  ("+dd+")":""));
 ok("JSエラーなし",errs.length===0,errs.join(" / ")||"なし");
 // 記録が空の状態でダッシュボードを開く
 await ev('localStorage.clear();plog=[];marks={};mode="parent";draw();1');await sleep(400);
 ok("記録ゼロでも開ける",(await ev('!!document.querySelector(".pv")')),await ev('(document.querySelector(".pv .lead")||{}).textContent'));
 await shot("pv_empty.png");
 // 20問を解いたことにする
 await ev(`(function(){
   subject="歴史";sources=["hi46"];current="all";
   const items=pool().slice(0,20);
   sess={items:items,i:0,res:{},range:"歴史46 鎌倉時代①"};mode="card";draw();
   for(let i=0;i<20;i++){judge(i%4===3?"ng":"ok");}
 })();1`);await sleep(500);
 ok("セッションが1件ログされる",(await ev('plog.length'))===1,JSON.stringify(await ev('plog[0]')));
 ok("内訳が合っている",(await ev('plog[0].ok'))===15&&(await ev('plog[0].ng'))===5,await ev('plog[0].ok+"/"+plog[0].ng'));
 // 結果画面を再描画してもログが増えない
 await ev('renderPlay();renderPlay();1');await sleep(200);
 ok("再描画で二重に記録されない",(await ev('plog.length'))===1,await ev('plog.length')+"件");
 // 過去の日付をまぜる
 await ev(`(function(){const D=86400000,now=Date.now();
   [1,2,3,5,8].forEach(function(k){plog.unshift({t:now-k*D,d:dstr(now-k*D),sub:"地理",range:"東北地方",n:20,ok:14+k%4,ng:6-k%4,sk:0,k:"card"});});
   plog.unshift({t:now-D,d:dstr(now-D),sub:"歴史",range:"単元40",n:30,ok:22,ng:8,sk:0,k:"flash"});
   saveLog();})();1`);
 await ev('mode="parent";draw();1');await sleep(500);
 ok("連続日数が出る",(await ev('streakDays(byDay())'))>=3,"連続"+await ev('streakDays(byDay())')+"日");
 ok("きょうの問題数",(await ev('(byDay()[dstr(Date.now())]||{}).n'))===20,await ev('(byDay()[dstr(Date.now())]||{}).n')+"問");
 ok("2週間グラフの棒が14本",(await ev('document.querySelectorAll(".pv .days i").length'))===14);
 ok("教科ごとの表が出る",(await ev('document.querySelectorAll(".pv table").length'))>=4,await ev('document.querySelectorAll(".pv table").length')+"表");
 ok("つまずき表に行がある",(await ev('[...document.querySelectorAll(".pv section")].some(s=>/つまずい/.test(s.textContent)&&s.querySelectorAll("tr").length>1)')));
 ok("設定バーが隠れる",(await ev('document.getElementById("bar").hidden'))===true);
 await shot("pv_full.png");
 // もどる
 await ev('document.querySelector(".pv .pv-top .btn").click();1');await sleep(400);
 ok("ドリルにもどれる",(await ev('mode'))==="list"&&(await ev('document.getElementById("bar").hidden'))===false);
 ok("記録（marks）は無事",(await ev('Object.keys(marks).length'))===20,await ev('Object.keys(marks).length')+"件");
 console.log(out.join("\n"));if(errs.length)console.log("ERR:",errs.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
