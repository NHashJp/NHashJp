"""Section headers, sub-labels, contact cards and language orbits."""
import math
from common import *

OUT = OUT_DIR + "/"
PANEL = "#04070E"
EDGE = "rgba(127,212,255,0.16)"


def drift_stars(seed, W, H, count, dur, clip_id, ymax=None):
    r = rng(seed)
    dots = []
    for _ in range(count):
        x, y = r.uniform(0, W), r.uniform(4, (ymax or H) - 4)
        dots.append(f'<circle cx="{n(x,1)}" cy="{n(y,1)}" r="{n(r.uniform(.3,.95),1)}" opacity="{n(r.uniform(.15,.6),1)}"/>')
    gid = f"ds{seed}"
    return (f'<g clip-path="url(#{clip_id})" fill="#DCEBFF"><g><animateTransform attributeName="transform" type="translate" '
            f'from="0 0" to="-{W} 0" dur="{dur}s" repeatCount="indefinite"/><g id="{gid}">{"".join(dots)}</g>'
            f'<use href="#{gid}" x="{W}"/></g></g>')


# ------------------------------------------------------------------ headers
def header(num, title, caption, fname, delay=0.0):
    W, H = 1000, 76
    o = [svg_open(W, H, f"{num} — {title}", f"Section header: {title} ({caption.strip('/ ').lower()}).")]
    o.append(f"""<defs><style>{REDUCED}</style>
<clipPath id="pc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10"/></clipPath>
<linearGradient id="tail" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset=".75" stop-color="{ACCENT}" stop-opacity=".55"/><stop offset="1" stop-color="{ACCENT_HI}"/></linearGradient>
<radialGradient id="hg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".55"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset=".18" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
</defs>""")
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{PANEL}" stroke="{EDGE}"/>')
    o.append(drift_stars(sum(map(ord, title)), W, H, 46, 48, "pc", ymax=52))
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" stroke="url(#edge)" stroke-opacity=".7"/>')
    p, wn = text(num, 28, 42, 13, "mono-bold", .06, fill=ACCENT_HI)
    o.append(p)
    o.append(f'<path d="M{n(36+wn)} 27V47" stroke="{HUD}"/>')
    p, wt = text(title, 52 + wn, 43, 25, "display", .07, fill=INK)
    o.append(p)
    # blinking cursor block after title
    o.append(f'<rect x="{n(62+wn+wt)}" y="25" width="9" height="18" fill="{ACCENT}" opacity=".85">'
             f'<animate attributeName="opacity" values=".85;.85;.15;.85" keyTimes="0;.55;.75;1" dur="2.6s" repeatCount="indefinite"/></rect>')
    p, _ = text(caption, 972, 41, 10.5, "mono", .2, "end", fill=DIM)
    o.append(p)
    # track with ticks
    ty = 61
    ticks = []
    for i, x in enumerate(range(28, 973, 12)):
        h = 5 if (x - 28) % 120 == 0 else 2
        ticks.append(f"M{x} {ty}v{h}")
    o.append(f'<path d="M28 {ty}H972" stroke="{CYAN}" stroke-opacity=".16"/>')
    o.append(f'<path d="{"".join(ticks)}" stroke="{CYAN}" stroke-opacity=".22"/>')
    # comet racing along the track
    o.append(f'<g clip-path="url(#pc)"><g transform="translate(-60 0)"><animateTransform attributeName="transform" type="translate" values="-60 0;1180 0;1180 0" '
             f'keyTimes="0;.42;1" calcMode="spline" keySplines=".45 0 .25 1;0 0 1 1" dur="10s" begin="{delay}s" repeatCount="indefinite"/>'
             f'<rect x="-190" y="{ty-.8}" width="190" height="1.6" fill="url(#tail)"/>'
             f'<circle cx="0" cy="{ty}" r="10" fill="url(#hg)"/><circle cx="0" cy="{ty}" r="1.8" fill="{ACCENT_HI}"/></g></g>')
    o.append("</svg>")
    open(OUT + fname, "w").write("".join(o))


def sublabel(code, title, fname, delay=0.0):
    W, H = 1000, 40
    o = [svg_open(W, H, f"{code} {title}", f"Sub-section label: {title}.")]
    o.append(f"""<defs><style>{REDUCED}</style><clipPath id="pc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="8"/></clipPath>
<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".45"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient></defs>""")
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{EDGE}"/>')
    o.append(f'<path d="M22 20l4.5 -4.5l4.5 4.5l-4.5 4.5z" fill="none" stroke="{ACCENT}" stroke-width="1.3"/>')
    p, wc = text(code, 42, 24, 10.5, "mono-bold", .16, fill=ACCENT_HI)
    o.append(p)
    p, wt = text(title, 56 + wc, 24, 11.5, "mono", .18, fill=INK)
    o.append(p)
    x0 = 72 + wc + wt
    o.append(f'<rect x="{n(x0)}" y="19.5" width="{n(976-x0)}" height="1" fill="url(#ln)"/>')
    o.append(f'<circle cx="{n(x0)}" cy="20" r="2" fill="{ACCENT_HI}" opacity="0"><animate attributeName="cx" values="{n(x0)};976;976" keyTimes="0;.32;1" '
             f'calcMode="spline" keySplines=".45 0 .3 1;0 0 1 1" dur="11s" begin="{delay}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="1;0;0" keyTimes="0;.32;1" dur="11s" begin="{delay}s" repeatCount="indefinite"/></circle>')
    o.append("</svg>")
    open(OUT + fname, "w").write("".join(o))


# ------------------------------------------------------------------ language orbits
def languages():
    W, H = 1000, 340
    CXo, CYo, RP = 300, 174, 26
    K = 0.34                       # foreshortening (orbit plane seen at ~70 deg)
    TILT = math.radians(-11)
    ct, stt = math.cos(TILT), math.sin(TILT)

    def proj(X, Y):
        sx, sy = X, Y * K
        return CXo + sx * ct - sy * stt, CYo + sx * stt + sy * ct

    bodies = [  # code, native, english, level, colour, a, e, phase, filled/24
        ("EN", "English", "ENGLISH", "NATIVE / FLUENT", "#5CC8FF", 74, .05, .1, 24),
        ("ES", "Español", "SPANISH", "NATIVE / FLUENT", "#FFB547", 110, .08, .55, 24),
        ("JA", "日本語", "JAPANESE", "NATIVE", "#FF6A55", 150, .06, .3, 24),
        ("CA", "Català", "CATALAN", "INTERMEDIATE", "#7DF0B0", 200, .24, .8, 14),
    ]
    kconst = 6.8 / 74 ** 1.5        # innermost orbit: 6.8 s        # Kepler III: period ~ a^1.5

    o = [svg_open(W, H, "Linguistic orbits — English, Spanish, Japanese, Catalan",
                  "Four languages shown as bodies orbiting a planet with Kepler-timed periods, ranked inner to outer: "
                  "English native/fluent, Spanish native/fluent, Japanese native, Catalan intermediate.")]
    defs = [f"<style>{REDUCED}</style>",
            f'<clipPath id="pc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14"/></clipPath>',
            f'<radialGradient id="pl" cx="{CXo+10}" cy="{CYo-12}" r="{RP*1.5}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#2D5B8A"/><stop offset=".55" stop-color="#0E2138"/><stop offset="1" stop-color="#050A14"/></radialGradient>',
            '<filter id="bl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>',
            f'<linearGradient id="shim" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="120" y2="0">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" values="420 0;1080 0;1080 0" keyTimes="0;.22;1" dur="11s" begin="1.8s" repeatCount="indefinite"/></linearGradient>']
    # front half-plane mask (Y > 0 in orbit plane)
    big = 2000
    p1 = proj(-big, 0)
    p2 = proj(big, 0)
    p3 = proj(big, big / K * 3)
    p4 = proj(-big, big / K * 3)
    defs.append(f'<clipPath id="front"><path d="M{n(p1[0])} {n(p1[1])}L{n(p2[0])} {n(p2[1])}L{n(p3[0])} {n(p3[1])}L{n(p4[0])} {n(p4[1])}Z"/></clipPath>')
    for c in bodies:
        col = c[4]
        defs.append(f'<radialGradient id="g{c[0]}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{col}" stop-opacity=".7"/>'
                    f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
    o.append("<defs>" + "".join(defs) + "</defs>")
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{PANEL}" stroke="{EDGE}"/>')
    o.append(drift_stars(404, W, H, 90, 120, "pc"))
    o.append(corner_brackets(W, H, m=12, L=14))
    p, _ = text("KEPLER III  ·  T² ~ a³", 30, 36, 9.5, "mono", .18, fill=CYAN, extra='fill-opacity=".6"')
    o.append(p)
    p, _ = text("ORBIT SIZE = FLUENCY RANK", 30, H - 26, 9.5, "mono", .18, fill=DIM, extra='fill-opacity=".8"')
    o.append(p)

    back, front, trails_back, trails_front, movers = [], [], [], [], []
    for code, native, eng, lvl, col, a, e, ph, _ in bodies:
        b = a * math.sqrt(1 - e * e)
        pts = []
        for i in range(721):
            E = 2 * math.pi * i / 720
            pts.append(proj(a * (math.cos(E) - e), b * math.sin(E)))
        pA, pB = proj(a * (1 - e), 0), proj(-a * (1 + e), 0)
        rot = n(math.degrees(TILT), 3)
        d = (f"M{n(pA[0],2)} {n(pA[1],2)}A{n(a,2)} {n(b*K,2)} {rot} 0 1 {n(pB[0],2)} {n(pB[1],2)}"
             f"A{n(a,2)} {n(b*K,2)} {rot} 0 1 {n(pA[0],2)} {n(pA[1],2)}Z")
        poly = Polyline(pts)
        back.append(f'<path d="{d}" stroke="{col}" stroke-opacity=".22" stroke-width="1" stroke-dasharray="2 4"/>')
        front.append(f'<path d="{d}" clip-path="url(#front)" stroke="{col}" stroke-opacity=".45" stroke-width="1.1"/>')
        P = kconst * a ** 1.5
        N = 160
        vals, svals, rvals, ovals = [], [], [], []
        for k in range(N + 1):
            M = 2 * math.pi * k / N + ph * 2 * math.pi
            E = M
            for _ in range(30):
                E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
            X, Y = a * (math.cos(E) - e), b * math.sin(E)
            sx, sy = proj(X, Y)
            vals.append(f"{n(sx,1)},{n(sy,1)}")
            Em = E % (2 * math.pi)
            # arclength fraction from periapsis along the drawn path
            idx = Em / (2 * math.pi) * 720
            s = poly.cum[int(idx)] + (poly.cum[min(int(idx) + 1, 720)] - poly.cum[int(idx)]) * (idx - int(idx))
            svals.append(math.floor(E / (2 * math.pi)) + s / poly.L)
            depth = Y / b                    # -1 back .. +1 front
            rvals.append(n(4.6 * (1 + .18 * depth), 2))
            hidden = Y < 0 and math.hypot(sx - CXo, sy - CYo) < RP + 3
            ovals.append("0" if hidden else n(.62 + .38 * (depth + 1) / 2, 2))
        dur = f'dur="{n(P,3)}s" repeatCount="indefinite"'
        tail_px = min(70, .32 * poly.L)
        for frac_len, op, sw in [(1, .22, 2.2), (.55, .45, 1.8), (.22, .9, 1.6)]:
            tl = tail_px * frac_len / poly.L * 1000
            offs = ";".join(n(tl - v * 1000, 1) for v in svals)
            trail = (f'<path d="{d}" pathLength="1000" stroke="{col}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round" '
                     f'stroke-dasharray="{n(tl,1)} {n(1000-tl,1)}"><animate attributeName="stroke-dashoffset" {dur} values="{offs}"/></path>')
            trails_back.append(trail)
        mv = (f'<g><animateMotion {dur} calcMode="linear" values="{";".join(vals)}"/>'
              f'<animate attributeName="opacity" {dur} calcMode="discrete" values="{";".join(ovals)}"/>'
              f'<circle r="13" fill="url(#g{code})"/>'
              f'<circle r="4.6" fill="{col}"><animate attributeName="r" {dur} values="{";".join(rvals)}"/></circle>'
              f'<circle r="1.6" fill="#fff" opacity=".9"/>')
        p, _ = text(code, 9, -7, 9, "mono-bold", .1, fill=col)
        mv += p + "</g>"
        movers.append(mv)

    o.extend(back)
    o.append('<g>' + "".join(trails_back) + "</g>")
    # home planet
    o.append(f'<circle cx="{CXo}" cy="{CYo}" r="{RP+10}" fill="#3B8BFF" opacity=".16" filter="url(#bl)"/>')
    o.append(f'<circle cx="{CXo}" cy="{CYo}" r="{RP}" fill="url(#pl)"/>')
    o.append(f'<circle cx="{CXo}" cy="{CYo}" r="{RP}" stroke="#8FD0FF" stroke-opacity=".55" stroke-width="1"/>')
    p, _ = text("NH", CXo, CYo + 4, 11, "mono-bold", .12, "middle", fill=INK, extra='fill-opacity=".9"')
    o.append(p)
    o.extend(front)
    # front trails re-drawn on top (only front half visible)
    o.append('<g clip-path="url(#front)">' + "".join(trails_back) + "</g>")
    o.extend(movers)

    # legend
    LX0, LX1 = 548, 962
    yr0, step = 54, 68
    segN, gap = 24, 3
    sw_ = (LX1 - LX0 - gap * (segN - 1)) / segN
    for i, (code, native, eng, lvl, col, a, e, ph, filled) in enumerate(bodies):
        yr = yr0 + i * step
        o.append(f'<circle cx="{LX0-14}" cy="{yr+15}" r="4.5" fill="{col}"/><circle cx="{LX0-14}" cy="{yr+15}" r="9" fill="url(#g{code})"/>')
        if code == "JA":
            p, wn = text(native, LX0, yr + 23, 21, "jp", 0, fill=INK)
        else:
            p, wn = text(native, LX0, yr + 23, 22, "display", .01, fill=INK)
        o.append(p)
        p, _ = text(f"{code} — {eng}", LX0 + wn + 14, yr + 21, 10, "mono", .18, fill=DIM)
        o.append(p)
        p, _ = text(lvl, LX1, yr + 21, 10, "mono-bold", .16, "end", fill=col)
        o.append(p)
        segs_on, segs_off = [], []
        for k in range(segN):
            x = LX0 + k * (sw_ + gap)
            r_ = f"M{n(x,1)} {yr+33}h{n(sw_,2)}v7h{n(-sw_,2)}Z"
            (segs_on if k < filled else segs_off).append(r_)
        o.append(f'<path d="{"".join(segs_off)}" fill="{col}" fill-opacity=".1"/>')
        b0 = .35 + i * .18
        o.append(f'<clipPath id="wipe{i}"><rect x="{LX0}" y="{yr+30}" width="{LX1-LX0}" height="14">'
                 f'<animate attributeName="width" values="0;0;{LX1-LX0}" keyTimes="0;{n(b0/(b0+1.1),4)};1" dur="{n(b0+1.1)}s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;.2 .7 .3 1"/></rect></clipPath>')
        o.append(f'<g clip-path="url(#wipe{i})"><path id="seg{i}" d="{"".join(segs_on)}" fill="{col}" fill-opacity=".85"/>'
                 f'<use href="#seg{i}" fill="url(#shim)"/></g>')
    o.append("</svg>")
    open(OUT + "languages.svg", "w").write("".join(o))


# ------------------------------------------------------------------ contact cards
def card(idx, channel, value, sub, color, icon, fname, delay=0.0):
    W, H = 480, 92
    o = [svg_open(W, H, f"{channel}: {value}", f"Contact channel {channel} — {value} ({sub}).")]
    o.append(f"""<defs><style>{REDUCED}</style><clipPath id="pc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12"/></clipPath>
<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="{color}" stop-opacity="0"/><stop offset=".5" stop-color="{color}" stop-opacity=".08"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>
<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{color}" stop-opacity=".9"/><stop offset=".35" stop-color="{color}" stop-opacity="0"/></linearGradient>
<radialGradient id="ig" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{color}" stop-opacity=".28"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>""")
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{PANEL}" stroke="{EDGE}"/>')
    o.append(drift_stars(31 + idx, W, H, 26, 60 + idx * 6, "pc"))
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" stroke="url(#edge)" stroke-opacity=".55"/>')
    # sweep of light across the card
    o.append(f'<g clip-path="url(#pc)"><rect x="-160" y="0" width="160" height="{H}" fill="url(#sw)" transform="skewX(-20)">'
             f'<animate attributeName="x" values="-200;{W+120};{W+120}" keyTimes="0;.14;1" calcMode="spline" keySplines=".45 0 .4 1;0 0 1 1" dur="18s" begin="{delay}s" repeatCount="indefinite"/></rect></g>')
    # icon tile
    cx_, cy_ = 52, H / 2
    o.append(f'<circle cx="{cx_}" cy="{cy_}" r="30" fill="url(#ig)"/>')
    o.append(f'<rect x="{cx_-23}" y="{cy_-23}" width="46" height="46" rx="11" fill="{color}" fill-opacity=".07" stroke="{color}" stroke-opacity=".55"/>')
    o.append(f'<g transform="translate({cx_} {cy_})" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" fill="none">{icon}</g>')
    p, _ = text(f"CH-0{idx} · {channel}", 96, 36, 9.5, "mono-bold", .2, fill=color)
    o.append(p)
    vsize = 20 if len(value) < 20 else 17.5
    p, _ = text(value, 96, 62, vsize, "display", .005, fill=INK)
    o.append(p)
    p, _ = text(sub, 96, 79, 9, "mono", .12, fill=DIM)
    o.append(p)
    # signal-strength bars: steady, only the top bar breathes softly
    bx = W - 70
    for k in range(4):
        h = 5 + k * 3.5
        anim = ('<animate attributeName="opacity" values=".9;.55;.9" dur="4.5s" repeatCount="indefinite" '
                'calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/>') if k == 3 else ""
        o.append(f'<rect x="{bx + k*6}" y="{n(34-h)}" width="3.6" height="{n(h)}" rx="1" fill="{color}" opacity=".9">{anim}</rect>')
    # launch arrow
    o.append(f'<g transform="translate({W-34} 60)" stroke="{INK}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none">'
             f'<path d="M-6 6L6 -6M-3 -6H6V3"/></g>')
    o.append("</svg>")
    open(OUT + fname, "w").write("".join(o))


ICONS = {
    # generic glyphs (no brand marks): profile, code, envelope, globe
    "profile": '<rect x="-11" y="-11" width="22" height="22" rx="4"/><circle cx="0" cy="-3" r="4"/><path d="M-6.5 8c1.2-4 3.6-5.5 6.5-5.5s5.3 1.5 6.5 5.5"/>',
    "code": '<path d="M-5 -7L-11 0L-5 7M5 -7L11 0L5 7M2.5 -9L-2.5 9"/>',
    "mail": '<rect x="-11" y="-8" width="22" height="16" rx="3"/><path d="M-10 -6.5L0 1L10 -6.5"/>',
    "globe": '<circle r="11"/><ellipse rx="4.6" ry="11"/><path d="M-11 0H11M-9.4 -5.5H9.4M-9.4 5.5H9.4"/>',
}

if __name__ == "__main__":
    header("01", "MISSION BRIEF", "// ABOUT", "h-about.svg", 0)
    header("02", "COMMS CHANNELS", "// CONTACT", "h-contact.svg", 2.5)
    header("03", "LINGUISTIC ORBITS", "// LANGUAGES", "h-languages.svg", 5)
    header("04", "PAYLOAD MANIFEST", "// TECH STACK", "h-stack.svg", 7.5)
    sublabel("SYS.A", "LANGUAGES", "s-languages.svg", 0)
    sublabel("SYS.B", "FRAMEWORKS & LIBRARIES", "s-frameworks.svg", 2.75)
    sublabel("SYS.C", "DATABASES & DEVOPS", "s-infra.svg", 5.5)
    sublabel("SYS.D", "TOOLS", "s-tools.svg", 8.25)
    languages()
    card(1, "LINKEDIN", "Naoki Hashimoto", "linkedin.com/in/n-hash9999", ACCENT, ICONS["profile"], "c-linkedin.svg", 0)
    card(2, "GITHUB", "NHashJp", "github.com/NHashJp", ACCENT, ICONS["code"], "c-github.svg", 4.5)
    card(3, "EMAIL", "nhnaokih25@gmail.com", "OPEN A CHANNEL — SAY HELLO", ACCENT, ICONS["mail"], "c-email.svg", 9)
    card(4, "PORTFOLIO", "portfolio2026", "nhashjp.github.io/portfolio2026", ACCENT, ICONS["globe"], "c-portfolio.svg", 13.5)
    print("sections ok")
