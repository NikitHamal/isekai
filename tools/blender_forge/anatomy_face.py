#!/usr/bin/env python3
"""Sculpted humanoid head: lofted skull + jaw, bmesh-sculpted eye sockets & brow, nose, lips, ears, layered anime eyes, brows, hair clumps."""
import math, random
from mathutils import Vector as V
from anatomy_core import *

HEAD_Z = 1.70   # eye line (reference 1.82 m body)

def build_head(skin, eye_rgb=(0.15, 0.55, 0.85), hs=1.0, jaw=1.0, ear=0.0, brow=1.0, nose=1.0, pivot=(0, 0, 1.53), lip_rgb=(0.62, 0.30, 0.28), lash=True, tusk=0.0, cheek=1.0, nm="head"):
    """Returns dict of created objects. hs scales head about the neck; jaw>1 = heavier jaw; ear>0 = pointed ear length."""
    pv = V(pivot); o = {}
    def Z(z): return pv.z + (z - pv.z) * hs
    def R(r): return r * hs
    secs = [  # z, rx, ry, cy, power
        (1.545, .050, .054, .006, 2), (1.575, .034 * jaw, .042, -.004, 2), (1.590, .056 * jaw, .062, -.012, 2.2), (1.612, .074 * jaw * cheek, .078, -.004, 2.3), (1.640, .084 * cheek, .090, .003, 2.3),
        (1.675, .090, .097, .008, 2.2), (1.715, .092, .100, .010, 2.1), (1.750, .089, .099, .012, 2.0), (1.785, .077, .090, .016, 2.0), (1.810, .052, .068, .020, 2.0), (1.828, .022, .033, .022, 2.0)]
    S = [(V((0, c, Z(z))), R(rx), R(ry), pw) for (z, rx, ry, c, pw) in secs]
    S = [(V((0, V(s[0]).y * hs, V(s[0]).z)), s[1], s[2], s[3]) for s in S]
    head = loft(nm + "_skull", S, skin, segs=24, tile=0.4, sub=1, pivot=pv)
    def sock(p):   # sculpt eye sockets, brow ridge, cheekbones, nose bridge + chin (world coords)
        d = V((0, 0, 0)); x, y, z = p.x, p.y, p.z
        if y < -0.03:
            for sx in (-1, 1):
                dx = (x - sx * 0.036 * hs) / (0.026 * hs); dz = (z - Z(HEAD_Z + 0.005)) / (0.020 * hs); f = max(0, 1 - (dx * dx + dz * dz)); d.y += 0.012 * f * f * hs
            bz = (z - Z(1.748)) / (0.012 * hs); fb = max(0, 1 - bz * bz) * max(0, 1 - abs(x) / (0.075 * hs)); d.y -= 0.011 * brow * fb * hs
            cz = (z - Z(1.655)) / (0.022 * hs); cx = (abs(x) - 0.062 * hs) / (0.024 * hs); fc = max(0, 1 - cz * cz - cx * cx); d.y -= 0.007 * cheek * fc
            nb = max(0, 1 - abs(x) / (0.012 * hs)) * max(0, 1 - ((z - Z(1.715)) / (0.028 * hs)) ** 2); d.y -= 0.007 * nose * nb
            ch = max(0, 1 - abs(x) / (0.022 * hs)) * max(0, 1 - ((z - Z(1.582)) / (0.016 * hs)) ** 2); d.y -= 0.007 * jaw * ch
        return d
    sculpt(head, sock); o["skull"] = head
    # neck with trapezius flare
    neck = loft(nm + "_neck", [(V((0, .004, 1.46)), .082, .070), (V((0, .004, 1.50)), .062, .062), (V((0, .006, Z(1.56))), .052 * hs, .056 * hs), (V((0, .008, Z(1.60))), .048 * hs, .054 * hs)], skin, segs=14, sub=1, pivot=pv, caps=(False, False))
    o["neck"] = neck
    # nose: bridge + tip + nostril wings
    ny = -0.088 * hs
    nose_o = tube(nm + "_nose", [V((0, ny + .006, Z(1.722))), V((0, ny - .010 * nose, Z(1.694))), V((0, ny - .026 * nose, Z(1.667))), V((0, ny - .024 * nose, Z(1.655)))], [.0042 * hs, .0075 * hs, .0098 * hs * nose, .0105 * hs], skin, segs=8, flat=0.95, sub=1, pivot=pv)
    o["nose"] = nose_o
    for sx in (-1, 1):
        o["nostril%d" % sx] = prim(nm + "_nostril%s" % ("l" if sx > 0 else "r"), "sphere", skin, (.0065 * hs, .0075 * hs, .0065 * hs), (sx * .0125 * hs, ny - .016 * nose, Z(1.656)), sub=1, segs=10, pivot=pv)
    # lips + mouth line
    lipm = material("lip", "skin", lip_rgb, n=256, seed=9, rough=0.4)
    mouth = material("mouth_dark", "plain", (0.08, 0.02, 0.025), n=128, rough=0.5)
    my = -0.082 * hs
    o["mouth"] = tube(nm + "_mouthline", [V((-.027 * hs, my + .004, Z(1.617))), V((0, my - .004, Z(1.6155))), V((.027 * hs, my + .004, Z(1.617)))], [.0032] * 3, mouth, segs=6, flat=.8, sub=0, pivot=pv)
    o["lip_u"] = tube(nm + "_lipup", [V((-.026 * hs, my + .005, Z(1.621))), V((-.01 * hs, my - .005, Z(1.623))), V((0, my - .0065, Z(1.622))), V((.01 * hs, my - .005, Z(1.623))), V((.026 * hs, my + .005, Z(1.621)))], [.0030, .0050, .0045, .0050, .0030], lipm, segs=8, flat=.7, sub=1, pivot=pv)
    o["lip_l"] = tube(nm + "_liplow", [V((-.022 * hs, my + .005, Z(1.610))), V((-.008 * hs, my - .004, Z(1.6085))), V((.008 * hs, my - .004, Z(1.6085))), V((.022 * hs, my + .005, Z(1.610)))], [.0030, .0058, .0058, .0030], lipm, segs=8, flat=.7, sub=1, pivot=pv)
    # ears (flattened ellipsoids, optionally elven / goblin pointed)
    for sx in (-1, 1):
        sd = "l" if sx > 0 else "r"
        e = prim(nm + "_ear" + sd, "sphere", skin, (.011 * hs, .022 * hs, .034 * hs), (sx * .094 * hs, .012 * hs, Z(1.685)), rot=(0, sx * .25, 0), sub=1, segs=12, pivot=pv); o["ear" + sd] = e
        if ear > 0:
            o["earp" + sd] = tube(nm + "_earpoint" + sd, [V((sx * .095 * hs, .014 * hs, Z(1.69))), V((sx * (.095 + ear * .5) * hs, .02 * hs, Z(1.72 + ear * .3))), V((sx * (.095 + ear) * hs, .03 * hs, Z(1.76 + ear * .7)))], [.014 * hs, .009 * hs, .0015 * hs], skin, segs=8, flat=.4, sub=1, pivot=pv)
    # layered anime eyes: sclera, iris (radial gradient), pupil, catch-light, brows, upper lash line
    white = material("eye_white", "plain", (.94, .93, .91), n=128, rough=.18)
    iris = material("eye_iris_%d" % int(sum(eye_rgb) * 255), "glow", eye_rgb, n=128, rough=.12, emit=tuple(c * 0.25 for c in eye_rgb), emit_str=0.6)
    black = material("eye_pupil", "plain", (.01, .01, .012), n=64, rough=.1)
    shine = material("eye_shine", "glow", (1, 1, 1), n=64, rough=.05, emit=(1, 1, 1), emit_str=1.4)
    brw = material("brow", "hair", (.05, .04, .04), n=256, rough=.5)
    for sx in (-1, 1):
        sd = "l" if sx > 0 else "r"; ex = sx * .036 * hs; ez = Z(HEAD_Z + .004); ey = -.0645 * hs
        o["eye" + sd] = prim(nm + "_eyeball" + sd, "sphere", white, (.0150 * hs,) * 3, (ex, ey, ez), sub=1, segs=14, pivot=pv)
        o["iris" + sd] = prim(nm + "_iris" + sd, "sphere", iris, (.0105 * hs, .0046 * hs, .0125 * hs), (ex, ey - .0132 * hs, ez - .0004), sub=1, segs=14, pivot=pv)
        o["pupil" + sd] = prim(nm + "_pupil" + sd, "sphere", black, (.0054 * hs, .0030 * hs, .0070 * hs), (ex, ey - .0158 * hs, ez), sub=0, segs=10, pivot=pv)
        o["shine" + sd] = prim(nm + "_shine" + sd, "sphere", shine, (.0030 * hs, .0018 * hs, .0034 * hs), (ex + sx * -.0038 * hs, ey - .0172 * hs, ez + .0062 * hs), sub=0, segs=8, pivot=pv)
        o["brow" + sd] = tube(nm + "_brow" + sd, [V((sx * .016 * hs, -.0875 * hs * 0 + ey - .014 * hs, Z(1.742))), V((sx * .038 * hs, ey - .0165 * hs, Z(1.7475 + .004 * brow))), V((sx * .062 * hs, ey - .006 * hs, Z(1.7405)))], [.0036, .0050, .0020], brw, segs=6, flat=.55, sub=1, pivot=pv)
        if lash:
            o["lash" + sd] = tube(nm + "_lash" + sd, [V((ex - sx * .0175 * hs, ey - .006 * hs, ez + .0035)), V((ex - sx * .005 * hs, ey - .0125 * hs, ez + .0145 * hs)), V((ex + sx * .011 * hs, ey - .0115 * hs, ez + .0135 * hs)), V((ex + sx * .0185 * hs, ey - .003 * hs, ez + .0035))], [.0014, .0034, .0030, .0020], black, segs=6, flat=.7, sub=1, pivot=pv)
    if tusk > 0:
        bone = material("tusk", "bone", (.9, .85, .7), n=256, rough=.5)
        for sx in (-1, 1):
            o["tusk%d" % sx] = tube(nm + "_tusk" + ("l" if sx > 0 else "r"), [V((sx * .028 * hs, -.074 * hs, Z(1.597))), V((sx * .034 * hs, -.092 * hs, Z(1.612))), V((sx * .036 * hs, -.098 * hs, Z(1.648 + tusk * .5)))], [.0075, .0065, .0014], bone, segs=8, sub=1, pivot=pv)
    return o

