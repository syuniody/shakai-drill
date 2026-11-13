const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9402;
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

 await ev('localStorage.clear();1');
 await ev('subject="地理";sources=["kd3","kd4"];current="all";filter="all";level="all";refresh();1');await sleep(400);
 ok("3・4 全部314",(await ev('pool().length'))===314,await ev('pool().length'));
 ok("レベル欄が出る",(await ev('$("lvWrap").hidden'))===false);
 await ev('$("level").value="k";$("level").onchange();1');await sleep(300);
 ok("基本186",(await ev('pool().length'))===186,await ev('pool().length'));
 await ev('$("level").value="h";$("level").onchange();1');await sleep(300);
 ok("発展128",(await ev('pool().length'))===128,await ev('pool().length'));
 await ev('$("level").value="all";$("level").onchange();1');await sleep(300);
 ok("第1章は231のまま",(await ev('(sources=["map1","map2"],refresh(),pool().length)'))===231);
 ok("プリセットに日本の国土",(await ev('JSON.stringify(PRESETS["地理"])')).includes("kd3"));
 ok("版数",(await ev('$("ver").textContent')),await ev('$("ver").textContent'));
 await ev('sources=["kd3"];refresh();1');await sleep(400);
 await shot(process.env.OUT+"/kd_list.png");
 ok("JSエラーなし（最後）",errs.length===0,errs.join(" / ")||"なし");
 console.log(out.join("\n"));ws.close();ch.kill();process.exit(0);
})();
