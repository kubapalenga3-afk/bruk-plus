#!/usr/bin/env python3
"""Generator szkiców logo BrukPlus (3 kierunki: A industrial, B nowoczesny, C premium).

Wyniki trafiają do brand/logo-drafts/<kierunek>/*.svg (tekst zamieniony na krzywe)
oraz brand/logo-drafts/cards/*.html (karty podglądowe, renderowane osobno do PNG).
Fonty: .claude/skills/canvas-design/canvas-fonts (licencja OFL).
Uruchom:  python3 brand/src/make_logos.py
"""
import pathlib

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
FONTS = ROOT / ".claude/skills/canvas-design/canvas-fonts"
OUT = ROOT / "brand/logo-drafts"

# ---------------------------------------------------------------- tekst -> krzywe
_cache = {}


def font(name):
    if name not in _cache:
        f = TTFont(FONTS / f"{name}.ttf")
        _cache[name] = dict(
            gs=f.getGlyphSet(),
            cmap=f.getBestCmap(),
            upm=f["head"].unitsPerEm,
            cap=f["OS/2"].sCapHeight / f["head"].unitsPerEm,
        )
    return _cache[name]


def measure(name, text, size, tracking=0.0):
    f = font(name)
    s = size / f["upm"]
    return sum(f["gs"][f["cmap"][ord(c)]].width * s for c in text) + tracking * (len(text) - 1)


def text_path(name, text, size, x, y, tracking=0.0):
    f = font(name)
    s = size / f["upm"]
    pen = SVGPathPen(f["gs"], ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    cx = x
    for c in text:
        g = f["gs"][f["cmap"][ord(c)]]
        g.draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
        cx += g.width * s + tracking
    return pen.getCommands()


def P(d, fill):
    return f'<path d="{d}" fill="{fill}"/>'


def svg(inner, w, h, pad=0):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}" '
        f'width="{w + 2 * pad}" height="{h + 2 * pad}">{inner}</svg>'
    )


def fit_tracking_size(name, text, width, track_ratio):
    """Rozmiar fontu tak, by tekst z trackingiem = track_ratio*size miał dokładnie `width`."""
    nat1 = measure(name, text, 1.0)
    size = width / (nat1 + track_ratio * (len(text) - 1))
    return size, size * track_ratio


# ---------------------------------------------------------------- ikony (100x100)
def icon_A(uid, tile="#1B1F23", plus="#FFB000"):
    """Pięć „kostek” brukowych układa się w plus; opcjonalnie ciemny kafel z połyskiem żywicy."""
    blocks = [(37, 37, 26, 26), (37, 16, 26, 18), (37, 66, 26, 18), (16, 37, 18, 26), (66, 37, 18, 26)]
    out = ""
    if tile:
        out += f'<clipPath id="{uid}c"><rect width="100" height="100" rx="9"/></clipPath>'
        out += f'<rect width="100" height="100" rx="9" fill="{tile}"/>'
    for x, y, w, h in blocks:
        out += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2.5" fill="{plus}"/>'
    if tile:
        out += f'<g clip-path="url(#{uid}c)"><path d="M0 46 L46 0 L66 0 L0 66 Z" fill="#fff" opacity=".07"/></g>'
    return out


def icon_B(uid, c1="#0E2A3B", c2="#12A5A0"):
    """Cztery płytki; plus powstaje w przerwie między nimi; jedna płytka z połyskiem."""
    tiles = [(0, 0, c1), (56, 0, c2), (0, 56, c1), (56, 56, c1)]
    out = (
        f'<linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="{uid}c"><rect x="56" y="0" width="44" height="44" rx="10"/></clipPath>'
    )
    for x, y, c in tiles:
        out += f'<rect x="{x}" y="{y}" width="44" height="44" rx="10" fill="{c}"/>'
    out += f'<g clip-path="url(#{uid}c)"><rect x="56" y="0" width="44" height="44" fill="url(#{uid}g)"/></g>'
    return out


def icon_C(uid, g1="#E8CF95", g2="#A8843D"):
    """Podwójny romb (kafelek układany po przekątnej) z pełnym plusem, szampański złoty gradient."""
    out = (
        f'<linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>'
        f'<polygon points="50,3 97,50 50,97 3,50" fill="none" stroke="url(#{uid}g)" stroke-width="2.6" stroke-linejoin="miter"/>'
        f'<polygon points="50,12 88,50 50,88 12,50" fill="none" stroke="url(#{uid}g)" stroke-width=".9" stroke-linejoin="miter"/>'
        f'<rect x="46" y="28" width="8" height="44" fill="url(#{uid}g)"/>'
        f'<rect x="28" y="46" width="44" height="8" fill="url(#{uid}g)"/>'
    )
    return out


# ---------------------------------------------------------------- loga (lockupy)
TAG = "POSADZKI ŻYWICZNE"


