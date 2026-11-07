#!/usr/bin/env python3
"""Sir Garrick, Royal Paladin - SDF-sculpted heroic body fitted with full plate (offset-shell armour with keel ridges, layered pauldrons, gauntlets,
cuisses, greaves, sabatons), plumed open helm, royal tabard, flared cloak, longsword and heater shield.  Pipeline: SDF -> marching cubes -> Blender
Smart UV -> PBR bake -> official glTF export with the engine's articulated part objects."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sdf_core import *
import sdf_core
sdf_core.H_SCALE = 1.3
import sdf_humanoid as hu, sdf_mats as sm
from sdf_bake import Model, noise
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def build(out):
    h = 1.92; f, J, hd = hu.humanoid(h=h, sh=.235, chest=(.2, .13), belly=0., arm=1.08, leg=1.05, mus=1.2, hunch=0., hs=.96, neck=1.1, jaw=1.1, brow=.9, nose=1.0, chin=1.15, cheek=1.0)
    s = J["s"]; k = s * .96; M = Model("pal", hu.pivots(J), tex=1024); hc = J["headc"]
    skin = sm.skin("pal_skin", (.86, .67, .55), (.72, .52, .42), (.93, .77, .67), pore=.5, wrinkle=.15, rough=.5, nstr=.6)
    hu.skin_pieces(M, f, hd, J, skin, (A(-.75, -.5, -.02), A(.75, .45, 2.1)), hb=.0155, hf=.0052)
    F = J["F"]; segs = J["segs"]; HC = J["HC"]
    eye = sm.eye("pal_eye", (hc[0] + .036 * k, hc[1] - .088 * k, hc[2] + .008 * k), (0, -1, 0), (.25, .5, .85)); hu.eyes_teeth(M, J, eye, k, False)
    steel = sm.metal("pal_steel", (.74, .76, .80), rough=.3, dent=.4); gold = sm.metal("pal_gold", (.95, .72, .25), rough=.3, dent=.2); blue = sm.cloth("pal_tabard", (.08, .16, .44), (.12, .22, .55), weave=70)
    red = sm.cloth("pal_cloak", (.52, .05, .08), (.34, .03, .06), weave=55); leather = sm.leather("pal_leather", (.25, .15, .08))
    sh_ = J["sh_l"][0]
    R = lambda fn, d, lo, hi, hh, keep, steel_=steel, rd=None, amp=.004: M.add(hu.shell(F, d, lo, hi, hh, keep, ridges=rd, amp=amp), steel_, segs=segs)
    z = lambda c: c[:, 2] / s
    R(F, .024 * s, A(-.4, -.3, 1.1) * s, A(.4, .3, 1.6) * s, .0135, lambda c: (z(c) > 1.09) & (z(c) < 1.55) & (np.abs(c[:, 0]) < sh_ - .03 * s), rd=lambda P: np.exp(-(P[:, 0] / .022) ** 2) * (P[:, 1] < J["waist"][1]) - .3 * (np.sin(P[:, 2] * 55) > .8), amp=.011)
    R(F, .03 * s, A(-.4, -.3, .82) * s, A(.4, .3, 1.15) * s, .0135, lambda c: (z(c) > .86) & (z(c) < 1.14), rd=lambda P: np.sin(P[:, 2] * 70 / s) * .5 + .5, amp=.004)
    R(F, .018 * s, A(-.2, -.2, 1.48) * s, A(.2, .2, 1.62) * s, .008, lambda c: (z(c) > 1.455) & (z(c) < 1.52) & (np.abs(c[:, 0]) < .12 * s), steel_=gold)
    for sd, sn in ((1, "l"), (-1, "r")):
        S_, E, W = J["sh_" + sn], J["el_" + sn], J["wr_" + sn]; ax = W - E; L2 = float(ax @ ax)
        pk = lambda c, S_=S_, sd=sd: (np.linalg.norm(c - S_, axis=1) < .18 * s) & (c[:, 2] > S_[2] - .02 * s) & ((c[:, 0] - S_[0]) * sd > -.05 * s)
        R(F, .046 * s, *hu.bb([S_], .26 * s), .0125, pk, rd=lambda P: (np.sin(P[:, 2] * 90 / s) > .6) * 1.0, amp=.006)
        R(F, .02 * s, *hu.bb([E, W], .14 * s), .0105, lambda c, E=E, ax=ax, L2=L2: (((c - E) @ ax) / L2 > .1) & (((c - E) @ ax) / L2 < .9) & (np.linalg.norm(c - E, axis=1) < .36 * s))
        R(F, .02 * s, *hu.bb([E], .12 * s), .0095, lambda c, E=E: (np.linalg.norm(c - E, axis=1) < .075 * s), steel_=gold)   # couter
        M.add(hu.shell(F, .013 * s, *hu.bb([HC[sn]], .16 * s), .0075, lambda c, h_=HC[sn]: np.linalg.norm(c - h_, axis=1) < .105 * s), steel, segs=segs)   # gauntlet
    R(F, .026 * s, A(-.3, -.25, .5) * s, A(.3, .25, .95) * s, .0135, lambda c: (z(c) > .53) & (z(c) < .93) & (np.abs(c[:, 0]) > .03 * s), rd=lambda P: np.exp(-((P[:, 2] / s - .74) / .05) ** 2) * .5, amp=.006)
    R(F, .022 * s, A(-.25, -.25, .08) * s, A(.25, .2, .55) * s, .0115, lambda c: (z(c) > .11) & (z(c) < .53) & (np.abs(c[:, 0]) > .02 * s))
    R(F, .026 * s, A(-.25, -.3, -.02) * s, A(.25, .2, .14) * s, .0105, lambda c: z(c) < .12)
    for sx in (-1, 1): R(F, .034 * s, A(sx * .09 - .08, -.2, .4) * s, A(sx * .09 + .08, .1, .6) * s, .0105, lambda c, sx=sx: (np.linalg.norm(c - A(sx * .092 * s, -.012 * s, .5 * s), axis=1) < .075 * s) & (c[:, 1] < 0), steel_=gold)   # poleyns
    M.add(hu.shell(F, .03 * s, A(-.3, -.3, .56) * s, A(.3, .1, 1.2) * s, .0125, lambda c: (z(c) > .62) & (z(c) < 1.02) & (c[:, 1] < J["waist"][1] - .04 * s) & (np.abs(c[:, 0]) < .17 * s)), blue, segs=segs)   # tabard
    M.add(extract(U([ell(A(0, J["waist"][1] + .13 * s, 1.34 * s), (.25 * s, .028 * s, .30 * s)), ell(A(0, J["waist"][1] + .2 * s, .86 * s), (.33 * s, .035 * s, .44 * s)), ell(A(0, J["waist"][1] + .26 * s, .45 * s), (.30 * s, .03 * s, .18 * s))], .09 * s), A(-.45, -.1, .2) * s, A(.45, .5, 1.7) * s, .011), red, part="cloak")
    hk = lambda c: (z(c) > (hc[2] / s + .018 * k / s)) & (c[:, 1] > hc[1] - .055 * k)
    M.add(hu.shell(F, .02 * k, *hu.bb([hc], .2 * k), .0075, lambda c: hk(c) | ((c[:, 2] > hc[2] - .02 * k) & (c[:, 1] > hc[1] + .03 * k))), steel, segs=segs)   # helm + cheek-less back
    p0 = A(0, hc[1] - .01 * k, hc[2] + .115 * k); p1 = A(0, hc[1] + .13 * k, hc[2] + .115 * k); p2 = A(0, hc[1] + .26 * k, hc[2] + .02 * k)
    M.add(extract(U([cap(p0, p1, .012 * k, .028 * k), cap(p1, p2, .028 * k, .006 * k)], .02 * k), *hu.bb([p0, p1, p2], .05 * k), .006), red, part="head")
    G = J["wr_r"] + J["lo_r"] * .125 * s + A(.022 * s, 0, 0); dh = hu.unit((0, -.5, .86))
    sw = lambda p: U([ell((0, 0, .72 * s), (.0075 * s, .028 * s, .53 * s))])(p)
    guard = rbox((0, 0, .17 * s), (.011 * s, .105 * s, .014 * s), .007); pom = ell((0, 0, -.2 * s), (.026 * s, .026 * s, .024 * s)); grip = cap((0, 0, -.19 * s), (0, 0, .16 * s), .0185 * s, .0185 * s)
    pts = [G - dh * .3 * s, G + dh * 1.3 * s]
    M.add(extract(hu.frame(U([sw, rbox((0, 0, .2 * s), (.006 * s, .02 * s, .03 * s), .004)], .008), G, dh, (1, 0, 0)), *hu.bb(pts, .15 * s), .0085), steel, part="weapon_r")
    M.add(extract(hu.frame(U([guard, pom], .004), G, dh, (1, 0, 0)), *hu.bb(pts, .15 * s), .0075), gold, part="weapon_r")
    M.add(extract(hu.frame(grip, G, dh, (1, 0, 0)), *hu.bb(pts, .15 * s), .0065), leather, part="weapon_r")
    oc = (J["el_l"] + J["wr_l"]) / 2 + A(.095 * s, -.05 * s, .02 * s)
    plate = U([ell((0, 0, .02 * s), (.016 * s, .17 * s, .27 * s)), rbox((0, 0, .15 * s), (.016 * s, .17 * s, .13 * s), .01)], .02); bos = ell((-.022 * s, 0, .05 * s), (.03 * s, .05 * s, .05 * s))
    rim = lambda p: np.maximum(plate(p) - .0, -(plate(p * np.array([1, .88, .91]) + np.array([0, 0, -.012 * s])) + .0)) if False else plate(p)
    M.add(extract(hu.frame(plate, oc, (0, 0, 1), (0, -1, 0)), *hu.bb([oc], .36 * s), .0095), steel, part="forearm_l")
    M.add(extract(hu.frame(bos, oc, (0, 0, 1), (0, -1, 0)), *hu.bb([oc], .36 * s), .006), gold, part="forearm_l")
    M.export(out)

if __name__ == "__main__":
    build(os.path.join(ROOT, "assets/models/characters/chr_ally_garrick_royal_paladin.glb"))
