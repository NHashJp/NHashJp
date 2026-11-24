"""Shared helpers for the profile SVG generators."""
import math
import os
import random
import svgtext as st

OUT_DIR = os.environ.get("OUT_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))
os.makedirs(OUT_DIR, exist_ok=True)

# Palette
BG = "#02040A"
INK = "#EEF4FF"
DIM = "#8796B2"
FAINT = "#4A5873"
CYAN = "#7FD4FF"
ORANGE = "#FF7A2F"
WARM = "#FFB070"
ACCENT = "#8BAE74"       # primary accent (sage green, from the reference swatch)
ACCENT_HI = "#A9C896"    # lighter tint for glows / small text
HUD = "rgba(127,212,255,0.38)"


def n(v, p=2):
    s = f"{v:.{p}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def text(s, x, y, size, kind="mono", tracking=0.0, anchor="start", fill=INK, extra=""):
    d, w = st.font(kind).path(s, x, y, size, tracking, anchor)
    return f'<path d="{d}" fill="{fill}" {extra}/>', w


def tw(s, size, kind="mono", tracking=0.0):
    return st.font(kind).width(s, size, tracking)


def kf(attr, frames, T, mode="linear", extra="", splines=None):
    """SMIL animate from absolute-time keyframes [(t, value), ...] over cycle T."""
    frames = sorted(frames, key=lambda f: f[0])
    if frames[0][0] > 0:
        frames.insert(0, (0, frames[0][1]))
    if frames[-1][0] < T:
        frames.append((T, frames[-1][1]))
    kt = ";".join(n(t / T, 5) for t, _ in frames)
    vals = ";".join(str(v) for _, v in frames)
    sp = ""
    if splines:
        sp = f' keySplines="{splines}"'
    return (f'<animate attributeName="{attr}" dur="{n(T)}s" repeatCount="indefinite" '
            f'calcMode="{mode}" keyTimes="{kt}" values="{vals}"{sp} {extra}/>')


def rng(seed):
    return random.Random(seed)


# ---- cubic-bezier easing helpers (CSS / SMIL keySplines semantics) ----
def _bez(u, a, b):
    return 3 * a * u * (1 - u) ** 2 + 3 * b * u * u * (1 - u) + u ** 3


def ease(tau, x1, y1, x2, y2):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _bez(mid, x1, x2) < tau:
            lo = mid
        else:
            hi = mid
    return _bez((lo + hi) / 2, y1, y2)


def ease_inv(p, x1, y1, x2, y2):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _bez(mid, y1, y2) < p:
            lo = mid
        else:
            hi = mid
    return _bez((lo + hi) / 2, x1, x2)


class Polyline:
    """Dense polyline with arclength lookup."""

    def __init__(self, pts):
        self.pts = pts
        self.cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            self.cum.append(self.cum[-1] + math.dist(a, b))
        self.L = self.cum[-1]

    def at(self, s):
        s = max(0, min(self.L, s))
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.cum[m] < s:
                lo = m
            else:
                hi = m
        a, b = self.pts[lo], self.pts[hi]
        seg = self.cum[hi] - self.cum[lo] or 1
        f = (s - self.cum[lo]) / seg
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), ang

    def find(self, pred):
        """First arclength where pred(point) is True."""
        for p, s in zip(self.pts, self.cum):
            if pred(p):
                return s
        return self.L


def cubic_pts(p0, p1, p2, p3, k=600):
    out = []
    for i in range(k + 1):
        u = i / k
        x = (1 - u) ** 3 * p0[0] + 3 * u * (1 - u) ** 2 * p1[0] + 3 * u * u * (1 - u) * p2[0] + u ** 3 * p3[0]
        y = (1 - u) ** 3 * p0[1] + 3 * u * (1 - u) ** 2 * p1[1] + 3 * u * u * (1 - u) * p2[1] + u ** 3 * p3[1]
        out.append((x, y))
    return out


def svg_open(w, h, title, desc):
    esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;")
    title, desc = esc(title), esc(desc)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'fill="none" role="img" aria-labelledby="t d">'
            f'<title id="t">{title}</title><desc id="d">{desc}</desc>')


REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def corner_brackets(w, h, m=14, L=18, stroke=HUD, sw=1.2):
    s = []
    for (x, y, dx, dy) in [(m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)]:
        s.append(f'<path d="M{n(x)} {n(y + dy * L)}V{n(y)}H{n(x + dx * L)}" stroke="{stroke}" stroke-width="{sw}"/>')
    return "".join(s)


class Sprite:
    """Glyphs defined once in <defs>, placed with <use> — keeps repeated readouts small."""

    def __init__(self, kind, size, prefix, tracking=0.0):
        self.f = st.font(kind)
        self.size, self.prefix, self.tracking = size, prefix, tracking
        self.defs = {}

    def _id(self, ch):
        if ch not in self.defs:
            d, _ = self.f.path(ch, 0, 0, self.size)
            self.defs[ch] = (f"{self.prefix}{len(self.defs)}", d)
        return self.defs[ch][0]

    def adv(self, ch):
        return self.f.width(ch, self.size) + self.tracking * self.size

    def use(self, s, x, y, fill=None, extra=""):
        parts = []
        for ch in s:
            if ch != " ":
                parts.append(f'<use href="#{self._id(ch)}" x="{n(x)}" y="{n(y)}"/>')
            x += self.adv(ch)
        f = f' fill="{fill}"' if fill else ""
        return f"<g{f} {extra}>" + "".join(parts) + "</g>"

    def defs_svg(self):
        return "".join(f'<path id="{i}" d="{d}"/>' for i, d in self.defs.values())
