"""Hero banner: orbital sunrise + live launch-to-orbit sequence."""
import math
import os
from common import *

W, H = 1000, 420
CX, CY, R = 640, 2100, 1800          # planet
KM = 6371 / R                         # km per px (Earth scale)
RK = R + 100 / KM                     # Karman line
RL = R + 408 / KM                     # LEO (ISS altitude)
FLARE = (782, 0)
FLARE = (782, CY - math.sqrt(R * R - (782 - CX) ** 2) - 1)


def horizon(x, r=R):
    return CY - math.sqrt(r * r - (x - CX) ** 2)


def alt_km(p):
    return max(0.0, (math.dist(p, (CX, CY)) - R) * KM)


# ---------------------------------------------------------------- trajectory
P0 = (548, horizon(548) + 16)
JX = 700
J = (JX, horizon(JX, RL))
slope = (JX - CX) / math.sqrt(RL * RL - (JX - CX) ** 2)
dl = math.hypot(1, slope)
tang = (1 / dl, slope / dl)
P1 = (548, 212)
P2 = (J[0] - tang[0] * 95, J[1] - tang[1] * 95)
EX = 1075
E = (EX, horizon(EX, RL))

bez = cubic_pts(P0, P1, P2, J, 800)
arc = []
a0 = math.atan2(J[1] - CY, J[0] - CX)
a1 = math.atan2(E[1] - CY, E[0] - CX)
for i in range(1, 401):
    a = a0 + (a1 - a0) * i / 400
    arc.append((CX + RL * math.cos(a), CY + RL * math.sin(a)))
poly = Polyline(bez + arc)
L = poly.L
Lb = Polyline(bez).L
ps = Lb / L                            # path fraction at SECO
TRAJ_D = (f"M{n(P0[0])} {n(P0[1])}C{n(P1[0])} {n(P1[1])} {n(P2[0])} {n(P2[1])} {n(J[0])} {n(J[1])}"
          f"A{n(RL)} {n(RL)} 0 0 1 {n(E[0])} {n(E[1])}")

# ---------------------------------------------------------------- timeline
t0 = 0.45            # ignition (craft is still behind the limb)
DA = 4.6             # powered ascent
SPL = (0.42, 0.0, 0.88, None)
m = 2.4              # end-of-burn speed relative to average burn speed
SPL = (0.42, 0.0, 0.88, 1 - m * (1 - 0.88))
tS = t0 + DA
v_c = m * ps / DA    # coast speed (path fraction per second)
tE = tS + (1 - ps) / v_c
T = round(max(10.0, tE + 2.6), 2)
FADE0, FADE1 = tE + 0.5, tE + 1.9


def p_at(t):
    if t <= t0:
        return 0.0
    if t <= tS:
        return ps * ease((t - t0) / DA, *SPL)
    if t <= tE:
        return ps + (t - tS) * v_c
    return 1.0


def t_at(p):
    if p <= ps:
        return t0 + DA * ease_inv(p / ps, *SPL)
    return tS + (p - ps) / v_c


def vel(t):
    if t <= t0:
        return 0.0
    if t >= tS:
        return 7.66
    return 7.66 * ((t - t0) / DA) ** 1.4


sM = poly.find(lambda q: alt_km(q) >= 70 and q[1] < P0[1] - 5)
tM = t_at(sM / L)
tSEP, tIGN = tM + 0.16, tM + 0.46
t_hz = t_at(poly.find(lambda q: q[1] < horizon(q[0])) / L)
PM, angM = poly.at(sM)

kp = f'keyPoints="0;0;{n(ps,5)};1;1" keyTimes="0;{n(t0/T,5)};{n(tS/T,5)};{n(tE/T,5)};1"'
ks = f'keySplines="0 0 1 1;{SPL[0]} {SPL[1]} {SPL[2]} {n(SPL[3],4)};0 0 1 1;0 0 1 1"'


