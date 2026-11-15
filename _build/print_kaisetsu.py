# -*- coding: utf-8 -*-
# 古墳時代・飛鳥時代（テスト範囲）の解説プリント A4
# 使い方: python3 _build/print_kaisetsu.py <出力フォルダ>
import io, os, re, subprocess, sys, tempfile, html, ast

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = sys.argv[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# ── ふりがな：ドリルの辞書＋print_series.py の追加分。各ページで最初に出たときだけ付ける
src = io.open(os.path.join(ROOT, "jp9pyw1wu4", "index.html"), encoding="utf-8").read()
i = src.index("const RUBY={") + len("const RUBY={"); j = src.index("};", i)
RUBY = {k: v for k, v in re.findall(r'"([^"]+)":"([^"]+)"', src[i:j]) if k != v and len(k) >= 2}
ps = io.open(os.path.join(HERE, "print_series.py"), encoding="utf-8").read()
a = ps.index("for k, v in {") + len("for k, v in "); b = ps.index("}.items()", a) + 1
RUBY.update(ast.literal_eval(ps[a:b]))
RUBY.update({"豪族": "ごうぞく", "連合": "れんごう", "飛鳥": "あすか", "儒教": "じゅきょう", "伽耶": "かや",
             "留学生": "りゅうがくせい", "煬帝": "ようだい", "厩戸王": "うまやどおう", "玉虫厨子": "たまむしのずし",
             "水城": "みずき", "刑罰": "けいばつ", "平城京": "へいじょうきょう", "皇子": "おうじ", "遷都": "せんと",
             "物部守屋": "もののべのもりや", "蘇我蝦夷": "そがのえみし", "大津": "おおつ", "陵": "りょう",
             "政権": "せいけん", "対等": "たいとう", "僧": "そう", "朝鮮半島": "ちょうせんはんとう"})
for k in ["冠", "讃", "珍", "済", "興", "武"]: RUBY.pop(k, None)
ONE = {"倭", "租", "調", "庸", "郡", "絹", "僧", "陵"}
KEYS = sorted(RUBY, key=len, reverse=True)
RE = re.compile("|".join(re.escape(k) for k in KEYS))

def add_ruby(page_html):
    seen = set(); out = []
    in_rt = False
    for part in re.split(r"(<[^>]+>)", page_html):
        if part.startswith("<"):
            if part.startswith("<rt") or part.startswith("<ruby"): in_rt = True
            if part.startswith("</ruby"): in_rt = False
            out.append(part); continue
        if in_rt or not part: out.append(part); continue
        res, last = [], 0
        for m in RE.finditer(part):
            w = m.group(0)
            if (len(w) == 1 and w not in ONE) or w in seen: continue
            seen.add(w)
            res.append(part[last:m.start()]); res.append(f"<ruby>{w}<rt>{RUBY[w]}</rt></ruby>"); last = m.end()
        res.append(part[last:]); out.append("".join(res))
    return "".join(out)

def box(kind, label, body):
    return f'<div class="bx {kind}"><div class="bl">{label}</div><div class="bb">{body}</div></div>'
def tbl(head, rows, cls=""):
    h = "".join(f"<th>{x}</th>" for x in head)
    r = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<table class="t {cls}"><tr>{h}</tr>{r}</table>'
def flow(items):
    return '<div class="flow">' + '<span class="ar">→</span>'.join(f'<div class="fb"><b>{t}</b><small>{s}</small></div>' for t, s in items) + "</div>"
K = lambda w: f'<b class="k">{w}</b>'

def band(t, sub=""):
    return f'<div class="band"><h1>{t}</h1><div class="sub">{sub}</div></div>'

# ───────── 1ページ目：全体の流れと年表
P1 = band("社会　解説プリント　古墳時代・飛鳥時代", "テスト範囲のまとめ") + f"""
<div class="lead">この範囲を一言でいうと、<b>豪族が集まった国（大和朝廷）だった日本が、中国や朝鮮半島のしくみを取り入れて、天皇を中心とした国（律令国家）になっていくお話</b>です。下の3つの段階で覚えましょう。</div>
{flow([("古墳時代", "3〜6世紀ごろ<br>大王と豪族の連合"), ("飛鳥時代①", "593年〜<br>聖徳太子が天皇中心の<br>しくみを始める"), ("飛鳥時代②", "645年〜701年<br>大化の改新から<br>律令国家の完成へ")])}
<h2>年表（この20こが言えれば、テストの大部分に答えられます）</h2>
""" + tbl(["年", "できごと", "覚え方・ひとこと"], [
 ["3世紀後半", "各地で" + K("古墳") + "がつくられはじめる", "王や豪族の大きな墓"],
 ["4世紀ごろ", K("大和朝廷") + "ができる（奈良県）", "王は" + K("大王")],
 ["5世紀", K("倭の五王") + "が中国（宋）に使いを送る", K("ワカタケル大王") + "の時代"],
 ["538年", K("百済") + "から" + K("仏教") + "が伝わる", "ご参拝（538）"],
 ["587年", K("蘇我馬子") + "が" + K("物部氏") + "をほろぼす", "仏教をめぐる争い"],
 ["589年", K("隋") + "が中国を統一", "約30年で終わる"],
 ["593年", K("聖徳太子") + "が" + K("推古天皇") + "の" + K("摂政") + "になる", "国民（593）のための摂政"],
 ["603年", K("冠位十二階"), "人の選び方"],
 ["604年", K("十七条の憲法"), "群れよ（604）、和をもって"],
 ["607年", K("小野妹子") + "を" + K("遣隋使") + "として送る", "このころ" + K("法隆寺")],
 ["618年", K("唐") + "が中国を統一", "約300年続く"],
 ["645年", K("大化の改新") + "が始まる", "虫殺し（645）"],
 ["646年", K("改新の詔") + "（" + K("公地公民") + "など）", "改革の方針"],
 ["663年", K("白村江の戦い") + "で唐・新羅に負ける", "→ 防人・大宰府"],
 ["668年", "中大兄皇子が即位して" + K("天智天皇") + "に", "大津宮"],
 ["672年", K("壬申の乱") + " → " + K("天武天皇"), "天智天皇の弟が勝つ"],
 ["694年", K("持統天皇") + "が" + K("藤原京") + "をつくる", "日本初の本格的な都"],
 ["701年", K("大宝律令") + "ができる", "なおい（701）律令"],
 ["（710年）", "平城京にうつる → 奈良時代へ", "次の範囲"],
], "nen") + """
<div class="foot">覚え方は語呂合わせの一例です。自分で覚えやすいものに変えてかまいません。</div>
"""

# ───────── 2ページ目：古墳時代
P2 = band("1　古墳時代", "3世紀後半〜6世紀ごろ") + f"""
<h3><span>1</span>古墳ってなに？</h3>
<p>{K("古墳")}は、王や豪族（地方の力の強い一族）の大きな墓です。土を盛り上げてつくり、形によって円墳（丸）・方墳（四角）・{K("前方後円墳")}（円と四角を組み合わせた、鍵穴のような形）があります。</p>
<p>日本最大の古墳は、大阪府堺市の{K("大仙古墳")}（仁徳天皇陵）で、長さは約486mもあります。大仙古墳をふくむ{K("百舌鳥・古市古墳群")}は、2019年に世界文化遺産になりました。</p>
""" + tbl(["", "はにわ", "副葬品"], [
 ["どこにある？", "古墳の" + K("まわりや上") + "にならべる", "古墳の" + K("中") + "に死者といっしょに納める"],
 ["どんな物？", "人・馬・家などの形の素焼きの土製品", "鏡・玉・武具（剣など）"],
], "two") + box("why", "なぜ？", "大きな古墳をつくるには、たくさんの人を長い間働かせる必要があります。大きな古墳は、<b>それだけ強い力をもった王がいた</b>しるしです。") + f"""
<h3><span>2</span>大和朝廷と大王</h3>
<p>4世紀ごろ、奈良県を中心とした地域の豪族たちが集まって、{K("大和朝廷")}（大和政権）をつくりました。その王を{K("大王")}といいます。大王は、のちに「天皇」とよばれるようになります。</p>
<p>埼玉県の{K("稲荷山古墳")}から出た鉄剣と、熊本県の{K("江田船山古墳")}から出た鉄刀には、どちらも{K("ワカタケル大王")}の名前が刻まれていました。これで、<b>5世紀には大和朝廷の力が関東から九州まで広がっていた</b>ことがわかります。</p>
<p>同じころ、{K("倭の五王")}（倭＝日本の王5人）が、中国の南朝（宋）に使いを送りました。5人目の「武」はワカタケル大王だと考えられています。</p>
""" + box("warn", "まちがえ注意", "<b>大王</b>は「王のよび名（役職）」、<b>ワカタケル大王</b>は「その中の1人の名前」です。「大和朝廷の王は何とよばれたか」の答えは「大王」です。")

P3 = band("1　古墳時代（つづき）", "") + f"""
<h3><span>3</span>渡来人がもたらしたもの</h3>
<p>中国や朝鮮半島から日本に移り住んだ人々を{K("渡来人")}といいます。渡来人は、進んだ技術や文化を伝え、大和朝廷に仕えて活やくしました。</p>
""" + tbl(["渡来人が伝えたもの", "ポイント"], [
 [K("須恵器"), "のぼりがまを使い、高温で焼いた、かたい灰色の土器"],
 [K("漢字"), "ワカタケル大王の鉄剣の文字も漢字"],
 ["機織り・土木・鉄の技術", "ため池や用水路づくりなどに役立った"],
 ["儒教・" + K("仏教"), "仏教はこのあと国の大きなテーマになる"],
], "two") + box("warn", "まちがえ注意", "<b>はにわ</b>＝古墳にならべる人や馬の形の焼き物（赤茶色）。<b>須恵器</b>＝渡来人の技術でつくる、ふだん使う器（灰色でかたい）。どちらも焼き物なので取りちがえやすい！") + f"""
<h3><span>4</span>仏教が伝わる</h3>
<p>{K("538年")}（定説）、朝鮮半島の{K("百済")}の聖明王から、仏像や経典（お経）が大和朝廷におくられました。これが仏教の伝来です。</p>
""" + tbl(["", "蘇我氏", "物部氏"], [
 ["仏教に", K("賛成"), K("反対")],
 ["理由", "渡来人と結びつき、新しい文化を取り入れたい", "昔からの日本の神をまつるべきだ"],
 ["結果", "587年、" + K("蘇我馬子") + "が勝つ", "ほろぼされる"],
], "two") + f"""
<h3><span>5</span>朝鮮半島の国々</h3>
<div class="kmap">
 <div class="km china">中国<br><small>南北朝 → 589年 隋 → 618年 唐</small></div>
 <div class="km kok">{K("高句麗")}<br><small>北部・大きな国</small></div>
 <div class="km kud">{K("百済")}<br><small>南西部<br>日本と仲がよい<br>仏教を伝えた</small></div>
 <div class="km shi">{K("新羅")}<br><small>南東部<br>のちに唐と結んで<br>半島を統一</small></div>
 <div class="km jp">日本<br><small>大和朝廷</small></div>
</div>
<div class="foot">位置のイメージ図です（実際の地形ではありません）。北が高句麗、西（左下）が百済、東（右下）が新羅。</div>
"""

# ───────── 飛鳥時代①
P4 = band("2　飛鳥時代①　聖徳太子と飛鳥文化", "593年〜") + f"""
<h3><span>1</span>聖徳太子と推古天皇</h3>
<p>593年、日本で最初の女性の天皇である{K("推古天皇")}が、おいの{K("聖徳太子")}（厩戸王）を{K("摂政")}にしました。摂政とは、天皇にかわって、または天皇を助けて政治を行う役職です。聖徳太子は、大きな力をもつ豪族の{K("蘇我馬子")}と協力して政治を進めました。</p>
""" + box("why", "なぜ？", "そのころ中国では隋が国をまとめ、強い国になっていました。聖徳太子は、<b>豪族がばらばらに力をもつ国から、天皇を中心にまとまる国</b>にしようと考えました。そのために作ったのが、下の2つのきまりです。") + f"""
<h3><span>2</span>冠位十二階と十七条の憲法</h3>
""" + tbl(["", "冠位十二階", "十七条の憲法"], [
 ["年", K("603年"), K("604年")],
 ["一言で", "<b>人の選び方</b>", "<b>役人の心がまえ</b>"],
 ["中身", "役人の位を12に分け、" + K("冠の色") + "で区別した。<b>家柄ではなく、能力や手がらのある人</b>を役人に取り立てる", "「" + K("和をもって貴しとなす") + "」（争わず、仲よくしなさい）から始まる。仏教をあつく信じること、天皇の命令に従うことなどを説いた"],
], "three") + f"""
<h3><span>3</span>遣隋使</h3>
<p>589年に中国を統一した{K("隋")}から、進んだ制度や文化を学ぶため、607年に{K("小野妹子")}を{K("遣隋使")}として送りました。国書（手紙）には「日出づる処の天子」と書き、隋と対等なつきあいをめざしました。いっしょに行った留学生や僧は、のちの大化の改新で活やくします。</p>
""" + box("warn", "まちがえ注意", "<b>隋</b>＝589年に統一、約30年と<b>短い</b>。遣「隋」使の行き先。<br><b>唐</b>＝618年に統一、約300年と<b>長い</b>。都は長安。白村江の戦いの相手。<br>「589年に統一、約30年」と聞かれたら隋。「とう」と書かないように！") + f"""
<h3><span>4</span>飛鳥文化</h3>
<p>聖徳太子のころ、奈良盆地の南部（飛鳥地方）を中心に栄えた、日本で最初の仏教文化を{K("飛鳥文化")}といいます。</p>
""" + tbl(["お寺", "ポイント"], [
 [K("法隆寺") + "（奈良県・斑鳩）", "聖徳太子が建てた。現存する世界最古の木造建築。1993年に日本で初めて世界文化遺産に登録。釈迦三尊像・玉虫厨子"],
 [K("四天王寺") + "（大阪府）", "聖徳太子が建てた寺"],
], "two")

# ───────── 飛鳥時代②
P5 = band("3　飛鳥時代②　大化の改新と律令国家", "645年〜701年") + f"""
<h3><span>1</span>大化の改新</h3>
<p>聖徳太子が亡くなったあと、蘇我氏（{K("蘇我蝦夷")}・{K("蘇我入鹿")}の親子）が天皇をしのぐほどの力をもちました。645年、{K("中大兄皇子")}と{K("中臣鎌足")}が蘇我入鹿をたおし、天皇中心の国づくりの改革を始めます。これを{K("大化の改新")}といいます。このとき「大化」という日本で初めての元号が使われました。</p>
""" + box("warn", "まちがえ注意", "「蘇我入鹿をたおした<b>2人</b>は？」と聞かれたら、<b>中大兄皇子・中臣鎌足</b>の2人とも書きます。中大兄皇子は、のちの<b>天智天皇</b>。中臣鎌足は、のちに「藤原」の姓をもらい、<b>藤原氏の祖先</b>になります。") + f"""
<h3><span>2</span>改新の詔と、土地のしくみ</h3>
<p>646年、改革の方針（{K("改新の詔")}）が出されました。土地と人々のしくみは、次の順番で覚えます。</p>
""" + flow([("公地公民", "考え方<br>土地も人も<br>国のもの"), ("戸籍", "人々の名前・<br>年れいを記録<br>（6年ごと）"), ("班田収授の法", "やり方<br>土地を貸しあたえ<br>死んだら返す"), ("口分田", "もらう田<br>6歳以上の<br>男女に"), ("租", "税<br>口分田の稲の<br>約3％を納める")]) + box("warn", "まちがえ注意", "公地公民＝<b>考え方</b>、班田収授の法＝<b>やり方（制度）</b>、口分田＝<b>田んぼそのもの</b>。「何というか」で聞かれているのが、考え方・制度・田のどれかを見分けよう。") + f"""
<h3><span>3</span>人々の負担（税と兵役）</h3>
""" + tbl(["名前", "納める物", "覚え方"], [
 [K("租"), "口分田でとれた<b>稲</b>の約3％", "租＝稲"],
 [K("調"), "地方の<b>特産物</b>（絹・魚・塩など）を都へ", "調＝特産物"],
 [K("庸"), "都で10日働く（労役）かわりに<b>布</b>を納める", "庸＝布"],
 [K("防人"), "九州北部の守りにつく兵士（おもに東国の人）", "兵役のひとつ"],
], "three")

P6 = band("3　飛鳥時代②（つづき）", "") + f"""
<h3><span>4</span>白村江の戦いと、九州の守り</h3>
<p>663年、日本は仲のよかった百済を助けるため、朝鮮半島に大軍を送りました。しかし、{K("唐")}と{K("新羅")}の連合軍に大敗します（{K("白村江の戦い")}）。</p>
""" + box("why", "なぜ？", "負けた日本は「唐や新羅がせめてくるかもしれない」とおそれました。そこで、九州北部に<b>" + K("防人") + "</b>という兵士を置き、外交と防衛の役所である<b>" + K("大宰府") + "</b>（「遠の朝廷」とよばれる）の守りを固めました。") + f"""
<h3><span>5</span>天智天皇・壬申の乱・天武天皇</h3>
<p>668年、中大兄皇子は近江（滋賀県）の大津宮で即位し、{K("天智天皇")}になりました。天智天皇は、初めて全国の戸籍をつくりました。</p>
<p>天智天皇が亡くなると、672年、天皇の位をめぐって、天智天皇の弟の大海人皇子と、天智天皇の子の大友皇子が争いました（{K("壬申の乱")}）。勝った大海人皇子が即位して{K("天武天皇")}となり、天皇の力はさらに強くなりました。</p>
<div class="kei">
 <div class="row"><div class="p">天智天皇<small>＝中大兄皇子</small></div><div class="l">兄 ── 弟</div><div class="p">天武天皇<small>＝大海人皇子</small></div><div class="l">夫 ── 妻</div><div class="p">持統天皇<small>天武天皇のきさき<br>（天智天皇のむすめ）</small></div></div>
 <div class="row2"><div class="p s">大友皇子<small>天智天皇の子</small></div><div class="l2">← 672年 壬申の乱で戦う →</div><div class="p s">大海人皇子<small>（勝って天武天皇に）</small></div></div>
</div>
<h3><span>6</span>藤原京と大宝律令 ― 律令国家の完成</h3>
<p>天武天皇のあとをついだ{K("持統天皇")}は、694年、中国の都にならって、日本で初めての本格的な都である{K("藤原京")}をつくりました。</p>
<p>701年には、唐の律令にならって{K("大宝律令")}が完成しました。<b>律</b>は刑罰のきまり、<b>令</b>は政治のきまりです。律令にもとづいて政治を行う国を{K("律令国家")}といいます。</p>
""" + tbl(["地方のしくみ", "どんな人？"], [
 ["国 → " + K("国司"), "都から送られた役人（貴族）"],
 ["郡 → " + K("郡司"), "その地方の豪族から選ばれた役人"],
 ["九州 → " + K("大宰府"), "外交と防衛を担当する役所"],
], "two") + "<p>このあと710年に都は平城京にうつり、奈良時代が始まります。</p>"

# ───────── まとめ
P7 = band("まとめ　テストでまちがえやすいところ", "最後にここだけ確認") + """
<h3><span>1</span>取りちがえやすい言葉</h3>
""" + tbl(["こっちは…", "こっちは…", "見分け方"], [
 [K("隋") + "（589年）", K("唐") + "（618年）", "隋は約30年、唐は約300年。遣隋使は隋へ"],
 [K("はにわ"), K("須恵器"), "はにわ＝古墳にならべる。須恵器＝渡来人が伝えたかたい土器"],
 [K("公地公民"), K("班田収授の法") + "・" + K("口分田"), "考え方 → やり方 → 田んぼ"],
 [K("租"), K("調") + "・" + K("庸"), "稲 ／ 特産物 ／ 布"],
 [K("大王"), K("ワカタケル大王"), "よび名 ／ 1人の名前"],
 [K("冠位十二階") + "（603年）", K("十七条の憲法") + "（604年）", "人の選び方 ／ 役人の心がまえ"],
 [K("蘇我氏") + "（賛成）", K("物部氏") + "（反対）", "仏教の受け入れ。蘇我氏が勝つ"],
 [K("天智天皇") + "（兄）", K("天武天皇") + "（弟）", "壬申の乱に勝ったのは弟の天武"],
 [K("国司"), K("郡司"), "都から来る ／ 地元の豪族"],
], "three") + """
<h3><span>2</span>漢字に注意（書けるようにしておく）</h3>
<div class="kj">@@KJ@@</div>
<h3><span>3</span>答え方のルール</h3>
<ul class="rule">
<li>「<b>2人</b>は？」と聞かれたら2人とも書く（例：中大兄皇子・中臣鎌足）。</li>
<li>「<b>何年</b>か」は数字を正確に。538年（仏教）を528年と書くような、1けたのまちがいに注意。</li>
<li>人名・用語は<b>漢字</b>で書く。ひらがなで書くと×になることがある（はにわ・ワカタケル大王はそのままでよい）。</li>
<li>聞き方が変わっても答えられるように、<b>言葉の意味</b>で覚える。「604年に定めたもの」も「和をもって貴しとなす」も、答えは十七条の憲法。</li>
</ul>
"""

CSS = """
@page { size: A4; margin: 10mm 12mm 9mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", sans-serif; color: #111; font-size: 10.4pt; line-height: 1.85; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.band { background: #12306a; color: #fff; display: flex; align-items: baseline; justify-content: space-between; padding: 3mm 5mm; margin-bottom: 2mm; }
.band h1 { margin: 0; font-size: 15.5pt; font-weight: 800; letter-spacing: .03em; line-height: 1.4; }
.band .sub { font-size: 9.5pt; font-weight: 700; }
h2 { font-size: 11.5pt; margin: 3mm 0 1mm; font-weight: 800; border-bottom: 1.4pt solid #111; }
h3 { font-size: 12pt; margin: 3.4mm 0 .6mm; font-weight: 800; border-bottom: 1pt solid #12306a; line-height: 1.6; }
h3 span { display: inline-block; background: #12306a; color: #fff; width: 6mm; text-align: center; margin-right: 2mm; }
p { margin: .8mm 0; text-indent: 1em; }
.lead { font-size: 10.6pt; margin: 1mm 0 2mm; }
b.k { color: #12306a; font-weight: 800; }
rt { font-size: 5.4pt; color: #333; font-weight: 400; }
table.t { width: 100%; border-collapse: collapse; margin: 1.4mm 0; break-inside: avoid; }
table.t th { background: #12306a; color: #fff; font-size: 9.4pt; padding: .6mm 2mm; text-align: left; border: .6pt solid #12306a; }
table.t td { border: .6pt solid #9aa3b5; padding: .5mm 2mm; vertical-align: top; line-height: 1.7; font-size: 9.8pt; }
table.nen td:first-child { width: 22mm; font-weight: 800; white-space: nowrap; }
table.nen td:last-child { width: 50mm; font-size: 9pt; color: #333; }
table.nen td { padding: .1mm 2mm; line-height: 1.65; }
table.two td:first-child { width: 42mm; font-weight: 700; }
table.three td:first-child { width: 26mm; font-weight: 700; }
.bx { border: 1.2pt solid #12306a; margin: 2mm 0; break-inside: avoid; display: flex; }
.bx .bl { background: #12306a; color: #fff; font-weight: 800; font-size: 9.5pt; padding: 1mm 2mm; writing-mode: horizontal-tb; min-width: 24mm; display: flex; align-items: center; justify-content: center; }
.bx .bb { padding: 1mm 3mm; font-size: 9.9pt; line-height: 1.8; }
.bx.warn { border-color: #b3261e; }
.bx.warn .bl { background: #b3261e; }
.flow { display: flex; align-items: stretch; gap: 1mm; margin: 2mm 0; break-inside: avoid; }
.flow .fb { flex: 1; border: 1.2pt solid #12306a; text-align: center; padding: 1.2mm 1mm; line-height: 1.5; }
.flow .fb b { display: block; color: #12306a; font-size: 11pt; }
.flow .fb small { font-size: 8.6pt; }
.flow .ar { align-self: center; font-weight: 900; color: #12306a; font-size: 13pt; }
.foot { font-size: 8.4pt; color: #444; margin-top: 1mm; }
.kmap { position: relative; height: 66mm; margin: 2mm 0 0; border: .6pt solid #9aa3b5; background: #f4f6fa; }
.km { position: absolute; border: 1.2pt solid #12306a; background: #fff; text-align: center; padding: 1mm 2mm; line-height: 1.45; font-weight: 800; }
.km small { font-weight: 500; font-size: 8.4pt; }
.km.china { left: 4mm; top: 4mm; width: 52mm; height: 34mm; padding-top: 8mm; }
.km.kok { left: 64mm; top: 4mm; width: 46mm; height: 18mm; }
.km.kud { left: 64mm; top: 25mm; width: 26mm; height: 37mm; }
.km.shi { left: 92mm; top: 25mm; width: 30mm; height: 37mm; }
.km.jp { left: 132mm; top: 30mm; width: 48mm; height: 24mm; padding-top: 4mm; }
.kei { border: .6pt solid #9aa3b5; padding: 2mm; margin: 2mm 0; break-inside: avoid; }
.kei .row, .kei .row2 { display: flex; align-items: center; gap: 1.5mm; }
.kei .row2 { margin-top: 2mm; justify-content: center; }
.kei .p { border: 1.2pt solid #12306a; text-align: center; font-weight: 800; padding: .8mm 2mm; line-height: 1.4; min-width: 38mm; }
.kei .p small { display: block; font-weight: 500; font-size: 8.2pt; }
.kei .p.s { border-color: #777; }
.kei .l { font-size: 8.8pt; font-weight: 700; color: #12306a; white-space: nowrap; }
.kei .l2 { font-size: 9pt; font-weight: 700; color: #b3261e; }
.kj { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2mm; margin: 1.4mm 0; }
.kc { border: .6pt solid #9aa3b5; text-align: center; padding: .6mm 0; line-height: 1.35; }
.kc b { font-size: 11.5pt; }
.kc small { display: block; font-size: 7.4pt; color: #333; }
.rule { margin: 1mm 0; padding-left: 6mm; }
.rule li { margin: .6mm 0; }
"""

KJ = "".join(f'<div class="kc"><b>{w}</b><small>{y}</small></div>' for w, y in [
 ("推古天皇", "すいこてんのう"), ("高句麗", "こうくり"), ("百済", "くだら"), ("新羅", "しらぎ"),
 ("須恵器", "すえき"), ("百舌鳥", "もず"), ("摂政", "せっしょう"), ("冠位十二階", "かんいじゅうにかい"),
 ("十七条の憲法", "じゅうしちじょうのけんぽう"), ("遣隋使", "けんずいし"), ("大化の改新", "たいかのかいしん"),
 ("中臣鎌足", "なかとみのかまたり"), ("中大兄皇子", "なかのおおえのおうじ"), ("班田収授", "はんでんしゅうじゅ"),
 ("口分田", "くぶんでん"), ("白村江", "はくすきのえ"), ("壬申の乱", "じんしんのらん"), ("大宰府", "だざいふ"),
 ("防人", "さきもり"), ("大宝律令", "たいほうりつりょう")])
pages = [P1, P2, P3, P4, P5, P6, P7]
body = "".join(f'<div class="page">{add_ruby(p).replace("@@KJ@@", KJ)}</div>' for p in pages)
doc = f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'
os.makedirs(OUT, exist_ok=True)
with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
    f.write(doc); tmp = f.name
pdf = os.path.join(OUT, "解説プリント_古墳・飛鳥.pdf")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + tmp],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if "--keep-html" in sys.argv: print(tmp)
else: os.unlink(tmp)
print(pdf)
