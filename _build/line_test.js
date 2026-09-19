const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function browser(port,ua){
  const prof=fs.mkdtempSync("/tmp/cdp-");
  const ch=spawn(CH,["--headless=new","--disable-gpu","--remote-debugging-port="+port,"--user-data-dir="+prof,"about:blank"],{stdio:"ignore"});
  let tabs=null;for(let i=0;i<40;i++){try{tabs=await (await fetch("http://127.0.0.1:"+port+"/json")).json();if(tabs.length)break;}catch(e){}await sleep(250);}
  const ws=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener("open",r));
  let id=0;const pend={};ws.addEventListener("message",ev=>{const m=JSON.parse(ev.data);if(m.id&&pend[m.id]){pend[m.id](m.result||m);delete pend[m.id];}});
  const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}));});
  const ev=async(x)=>{const r=await send("Runtime.evaluate",{expression:x,awaitPromise:true,returnByValue:true});return r.result?r.result.value:r;};
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride",{width:390,height:760,deviceScaleFactor:1.5,mobile:true});
  if(ua)await send("Emulation.setUserAgentOverride",{userAgent:ua});
  return {send,ev,close:()=>{ws.close();ch.kill();}};
}
(async()=>{
  const base="file://"+path.resolve("t.html");const out=[];const ok=(n,c,d)=>out.push((c?"OK   ":"FAIL ")+n+(d!==undefined?"  ("+d+")":""));
  const LINEUA="Mozilla/5.0 (Linux; Android 14; SC-51D Build/UP1A) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/128.0.0.0 Mobile Safari/537.36 Line/14.15.1/IAB";
  const A=await browser(9351,LINEUA);
  await A.send("Page.navigate",{url:base});await sleep(1500);
  await A.ev('localStorage.clear();sources=["chubu"];current="c1";count=10;draw();$("start").click();for(let i=0;i<10;i++)judge(i<7?"ok":"ng");goList();1');await sleep(600);
  ok("LINEのブラウザでお知らせが出る", await A.ev('!$("lineBar").hidden'));
  const href=await A.ev('$("lineOpen").href');
  ok("ボタンのリンク先に openExternalBrowser=1 と記録", /openExternalBrowser=1/.test(href)&&/#m=/.test(href), href.slice(href.indexOf("?"),href.indexOf("?")+60)+"…");
  const r=await A.send("Page.captureScreenshot",{format:"png"});fs.writeFileSync("l1.png",Buffer.from(r.data,"base64"));
  A.close();
  const B=await browser(9352,null);
  const target=base+href.slice(href.indexOf("?"));
  await B.send("Page.navigate",{url:target});await sleep(1700);
  ok("普段のブラウザ側ではLINEのお知らせは出ない", await B.ev('$("lineBar").hidden'));
  ok("記録が引き継がれる", await B.ev('Object.keys(marks).length')===10, await B.ev('Object.values(marks).filter(v=>v==="ok").length+"◯ "+Object.values(marks).filter(v=>v==="ng").length+"△"'));
  ok("引き継ぎ完了のお知らせ", await B.ev('!$("carryBar").hidden'), await B.ev('$("carryText").textContent'));
  ok("アドレスから記録の部分が消えている", await B.ev('location.hash===""&&!/openExternalBrowser/.test(location.search)'), await B.ev('location.search+location.hash'));
  await B.send("Page.reload",{});await sleep(1500);
  ok("読み込み直しても記録が残る", await B.ev('Object.keys(marks).length')===10);
  const r2=await B.send("Page.navigate",{url:target});await sleep(1500);
  const r3=await B.send("Page.captureScreenshot",{format:"png"});fs.writeFileSync("l2.png",Buffer.from(r3.data,"base64"));
  B.close();
  console.log(out.join("\n"));
})().catch(e=>{console.error(e);process.exit(1);});
