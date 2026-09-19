// 使い方: node shot.js  （Chromeをデバッグ接続で起動し、スクロール後の画面を撮る）
const {spawn}=require("child_process");const fs=require("fs");const path=require("path");
const CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";const PORT=9337;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shots=JSON.parse(fs.readFileSync("shots.json","utf8"));
(async()=>{
  const prof=fs.mkdtempSync("/tmp/cdp-");
  const ch=spawn(CH,["--headless=new","--disable-gpu","--remote-debugging-port="+PORT,"--user-data-dir="+prof,"about:blank"],{stdio:"ignore"});
  let tabs=null;for(let i=0;i<40;i++){try{tabs=await (await fetch("http://127.0.0.1:"+PORT+"/json")).json();if(tabs.length)break;}catch(e){}await sleep(250);}
  const ws=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);
  await new Promise(r=>ws.addEventListener("open",r));
  let id=0;const pend={};ws.addEventListener("message",ev=>{const m=JSON.parse(ev.data);if(m.id&&pend[m.id]){pend[m.id](m.result||m);delete pend[m.id];}});
  const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}));});
  await send("Page.enable");
  for(const s of shots){
    await send("Emulation.setDeviceMetricsOverride",{width:s.w,height:s.h,deviceScaleFactor:s.dsf||1,mobile:!!s.mobile});
    await send("Page.navigate",{url:"file://"+path.resolve(s.file)});await sleep(1500);
    if(s.js){await send("Runtime.evaluate",{expression:s.js});await sleep(s.wait||700);}
    if(s.js2){await send("Runtime.evaluate",{expression:s.js2});await sleep(700);}
    const r=await send("Page.captureScreenshot",{format:"png"});
    fs.writeFileSync(s.out,Buffer.from(r.data,"base64"));console.log("saved",s.out);
  }
  ws.close();ch.kill();
})().catch(e=>{console.error(e);process.exit(1);});
