# -*- coding: utf-8 -*-
# 地図記号の図（国土地理院の記号をもとに簡略化して作図）。中心(0,0)・おおよそ半径16の枠で描く
W, COLS, CW, CH = 420, 5, 84, 98

def C(r, x=0, y=0, fill=False):
    return '<circle class="%s" cx="%g" cy="%g" r="%g"/>' % ("symf" if fill else "sym", x, y, r)
def P(d): return '<path class="sym" d="%s"/>' % d
def T(t, size, y=0): return '<text class="symt" x="0" y="%g" font-size="%g" text-anchor="middle" dominant-baseline="central">%s</text>' % (y, size, t)

def gear():
    import math
    s = C(8)
    for k in range(8):
        a = math.pi * k / 4
        s += P("M%.1f,%.1f L%.1f,%.1f" % (8 * math.cos(a), 8 * math.sin(a), 14 * math.cos(a), 14 * math.sin(a)))
    return s

SYM = {
 "市役所": C(16) + C(9),
 "町・村役場": C(14),
 "警察署": C(16) + P("M-9,-9 L9,9 M9,-9 L-9,9"),
 "交番": P("M-12,-12 L12,12 M12,-12 L-12,12"),
 "消防署": P("M-12,-15 L-12,-6 Q-12,3 0,3 Q12,3 12,-6 L12,-15 M0,3 L0,17"),
 "郵便局": C(16) + P("M-9,-7 L9,-7 M-9,-1 L9,-1 M0,-1 L0,11"),
 "小・中学校": T("文", 32),
 "高等学校": C(17) + T("文", 21),
 "病院": P("M-14,-14 L14,-14 L14,1 Q14,16 0,16 Q-14,16 -14,1 Z M0,-9 L0,11 M-9,1 L9,1"),
 "保健所": C(16) + P("M0,-10 L0,10 M-10,0 L10,0"),
 "寺院": T("卍", 30),
 "神社": P("M-16,-13 Q0,-17 16,-13 M-12,-6 L12,-6 M-8,-14 L-8,16 M8,-14 L8,16"),
 "工場": gear(),
 "発電所": gear() + P("M0,-14 L0,-21 M-5,-21 L5,-21"),
 "図書館": P("M0,-8 Q-8,-14 -15,-10 L-15,10 Q-8,6 0,12 Q8,6 15,10 L15,-10 Q8,-14 0,-8 Z M0,-8 L0,12"),
 "博物館": P("M-16,-6 L0,-16 L16,-6 Z M-10,-3 L-10,10 M0,-3 L0,10 M10,-3 L10,10 M-16,13 L16,13"),
 "老人ホーム": P("M-16,-1 L0,-15 L16,-1 M-11,-4 L-11,15 L11,15 L11,-4 M3,12 L3,-1 Q3,-5 -1,-5"),
 "史跡・名勝・天然記念物": C(2.6, 0, -7, True) + C(2.6, -8, 6, True) + C(2.6, 8, 6, True),
 "城跡": P("M-13,13 L-13,-1 L-5,-1 L-5,-12 L5,-12 L5,-1 L13,-1 L13,13"),
 "税務署": P("M0,-11 L11,0 L0,11 L-11,0 Z M-18,0 L18,0"),
 "裁判所": P("M0,-15 L-12,5 L12,5 Z M0,-15 L0,17"),
 "風車（発電用）": P("M0,-2 L0,17 M-6,17 L6,17 M0,-2 L0,-17 M0,-2 L-13,6 M0,-2 L13,6"),
 "自然災害伝承碑": P("M-8,14 L-8,-7 Q0,-16 8,-7 L8,14 M0,-5 L0,9 M-13,14 L13,14"),
 "水準点": P("M-12,-12 L12,-12 L12,12 L-12,12 Z") + C(2.6, 0, 0, True),
 "三角点": P("M0,-14 L-14,11 L14,11 Z") + C(2.6, 0, 3, True),
 "鉄道（JR線）": '<rect class="symf" x="-30" y="-4" width="60" height="8"/>' + ''.join('<rect class="symw" x="%d" y="-2" width="8" height="4"/>' % x for x in (-22, -6, 10)),
 "鉄道（JR以外）": P("M-30,0 L30,0") + ''.join(P("M%d,-5 L%d,5" % (x, x)) for x in (-24, -12, 0, 12, 24)),
}