def lockup_A(dark, uid="a"):
    ink = "#F4F2EE" if dark else "#1B1F23"
    sub = "#A3A9AF" if dark else "#5F656B"
    ic = icon_A(uid, tile=None if dark else "#1B1F23")
    bold, reg, tf = "BigShoulders-Bold", "BigShoulders-Regular", "WorkSans-Regular"
    cap = 58
    size = cap / font(bold)["cap"]
    tr = size * 0.07
    x0 = 100 + 26
    w1 = measure(bold, "BRUK", size, tr)
    w2 = measure(reg, "PLUS", size, tr)
    W = w1 + tr + w2
    tsize, ttr = fit_tracking_size(tf, TAG, W, 0.32)
    tcap = font(tf)["cap"] * tsize
    gap = 15
    top = (100 - (cap + gap + tcap)) / 2
    by = top + cap
    ty = by + gap + tcap
    inner = ic
    inner += P(text_path(bold, "BRUK", size, x0, by, tr), ink)
    inner += P(text_path(reg, "PLUS", size, x0 + w1 + tr, by, tr), ink)
    inner += P(text_path(tf, TAG, tsize, x0, ty, ttr), sub)
    return inner, x0 + W, 100


def lockup_B(dark, uid="b"):
    ink = "#F2F7F7" if dark else "#0E2A3B"
    acc = "#34D1CA" if dark else "#12A5A0"
    sub = "#8FA7B3" if dark else "#5C7684"
    ic = icon_B(uid, c1="#E4EEF0" if dark else "#0E2A3B", c2="#34D1CA" if dark else "#12A5A0")
    bold, reg, tf = "Outfit-Bold", "Outfit-Regular", "Outfit-Regular"
    cap = 47
    size = cap / font(bold)["cap"]
    tr = size * -0.005
    x0 = 100 + 26
    w1 = measure(bold, "bruk", size, tr)
    w2 = measure(bold, "plus", size, tr)
    W = w1 + tr + w2
    tsize, ttr = fit_tracking_size(tf, TAG, W, 0.30)
    tcap = font(tf)["cap"] * tsize
    desc = size * 0.2
    gap = 12
    total = cap + desc + gap + tcap
    top = (100 - total) / 2
    by = top + cap
    ty = by + desc + gap + tcap
    inner = ic
    inner += P(text_path(bold, "bruk", size, x0, by, tr), ink)
    inner += P(text_path(bold, "plus", size, x0 + w1 + tr, by, tr), acc)
    inner += P(text_path(tf, TAG, tsize, x0, ty, ttr), sub)
    return inner, x0 + W, 100


def lockup_C(dark, uid="c"):
    ink = "#F2EDE3" if dark else "#16161A"
    gold = "#C8A96A" if dark else "#98783A"
    ic = icon_C(uid, "#E8CF95" if dark else "#C9A55B", "#A8843D" if dark else "#8A6A2F")
    reg, tf = "InstrumentSans-Regular", "InstrumentSans-Regular"
    size = 30
    tr = size * 0.34
    W = measure(reg, "BRUKPLUS", size, tr)
    tsize = 9.5
    ttr = tsize * 0.4
    TW = measure(tf, TAG, tsize, ttr)
    CW = max(W, TW, 100)
    cx = CW / 2
    inner = f'<g transform="translate({cx - 50} 0)">{ic}</g>'
    cap = font(reg)["cap"] * size
    by = 100 + 30 + cap
    inner += P(text_path(reg, "BRUKPLUS", size, cx - W / 2, by, tr), ink)
    inner += f'<rect x="{cx - 14}" y="{by + 14}" width="28" height="1.4" fill="{gold}"/>'
    tcap = font(tf)["cap"] * tsize
    ty = by + 14 + 1.4 + 14 + tcap
    inner += P(text_path(tf, TAG, tsize, cx - TW / 2, ty, ttr), gold)
    return inner, CW, ty


def icon_svg(kind, dark=False):
    if kind == "A":
        return svg(icon_A("ia", tile=None if dark else "#1B1F23"), 100, 100)
    if kind == "B":
        return svg(icon_B("ib", c1="#E4EEF0" if dark else "#0E2A3B", c2="#34D1CA" if dark else "#12A5A0"), 100, 100)
    return svg(icon_C("ic", "#E8CF95" if dark else "#C9A55B", "#A8843D" if dark else "#8A6A2F"), 100, 100)


DIRS = {
    "A": dict(
        folder="A-industrial", lock=lockup_A, name="A · Industrialny", tag="mocny, rzemieślniczy",
        why="Pięć „kostek” brukowych układa się w plus (bruk + plus). Żółć jak oznakowanie na halach i garażach. Mocny, konkretny klimat.",
        light="#ECE9E3", dark="#14171A", av_bg="#1B1F23",
        pal=[("Grafit", "#1B1F23"), ("Żółć znakowania", "#FFB000"), ("Beton", "#ECE9E3"), ("Stal", "#5F656B"), ("Biel", "#F4F2EE")],
    ),
    "B": dict(
        folder="B-nowoczesny", lock=lockup_B, name="B · Nowoczesny", tag="czysty, świeży",
        why="Cztery płytki, a plus tworzy się w przerwie między nimi. Jedna płytka z połyskiem żywicy. Pasuje do mieszkań i lokali.",
        light="#F2F7F7", dark="#0B1F2C", av_bg="#0E2A3B",
        pal=[("Granat", "#0E2A3B"), ("Morski", "#12A5A0"), ("Piana", "#F2F7F7"), ("Stalowy", "#5C7684"), ("Jasny morski", "#34D1CA")],
    ),
    "C": dict(
        folder="C-premium", lock=lockup_C, name="C · Premium", tag="elegancki, spokojny",
        why="Kafelek ułożony po przekątnej, a w nim plus, w szampańskim złocie. Droższy, spokojniejszy klimat: showroomy, domy, tarasy.",
        light="#F5F1EA", dark="#101012", av_bg="#1A1A1D",
        pal=[("Czerń", "#101012"), ("Szampan", "#C8A96A"), ("Ciepła biel", "#F5F1EA"), ("Grafit", "#2A2A2E"), ("Brąz", "#8A6A2F")],
    ),
}

