const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9403;
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
 const shot=async n=>{const r=await send("Page.captureScreenshot",{format:"png"});fs.writeFileSync(n,Buffer.from(r.data,"base64"));};
 await send("Page.enable");await send("Runtime.enable");
 await send("Emulation.setDeviceMetricsOverride",{width:500,height:900,deviceScaleFactor:1.5,mobile:true});
 await send("Page.navigate",{url:"file://"+path.resolve("../jp9pyw1wu4/index.html")});await sleep(1900);
 const out=[];const ok=(n,c,dd)=>out.push((c?"OK   ":"FAIL ")+n+(dd!==undefined?"  ("+dd+")":""));
 ok("JSエラーなし",errs.length===0,errs.join(" / ")||"なし");



 ok("JSエラーなし（読み込み）",errs.length===0,errs.join(" / ")||"なし");
 await ev('localStorage.clear();subject="地理";sources=["kd3","kd4"];current="all";filter="all";level="all";refresh();1');await sleep(300);
 ok("3・4 全部552",(await ev('pool().length'))===552,await ev('pool().length'));
 await ev('$("level").value="k";$("level").onchange();1');await sleep(300);
 ok("3・4 基本188",(await ev('pool().length'))===188,await ev('pool().length'));
 ok("地図の分野は名前だけ",(await ev('pool().filter(r=>/^kd(1[7-9]|2[0-4])-/.test(r.key)).every(r=>/の名前は。$/.test(r.q))')));
 ok("文章の基本に県名などは残る",(await ev('pool().some(r=>r.q.indexOf("阿蘇山がある県")>=0)')));
 ok("記録キーは変わらない kd2-0",(await ev('DATA.find(s=>s.id==="kd2").items[0][2]'))==="kd2-0");
 await ev('$("level").value="h";$("level").onchange();1');await sleep(300);
 ok("3・4 発展364",(await ev('pool().length'))===364,await ev('pool().length'));
 await ev('sources=["map1","map2"];level="k";refresh();1');await sleep(300);
 ok("第1章の基本は144のまま",(await ev('pool().length'))===144,await ev('pool().length'));
 ok("JSエラーなし（最後）",errs.length===0,errs.join(" / ")||"なし");
 console.log(out.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
