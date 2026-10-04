const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9398;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const prof=fs.mkdtempSync("/tmp/cdp-");
 const ch=spawn(CH,["--headless=new","--disable-gpu","--remote-debugging-port="+PORT,"--user-data-dir="+prof,"about:blank"],{stdio:"ignore"});
 let tabs=null;for(let i=0;i<40;i++){try{tabs=await (await fetch("http://127.0.0.1:"+PORT+"/json")).json();if(tabs.length)break;}catch(e){}await sleep(250);}
 const ws=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener("open",r));
 let id=0;const pend={};let errs=[];
 ws.addEventListener("message",ev=>{const m=JSON.parse(ev.data);
   if(m.method==="Runtime.exceptionThrown")errs.push(m.params.exceptionDetails.text+" "+((m.params.exceptionDetails.exception||{}).description||""));
   if(m.id&&pend[m.id]){pend[m.id](m.result||m);delete pend[m.id];}});
 const send=(m,p={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method:m,params:p}));});
 const ev=async x=>{const r=await send("Runtime.evaluate",{expression:x,awaitPromise:true,returnByValue:true});
   if(r.exceptionDetails)errs.push("eval:"+JSON.stringify(r.exceptionDetails.exception||r.exceptionDetails.text));return r.result?r.result.value:r;};
 const shot=async n=>{const r=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:true});fs.writeFileSync(n,Buffer.from(r.data,"base64"));};
 await send("Page.enable");await send("Runtime.enable");
 await send("Emulation.setDeviceMetricsOverride",{width:390,height:900,deviceScaleFactor:1.5,mobile:true});
 const F="file://"+path.resolve("t.html");
 await send("Page.navigate",{url:F});await sleep(1800);
 const out=[];const ok=(n,c,dd)=>out.push((c?"OK   ":"FAIL ")+n+(dd!==undefined?"  ("+dd+")":""));
 ok("JSエラーなし",errs.length===0,errs.join(" / ")||"なし");
 // 子の端末のふりをして記録をつくる
 await ev(`(function(){localStorage.clear();marks={};plog=[];
   subject="歴史";sources=["hi46"];current="all";
   const items=pool().slice(0,20);
   sess={items:items,i:0,res:{},range:"歴史46 鎌倉時代①"};mode="card";draw();
   for(let i=0;i<20;i++)judge(i%4===3?"ng":"ok");
   const D=86400000,now=Date.now();
   [1,2,4].forEach(function(k){plog.unshift({t:now-k*D,d:dstr(now-k*D),sub:"地理",range:"東北地方",n:20,ok:16,ng:4,sk:0,k:"card"});});
   saveLog();})();1`);await sleep(300);
 await ev('mode="parent";draw();1');await sleep(400);
 ok("同期の案内が出ている",(await ev('!!document.querySelector(".pv .sync .btn")')),await ev('(document.querySelector(".pv .sync .btn")||{}).textContent'));
 await ev('document.querySelector(".pv .sync .btn").click();1');
 for(let i=0;i<20&&!(await ev('!!(syncCfg()||{}).last'));i++)await sleep(400);
 const cfg=await ev('syncCfg()');
 ok("鍵ができて送信された",!!(cfg&&cfg.id&&cfg.last),JSON.stringify(cfg));
 await ev('draw();1');await sleep(300);
 const purl=await ev('(document.querySelector(".pv .sync input")||{}).value');
 ok("親用URLが出る",/\?p=[a-f0-9]{20}$/.test(purl||""),purl);
 await shot("sy_child.png");
 // 親の端末のふり（別プロファイル相当：localStorage を消してから ?p= で開く）
 errs=[];
 await send("Page.navigate",{url:F+"?p="+cfg.id});await sleep(1200);
 await ev('localStorage.clear();1');
 await send("Page.navigate",{url:F+"?p="+cfg.id});await sleep(3000);
 ok("親側でJSエラーなし",errs.length===0,errs.join(" / ")||"なし");
 ok("同期された記録が表示される",(await ev('!!pvData&&!!pvData.sec')),JSON.stringify(await ev('pvData?Object.keys(pvData.sec).length+"分野":null')));
 ok("最終更新のおしらせが出る",(await ev('!!document.querySelector(".pv .remote")')),await ev('(document.querySelector(".pv .remote")||{}).textContent'));
 ok("親側には同期ボタンを出さない",!(await ev('!!document.querySelector(".pv .sync")')));
 ok("きょうの問題数が引きつがれる",(await ev('(byDay()[dstr(Date.now())]||{}).n'))===20,await ev('(byDay()[dstr(Date.now())]||{}).n')+"問");
 ok("進みぐあいが引きつがれる",(await ev('progBySource().filter(p=>p.ok+p.ng>0).map(p=>p.short+":"+p.ok+"/"+p.ng).join(",")'))==="46 鎌倉時代①:15/5",
    await ev('progBySource().filter(p=>p.ok+p.ng>0).map(p=>p.short+":"+p.ok+"/"+p.ng).join(",")'));
 ok("親の端末のローカル記録は空のまま",(await ev('Object.keys(marks).length'))===0);
 await shot("sy_parent.png");
 // 存在しない鍵
 await send("Page.navigate",{url:F+"?p=0000000000000000ffff"});await sleep(2500);
 ok("記録がない鍵では案内が出る",(await ev('!!document.querySelector(".pv .err")')),await ev('(document.querySelector(".pv .err")||{}).textContent'));
 console.log(out.join("\n"));if(errs.length)console.log("ERR:",errs.join("\n"));
 console.log("KEY="+cfg.id);
 ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
