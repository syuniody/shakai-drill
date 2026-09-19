import io,os
dep=os.path.expanduser("~/Desktop/shakai-drill-deploy/jp9pyw1wu4/index.html")
s=io.open(dep,encoding="utf-8").read()
s=s[s.index("<title>"):]; s=s[:s.rindex("</body>")].rstrip()+"\n"
assert "v25" in s
def rep(a,b):
    global s
    assert s.count(a)==1,"COUNT %d: %s"%(s.count(a),a[:70])
    s=s.replace(a,b,1)
# CSS
rep(".nudge .rt{",""".nudge.line{border-color:color-mix(in srgb,var(--red) 55%,transparent);background:color-mix(in srgb,var(--film) 10%,var(--paper))}
.nudge a.btn{text-decoration:none;display:inline-flex;align-items:center}
.nudge .rt{""")
# HTML：LINE用のお知らせと、引き継ぎ完了のお知らせ（見出しの直後＝一番目立つ位置）
rep('''  <nav class="bar" id="bar">''','''  <div class="nudge line" id="lineBar" hidden style="margin-top:14px">
    <span class="rt">いまLINEの中のブラウザで開いています。LINEのブラウザは、戻るボタンで閉じたときなどに記録が消えることがあります。下のボタンで、いつものブラウザ（Chromeなど）で開き直してください。記録もいっしょに引き継ぎます。</span>
    <a class="btn primary" id="lineOpen" href="#" rel="noopener">いつものブラウザで開く</a>
  </div>
  <div class="resume" id="carryBar" hidden style="margin-top:14px">
    <span class="rt" id="carryText"></span>
    <button class="btn small" id="carryClose" type="button">閉じる</button>
  </div>

  <nav class="bar" id="bar">''')
# JS：記録をURLにのせて運ぶ／受け取る
rep('\ndraw();\nif(!Object.keys(marks).length){','''
function packMarks(){return Object.keys(marks).filter(k=>marks[k]==="ok"||marks[k]==="ng").map(k=>k+(marks[k]==="ok"?"!":"_")).join(",");}
function openURL(){return location.origin+location.pathname+"?openExternalBrowser=1"+(Object.keys(marks).length?"#m="+packMarks():"");}
const IN_LINE=/\\bLine\\//i.test(navigator.userAgent||"");
if(IN_LINE){
  $("lineBar").hidden=false;
  const a=$("lineOpen");a.href=openURL();
  a.addEventListener("click",function(){a.href=openURL();});
}
(function(){
  const h=location.hash||"";
  if(h.indexOf("#m=")!==0)return;
  let n=0;
  decodeURIComponent(h.slice(3)).split(",").forEach(function(t){
    const m=/^([A-Za-z0-9-]+)([!_])$/.exec(t);if(!m)return;
    marks[m[1]]=(m[2]==="!")?"ok":"ng";n++;
  });
  try{history.replaceState(history.state,"",location.pathname+location.search.replace(/[?&]openExternalBrowser=1/,"").replace(/^&/,"?"));}catch(e){}
  if(n){
    save();
    $("carryText").textContent="LINEのブラウザから記録を引き継ぎました（"+n+"件）。これからはこのブラウザで使ってください。ホーム画面に追加しておくと便利です。";
    $("carryBar").hidden=false;
  }
})();
$("carryClose").onclick=function(){$("carryBar").hidden=true;};

draw();
if(!Object.keys(marks).length){''')
rep("v25 ・ 9/20更新","v26 ・ 9/20更新")
io.open("kankyo-drill.html","w",encoding="utf-8").write(s); io.open("env-drill.html","w",encoding="utf-8").write(s)
i=s.rindex("<script>"); io.open("check.js","w",encoding="utf-8").write(s[i+8:s.rindex("</script>")])
print("built",len(s))