def vis(a, b=None, extra=""):
    """discrete opacity: visible in [a, b) seconds of the cycle"""
    if b is None or b >= T:
        if a <= 0:
            return ""
        return (f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
                f'keyTimes="0;{n(a/T,5)}" values="0;1"/>')
    if a <= 0:
        return (f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
                f'keyTimes="0;{n(b/T,5)}" values="1;0"/>')
    return (f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{n(a/T,5)};{n(b/T,5)}" values="0;1;0"/>')


out = []
o = out.append
o(svg_open(W, H, "Naoki Hashimoto — Software Engineer",
           "Orbital sunrise over Earth's limb. A rocket rises from beyond the horizon, drops its first stage "
           "and inserts into low Earth orbit while live telemetry updates."))

# ---------------------------------------------------------------- defs
o("<defs>")
o(f"""<style>
.tw{{animation:tw 3.2s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
.fl{{transform-box:fill-box;transform-origin:100% 50%;animation:fl .09s linear infinite alternate}}
@keyframes fl{{from{{transform:scaleX(.82) scaleY(.92)}}to{{transform:scaleX(1.08) scaleY(1.05)}}}}
.blink{{animation:bl 1.1s steps(1) infinite}}
@keyframes bl{{0%,55%{{opacity:1}}56%,100%{{opacity:.15}}}}
.strobe{{animation:sb 1s steps(1) infinite}}
@keyframes sb{{0%,12%{{opacity:1}}13%,100%{{opacity:0}}}}
.anam{{transform-box:fill-box;transform-origin:50% 50%;animation:an 3.4s ease-in-out infinite}}
@keyframes an{{0%,100%{{transform:scaleX(.9);opacity:.75}}50%{{transform:scaleX(1.12);opacity:1}}}}
{REDUCED}
</style>""")
o(f"""<radialGradient id="bg" cx="{FLARE[0]}" cy="{FLARE[1]}" r="760" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#0D1A2E"/><stop offset=".42" stop-color="#050913"/><stop offset="1" stop-color="{BG}"/></radialGradient>
<radialGradient id="planet" cx="{FLARE[0]}" cy="{FLARE[1]+14}" r="560" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#1B3A5C"/><stop offset=".22" stop-color="#0C1B2E"/><stop offset=".6" stop-color="#060C16"/><stop offset="1" stop-color="#03060B"/></radialGradient>
<radialGradient id="sunglow" cx="{FLARE[0]}" cy="{FLARE[1]}" r="300" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#FFD3A0" stop-opacity=".55"/><stop offset=".18" stop-color="#FF9F5A" stop-opacity=".22"/>
<stop offset=".5" stop-color="#3D6FB0" stop-opacity=".08"/><stop offset="1" stop-color="#0A1830" stop-opacity="0"/></radialGradient>
<radialGradient id="core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="#FFF4E2" stop-opacity=".9"/>
<stop offset="1" stop-color="#FFB070" stop-opacity="0"/></radialGradient>
<linearGradient id="anam" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#9FD8FF" stop-opacity="0"/>
<stop offset=".5" stop-color="#F4FBFF" stop-opacity=".9"/><stop offset="1" stop-color="#9FD8FF" stop-opacity="0"/></linearGradient>
<radialGradient id="rimfall" cx="{FLARE[0]}" cy="{FLARE[1]}" r="820" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="#9a9a9a"/><stop offset="1" stop-color="#2a2a2a"/></radialGradient>
<radialGradient id="warmfall" cx="{FLARE[0]}" cy="{FLARE[1]}" r="190" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="rimMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#rimfall)"/></mask>
<mask id="warmMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#warmfall)"/></mask>
<filter id="b30" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="30"/></filter>
<filter id="b9" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="b3" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="2.6"/></filter>
<clipPath id="planetClip"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>
<linearGradient id="vfade" gradientUnits="userSpaceOnUse" x1="0" y1="300" x2="0" y2="352">
<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>
<radialGradient id="dayHole" cx="{FLARE[0]}" cy="{FLARE[1]}" r="230" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#000"/><stop offset=".6" stop-color="#000" stop-opacity=".6"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<mask id="cityMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
<rect width="{W}" height="{H}" fill="url(#vfade)"/><rect width="{W}" height="{H}" fill="url(#dayHole)"/></mask>
<linearGradient id="arcfade" gradientUnits="userSpaceOnUse" x1="470" y1="0" x2="640" y2="0">
<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="arcMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#arcfade)"/></mask>
<linearGradient id="streak" x1="0" x2="1"><stop offset="0" stop-color="#EAF4FF"/><stop offset="1" stop-color="#EAF4FF" stop-opacity="0"/></linearGradient>
<linearGradient id="plume1" x1="1" x2="0"><stop offset="0" stop-color="#FFFBEF"/><stop offset=".18" stop-color="#FFD27A"/>
<stop offset=".5" stop-color="{ORANGE}" stop-opacity=".75"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></linearGradient>
<linearGradient id="plume2" x1="1" x2="0"><stop offset="0" stop-color="#F5FBFF"/><stop offset=".3" stop-color="#A9DDFF" stop-opacity=".7"/>
<stop offset="1" stop-color="#6FB8FF" stop-opacity="0"/></linearGradient>
<radialGradient id="hot" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFC07A" stop-opacity=".85"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
<radialGradient id="cool" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#BFE6FF" stop-opacity=".7"/><stop offset="1" stop-color="#6FB8FF" stop-opacity="0"/></radialGradient>
<linearGradient id="nameFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#BFCDE6"/></linearGradient>
<linearGradient id="glint" gradientUnits="userSpaceOnUse" x1="0" y1="60" x2="140" y2="230">
<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".44" stop-color="#fff" stop-opacity="0"/>
<stop offset=".5" stop-color="#fff" stop-opacity=".85"/><stop offset=".56" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
<animateTransform attributeName="gradientTransform" type="translate" values="-420 0;640 0;640 0" keyTimes="0;.22;1" dur="6.5s" begin="1.9s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="laser" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".8" stop-color="{CYAN}" stop-opacity=".9"/><stop offset="1" stop-color="#fff"/></linearGradient>
""")
o("</defs>")

# ---------------------------------------------------------------- space
o(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
o(f'<g filter="url(#b30)" opacity=".9"><ellipse cx="300" cy="96" rx="280" ry="62" fill="#1C5A7A" opacity=".16"/>'
  f'<ellipse cx="560" cy="58" rx="300" ry="54" fill="#3A3580" opacity=".12"/>'
  f'<ellipse cx="900" cy="150" rx="200" ry="70" fill="#2B5E9A" opacity=".12"/></g>')


def star_layer(seed, count, rmin, rmax, omin, omax, dur, twinkle=0):
    r = rng(seed)
    base, tw_ = [], []
    for i in range(count):
        x, y = r.uniform(0, W), r.uniform(0, 362)
        rad = r.uniform(rmin, rmax) ** 1.0
        op = r.uniform(omin, omax)
        col = r.choices(["#FFFFFF", "#CFE3FF", "#FFE7CC"], [6, 3, 1])[0]
        if i < twinkle:
            tw_.append(f'<circle class="tw" style="animation-delay:-{n(r.uniform(0,3.2),1)}s" cx="{n(x,1)}" cy="{n(y,1)}" r="{n(rad*1.3,1)}" fill="{col}"/>')
        else:
            base.append(f'<circle cx="{n(x,1)}" cy="{n(y,1)}" r="{n(rad,1)}" fill="{col}" opacity="{n(op,1)}"/>')
    lid = f"sl{seed}"
    return (f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" dur="{dur}s" repeatCount="indefinite"/>'
            f'<g id="{lid}">' + "".join(base) + "".join(tw_) + f'</g><use href="#{lid}" x="{W}"/></g>')


o(star_layer(11, 170, .3, .85, .22, .7, 90, twinkle=12))
o(star_layer(23, 55, .7, 1.25, .45, .9, 32))
# velocity streaks (nearest layer)
r = rng(5)
st_ = []
for i in range(13):
    x, y = r.uniform(0, W), r.uniform(10, 330)
    ln = r.uniform(18, 74)
    h = r.uniform(.7, 1.3)
    op = r.uniform(.25, .6)
    st_.append(f'<rect x="{n(x,1)}" y="{n(y,1)}" width="{n(ln,1)}" height="{n(h,1)}" rx="{n(h/2,1)}" fill="url(#streak)" opacity="{n(op,1)}"/>')
o(f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" dur="3.6s" repeatCount="indefinite"/><g id="stk">{"".join(st_)}</g><use href="#stk" x="{W}"/></g>')

# sun bloom behind the limb
o(f'<circle cx="{FLARE[0]}" cy="{n(FLARE[1])}" r="300" fill="url(#sunglow)"/>')

# orbit reference arcs (Karman line + LEO)
o('<g mask="url(#arcMask)">')
o(f'<circle cx="{CX}" cy="{CY}" r="{n(RK)}" stroke="{CYAN}" stroke-opacity=".28" stroke-width=".9" stroke-dasharray="1.2 5"/>')
o(f'<circle cx="{CX}" cy="{CY}" r="{n(RL)}" stroke="{CYAN}" stroke-opacity=".42" stroke-width="1" stroke-dasharray="7 7">'
  f'<animate attributeName="stroke-dashoffset" from="0" to="-14" dur=".9s" repeatCount="indefinite"/></circle>')
o("</g>")


def arc_label(s, x, rr, size=9.2, fill=CYAN, op=.75):
    y = horizon(x, rr)
    ang = math.degrees(math.atan2(x - CX, math.sqrt(rr * rr - (x - CX) ** 2)))
    d, _ = st.font("mono").path(s, 0, -5, size, .16, "middle")
    return f'<path transform="translate({n(x)} {n(y)}) rotate({n(ang,3)})" d="{d}" fill="{fill}" fill-opacity="{op}"/>'


o(arc_label("KÁRMÁN LINE · 100 KM", 905, RK, op=.55))
o(arc_label("LEO · 408 KM", 925, RL, op=.8))

# ---------------------------------------------------------------- launch
# ignition bloom behind the horizon
o(f'<circle cx="{n(P0[0])}" cy="{n(horizon(P0[0]))}" r="34" fill="url(#hot)" opacity="0">'
  + kf("opacity", [(0, 0), (t0, 0), (t0 + .35, .9), (t_hz + .5, .5), (tM, 0)], T) + "</circle>")

# exhaust trail: diffuse sunlit plume + bright core, drawn progressively, ends at SECO
LS = 1000 * ps
trail = kf("stroke-dashoffset", [(0, 1000), (t0, 1000)] + [(t0 + DA * i / 40, n(1000 - 1000 * p_at(t0 + DA * i / 40), 3)) for i in range(1, 41)], T)
o('<g opacity="1">' + kf("opacity", [(0, 1), (FADE0, 1), (FADE1, 0)], T))
o(f'<path d="{TRAJ_D}" pathLength="1000" stroke="#A9DCFF" stroke-opacity=".13" stroke-width="3" stroke-linecap="round" stroke-dasharray="1000 1000" filter="url(#b3)">'
  + trail + kf("stroke-width", [(0, 3), (t0, 3), (FADE1, 16)], T) + "</path>")
o(f'<path d="{TRAJ_D}" pathLength="1000" stroke="#FFE6CC" stroke-opacity=".55" stroke-width="1.1" stroke-linecap="round" stroke-dasharray="1000 1000">' + trail + "</path>")
# hot tail riding with the craft
tail = kf("stroke-dashoffset", [(0, 70), (t0, 70)] + [(t0 + DA * i / 40, n(70 - 1000 * p_at(t0 + DA * i / 40), 3)) for i in range(1, 41)], T)
o(f'<path d="{TRAJ_D}" pathLength="1000" stroke="{WARM}" stroke-width="2.1" stroke-linecap="round" stroke-dasharray="70 3000">'
  + tail + kf("opacity", [(0, 1), (tM, 1), (tM + .05, 0), (tIGN, 0), (tIGN + .08, 1), (tS, 1), (tS + .25, 0)], T) + "</path>")
o("</g>")

# spent first stage tumbling away
ca, sa = math.cos(math.radians(angM)), math.sin(math.radians(angM))
S0 = (PM[0] - 6.5 * ca, PM[1] - 6.5 * sa)
S1 = (S0[0] + 16 * ca + 4, S0[1] + 16 * sa)
S2 = (S0[0] + 20, S0[1] + 58)
o(f'<g opacity="0">{vis(tSEP, tSEP + 2.4)}'
  f'<g><animateMotion dur="{T}s" repeatCount="indefinite" calcMode="spline" path="M{n(S0[0])} {n(S0[1])}Q{n(S1[0])} {n(S1[1])} {n(S2[0])} {n(S2[1])}" '
  f'keyPoints="0;0;1;1" keyTimes="0;{n(tSEP/T,5)};{n((tSEP+2.4)/T,5)};1" keySplines="0 0 1 1;.3 0 .7 1;0 0 1 1"/>'
  f'<g transform="rotate({n(angM)})"><g>'
  f'<animateTransform attributeName="transform" type="rotate" dur="{T}s" repeatCount="indefinite" values="0;0;230;230" keyTimes="0;{n(tSEP/T,5)};{n((tSEP+2.4)/T,5)};1"/>'
  f'<rect x="-6.4" y="-1.7" width="12.8" height="3.4" rx=".6" fill="#C9D4E6"/><rect x="5.6" y="-1.7" width=".9" height="3.4" fill="#5B6B85"/>'
  f"</g></g></g></g>")

# the vehicle
o(f'<g><animateMotion dur="{T}s" repeatCount="indefinite" path="{TRAJ_D}" rotate="auto" calcMode="spline" {kp} {ks}/>')
# stage-1 plume + glow
o(f'<g>{kf("opacity", [(0, 1), (tM, 1), (tM + .03, 0)], T, mode="discrete")}'
  f'<circle cx="-15" cy="0" r="17" fill="url(#hot)"/>'
  f'<path class="fl" d="M-13 -1.6C-22 -3.4 -34 -2.6 -46 0C-34 2.6 -22 3.4 -13 1.6Z" fill="url(#plume1)"/></g>')
# stage-2 vacuum plume (wider, bluer)
o(f'<g opacity="0">{vis(tIGN, tS)}'
  f'<circle cx="-2" cy="0" r="13" fill="url(#cool)"/>'
  f'<path class="fl" d="M-.6 -1.3C-8 -5.5 -18 -6.5 -26 0C-18 6.5 -8 5.5 -.6 1.3Z" fill="url(#plume2)"/></g>')
# airframe
o(f'<g>{vis(0, tSEP)}<rect x="-13" y="-1.7" width="12.4" height="3.4" rx=".6" fill="#DCE5F4"/>'
  f'<rect x="-12.2" y="-2.6" width="1.4" height="5.2" rx=".4" fill="#9AA8BF"/></g>')
o('<rect x="-.7" y="-1.65" width=".9" height="3.3" fill="#56657E"/>'
  '<path d="M.2 -1.6H7.2C9.6 -1.6 11.4 -.8 12.6 0C11.4 .8 9.6 1.6 7.2 1.6H.2Z" fill="#F2F6FF"/>')
o('<circle cx="4" cy="0" r="7" fill="url(#cool)" opacity=".55"/>')
o('<circle cx="5" cy="0" r="8" fill="url(#cool)" opacity=".5"/>')
o(f'<circle class="strobe" cx="3.5" cy="-2.6" r="1" fill="#fff" opacity="0">{vis(tS)}</circle>')
o("</g>")


# the Moon, lit from the sunrise side, with an acquisition reticle
MX, MY, MR = 880, 112, 13
sx_, sy_ = FLARE[0] - MX, FLARE[1] - MY
sl = math.hypot(sx_, sy_)
ux, uy = sx_ / sl, sy_ / sl
o(f'<mask id="moonLit" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><circle cx="{MX}" cy="{MY}" r="{MR}" fill="#fff"/>'
  f'<circle cx="{n(MX - ux*MR*.62)}" cy="{n(MY - uy*MR*.62)}" r="{MR}" fill="#000"/></mask>')
o(f'<radialGradient id="moonG" cx="{n(MX+ux*MR*.5)}" cy="{n(MY+uy*MR*.5)}" r="{MR*1.6}" gradientUnits="userSpaceOnUse">'
  f'<stop offset="0" stop-color="#FFF6E8"/><stop offset="1" stop-color="#A9B6CC"/></radialGradient>')
o(f'<circle cx="{MX}" cy="{MY}" r="{MR*2.2}" fill="url(#cool)" opacity=".12"/>')
o(f'<circle cx="{MX}" cy="{MY}" r="{MR}" fill="#16202F" fill-opacity=".9"/>')
o(f'<circle cx="{MX}" cy="{MY}" r="{MR}" fill="url(#moonG)" mask="url(#moonLit)"/>')
rk = []
for ang in (45, 135, 225, 315):
    rk.append(f'<path transform="rotate({ang} {MX} {MY})" d="M{MX+22} {MY-5}V{MY}H{MX+27}" stroke="{CYAN}" stroke-width="1" stroke-opacity=".7" fill="none"/>')
o(f'<g transform="translate({MX} {MY})"><g><animateTransform attributeName="transform" type="scale" values="1.6;1;1;1.6" keyTimes="0;.07;.9;1" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines=".16 1 .3 1;0 0 1 1;.7 0 .84 0"/>'
  f'<g transform="translate({-MX} {-MY})">' + "".join(rk) + '</g></g></g>')
p_, _ = text("MOON · 384,400 KM", MX - 36, MY + 3.5, 9, tracking=.16, anchor="end", fill=CYAN, extra='fill-opacity=".6"')
o(p_)

# ---------------------------------------------------------------- planet
o(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#planet)"/>')
# night-side city lights, two parallax bands sliding beneath the orbit
o(f'<g clip-path="url(#planetClip)"><g mask="url(#cityMask)">')
for seed, ymin, ymax, rr, dur, cnt in [(41, 306, 352, (.35, .7), 46, 26), (57, 340, 420, (.55, 1.15), 19, 22)]:
    r = rng(seed)
    dots = []
    for c in range(cnt):
        cx_, cy_ = r.uniform(0, W), r.uniform(ymin, ymax)
        k = r.randint(3, 11)
        for _ in range(k):
            x = cx_ + r.gauss(0, 9)
            y = cy_ + r.gauss(0, 2.4 if ymax < 360 else 4)
            rad = r.uniform(*rr)
            op = r.uniform(.25, .8)
            dots.append(f'<circle cx="{n(x % W,1)}" cy="{n(y,1)}" r="{n(rad,1)}" opacity="{n(op,1)}"/>')
    o(f'<g fill="#FFC27A"><animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" dur="{dur}s" repeatCount="indefinite"/>'
      f'<g id="city{seed}">{"".join(dots)}</g><use href="#city{seed}" x="{W}"/></g>')
o("</g></g>")

# atmosphere: layered limb glow, brightest toward the sunrise
o('<g mask="url(#rimMask)">')
o(f'<circle cx="{CX}" cy="{CY}" r="{R+4}" stroke="#2F8CFF" stroke-opacity=".35" stroke-width="22" filter="url(#b9)"/>')
o(f'<circle cx="{CX}" cy="{CY}" r="{R+1.5}" stroke="#56B4FF" stroke-opacity=".7" stroke-width="5" filter="url(#b3)"/>')
o(f'<circle cx="{CX}" cy="{CY}" r="{R}" stroke="#D2EEFF" stroke-width="1.3"/>')
o("</g>")
o(f'<g mask="url(#warmMask)"><circle cx="{CX}" cy="{CY}" r="{R+2}" stroke="#FFB874" stroke-width="4" filter="url(#b3)"/>'
  f'<circle cx="{CX}" cy="{CY}" r="{R}" stroke="#FFE7CC" stroke-width="1.4"/></g>')

# sun cresting the limb
fx, fy = FLARE
o(f'<circle cx="{fx}" cy="{n(fy)}" r="46" fill="url(#core)" opacity=".9"/>')
o(f'<circle cx="{fx}" cy="{n(fy)}" r="3.2" fill="#fff"/>')
o(f'<ellipse class="anam" cx="{fx}" cy="{n(fy)}" rx="330" ry="1.6" fill="url(#anam)"/>')
o(f'<ellipse class="anam" style="animation-delay:-1.7s" cx="{fx}" cy="{n(fy)}" rx="170" ry="3.2" fill="url(#anam)" opacity=".45"/>')

# ---------------------------------------------------------------- mission events
def event(pt, t_on, label, lx, ly, color=CYAN):
    x, y = pt
    s = [f'<g opacity="0">{kf("opacity", [(0, 0), (t_on, 0), (t_on + .2, 1), (FADE0, 1), (FADE1, 0)], T)}']
    s.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="2" stroke="{color}" stroke-width="1">'
             + kf("r", [(0, 2), (t_on, 2), (t_on + .7, 13)], T) + kf("stroke-opacity", [(0, 1), (t_on, 1), (t_on + .7, 0)], T) + "</circle>")
    s.append(f'<path d="M{n(x)} {n(y)}L{n(lx)} {n(ly)}H{n(lx + tw(label, 9.5, tracking=.14) + 8)}" stroke="{color}" stroke-opacity=".55" stroke-width=".8"/>')
    p, _ = text(label, lx + 4, ly - 4.5, 9.5, tracking=.14, fill=color)
    s.append(p + "</g>")
    return "".join(s)


PS_ = poly.at(Lb)[0]
o(event(PM, tM, "MECO · STAGE SEP", PM[0] + 26, PM[1] - 12))
o(event(PS_, tS, "SECO · ORBIT INSERTION", PS_[0] + 6, PS_[1] - 30))

# ---------------------------------------------------------------- HUD
o(corner_brackets(W, H))
# top-left call sign
o(f'<path d="M60 58l5 -5l5 5l-5 5z" fill="{ACCENT}"/>')
p, _ = text("#NHashJP", 78, 62, 11, tracking=.16, fill=ACCENT_HI)
o(p)

# name with laser-etch reveal + periodic glint
NAME_X = 58
lines = [("NAOKI", 140), ("HASHIMOTO", 210)]
size = 70
name_paths = []
for i, (s, y) in enumerate(lines):
    d, w = st.font("display").path(s, NAME_X, y, size, -0.01)
    name_paths.append((d, w, y, i))
for d, w, y, i in name_paths:
    b = .15 + i * .22
    # base state is fully visible (static renderers show the name); animation wipes it in
    o(f'<clipPath id="rv{i}"><rect x="{NAME_X-4}" y="{y-60}" width="{n(w+10)}" height="72">'
      f'<animate attributeName="width" values="0;0;{n(w+10)}" keyTimes="0;{n(b/(b+1.05),4)};1" dur="{n(b+1.05)}s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;.16 1 .3 1"/></rect></clipPath>')
    o(f'<defs><path id="nm{i}" d="{d}"/></defs><g clip-path="url(#rv{i})"><use href="#nm{i}" fill="url(#nameFill)"/><use href="#nm{i}" fill="url(#glint)"/></g>')
    o(f'<rect x="{NAME_X-4}" y="{y-58}" width="26" height="66" fill="url(#laser)" opacity="0">'
      f'<animate attributeName="x" from="{NAME_X-30}" to="{n(NAME_X+w-16)}" begin="{b}s" dur="1.05s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".16 1 .3 1"/>'
      f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.6;1" begin="{b}s" dur="1.05s" fill="freeze"/></rect>')

# role + chips
o(f'<g><animate attributeName="opacity" values="0;0;1" keyTimes="0;.59;1" dur="1.45s" fill="freeze"/>'
  f'<animateTransform attributeName="transform" type="translate" values="0 8;0 8;0 0" keyTimes="0;.59;1" dur="1.45s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;.16 1 .3 1"/>')
p, _ = text("JUNIOR SOFTWARE & AEROSPACE ENGINEER", NAME_X + 2, 248, 13, tracking=.2, fill=INK, extra='fill-opacity=".92"')
o(p)
cx_ = NAME_X + 2
for i, lab in enumerate(["FULL-STACK", "ROBOTICS", "AEROSPACE", "EN · ES · JA · CA"]):
    wl = tw(lab, 10.5, tracking=.14)
    col = ACCENT if i < 3 else CYAN
    o(f'<rect x="{n(cx_)}" y="264" width="{n(wl+20)}" height="22" rx="11" stroke="{col}" stroke-opacity=".6" fill="{col}" fill-opacity=".06"/>')
    p, _ = text(lab, cx_ + 10, 278.8, 10.5, tracking=.14, fill=INK)
    o(p)
    cx_ += wl + 30
o("</g>")

# top-right status
lab = "LIVE TELEMETRY"
wl = tw(lab, 10, tracking=.2)
p, _ = text(lab, 960, 62, 10, tracking=.2, anchor="end", fill=CYAN, extra='fill-opacity=".85"')
o(f'<circle class="blink" cx="{n(960-wl-12)}" cy="58.6" r="3.2" fill="{ACCENT}"/>' + p)

# telemetry panel (values derived from the animation itself)
PX, PY, PW, PH = 770, 330, 196, 74
o(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="4" fill="#03060C" fill-opacity=".72" stroke="{HUD}" stroke-width=".8"/>')
o(f'<path d="M{PX} {PY+8}V{PY}H{PX+8}M{PX+PW-8} {PY+PH}H{PX+PW}V{PY+PH-8}" stroke="{CYAN}" stroke-width="1.2"/>')
LX, VX = PX + 12, PX + 62
rows = [PY + 19, PY + 35, PY + 51, PY + 67]
for lab_, y in zip(["MET", "PHASE", "ALT", "VEL"], rows):
    p, _ = text(lab_, LX, y, 10, tracking=.14, fill=DIM)
    o(p)

# MET odometer: real elapsed time since the page loaded
f = st.font("mono")
CW = f.width("0", 11)
y = rows[0]
xx = VX
hh = 15


def roller(x, nd, period, roll=.2):
    """digit strip rolling 0..nd-1, one step every `period` seconds"""
    d_parts = []
    for k in range(nd + 1):
        dd, _ = f.path(str(k % nd), x, y + k * hh, 11)
        d_parts.append(dd)
    T_ = nd * period
    vals, kts, sps = [], [], []
    for k in range(nd):
        vals += [f"0 {-k*hh}", f"0 {-k*hh}"]
        kts += [k / nd, (k + 1 - roll / period) / nd]
        sps += ["0 0 1 1", ".5 0 .2 1"]
    vals.append(f"0 {-nd*hh}")
    kts.append(1)
    return (f'<g clip-path="url(#odo)"><g><animateTransform attributeName="transform" type="translate" dur="{n(T_)}s" repeatCount="indefinite" '
            f'calcMode="spline" values="{";".join(vals)}" keyTimes="{";".join(n(k_,6) for k_ in kts)}" keySplines="{";".join(sps)}"/>'
            f'<path d="{" ".join(d_parts)}" fill="{INK}"/></g></g>')


o(f'<clipPath id="odo"><rect x="{VX-2}" y="{y-11}" width="80" height="14"/></clipPath>')
p, _ = text("00:", xx, y, 11, fill=INK)
o(p)
xx += CW * 3
o(roller(xx, 6, 600))
xx += CW
o(roller(xx, 10, 60))
xx += CW
p, _ = text(":", xx, y, 11, fill=INK)
o(p)
xx += CW
o(roller(xx, 6, 10))
xx += CW
o(roller(xx, 10, 1))

# phase
phases = [(0, t_hz, "IGNITION", WARM), (t_hz, tM, "ASCENT", INK), (tM, tIGN, "MECO / SEP", WARM),
          (tIGN, tS, "STAGE 2 BURN", INK), (tS, T, "ORBIT NOMINAL", ACCENT_HI)]
for a, b, lab_, col in phases:
    p, _ = text(lab_, VX, rows[1], 11, fill=col, extra=f'opacity="{1 if a == 0 else 0}"')
    o(p.replace("/>", ">" + vis(a, b) + "</path>"))

# ALT / VEL sampled from the actual trajectory + speed profile (digits via glyph sprite)
SP = Sprite("mono", 11, "g")
for val, row, k in [("KM", rows[2], 6), ("KM/S", rows[3], 5)]:
    o(SP.use(val, VX + SP.adv("0") * k, row, fill=INK))
samples = sorted(set([0.0, tM, tIGN, tS] + [t_hz + i * .34 for i in range(0, 60) if t_hz + i * .34 < tS]))
for i, t in enumerate(samples):
    a = t if i else 0
    b = samples[i + 1] if i + 1 < len(samples) else T
    pt, _ = poly.at(p_at(t) * L)
    alt = alt_km(pt) if t > t0 else 0
    v = vel(t)
    if t >= tS:
        alt, v = 408.0, 7.66
    for val, row in [(f"{alt:05.1f}", rows[2]), (f"{v:4.2f}", rows[3])]:
        g = SP.use(val, VX, row, fill=INK, extra=f'opacity="{1 if a == 0 else 0}"')
        o(g[:-4] + vis(a, b) + "</g>")
o("<defs>" + SP.defs_svg() + "</defs>")

o("</svg>")
svg = "".join(out)
open(os.path.join(OUT_DIR, "hero.svg"), "w").write(svg)
print("hero.svg", len(svg) // 1024, "KB", "T=", T, "tM", round(tM, 2), "tS", round(tS, 2), "tE", round(tE, 2), "ps", round(ps, 3))
