# -*- coding: utf-8 -*-
# 古墳・飛鳥テスト（A・B）でまちがえた問題の直しプリント
#   1枚目 覚える表（まちがえやすい組）／2枚目 漢字練習／3枚目 直しテスト20問／4枚目 解答
# 使い方: python3 _build/print_naoshi.py <出力フォルダ>
import io, os, re, subprocess, sys, tempfile, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TITLE = "古墳時代・飛鳥時代"
E = html.escape

src = io.open(os.path.join(ROOT, "jp9pyw1wu4", "index.html"), encoding="utf-8").read()
i = src.index("const RUBY={") + len("const RUBY={"); j = src.index("};", i)
RUBY = {k: v for k, v in re.findall(r'"([^"]+)":"([^"]+)"', src[i:j]) if k != v and len(k) >= 2}
RUBY.update({"須恵器": "すえき", "百舌鳥": "もず", "古市": "ふるいち", "高句麗": "こうくり", "推古天皇": "すいこてんのう",
             "中臣鎌足": "なかとみのかまたり", "中大兄皇子": "なかのおおえのおうじ", "天智天皇": "てんじてんのう",
             "口分田": "くぶんでん", "班田収授": "はんでんしゅうじゅ", "公地公民": "こうちこうみん", "蘇我入鹿": "そがのいるか",
             "大化の改新": "たいかのかいしん", "冠位十二階": "かんいじゅうにかい", "十七条の憲法": "じゅうしちじょうのけんぽう",
             "大王": "おおきみ", "長安": "ちょうあん", "素焼き": "すやき", "労役": "ろうえき", "改新の詔": "かいしんのみことのり", "特産物": "とくさんぶつ"})
KEYS = sorted(RUBY, key=len, reverse=True)
RE = re.compile("|".join(re.escape(k) for k in KEYS))

def ruby(q, ans=""):
    out, last = [], 0
    for m in RE.finditer(q):
        w = m.group(0)
        out.append(E(q[last:m.start()]))
        out.append(E(w) if ans and w in ans else f"<ruby>{E(w)}<rt>{RUBY[w]}</rt></ruby>")
        last = m.end()
    out.append(E(q[last:]))
    return "".join(out)

# ── 1枚目：まちがえやすい組（見出し, 覚え方, [(言葉, 説明)]）
PAIRS = [
 ("中国の王朝　隋と唐", "隋は短い（約30年）→ 唐は長い（約300年）。遣「隋」使の字で隋を思い出す", [
   ("隋", "589年に中国を統一。約30年で終わる。607年に小野妹子が遣隋使として行った国"),
   ("唐", "618年に隋にかわって統一。約300年続く。都は長安。663年の白村江の戦いの相手（唐・新羅）")]),
 ("土地のしくみ　3つの順番", "考え方 → やり方 → もらう田んぼ　の順に大きい話から小さい話へ", [
   ("公地公民", "考え方：土地も人も、すべて国のもの（大化の改新の方針）"),
   ("班田収授の法", "やり方：戸籍にもとづいて土地を貸しあたえ、死んだら国に返させる"),
   ("口分田", "もらう田んぼそのもの：6歳以上の男女にあたえられた田")]),
 ("税　租・調・庸", "租＝稲（いね）、調＝特産物、庸＝布。納める物で区別する", [
   ("租", "口分田でとれた稲の約3％を納める"),
   ("調", "地方の特産物（絹・魚・塩など）を都に納める"),
   ("庸", "都で働く（労役）かわりに布を納める")]),
 ("古墳時代の焼き物　はにわと須恵器", "はにわ＝古墳にならべる人や馬の形。須恵器＝渡来人の技術でつくる器", [
   ("はにわ", "古墳のまわりや上にならべた素焼きの土製品。赤茶色"),
   ("須恵器", "渡来人が伝えた、高温で焼いたかたい灰色の土器")]),
 ("大王とワカタケル大王", "大王は「役職」、ワカタケル大王は「その中の1人の名前」", [
   ("大王", "大和朝廷の王のよび名（のちに「天皇」とよばれるようになる）"),
   ("ワカタケル大王", "5世紀の大王の1人。名前が稲荷山古墳（埼玉県）の鉄剣にある")]),
 ("聖徳太子の2つのきまり", "603年は「人の選び方」、604年は「役人の心がまえ」", [
   ("冠位十二階", "603年。家柄ではなく能力のある人を役人にする。位は冠の色で表す"),
   ("十七条の憲法", "604年。「和をもって貴しとなす」から始まる、役人の心がまえ")]),
 ("645年の人物", "たおした2人は「中大兄皇子と中臣鎌足」でセット。1人だけ書かない", [
   ("中大兄皇子", "大化の改新の中心。のちに即位して天智天皇になる"),
   ("中臣鎌足", "中大兄皇子といっしょに蘇我入鹿をたおす。のちの藤原氏の祖先")]),
]

