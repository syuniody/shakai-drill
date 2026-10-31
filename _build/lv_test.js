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
 ok("初期はレベル欄なし（地理すべて＝第1章も含むので出る）",(await ev('$("lvWrap").hidden'))===false);
 await ev('subject="歴史";sources=[];current="all";refresh();1');await sleep(300);
 ok("歴史ではレベル欄が隠れる",(await ev('$("lvWrap").hidden'))===true);
 await ev('subject="地理";sources=["map1","map2"];current="all";filter="all";level="all";refresh();1');await sleep(300);
 ok("第1章 全部231",(await ev('pool().length'))===231,await ev('pool().length'));
 await ev('$("level").value="k";$("level").onchange();1');await sleep(300);
 ok("基本144",(await ev('pool().length'))===144,await ev('pool().length'));
 ok("一覧の行も144",(await ev('document.querySelectorAll("#list .q").length'))===144,await ev('document.querySelectorAll("#list .q").length'));
 ok("保存される",(await ev('JSON.parse(localStorage.getItem(PKEY)).level'))==="k");
 await ev('$("level").value="h";$("level").onchange();1');await sleep(300);
 ok("発展87",(await ev('pool().length'))===87,await ev('pool().length'));
 await shot(process.env.OUT+"/lv_list.png");
 // 他の地方は絞り込みの影響を受けない
 await ev('sources=["kanto"];refresh();1');await sleep(300);
 ok("関東はレベル欄なし",(await ev('$("lvWrap").hidden'))===true);
 ok("関東は全部出る",(await ev('pool().length'))===(await ev('DATA.filter(s=>s.from==="kanto").reduce((a,s)=>a+s.items.length,0)')));
 // 地理すべて＋基本：第1章の発展だけ消える
 await ev('sources=[];level="k";refresh();1');await sleep(300);
 ok("地理すべて＋基本＝1944-87",(await ev('pool().length'))===1944-87,await ev('pool().length'));
 // カード
 await ev('sources=["map2"];current="mp14";level="all";refresh();startSession(pool().filter(r=>LV[r.key]==="h").slice(0,1));1');await sleep(1000);
 ok("カードに［発展］",(await ev('document.querySelector(".card .tag, .tag").textContent')).indexOf("発展")>=0,await ev('document.querySelector(".tag").textContent'));
 await shot(process.env.OUT+"/lv_card.png");
 await ev(`mode="list";sources=["map1"];current="mp8";level="all";refresh();window.scrollTo(0,document.querySelector(".sec").getBoundingClientRect().top+scrollY);1`);await sleep(500);
 await shot(process.env.OUT+"/lv_top.png");
 ok("JSエラーなし",errs.length===0,errs.join(" / ")||"なし");
 console.log(out.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
