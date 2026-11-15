# -*- coding: utf-8 -*-
# ドリルの問題から A4 の20問テスト（問題1枚＋解答1枚）を作る。3パターンは同じ単元を同じ順で、別の問題で聞く
# 使い方: python3 _build/print_test.py <出力フォルダ>
#   → 歴史テスト_古墳・飛鳥_A.pdf / _B / _C（Chrome のヘッドレスで印刷）
import io, os, re, subprocess, sys, tempfile, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TITLE = "古墳時代・飛鳥時代"

# (大問の見出し, [(A問, A答), (B問, B答), (C問, C答)] × 小問)
SECTIONS = [
 ("古墳時代", [
  [("円と四角を組み合わせた形の古墳を何というか。", "前方後円墳"),
   ("日本最大の古墳は何か。", "大仙古墳（仁徳天皇陵）"),
   ("古墳のまわりや上にならべられた、素焼きの土製品を何というか。", "はにわ")],
  [("日本最大の古墳である大仙古墳がある都道府県は。", "大阪府"),
   ("2019年に世界文化遺産に登録された、大阪府の古墳群は。", "百舌鳥・古市古墳群"),
   ("古墳の中に、死者とともに納められた鏡・玉・武具などの品物を何というか。", "副葬品")],
  [("4世紀ごろ、奈良県を中心に有力な豪族が連合してつくった政権は。", "大和朝廷（大和政権）"),
   ("大和朝廷の王は、何とよばれたか。", "大王"),
   ("埼玉県の稲荷山古墳から出土した鉄剣に刻まれていた大王の名は。", "ワカタケル大王")],
  [("5世紀に中国の南朝（宋）に使いを送った、5人の倭の王をまとめて何というか。", "倭の五王"),
   ("ワカタケル大王の名が刻まれた鉄剣が出土した稲荷山古墳は、何県にあるか。", "埼玉県"),
   ("ワカタケル大王の名が刻まれた鉄刀が出土した江田船山古墳は、何県にあるか。", "熊本県")],
  [("中国や朝鮮半島から日本に移り住み、進んだ技術や文化を伝えた人々を何というか。", "渡来人"),
   ("渡来人が伝えた、かたくて黒っぽい土器を何というか。", "須恵器"),
   ("渡来人が伝えた文字は何か。", "漢字")],
  [("仏教が日本に伝わったのは何年か（定説）。", "538年"),
   ("仏教の受け入れに反対した豪族は。", "物部氏"),
   ("仏教の受け入れに賛成した豪族は。", "蘇我氏")],
  [("4世紀ごろ、朝鮮半島の北部にあった国は。", "高句麗"),
   ("日本に仏教を伝えた、朝鮮半島南西部の国は。", "百済"),
   ("4世紀ごろ、朝鮮半島の南東部にあった国は。", "新羅")],
 ]),
 ("飛鳥時代①　聖徳太子と飛鳥文化", [
  [("聖徳太子が摂政となった天皇は。", "推古天皇"),
   ("聖徳太子が協力して政治を行った豪族は。", "蘇我馬子"),
   ("593年に推古天皇の摂政となった人物は。", "聖徳太子")],
  [("603年に、家柄にとらわれず能力のある人を役人にするために定めた制度は。", "冠位十二階"),
   ("604年に、役人の心がまえを示すために定めたものは。", "十七条の憲法"),
   ("冠位十二階では、位の高さを何で表したか。", "冠の色")],
  [("「和をもって貴しとなす」から始まる、役人の心がまえを示したものは。", "十七条の憲法"),
   ("冠位十二階のねらいは何か。かんたんに書きなさい。", "家柄ではなく能力で役人を選ぶこと"),
   ("十七条の憲法が定められたのは何年か。", "604年")],
  [("隋の進んだ制度や文化を取り入れるために送られた使者を何というか。", "遣隋使"),
   ("607年に遣隋使として隋にわたった人物は。", "小野妹子"),
   ("小野妹子が遣隋使として隋にわたったのは何年か。", "607年")],
  [("聖徳太子が奈良県に建てた、現存する世界最古の木造建築の寺は。", "法隆寺"),
   ("聖徳太子のころに栄えた、日本で最初の仏教文化を何というか。", "飛鳥文化"),
   ("聖徳太子が大阪に建てた寺は。", "四天王寺")],
  [("589年に中国を統一し、約30年続いた王朝は。", "隋"),
   ("618年に隋にかわって中国を統一し、約300年続いた王朝は。", "唐"),
   ("唐の都はどこか。", "長安")],
 ]),
 ("飛鳥時代②　大化の改新と律令国家", [
  [("645年から始まった、天皇中心の国づくりをめざす政治改革を何というか。", "大化の改新"),
   ("645年に蘇我入鹿をたおした2人の人物は。", "中大兄皇子・中臣鎌足"),
   ("645年に中大兄皇子と中臣鎌足にたおされた人物は。", "蘇我入鹿")],
  [("すべての土地と人民を国のものとする原則を何というか。", "公地公民"),
   ("戸籍にもとづいて人々に土地を貸しあたえ、死ねば国に返させる制度は。", "班田収授の法"),
   ("646年に出された、大化の改新の方針を示したものは。", "改新の詔")],
  [("663年に、日本が唐・新羅の連合軍に敗れた戦いは。", "白村江の戦い"),
   ("白村江の戦いのあと、九州北部の守りのために置かれた兵士を何というか。", "防人"),
   ("九州に置かれた、外交や防衛を担当する役所は。", "大宰府")],
  [("672年に、天智天皇の死後に起こった皇位をめぐる争いは。", "壬申の乱"),
   ("中大兄皇子は、即位して何天皇となったか。", "天智天皇"),
   ("壬申の乱に勝って即位した、大海人皇子は何天皇か。", "天武天皇")],
  [("701年に定められた、律令国家の基本となる法律は。", "大宝律令"),
   ("持統天皇がつくった、日本で初めての本格的な都は。", "藤原京"),
   ("日本で初めての本格的な都、藤原京をつくった天皇は。", "持統天皇")],
  [("6歳以上の男女にあたえられた土地を何というか。", "口分田"),
   ("国を治めるために、都から派遣された役人を何というか。", "国司"),
   ("郡を治めた、その地方の豪族から選ばれた役人を何というか。", "郡司")],
  [("収穫した稲の約3％を納める税を何というか。", "租"),
   ("地方の特産物を都に納める税を何というか。", "調"),
   ("都での労役のかわりに布を納める税を何というか。", "庸")],
 ]),
]

