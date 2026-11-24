"""Text -> SVG path conversion (HarfBuzz shaping + fontTools outlines).

Converting text to outlines means the SVGs look identical everywhere and need
no font loading, which GitHub's image sandbox would block anyway.
"""
import io
import os
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = os.environ.get("FONT_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_modules", "@fontsource"))


class Font:
    def __init__(self, path):
        tt = TTFont(path)
        tt.flavor = None
        buf = io.BytesIO()
        tt.save(buf)
        data = buf.getvalue()
        self.tt = TTFont(io.BytesIO(data))
        self.gs = self.tt.getGlyphSet()
        self.upem = self.tt["head"].unitsPerEm
        self.order = self.tt.getGlyphOrder()
        face = hb.Face(data)
        self.hbfont = hb.Font(face)
        self.cache = {}

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": True, "liga": False})
        return list(zip(buf.glyph_infos, buf.glyph_positions))

    def width(self, text, size, tracking=0.0):
        sc = size / self.upem
        run = self.shape(text)
        adv = sum(p.x_advance for _, p in run) * sc
        return adv + tracking * size * max(len(run) - 1, 0)

    def path(self, text, x, y, size, tracking=0.0, anchor="start"):
        """Return SVG path data for `text` with baseline at y.

        tracking is extra letter spacing in em.
        """
        sc = size / self.upem
        w = self.width(text, size, tracking)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        pen_x = x
        parts = []
        for info, pos in self.shape(text):
            gname = self.order[info.codepoint]
            gx = pen_x + pos.x_offset * sc
            gy = y - pos.y_offset * sc
            svgpen = SVGPathPen(self.gs, ntos=lambda v: (f"{v:.1f}".rstrip("0").rstrip(".") or "0"))
            tpen = TransformPen(svgpen, (sc, 0, 0, -sc, gx, gy))
            self.gs[gname].draw(tpen)
            d = svgpen.getCommands()
            if d:
                parts.append(d)
            pen_x += pos.x_advance * sc + tracking * size
        return " ".join(parts), w


def _f(rel):
    return Font(os.path.join(FONT_DIR, rel))


_cache = {}


def font(name):
    table = {
        "display": "space-grotesk/files/space-grotesk-latin-700-normal.woff2",
        "display-med": "space-grotesk/files/space-grotesk-latin-500-normal.woff2",
        "mono": "jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2",
        "mono-bold": "jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2",
        "mono-light": "jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2",
        "jp": "noto-sans-jp/files/noto-sans-jp-japanese-500-normal.woff2",
    }
    if name not in _cache:
        _cache[name] = _f(table[name])
    return _cache[name]
