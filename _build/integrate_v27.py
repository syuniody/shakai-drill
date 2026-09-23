import io,json,os,re
import data_rika1,data_rika2
dep=os.path.expanduser("~/Desktop/shakai-drill-deploy/jp9pyw1wu4/index.html")
s=io.open(dep,encoding="utf-8").read()
s=s[s.index("<title>"):]; s=s[:s.rindex("</body>")].rstrip()+"\n"
assert "v26" in s and "subject" not in s
def rep(a,b):
    global s
    assert s.count(a)==1,"COUNT %d: %s"%(s.count(a),a[:70])
    s=s.replace(a,b,1)

# 1) 名前
rep("<title>小学生社会一問一答ドリル</title>","<title>小学生一問一答ドリル</title>")
rep("<h1>小学生社会　<span class=\"mark\">一問一答</span>ドリル</h1>","<h1>小学生　<span class=\"mark\">一問一答</span>ドリル</h1>")
rep('    <p class="eyebrow">テキスト準拠　赤シート式</p>','    <p class="eyebrow">社会・理科　赤シート式</p>')
rep("テキストで赤線・青線が引かれた語句を答えにしたドリルです。はんいと問題数を選んで「はじめる」を押すと、1問ずつ出ます。赤いところを1回押すとヒント、もう一度押すと答えです。",
    "教科とはんいと問題数を選んで「はじめる」を押すと、1問ずつ出ます。赤いところを1回押すとヒント、もう一度押すと答えです。")

# 2) SOURCES に教科をつける＋理科を追加
i=s.index("const SOURCES=["); j=s.index("\n];",i)
block=s[i:j]
block=re.sub(r'\{id:"(u31|u32|tohoku|kanto|chubu|kinki|chushikoku|kyushu)"', lambda m:'{subject:"社会",id:"%s"'%m.group(1), block)
block+=',\n{subject:"理科",id:"rika",short:"理科",title:"理科（中学受験の頻出）"}'
s=s[:i]+block+s[j:]

# 3) 理科の問題を追加
secs=[]
for M in (data_rika1,data_rika2):
    for sid,title,fig,items in M.SECTIONS:
        its=",\n".join("["+json.dumps(q,ensure_ascii=False)+","+json.dumps(a,ensure_ascii=False)+"]" for q,a in items)
        f=(',figure:"%s"'%fig) if fig else ""
        secs.append('{id:"%s",from:"rika",title:%s,page:"受験頻出"%s,items:[\n%s\n]}'%(sid,json.dumps(title,ensure_ascii=False),f,its))
k=s.index("DATA.forEach(s=>s.items.forEach(")
e=s.rindex("];",0,k)
s=s[:e].rstrip()+",\n"+",\n".join(secs)+"\n"+s[e:]

# 4) 教科の選択UI
rep('''      <div class="row2">
        <span class="lab">はんい</span>''','''      <div class="row2">
        <span class="lab">教科</span>
        <span class="chips" id="subjects"></span>
      </div>
      <div class="row2">
        <span class="lab">はんい</span>''')

# 5) ロジック：教科でしぼる
rep('let sources=[], current="all", filter="all", count=20;','let subject="社会", sources=[], current="all", filter="all", count=20;')
rep('function savePrefs(){try{localStorage.setItem(PKEY,JSON.stringify({sources:sources,current:current,filter:filter,count:count}));}catch(e){}}',
    'function savePrefs(){try{localStorage.setItem(PKEY,JSON.stringify({subject:subject,sources:sources,current:current,filter:filter,count:count}));}catch(e){}}')
rep('const total=DATA.reduce((n,s)=>n+s.items.length,0);',
'''const SUBJECTS=SOURCES.map(x=>x.subject).filter((x,i,a)=>a.indexOf(x)===i);
function subSrc(){return SOURCES.filter(x=>x.subject===subject);}
function subSecs(){return DATA.filter(x=>(SRC[x.from]||{}).subject===subject);}
let total=0;
function recount(){total=subSecs().reduce((n,s)=>n+s.items.length,0);$("total").textContent=total;$("nsrc").textContent=subSrc().length;$("nsec").textContent=subSecs().length;}''')
rep('function sections(){return DATA.filter(x=>!sources.length||sources.indexOf(x.from)>=0);}',
    'function sections(){return subSecs().filter(x=>!sources.length||sources.indexOf(x.from)>=0);}')
rep('''    ...SOURCES.map(function(x){''','''    ...subSrc().map(function(x){''')
rep('''function drawSources(){''','''function drawSubjects(){
  $("subjects").replaceChildren(...SUBJECTS.map(function(sb){
    const b=document.createElement("button");b.className="tab";b.type="button";
    b.setAttribute("aria-selected",String(sb===subject));
    const n=DATA.filter(d=>(SRC[d.from]||{}).subject===sb).reduce((a,d)=>a+d.items.length,0);
    b.appendChild(document.createTextNode(sb));
    const sp=document.createElement("span");sp.className="n";sp.textContent=n;b.appendChild(sp);
    b.onclick=function(){if(sb===subject)return;subject=sb;sources=[];current="all";recount();refresh();};
    return b;
  }));
}
function drawSources(){''')
rep("  drawSources();drawUnits();drawCounts();","  recount();drawSubjects();drawSources();drawUnits();drawCounts();")
# 起動時：保存した教科を戻す
rep('''    if(p){
      if(Array.isArray(p.sources))sources=p.sources.filter(id=>SRC[id]);''','''    if(p){
      if(p.subject&&SUBJECTS.indexOf(p.subject)>=0)subject=p.subject;
      if(Array.isArray(p.sources))sources=p.sources.filter(id=>SRC[id]&&SRC[id].subject===subject);''')
# 教科をまたぐ記録も数えられるよう、右下の表示は選択中の教科の中で数える（scopeItemsは既に教科でしぼられる）

# 6) ふりがな
RB=json.load(io.open("rb3.json",encoding="utf-8"))
add=",".join(json.dumps(k,ensure_ascii=False)+":"+json.dumps(v,ensure_ascii=False) for k,v in RB.items() if ('"'+k+'":') not in s)
m=re.search(r'\n\};\nconst RUBY_KEYS=',s); assert m
if add: s=s[:m.start()]+",\n"+add+s[m.start():]

rep("v26 ・ 9/20更新","v27 ・ 9/23更新")
io.open("kankyo-drill.html","w",encoding="utf-8").write(s); io.open("env-drill.html","w",encoding="utf-8").write(s)
i=s.rindex("<script>"); io.open("check.js","w",encoding="utf-8").write(s[i+8:s.rindex("</script>")])
print("built",len(s))