# ── 2枚目：漢字練習（言葉, よみ）
KANJI = [("推古天皇", "すいこてんのう"), ("高句麗", "こうくり"), ("百舌鳥", "もず"), ("須恵器", "すえき"),
         ("大化の改新", "たいかのかいしん"), ("中臣鎌足", "なかとみのかまたり"), ("天智天皇", "てんじてんのう"),
         ("十七条の憲法", "じゅうしちじょうのけんぽう"), ("公地公民", "こうちこうみん"), ("口分田", "くぶんでん"),
         ("隋", "ずい"), ("租", "そ")]

# ── 3枚目：直しテスト（大問見出し, [(問, 答)]）
TEST = [
 ("前回まちがえた問題（聞き方を変えています）", [
  ("百済の王から、仏像や経典が日本におくられた年は（定説）。", "538年"),
  ("朝鮮半島の北部にあり、4〜5世紀に南へ勢力を広げた国は。", "高句麗"),
  ("大阪府にある、大仙古墳をふくむ古墳群は。", "百舌鳥・古市古墳群"),
  ("大和朝廷の中心となった王のよび名を、漢字2字で書きなさい。", "大王"),
  ("渡来人の技術で、高温で焼いてつくられた、かたい灰色の土器は。", "須恵器"),
  ("日本で最初の女性の天皇で、聖徳太子を摂政にした天皇は。", "推古天皇"),
  ("冠位十二階で、役人を選ぶときに家柄のかわりに重く見たものは何か。", "能力（才能）"),
  ("聖徳太子が定めた、仏教を大切にすることや、天皇の命令に従うことなどを説いた役人の心がまえは。", "十七条の憲法"),
  ("聖徳太子が小野妹子を使者として送った、中国の王朝は。", "隋"),
  ("645年に蘇我氏をたおして始まった、天皇中心の国づくりの改革を何というか。", "大化の改新"),
  ("蘇我入鹿をたおした2人のうち、のちに藤原氏の祖先となった人物は。", "中臣鎌足"),
  ("645年の改革を進めた中大兄皇子は、即位して何天皇になったか。", "天智天皇"),
  ("646年の改新の詔で示された、「土地も人も国のもの」という考え方を何というか。", "公地公民"),
  ("戸籍にもとづいて、6歳以上の男女に貸しあたえられた田を何というか。", "口分田"),
  ("人々にあたえられた田でとれた稲の約3％を納める税を何というか。", "租"),
 ]),
 ("まちがえやすい言葉", [
  ("618年に中国を統一し、約300年続いた王朝は。", "唐"),
  ("古墳のまわりや上にならべられた、人や馬の形をした素焼きの土製品は。", "はにわ"),
  ("人々に土地を貸しあたえ、死んだら国に返させる制度は。", "班田収授の法"),
  ("地方の特産物を都に納める税を何というか。", "調"),
  ("都で働くかわりに布を納める税を何というか。", "庸"),
 ]),
]

CSS = """
@page { size: A4; margin: 9mm 11mm 8mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", sans-serif; color: #111; font-size: 10.6pt; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.band { background: #12306a; color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 3.2mm 5mm; }
.band h1 { margin: 0; font-size: 16pt; font-weight: 800; letter-spacing: .04em; }
.band .pt { font-size: 10pt; font-weight: 700; }
.band .pat { background: #fff; color: #12306a; font-weight: 900; font-size: 13pt; padding: .6mm 3mm; margin-left: 4mm; }
.meta { display: flex; gap: 4mm; margin: 2mm 0 .6mm; align-items: stretch; }
.meta .note { flex: 1; font-size: 9.2pt; line-height: 1.5; padding-top: .6mm; }
.lead { font-size: 9.4pt; line-height: 1.55; margin: 2mm 0 1mm; }
.box { border: 1.4pt solid #111; display: flex; align-items: center; }
.box span { background: #111; color: #fff; font-weight: 700; font-size: 9pt; padding: 0 2.4mm; align-self: stretch; display: flex; align-items: center; }
.name { width: 64mm; height: 10mm; }
.score { width: 34mm; height: 10mm; }
.score b { margin-left: auto; padding-right: 2mm; font-size: 9pt; }
h2 { font-size: 11pt; margin: 1.6mm 0 .2mm; padding: .5mm 0; border-bottom: 1.6pt solid #111; font-weight: 800; }
h2 .n { display: inline-block; background: #111; color: #fff; padding: 0 2mm; margin-right: 2mm; }
table { width: 100%; border-collapse: collapse; }
td { border-bottom: .6pt solid #9aa3b5; padding: 0; vertical-align: middle; }
td.no { width: 9.5mm; font-weight: 900; font-size: 12pt; text-align: center; white-space: nowrap; }
td.q { padding: .5mm 2mm .4mm 0; line-height: 1.6; }
td.a { width: 56mm; height: 9.6mm; }
td.a div { border: 1pt solid #111; height: 8.2mm; margin: .7mm 0; }
rt { font-size: 5.6pt; color: #333; }
.ans td.k { width: 62mm; font-weight: 800; font-size: 11pt; padding: .8mm 0; }
.foot { margin-top: 2mm; font-size: 8.4pt; color: #444; }
/* 覚える表 */
.pair { margin-top: 2.6mm; break-inside: avoid; }
.pair h3 { margin: 0; font-size: 11pt; font-weight: 800; border-left: 2.4mm solid #12306a; padding: .2mm 0 .2mm 2mm; }
.pair .tip { font-size: 8.8pt; color: #b3261e; font-weight: 700; margin: .6mm 0 .6mm 4.4mm; }
.pair table td { border: .6pt solid #9aa3b5; padding: .9mm 2mm; line-height: 1.5; font-size: 9.8pt; }
.pair td.w { width: 36mm; font-weight: 900; font-size: 12pt; background: #eef1f7; text-align: center; }
/* 漢字練習 */
.kj td { border: .8pt solid #555; height: 15.5mm; }
.kj td.m { width: 36mm; text-align: center; font-weight: 800; font-size: 13pt; background: #eef1f7; line-height: 1.2; }
.kj td.m small { display: block; font-size: 7pt; font-weight: 500; color: #333; }
.kj td.n { width: 8mm; text-align: center; font-weight: 900; }
"""

