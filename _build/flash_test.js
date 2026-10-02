const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9381;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const prof=fs.mkdtempSync("/tmp/cdp-");
 const ch=spawn(CH,["--headless=new","--disable-gpu","--remote-debugging-port="+PORT,"--user-data-dir="+prof,"about:blank"],{stdio:"ignore"});
 let tabs=null;for(let i=0;i<40;i++){try{tabs=await (await fetch("http://127.0.0.1:"+PORT+"/json")).json();if(tabs.length)break;}catch(e){}await sleep(250);}
 const ws=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener("open",r));
 let id=0;const pend={};const errs=[];
 ws.addEventListener("message",ev=>{const m=JSON.parse(ev.data);
  if(m.method==="Runtime.exceptionThrown")errs.push(String(m.params.exceptionDetails.exception&&m.params.exceptionDetails.exception.description||"").slice(0,200));
  if(m.id&&pend[m.id]){pend[m.id](m.result||m);delete pend[m.id];}});
 const send=(m,p={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method:m,params:p}));});
 const ev=async x=>{const r=await send("Runtime.evaluate",{expression:x,awaitPromise:true,returnByValue:true});return r.result?r.result.value:r;};
 await send("Runtime.enable");await send("Page.enable");
 await send("Emulation.setDeviceMetricsOverride",{width:390,height:760,deviceScaleFactor:1.5,mobile:true});
 await send("Page.navigate",{url:"file://"+path.resolve("t.html")});await sleep(1700);
 const out=[];const ok=(n,c,d)=>out.push((c?"OK   ":"FAIL ")+n+(d!==undefined?"  ("+d+")":""));
 await ev('localStorage.clear();draw();1');
 ok("教科に「フラッシュ暗算」がある", (await ev('[...$("subjects").children].map(b=>b.textContent).join("/")')).includes("フラッシュ暗算"), await ev('[...$("subjects").children].map(b=>b.textContent).join(" / ")'));
 await ev('[...$("subjects").children].find(b=>/フラッシュ/.test(b.textContent)).click();1');await sleep(400);
 ok("暗算の画面に切り替わる", (await ev('!$("flashWrap").hidden && $("list").hidden')), await ev('subject'));
 ok("レベルと設定が並ぶ", (await ev('$("flevel").children.length'))===8 && (await ev('$("fdigits").children.length'))===3);
 const shot=async(name)=>{const r=await send("Page.captureScreenshot",{format:"png"});fs.writeFileSync(name,Buffer.from(r.data,"base64"));};
 // 1けた3口・いちばんゆっくり・5問
 await ev('fset={d:1,t:3,ms:900,n:5,minus:false};drawFset();$("fstart").click();1');
 await sleep(900);
 ok("カウントダウンが出る", /^[123]$/.test(String(await ev('($("fstageIn").textContent||"").trim()'))), await ev('($("fstageIn").textContent||"").trim()'));
 await sleep(1400);
 await shot("f1_flash.png");
 const seen=[];for(let i=0;i<14;i++){const t=await ev('($("fstageIn").textContent||"").trim()');if(t&&!seen.includes(t))seen.push(t);await sleep(180);}
 ok("数字が次々に出る", seen.filter(x=>/^[0-9−]/.test(x)).length>=2, seen.join(","));
 for(let i=0;i<40 && await ev('$("fans").hidden');i++)await sleep(200);
 ok("入力画面が出る", !(await ev('$("fans").hidden')));
 await shot("f2_answer.png");
 ok("テンキーは12個", (await ev('$("fkeys").children.length'))===12);
 // わざと間違える
 await ev('["1","2","3"].forEach(c=>keyIn(c));submitAnswer();1');await sleep(300);
 ok("まちがえると正解を表示", /こたえは/.test(await ev('$("fstageIn").textContent')), await ev('$("fstageIn").textContent'));
 // 残りは正解を入れて進める
 for(let q=0;q<5;q++){
   for(let i=0;i<60 && await ev('$("fans").hidden') && await ev('!!fsess');i++)await sleep(200);
   if(!(await ev('!!fsess')))break;
   await ev('(function(){const q=fsess.qs[fsess.i];$("finput").value=String(q.sum);submitAnswer();})();1');await sleep(900);
 }
 for(let i=0;i<40 && await ev('!!fsess');i++)await sleep(200);
 ok("結果画面が出る", (await ev('$("fstageIn").textContent')).indexOf(" / 5")>0, (await ev('$("fstageIn").textContent')).slice(0,40));
 ok("4問正解（1問はわざと誤答）", (await ev('$("fstageIn").textContent')).indexOf("4 / 5")===0, (await ev('$("fstageIn").textContent')).slice(0,12));
 ok("出題内容のふりかえりが出る", (await ev('document.querySelectorAll(".freview div").length'))===5);
 await shot("f3_result.png");
 ok("記録が保存される", (await ev('(JSON.parse(localStorage.getItem("env-drill-flash")).hist||[]).length'))===1, await ev('JSON.stringify((JSON.parse(localStorage.getItem("env-drill-flash")).hist||[])[0])'));
 // 社会に戻れるか
 await ev('[...$("subjects").children][0].click();1');await sleep(400);
 ok("社会にもどせる", (await ev('subject'))==="社会" && (await ev('$("flashWrap").hidden')) && !(await ev('$("list").hidden')));
 await send("Page.reload",{});await sleep(1700);
 ok("再読込で社会のまま", (await ev('subject'))==="社会");
 out.push(errs.length?("ERR "+errs.join(" | ")):"OK   エラーなし");
 console.log(out.join("\n"));ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
