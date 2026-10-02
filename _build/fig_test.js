const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9393;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const prof=fs.mkdtempSync("/tmp/cdp-");
 const ch=spawn(CH,["--headless=new","--disable-gpu","--remote-debugging-port="+PORT,"--user-data-dir="+prof,"about:blank"],{stdio:"ignore"});
 let tabs=null;for(let i=0;i<40;i++){try{tabs=await (await fetch("http://127.0.0.1:"+PORT+"/json")).json();if(tabs.length)break;}catch(e){}await sleep(250);}
 const ws=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener("open",r));
 let id=0;const pend={};ws.addEventListener("message",ev=>{const m=JSON.parse(ev.data);if(m.id&&pend[m.id]){pend[m.id](m.result||m);delete pend[m.id];}});
 const send=(m,p={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method:m,params:p}));});
 const ev=async x=>{const r=await send("Runtime.evaluate",{expression:x,awaitPromise:true,returnByValue:true});return r.result?r.result.value:r;};
 const shot=async n=>{const r=await send("Page.captureScreenshot",{format:"png"});fs.writeFileSync(n,Buffer.from(r.data,"base64"));};
 await send("Page.enable");await send("Emulation.setDeviceMetricsOverride",{width:390,height:820,deviceScaleFactor:1.5,mobile:true});
 await send("Page.navigate",{url:"file://"+path.resolve("t.html")});await sleep(1700);
 const out=[];const ok=(n,c,d)=>out.push((c?"OK   ":"FAIL ")+n+(d!==undefined?"  ("+d+")":""));
 await ev('localStorage.clear();draw();1');
 // コンビナートの問題（地図不要）をカードで出す
 await ev(`(function(){const s=DATA.find(x=>x.id==="cs7");const i=s.items.findIndex(it=>/パイプライン/.test(it[0]));
   const r=rows(s)[i];sess={items:[r],i:0,res:{},range:"テスト"};mode="card";draw();return i;})()`);await sleep(400);
 ok("コンビナートの問題で地図が出ない", !(await ev('!!document.querySelector(".card-map")')), await ev('document.querySelector(".card-q").textContent.slice(0,22)'));
 await shot("n1_nomap.png");
 // 地図中のAの問題
 await ev(`(function(){const s=DATA.find(x=>x.id==="cs7");const i=s.items.findIndex(it=>/地図中のA/.test(it[0]));
   const r=rows(s)[i];sess={items:[r],i:0,res:{},range:"テスト"};mode="card";draw();})();1`);await sleep(400);
 ok("「地図中のA」の問題では地図が出る", (await ev('!!document.querySelector(".card-map .cmap")')), await ev('document.querySelector(".card-q").textContent.slice(0,20)'));
 await shot("n2_map.png");
 // フラッシュ暗記でも同じ判定
 await ev(`(function(){const s=DATA.find(x=>x.id==="cs7");const a=rows(s).filter(r=>/パイプライン/.test(r.q));
   fl={items:a,i:0,phase:"q",paused:true,range:"テスト"};mode="flash";draw();})();1`);await sleep(400);
 ok("フラッシュ暗記でも不要なら出ない", !(await ev('!!document.querySelector(".fl-map")')));
 await ev(`(function(){const s=DATA.find(x=>x.id==="cs7");const a=rows(s).filter(r=>/地図中のB/.test(r.q));
   fl={items:a,i:0,phase:"q",paused:true,range:"テスト"};mode="flash";draw();})();1`);await sleep(400);
 ok("フラッシュ暗記で必要なら出る", (await ev('!!document.querySelector(".fl-map .cmap")')));
 // 一覧では分野の先頭に1枚だけ出る
 await ev('flClear();fl=null;mode="list";sources=["chushikoku"];current="cs7";draw();1');await sleep(500);
 ok("一覧は分野の先頭に1枚だけ", (await ev('document.querySelectorAll("#list .mapbox").length'))===1, "枚数="+await ev('document.querySelectorAll("#list .mapbox").length'));
 console.log(out.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
