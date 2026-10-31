const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9401;
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

 ok("地理の合計",(await ev('DATA.filter(s=>(SRC[s.from]||{}).subject==="地理").reduce((a,s)=>a+s.items.length,0)'))===1713+231,await ev('DATA.filter(s=>(SRC[s.from]||{}).subject==="地理").reduce((a,s)=>a+s.items.length,0)'));
 ok("歴史は812のまま",(await ev('DATA.filter(s=>(SRC[s.from]||{}).subject==="歴史").reduce((a,s)=>a+s.items.length,0)'))===812);
 ok("既存キー th6",(await ev('DATA.find(s=>s.id==="th6").items[9][1]'))==="南部鉄器");
 ok("既存キー hz34c",(await ev('DATA.find(s=>s.id==="hz34c").items[3][1]'))==="三内丸山遺跡");
 ok("地理のはんい先頭が地図の見方",(await ev('subSrc().map(s=>s.id).slice(0,2).join()'))==="map1,map2",await ev('subSrc().map(s=>s.id).slice(0,3).join()'));
 await ev('localStorage.clear();subject="地理";sources=[];current="all";draw();srcOpen(true);1');await sleep(400);
 await shot(process.env.OUT+"/chizu_menu.png");
 await ev('[...document.querySelectorAll("#srcPop .opt")].find(x=>x.textContent.indexOf("第1章")>=0).click();1');await sleep(400);
 ok("プリセットで map1+map2",JSON.stringify(await ev('sources'))==='["map1","map2"]',JSON.stringify(await ev('sources')));
 ok("プール231問",(await ev('pool().length'))===231,await ev('pool().length'));
 // カード：建物①の図
 await ev('srcOpen(false);sources=["map1"];current="mp5";count=0;refresh();startSession(pool());1');await sleep(1200);
 ok("カードに図が出る",(await ev('!!document.querySelector(".cmap .cell")')));
 ok("図の注記",(await ev('(document.querySelector(".mapcap")||{}).textContent'))||"",await ev('(document.querySelector(".mapcap")||{}).textContent'));
 await shot(process.env.OUT+"/chizu_card.png");
 // 図のない分野ではカードに図が出ない
 await ev('mode="list";sources=["map2"];current="mp14";refresh();startSession(pool());1');await sleep(1200);
 ok("時差の計算は図なし",!(await ev('!!document.querySelector(".cmap")')));
 await shot(process.env.OUT+"/chizu_card2.png");
 // 広い画面の一覧
 await send("Emulation.setDeviceMetricsOverride",{width:1280,height:900,deviceScaleFactor:1,mobile:false});
 await ev('mode="list";sources=["map1"];current="mp6";refresh();draw();window.scrollTo(0,document.querySelector(".has-map").getBoundingClientRect().top+scrollY-20);1');await sleep(900);
 await shot(process.env.OUT+"/chizu_list.png");
 // 黒背景
 await ev('document.documentElement.setAttribute("data-theme","dark");1');await sleep(400);
 await shot(process.env.OUT+"/chizu_dark.png");
 ok("JSエラーなし（最後）",errs.length===0,errs.join(" / ")||"なし");
 console.log(out.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
