const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9396;
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
   if(r.exceptionDetails)errs.push("eval:"+r.exceptionDetails.text);return r.result?r.result.value:r;};
 const shot=async n=>{const r=await send("Page.captureScreenshot",{format:"png"});fs.writeFileSync(n,Buffer.from(r.data,"base64"));};
 await send("Page.enable");await send("Runtime.enable");
 await send("Emulation.setDeviceMetricsOverride",{width:390,height:900,deviceScaleFactor:1.5,mobile:true});
 await send("Page.navigate",{url:"file://"+path.resolve("t.html")});await sleep(2000);
 const out=[];const ok=(n,c,dd)=>out.push((c?"OK   ":"FAIL ")+n+(dd!==undefined?"  ("+dd+")":""));
 ok("JSエラーなし",errs.length===0,errs.join(" / ")||"なし");
 const hs=await ev('SOURCES.filter(x=>x.subject==="歴史").map(x=>x.short)');
 ok("歴史の出典16",hs.length===16,hs.join("／"));
 const hn=await ev('DATA.filter(s=>(SRC[s.from]||{}).subject==="歴史").reduce((a,s)=>a+s.items.length,0)');
 ok("歴史の問題数",hn===771,hn+"問");
 ok("地理1713問のまま",(await ev('DATA.filter(s=>(SRC[s.from]||{}).subject==="地理").reduce((a,s)=>a+s.items.length,0)'))===1713);
 ok("理科399問のまま",(await ev('DATA.filter(s=>(SRC[s.from]||{}).subject==="理科").reduce((a,s)=>a+s.items.length,0)'))===399);
 ok("地理の記録キーが保てている",(await ev('DATA.find(s=>s.id==="th6").items[9][1]'))==="南部鉄器");
 // 出典ごとの件数
 const per=await ev('SOURCES.filter(x=>x.subject==="歴史").map(x=>x.short+":"+DATA.filter(s=>s.from===x.id).reduce((a,s)=>a+s.items.length,0))');
 out.push("     "+per.join(" / "));
 ok("答えが空の問題がない",(await ev('DATA.flatMap(s=>s.items).filter(it=>!it[1]||!it[0]).length'))===0);
 ok("英単語の混入がない",(await ev('DATA.flatMap(s=>s.items).filter(it=>/[a-z]{4,}/.test(it[0].replace(/B\\.C\\.|A\\.D\\./g,""))).length'))===0,
    JSON.stringify(await ev('DATA.flatMap(s=>s.items).filter(it=>/[a-z]{4,}/.test(it[0].replace(/B\\.C\\.|A\\.D\\./g,""))).slice(0,3).map(x=>x[0])')));
 const dup=await ev('(function(){const m={},d=[];DATA.flatMap(s=>s.items).forEach(it=>{if(m[it[0]])d.push(it[0]);else m[it[0]]=1;});return d.slice(0,5);})()');
 ok("問題文の重複がない",dup.length===0,dup.join(" / ")||"なし");
 // 出題できる
 await ev('localStorage.clear();subject="歴史";sources=["hi46"];current="all";draw();1');await sleep(400);
 ok("単元46だけ選べる",(await ev('pool().length'))===37,await ev('pool().length')+"問");
 await ev(`(function(){const s=DATA.find(x=>x.id==="hz99a");sess={items:[rows(s)[8]],i:0,res:{},range:"テスト"};mode="card";draw();})();1`);await sleep(400);
 ok("年号の問題がカードで出る",(await ev('document.querySelector(".card-q").textContent')).indexOf("701")>=0,await ev('document.querySelector(".card-q").textContent.slice(0,24)'));
 ok("地図は出ない",!(await ev('!!document.querySelector(".card-map")')));
 await shot("hh1.png");
 await ev('sess=null;mode="list";subject="歴史";sources=SOURCES.filter(x=>x.subject==="歴史").map(x=>x.id);current="hz45c";draw();1');await sleep(600);
 await shot("hh2.png");
 console.log(out.join("\n"));if(errs.length)console.log("ERR:",errs.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