# ふりがな（ドリルの辞書）。答えにふくまれる語には付けない
src = io.open(os.path.join(ROOT, "jp9pyw1wu4", "index.html"), encoding="utf-8").read()
i = src.index("const RUBY={") + len("const RUBY={"); j = src.index("};", i)
RUBY = {k: v for k, v in re.findall(r'"([^"]+)":"([^"]+)"', src[i:j]) if k != v and len(k) >= 2}
KEYS = sorted(RUBY, key=len, reverse=True)
RE = re.compile("|".join(re.escape(k) for k in KEYS))

def ruby(q, ans):
    out, last = [], 0
    for m in RE.finditer(q):
        w = m.group(0)
        out.append(html.escape(q[last:m.start()]))
        out.append(html.escape(w) if w in ans else f"<ruby>{html.escape(w)}<rt>{RUBY[w]}</rt></ruby>")
        last = m.end()
    out.append(html.escape(q[last:]))
    return "".join(out)

CSS = """
@page { size: A4; margin: 9mm 11mm 8mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", sans-serif; color: #111; font-size: 10.6pt; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.band { background: #12306a; color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 3.2mm 5mm; }
.band h1 { margin: 0; font-size: 16pt; font-weight: 800; letter-spacing: .04em; }
.band .pt { font-size: 10pt; font-weight: 700; }
.band .pat { background: #fff; color: #12306a; font-weight: 900; font-size: 15pt; padding: .6mm 4mm; margin-left: 4mm; }
.meta { display: flex; gap: 4mm; margin: 2mm 0 .6mm; align-items: stretch; }
.meta .note { flex: 1; font-size: 9.2pt; line-height: 1.5; padding-top: .6mm; }
.box { border: 1.4pt solid #111; display: flex; align-items: center; }
.box span { background: #111; color: #fff; font-weight: 700; font-size: 9pt; padding: 0 2.4mm; align-self: stretch; display: flex; align-items: center; }
.name { width: 64mm; height: 10mm; }
.score { width: 34mm; height: 10mm; }
.score b { margin-left: auto; padding-right: 2mm; font-size: 9pt; }
h2 { font-size: 11pt; margin: 1.6mm 0 .2mm; padding: .5mm 0 .5mm 0; border-bottom: 1.6pt solid #111; font-weight: 800; }
h2 .n { display: inline-block; background: #111; color: #fff; padding: 0 2mm; margin-right: 2mm; }
table { width: 100%; border-collapse: collapse; }
td { border-bottom: .6pt solid #9aa3b5; padding: 0; vertical-align: middle; }
td.no { width: 9.5mm; font-weight: 900; font-size: 12pt; text-align: center; white-space: nowrap; }
td.q { padding: .5mm 2mm .4mm 0; line-height: 1.6; }
td.a { width: 56mm; height: 9.6mm; }
td.a div { border: 1pt solid #111; height: 8.2mm; margin: .7mm 0; }
rt { font-size: 5.6pt; color: #333; }
.ans td.q { width: auto; }
.ans td.k { width: 66mm; font-weight: 800; font-size: 11pt; padding: .8mm 0; }
.foot { margin-top: 2mm; font-size: 8.4pt; color: #444; }
"""

