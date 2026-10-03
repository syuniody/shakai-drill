const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9394;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const prof=fs.mkdtempSync("/tmp/cdp-");
 const ch=spawn(CH,["--headless=new","--disable-gpu","--remote-debugging-port="+PORT,"--user-data-dir="+prof,"about:blank"],{stdio:"ignore"});
 let tabs=null;for(let i=0;i<40;i++){try{tabs=await (await fetch("http://127.0.0.1:"+PORT+"/json")).json();if(tabs.length)break;}catch(e){}await sleep(250);}
 const ws=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener("open",r));
 let id=0;const pend={};const errs=[];
 ws.addEventListener("message",ev=>{const m=JSON.parse(ev.data);
   if(m.method==="Runtime.exceptionThrown")errs.push(m.params.exceptionDetails.text+" "+(m.params.exceptionDetails.exception||{}).description);
   if(m.id&&pend[m.id]){pend[m.id](m.result||m);delete pend[m.id];}});
 const send=(m,p={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method:m,params:p}));});
 const ev=async x=>{const r=await send("Runtime.evaluate",{expression:x,awaitPromise:true,returnByValue:true});
   if(r.exceptionDetails)errs.push("eval:"+r.exceptionDetails.text);return r.result?r.result.value:r;};
 const shot=async n=>{const r=await send("Page.captureScreenshot",{format:"png"});fs.writeFileSync(n,Buffer.from(r.data,"base64"));};
 await send("Page.enable");await send("Runtime.enable");
 await send("Emulation.setDeviceMetricsOverride",{width:390,height:820,deviceScaleFactor:1.5,mobile:true});
 await send("Page.navigate",{url:"file://"+path.resolve("t.html")});await sleep(1800);
 const out=[];const ok=(n,c,d)=>out.push((c?"OK   ":"FAIL ")+n+(d!==undefined?"  ("+d+")":""));
 ok("JSエラーなし",errs.length===0,errs.join(" / ")||"なし");
 ok("全問題数",(await ev('DATA.reduce((a,s)=>a+s.items.length,0)'))>0,"計"+await ev('DATA.reduce((a,s)=>a+s.items.length,0)')+"問");
 const th=await ev('DATA.filter(s=>s.from==="tohoku").reduce((a,s)=>a+s.items.length,0)');
 ok("東北の問題数",th===194+31,th+"問（194→225）");
 // 既存の並びが変わっていないこと
 ok("th1の先頭が北海道のまま",(await ev('DATA.find(s=>s.id==="th1").items[0][1]'))==="北海道");
 ok("th4の15番目が八郎潟のまま",(await ev('DATA.find(s=>s.id==="th4").items[15][1]'))==="八郎潟");
 ok("th6の10番目が南部鉄器のまま",(await ev('DATA.find(s=>s.id==="th6").items[9][1]'))==="南部鉄器");
 // 新問題が引ける
 for(const [q,a] of [["南部鉄器の産地で","盛岡市"],["おうとうと西洋なし","山形盆地"],["日本三美林","青森ひば・秋田すぎ・木曽ひのき"],["あきたこまち","秋田県"],["はちろうがた","八郎潟"]]){
   const got=await ev(`(function(){const r=DATA.flatMap(s=>s.items).find(it=>it[0].indexOf(${JSON.stringify(q)})>=0);return r?r[1]:"(なし)";})()`);
   ok("新問題「"+q+"…」",got===a,got);
 }
 // 盛岡市の問題を1問カードで出す → 地図が出ないこと
 await ev('localStorage.clear();1');
 await ev(`(function(){const s=DATA.find(x=>x.id==="th6");const i=s.items.findIndex(it=>/南部鉄器の産地/.test(it[0]));
   sess={items:[rows(s)[i]],i:0,res:{},range:"テスト"};mode="card";draw();})();1`);await sleep(400);
 ok("盛岡市の問題に地図が出ない",!(await ev('!!document.querySelector(".card-map")')),await ev('document.querySelector(".card-q").textContent.slice(0,24)'));
 await shot("t1.png");
 // 東北の地図問題では出る
 await ev(`(function(){const s=DATA.find(x=>x.id==="th4");const i=s.items.findIndex(it=>/地図中のE/.test(it[0]));
   sess={items:[rows(s)[i]],i:0,res:{},range:"テスト"};mode="card";draw();})();1`);await sleep(400);
 ok("「地図中のE」では地図が出る",(await ev('!!document.querySelector(".card-map .cmap")')),await ev('document.querySelector(".card-q").textContent.slice(0,20)'));
 await shot("t2.png");
 // 東北だけ選んでランダム20問が組めること
 await ev('sess=null;mode="list";sources=["tohoku"];current="all";draw();1');await sleep(400);
 const n=await ev('pool().length');ok("東北を選んだときの出題プール",n===225,n+"問");
 console.log(out.join("\n"));if(errs.length)console.log("ERR:",errs.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