def head(title, right):
    return f'<div class="band"><h1>{E(title)}</h1><div class="pt">{right}</div></div>'

def page_pairs():
    body = []
    for h, tip, rows in PAIRS:
        trs = "".join(f'<tr><td class="w">{E(w)}</td><td>{ruby(d)}</td></tr>' for w, d in rows)
        body.append(f'<div class="pair"><h3>{E(h)}</h3><div class="tip">覚え方：{E(tip)}</div><table>{trs}</table></div>')
    return f"""<div class="page">{head("直しプリント①　まちがえやすい組を覚える", '<span class="pat">直し</span>')}
<div class="lead">テストでまちがえた言葉は、似た言葉と取りちがえていたものが多くありました。左の言葉を手でかくして、説明を見て言葉が言えるか試してから、②の漢字練習に進みましょう。</div>
{''.join(body)}</div>"""

def page_kanji():
    trs = "".join(f'<tr><td class="n">{i + 1}</td><td class="m">{E(w)}<small>{E(y)}</small></td>' + "<td></td>" * 4 + "</tr>"
                  for i, (w, y) in enumerate(KANJI))
    return f"""<div class="page">{head("直しプリント②　漢字練習", '<span class="pat">直し</span>')}
<div class="lead">テストで書けなかった・取りちがえた言葉です。左の見本を見ないで書けるまで、1つにつき4回書きます。書き終わったら見本を折って、もう1回書いてみましょう。</div>
<table class="kj">{trs}</table></div>"""

def page_test():
    n, rows = 0, []
    for si, (h, items) in enumerate(TEST):
        rows.append(f'<h2><span class="n">{si + 1}</span>{E(h)}</h2><table>')
        for q, a in items:
            n += 1
            rows.append(f'<tr><td class="no">{n}</td><td class="q">{ruby(q, a)}</td><td class="a"><div></div></td></tr>')
        rows.append("</table>")
    return f"""<div class="page">{head("社会　直しテスト　" + TITLE, '20問×5点<span class="pat">直し</span>')}
<div class="meta"><div class="note">①②で覚えてから、<b>3日後</b>にやりましょう。人名・用語は<b>漢字</b>で書くこと（はにわはそのままでよい）。</div>
<div class="box name"><span>名前</span></div><div class="box score"><span>点数</span><b>／100</b></div></div>
{''.join(rows)}</div>"""

def page_ans():
    n, rows = 0, []
    for si, (h, items) in enumerate(TEST):
        rows.append(f'<h2><span class="n">{si + 1}</span>{E(h)}</h2><table class="ans">')
        for q, a in items:
            n += 1
            rows.append(f'<tr><td class="no">{n}</td><td class="q">{E(q)}</td><td class="k">{E(a)}</td></tr>')
        rows.append("</table>")
    return f"""<div class="page">{head("解答　直しテスト　" + TITLE, '各5点<span class="pat">直し</span>')}
{''.join(rows)}
<div class="foot">（ ）の中は、書いてあってもなくても正解。7は「家柄ではなく能力」の意味が書けていれば正解。11は中臣鎌足のみ（2人書いたら△）。</div></div>"""

os.makedirs(OUT, exist_ok=True)
doc = f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{page_pairs()}{page_kanji()}{page_test()}{page_ans()}</body></html>'
with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
    f.write(doc); tmp = f.name
pdf = os.path.join(OUT, "歴史テスト_古墳・飛鳥_直し.pdf")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + tmp],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.unlink(tmp)
print(pdf)
