import io,os,json,re
dep=os.path.expanduser("~/Desktop/shakai-drill-deploy/jp9pyw1wu4/index.html")
s=io.open(dep,encoding="utf-8").read()
s=s[s.index("<title>"):]; s=s[:s.rindex("</body>")].rstrip()+"\n"
assert "v29" in s and 'id:"hokkaido"' not in s
def rep(a,b):
    global s
    assert s.count(a)==1,"COUNT %d: %s"%(s.count(a),a[:80])
    s=s.replace(a,b,1)

# 1) はんいを2つに分ける（北海道を東北の前に置く）
rep('{subject:"社会",id:"tohoku",short:"北海道・東北地方",title:"北海道・東北地方（北海道・青森・岩手・宮城・秋田・山形・福島）"}',
    '{subject:"社会",id:"hokkaido",short:"北海道",title:"北海道地方"},\n{subject:"社会",id:"tohoku",short:"東北地方",title:"東北地方（青森・岩手・宮城・秋田・山形・福島）"}')

# 2) 北海道の分野を付けかえ（idは変えないので記録は残る）
for sid in ["th11","th12","th13","th14","th15","th16","th17","th18"]:
    rep('{id:"%s",from:"tohoku"'%sid,'{id:"%s",from:"hokkaido"'%sid)

# 3) 両方にまたがる分野は東北側に残し、名前を実態に合わせる
rep('"北海道・東北：道県と道県庁所在地（地図）"','"東北・北海道：道県と道県庁所在地（地図）"')
rep('"北海道・東北：テスト形式（道県の説明→名前と位置）"','"東北・北海道：テスト形式（道県の説明→名前と位置）"')
rep('"北海道・東北：テスト形式（地域の特色）"','"東北・北海道：テスト形式（地域の特色）"')
rep('"北海道・東北：漢字で書く（テスト対策）"','"東北・北海道：漢字で書く（テスト対策）"')

# 4) 北海道だけで完結するよう、テスト形式と漢字を追加
def W(y,k): return ("「%s」を漢字で書くと。"%y,k)
NEW=[
("hk1","hokkaido","北海道：テスト形式（地域の特色）","",[
("面積が全国1位で、日本の面積の約22％をしめる都道府県は。","北海道"),
("北海道の道庁所在地と、その町なみの特色は。","札幌市・碁盤の目のように区画された計画都市"),
("かつては泥炭地で稲作に向かなかったが、客土によって日本有数の米どころになった平野は。","石狩平野"),
("じゃがいも・てんさい・小麦・豆類を、年ごとに作物をかえる輪作でつくっている平野は。","十勝平野"),
("夏の濃霧で気温が上がらず、火山灰の土地のため、大規模な酪農地帯になった台地は。","根釧台地"),
("かつては炭鉱で栄えたが、閉山後にメロンや観光で知られるようになった市は。","夕張市"),
("砂浜を掘りこんでつくった港を中心に、製紙・パルプ工業が発達した市は。","苫小牧市"),
("冬にオホーツク海の沿岸へおしよせるものは。","流氷"),
("2005年に世界自然遺産に登録された、北海道の半島は。","知床半島"),
("日本で最初にラムサール条約に登録され、タンチョウがすむ湿原は。","釧路湿原"),
("ロシアが占拠している、択捉島・国後島・色丹島・歯舞群島をまとめて何というか。","北方領土"),
("北海道の先住民族と、2020年に白老町に開かれた施設の愛称は。","アイヌ民族・ウポポイ"),
("明治時代に、北海道の開拓と警備にあたった人々は。","屯田兵"),
("北海道の工業で、出荷額の割合が最も高い工業は。","食料品工業"),
("農業産出額・漁獲量・生乳の生産量が全国1位の都道府県は。","北海道"),
]),
("hk2","hokkaido","北海道：漢字で書く（テスト対策）","",[
W("ほっかいどう","北海道"),("北海道の道庁所在地「さっぽろ」市を漢字で書くと。","札幌市"),
W("いしかり平野","石狩平野"),W("とかち平野","十勝平野"),W("こんせん台地","根釧台地"),W("かみかわ盆地","上川盆地"),
W("しれとこ半島","知床半島"),W("そうやみさき","宗谷岬"),W("えりもみさき","襟裳岬"),W("くしろしつげん","釧路湿原"),
W("とうやこ","洞爺湖"),W("りゅうひょう","流氷"),W("きゃくど","客土"),W("りんさく","輪作"),W("らくのう","酪農"),
W("ほっぽうりょうど","北方領土"),W("えとろふ島","択捉島"),W("くなしり島","国後島"),W("しこたん島","色丹島"),W("はぼまい群島","歯舞群島"),
W("とんでんへい","屯田兵"),W("かいたくし","開拓使"),W("とまこまい市","苫小牧市"),W("むろらん市","室蘭市"),W("はこだて市","函館市"),
]),
]
secs=[]
for sid,src,title,fig,items in NEW:
    assert all(len(x)==2 and x[0] and x[1] for x in items),sid
    its=",\n".join("["+json.dumps(q,ensure_ascii=False)+","+json.dumps(a,ensure_ascii=False)+"]" for q,a in items)
    f=(',figure:"%s"'%fig) if fig else ""
    secs.append('{id:"%s",from:"%s",title:%s,page:"テスト形式"%s,items:[\n%s\n]}'%(sid,src,json.dumps(title,ensure_ascii=False),f,its))
k=s.index("DATA.forEach(s=>s.items.forEach(")
e=s.rindex("];",0,k)
s=s[:e].rstrip()+",\n"+",\n".join(secs)+"\n"+s[e:]

RB={"苫小牧市":"とまこまいし","室蘭市":"むろらん市".replace("市",""),"函館市":"はこだてし","上川盆地":"かみかわぼんち","白老町":"しらおいちょう","泥炭地":"でいたんち","豆類":"るいまめ"}
RB["室蘭市"]="むろらんし"; RB["豆類"]="まめるい"
add=",".join(json.dumps(k2,ensure_ascii=False)+":"+json.dumps(v,ensure_ascii=False) for k2,v in RB.items() if ('"'+k2+'":') not in s)
m=re.search(r'\n\};\nconst RUBY_KEYS=',s); assert m
if add: s=s[:m.start()]+",\n"+add+s[m.start():]

rep("v29 ・ 9/28更新","v30 ・ 10/2更新")
io.open("kankyo-drill.html","w",encoding="utf-8").write(s); io.open("env-drill.html","w",encoding="utf-8").write(s)
i=s.rindex("<script>"); io.open("check.js","w",encoding="utf-8").write(s[i+8:s.rindex("</script>")])
print("built",len(s))