def page_q(pat, k):
    n, rows = 0, []
    for si, (head, slots) in enumerate(SECTIONS):
        rows.append(f'<h2><span class="n">{si + 1}</span>{html.escape(head)}</h2><table>')
        for sl in slots:
            n += 1; q, a = sl[k]
            rows.append(f'<tr><td class="no">{n}</td><td class="q">{ruby(q, a)}</td><td class="a"><div></div></td></tr>')
        rows.append("</table>")
    return f"""<div class="page">
<div class="band"><h1>社会　確認テスト　{TITLE}</h1><div class="pt">20問×5点<span class="pat">{pat}</span></div></div>
<div class="meta"><div class="note">答えは右のわくに書きなさい。人名・用語は<b>漢字</b>で書くこと（はにわ・ワカタケル大王はそのままでよい）。</div>
<div class="box name"><span>名前</span></div><div class="box score"><span>点数</span><b>／100</b></div></div>
{''.join(rows)}</div>"""

def page_a(pat, k):
    n, rows = 0, []
    for si, (head, slots) in enumerate(SECTIONS):
        rows.append(f'<h2><span class="n">{si + 1}</span>{html.escape(head)}</h2><table class="ans">')
        for sl in slots:
            n += 1; q, a = sl[k]
            rows.append(f'<tr><td class="no">{n}</td><td class="q">{html.escape(q)}</td><td class="k">{html.escape(a)}</td></tr>')
        rows.append("</table>")
    return f"""<div class="page">
<div class="band"><h1>解答　{TITLE}</h1><div class="pt">各5点<span class="pat">{pat}</span></div></div>
{''.join(rows)}
<div class="foot">（ ）の中は、書いてあってもなくても正解。漢字のまちがいは、テストに合わせて採点してください。</div></div>"""

os.makedirs(OUT, exist_ok=True)
for k, pat in enumerate("ABC"):
    doc = f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{page_q(pat, k)}{page_a(pat, k)}</body></html>'
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(doc); tmp = f.name
    pdf = os.path.join(OUT, f"歴史テスト_古墳・飛鳥_{pat}.pdf")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + tmp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.unlink(tmp)
    print(pdf)