def hair_clumps(color, locks, pivot=(0, 0, 1.53), hs=1.0, nm="head_hair", seed=3, cap=True, kind="hair"):
    """locks: list of dicts(root=(x,y,z), dirs=[(dx,dy,dz)...], length, r, curl) -> tapered flattened tubes (anime spikes)."""
    pv = V(pivot); mat = material("hair_" + str(int(sum(color) * 255)), kind, color, n=512, seed=5, rough=.35); out = []
    if cap:
        pts = [(V((0, .020 * hs, 1.826)), .028, .038), (V((0, .018 * hs, 1.80)), .072, .084), (V((0, .012 * hs, 1.765)), .098, .108), (V((0, .016 * hs, 1.72)), .1, .11), (V((0, .024 * hs, 1.66)), .088, .1)]
        out.append(loft(nm + "_cap", pts, mat, segs=22, tile=.3, sub=1, pivot=pv, solid=.006, keep=lambda c: not (c.y < 0.0 and c.z < 1.775 + (0.0 if abs(c.x) > 0.055 else 0.015)) and not (c.z < 1.69 and c.y < 0.03) and c.z > 1.665, caps=(False, False)))
    for L in locks:
        r0 = L.get("r", .014); p = V(L["root"]); pts = [p]; d = V(L["dir"]).normalized(); ln = L.get("length", .12); n = L.get("n", 5); curl = V(L.get("curl", (0, 0, -0.5)))
        for i in range(n - 1):
            d = (d + curl * (1.0 / n)).normalized(); p = p + d * (ln / (n - 1)); pts.append(p.copy())
        rad = [r0 * (1 - (i / (n - 1)) ** 1.3 * .96) + .0006 for i in range(n)]
        out.append(tube(nm + "_lock", pts, rad, mat, segs=6, flat=.55, sub=0, pivot=pv, caps=(True, True)))
    return [join(out[1:] if cap else out, nm + "_locks")] + (out[:1] if cap else [])
