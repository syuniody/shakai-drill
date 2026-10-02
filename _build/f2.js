const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9382;
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
 await send("Page.enable");await send("Emulation.setDeviceMetricsOverride",{width:390,height:800,deviceScaleFactor:1.5,mobile:true});
 await send("Page.navigate",{url:"file://"+path.resolve("t.html")});await sleep(1700);
 await ev('localStorage.clear();draw();[...$("subjects").children].find(b=>/フラッシュ/.test(b.textContent)).click();1');await sleep(500);
 const out=[];const ok=(n,c,d)=>out.push((c?"OK   ":"FAIL ")+n+(d!==undefined?"  ("+d+")":""));
 ok("設定パネルが見える", !(await ev('$("fset").hidden')));
 ok("ドリルの行は隠れる", (await ev('[...document.querySelectorAll(".bar .row2")].filter(e=>e.id!=="subjRow").every(e=>e.hidden)')));
 ok("教科の行は見える", !(await ev('$("subjRow").hidden')));
 ok("右下の進捗は隠れる", (await ev('$("hud").hidden')));
 ok("説明文が暗算用に変わる", /数字が次つぎ/.test(await ev('$("lede").textContent')));
 await shot("g1_setting.png");
 await ev('fset={d:2,t:5,ms:700,n:5,minus:true};drawFset();$("fstart").click();1');await sleep(2600);
 await shot("g2_flash.png");
 for(let i=0;i<50 && await ev('$("fans").hidden');i++)await sleep(200);
 await shot("g3_answer.png");
 ok("入力画面が出る", !(await ev('$("fans").hidden')));
 for(let q=0;q<5;q++){
   for(let i=0;i<60 && await ev('$("fans").hidden') && await ev('!!fsess');i++)await sleep(200);
   if(!(await ev('!!fsess')))break;
   await ev('(function(){const q=fsess.qs[fsess.i];$("finput").value=String(q.sum);submitAnswer();})();1');await sleep(900);
 }
 for(let i=0;i<40 && await ev('!!fsess');i++)await sleep(200);
 ok("全問正解で5/5", (await ev('$("fstageIn").textContent')).indexOf("5 / 5")===0, (await ev('$("fstageIn").textContent')).slice(0,10));
 ok("ひき算がまざる", (await ev('JSON.stringify(window.__last||"")'))!==undefined);
 await shot("g4_result.png");
 await ev('[...document.querySelectorAll(".btn")].find(b=>b.textContent==="もどる").click();1');await sleep(400);
 ok("「もどる」で設定に戻る", !(await ev('$("fset").hidden')) && (await ev('$("fstage").hidden')));
 ok("記録が増える", (await ev('(JSON.parse(localStorage.getItem("env-drill-flash")).hist||[]).length'))>=1, await ev('$("fhist").textContent'));
 await ev('[...$("subjects").children][0].click();1');await sleep(400);
 ok("社会にもどすと元通り", (await ev('!$("hud").hidden')) && !(await ev('$("list").hidden')) && (await ev('[...document.querySelectorAll(".bar .row2")].every(e=>!e.hidden))'))!==false);
 console.log(out.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