CARD_CSS = f"""
@font-face{{font-family:'Work Sans';src:url('file://{FONTS}/WorkSans-Regular.ttf');font-weight:400}}
@font-face{{font-family:'Work Sans';src:url('file://{FONTS}/WorkSans-Bold.ttf');font-weight:700}}
*{{box-sizing:border-box;margin:0}}
body{{width:1080px;height:1350px;font-family:'Work Sans',sans-serif;background:#fff;color:#14171A}}
.card{{width:1080px;height:1350px;display:flex;flex-direction:column}}
.head{{height:200px;padding:44px 64px 0;background:#fff}}
.head .t{{font-size:44px;font-weight:700;letter-spacing:-.5px}}
.head .t span{{font-weight:400;color:#8a8f94;font-size:26px;margin-left:10px}}
.head p{{margin-top:12px;font-size:23px;line-height:1.4;color:#4a4f55;max-width:930px}}
.light{{height:470px;display:flex;align-items:center;justify-content:center}}
.dark{{height:480px;display:flex;align-items:center;justify-content:space-around;padding:0 48px}}
.av{{display:flex;flex-direction:column;align-items:center;gap:18px;color:#8b9298;font-size:20px;letter-spacing:.5px}}
.circ{{width:230px;height:230px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid rgba(255,255,255,.12)}}
.light svg,.dark svg,.circ svg{{width:100%;height:auto;display:block}}
.pal{{height:200px;display:flex}}
.pal div{{flex:1;display:flex;flex-direction:column;justify-content:flex-end;padding:0 0 16px 16px;font-size:17px;line-height:1.35}}
.loc{{position:absolute;right:64px;top:50px;font-size:20px;color:#8a8f94;letter-spacing:.4px}}
"""


def luma(hexc):
    h = hexc.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def card_html(key):
    d = DIRS[key]
    l_in, lw, lh = d["lock"](False, key.lower() + "l")
    r_in, rw, rh = d["lock"](True, key.lower() + "d")
    light_svg = svg(l_in, lw, lh)
    dark_svg = svg(r_in, rw, rh)
    ic_dark = icon_svg(key, dark=True)
    if key == "A":
        av_inner = icon_A("aav", tile=None)
    elif key == "B":
        av_inner = icon_B("bav", c1="#E4EEF0", c2="#34D1CA")
    else:
        av_inner = icon_C("cav", "#E8CF95", "#A8843D")
    av = svg(av_inner, 100, 100)
    pal = "".join(
        f'<div style="background:{c};color:{"#111" if luma(c) > 150 else "#fff"}"><b>{n}</b>{c}</div>' for n, c in d["pal"]
    )
    # skala lockupu: szerokie poziome na ok. 800 px, pionowe (C) na ok. 330 px szerokości
    lw_px = 800 if key != "C" else 440
    rw_px = 540 if key != "C" else 300
    return f"""<!doctype html><html lang="pl"><head><meta charset="utf-8"><style>{CARD_CSS}</style></head><body><div class="card">
<div class="head" style="position:relative"><div class="t">{d['name']}<span>{d['tag']}</span></div><p>{d['why']}</p></div>
<div class="light" style="background:{d['light']}"><div style="width:{lw_px}px">{light_svg}</div></div>
<div class="dark" style="background:{d['dark']}"><div style="width:{rw_px}px">{dark_svg}</div>
<div class="av"><div class="circ" style="background:{d['av_bg']}"><div style="width:150px">{av}</div></div>awatar (Instagram / FB)</div></div>
<div class="pal">{pal}</div></div></body></html>"""


def main():
    (OUT / "cards").mkdir(parents=True, exist_ok=True)
    for key, d in DIRS.items():
        folder = OUT / d["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        for dark, name in ((False, "logo-na-jasnym.svg"), (True, "logo-na-ciemnym.svg")):
            inner, w, h = d["lock"](dark, key.lower() + ("d" if dark else "l"))
            (folder / name).write_text(svg(inner, w, h, pad=10), encoding="utf-8")
        (folder / "ikona.svg").write_text(icon_svg(key), encoding="utf-8")
        (folder / "ikona-na-ciemnym.svg").write_text(icon_svg(key, dark=True), encoding="utf-8")
        (OUT / "cards" / f"{key}.html").write_text(card_html(key), encoding="utf-8")
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