def mark(d, x, y, k=0.72):
    return '<g transform="translate(%g %g) scale(%g)">%s</g>' % (x, y, k, d)

LAND1 = {
 "田": P("M-4,-9 L-4,9 M4,-9 L4,9"),
 "畑": P("M-8,-8 Q-4,6 0,8 Q4,6 8,-8"),
 "果樹園": C(6, 0, 4) + P("M0,-2 L-3,-11"),
 "茶畑": C(3.2, 0, -6) + C(3.2, -7, 5) + C(3.2, 7, 5),
 "桑畑": P("M0,10 L0,0 L-8,-10 M0,0 L8,-10"),
 "広葉樹林": C(7, 0, -3) + P("M4,3 L8,10"),
 "針葉樹林": P("M-8,6 L0,-10 L8,6 M0,-2 L0,11"),
 "荒地": P("M-10,8 L10,8 M-6,8 L-6,0 M0,8 L0,-9 M6,8 L6,0"),
}
LAND = {k: mark(v, -15, -10) + mark(v, 15, -10) + mark(v, 0, 12) for k, v in LAND1.items()}

NUMS = "①②③④⑤⑥⑦⑧⑨⑩"

def panel(names, table):
    rows = (len(names) + COLS - 1) // COLS
    s = ""
    for i, n in enumerate(names):
        c, r = i % COLS, i // COLS
        x, y = CW * c + CW / 2, CH * r + 42
        s += '<rect class="cell" x="%g" y="%g" width="%g" height="%g" rx="8"/>' % (CW * c + 4, CH * r + 4, CW - 8, CH - 8)
        s += '<g transform="translate(%g %g)">%s</g>' % (x, y, table[n])
        s += '<text class="snum" x="%g" y="%g" text-anchor="middle">%s</text>' % (x, CH * r + 84, NUMS[i])
    return s, rows * CH

FIGS = {
 "sym_land": ["田", "果樹園", "広葉樹林", "針葉樹林", "畑", "桑畑", "茶畑", "荒地"],
 "sym_b1": ["市役所", "町・村役場", "警察署", "交番", "消防署", "郵便局", "小・中学校", "高等学校", "病院", "保健所"],
 "sym_b2": ["寺院", "神社", "工場", "発電所", "図書館", "博物館", "老人ホーム", "史跡・名勝・天然記念物", "城跡", "税務署"],
 "sym_b3": ["裁判所", "風車（発電用）", "自然災害伝承碑", "水準点", "三角点", "鉄道（JR線）", "鉄道（JR以外）"],
}
CAP = "地図記号（国土地理院の記号をもとに、形を簡単にして作図）"

def build():
    reg, over = {}, {}
    for key, names in FIGS.items():
        table = LAND if key == "sym_land" else SYM
        svg, h = panel(names, table)
        reg[key] = {"w": W, "h": h, "base": ""}
        over[key] = {"r": key, "svg": svg, "cap": CAP}
    return reg, over

if __name__ == "__main__":
    import sys
    reg, over = build()
    for k in FIGS:
        open(sys.argv[1] + "/%s.svg" % k, "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d"><style>.sym{fill:none;stroke:#222;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}.symf,.symt{fill:#222}.symw{fill:#fff}.cell{fill:#f6f5f1;stroke:#ddd}.snum{fill:#b93328;font-size:15px}</style>%s</svg>' % (W, reg[k]["h"], over[k]["svg"]))
    print("ok")
