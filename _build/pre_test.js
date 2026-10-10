const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9399;
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
 await send("Emulation.setDeviceMetricsOverride",{width:390,height:900,deviceScaleFactor:1.5,mobile:true});
 await send("Page.navigate",{url:"file://"+path.resolve("t.html")});await sleep(1900);
 const out=[];const ok=(n,c,dd)=>out.push((c?"OK   ":"FAIL ")+n+(dd!==undefined?"  ("+dd+")":""));
 ok("JSエラーなし",errs.length===0,errs.join(" / ")||"なし");
 ok("歴史812問",(await ev('DATA.filter(s=>(SRC[s.from]||{}).subject==="歴史").reduce((a,s)=>a+s.items.length,0)'))===812);
 ok("地理1713問のまま",(await ev('DATA.filter(s=>(SRC[s.from]||{}).subject==="地理").reduce((a,s)=>a+s.items.length,0)'))===1713);
 ok("東北の記録キーが保てている",(await ev('DATA.find(s=>s.id==="th6").items[9][1]'))==="南部鉄器");
 ok("既存の歴史セクションも無事",(await ev('DATA.find(s=>s.id==="hz34c").items[3][1]'))==="三内丸山遺跡",await ev('DATA.find(s=>s.id==="hz34c").items[3][0]'));
 // プリセット
 await ev('localStorage.clear();subject="歴史";sources=[];current="all";draw();srcOpen(true);1');await sleep(400);
 const heads=await ev('[...document.querySelectorAll("#srcPop .opt.head")].map(x=>x.textContent)');
 ok("まとめて選ぶ見出しが出る",heads.length===2,heads.join(" / "));
 const names=await ev('[...document.querySelectorAll("#srcPop .opt")].filter(x=>!x.classList.contains("head")).map(x=>x.textContent).slice(0,8)');
 ok("原始時代のプリセットがある",names.some(x=>x.indexOf("原始時代")>=0),names.join(" / "));
 await shot("pre_menu.png");
 // 押すと3単元が選ばれる
 await ev('[...document.querySelectorAll("#srcPop .opt")].find(x=>x.textContent.indexOf("原始時代")>=0).click();1');await sleep(400);
 ok("原始時代＝34・35・36が選ばれる",JSON.stringify(await ev('sources'))===JSON.stringify(["hi34","hi35","hi36"]),JSON.stringify(await ev('sources')));
 const n=await ev('pool().length');
 ok("原始時代の問題数",n===49+47+37+41-0,n+"問");
 ok("弥生の問題が入っている",(await ev('pool().some(r=>/吉野ヶ里/.test(r.q))')));
 ok("古墳の問題は入らない",!(await ev('pool().some(r=>/前方後円墳/.test(r.q))')));
 // 今回落とした論点が引ける
 for(const [q,a] of [["青銅器","青銅器"],["つりがね形","銅鐸"],["石包丁は、何をする","稲の穂先を刈り取るため"],["穂先だけを刈り取ること","穂首刈り"],
   ["岩宿遺跡の時代と県","旧石器時代・群馬県"],["吉野ヶ里遺跡の時代と県","弥生時代・佐賀県"],["楽浪郡の海の向こう","漢書地理志"],
   ["高床倉庫の「ゆか」","床"],["くわ・すき・田げた","弥生時代"]]){
   const got=await ev(`(function(){const r=DATA.flatMap(s=>s.items).find(it=>it[0].indexOf(${JSON.stringify(q)})>=0);return r?r[1]:"(なし)";})()`);
   ok("「"+q+"…」",got===a,got);
 }
 // 地理にはプリセットを出さない
 await ev('subject="地理";sources=[];draw();srcOpen(true);1');await sleep(300);
 ok("地理には出さない",(await ev('document.querySelectorAll("#srcPop .opt.head").length'))===0);
 console.log(out.join("\n"));if(errs.length)console.log("ERR:",errs.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
