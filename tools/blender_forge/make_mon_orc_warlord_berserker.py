#!/usr/bin/env python3
"""Orc Warlord Gorrash - SDF-sculpted in numpy (smooth-union muscle volumes, marching cubes), unwrapped with Blender Smart UV Project, PBR-baked
(pores, scars, war paint, rust, hide, bone) and exported through bpy.ops.export_scene.gltf with the engine's named, pivoted body-part objects."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sdf_core import *
import sdf_humanoid as hu, sdf_mats as sm
from sdf_bake import Model, noise
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def build(out):
    h = 2.08; f, J, hd = hu.humanoid(h=h, sh=.31, chest=(.265, .175), belly=.5, arm=1.32, leg=1.14, mus=1.5, hunch=.17, hs=.92, armL=1.12, neck=1.55,
                                     jaw=1.3, brow=1.45, cheek=1.05, nose=1.0, chin=1.35, ear=.75, ear_up=.5, brow_drop=.004)
    s = J["s"]; k = s * .92; M = Model("orc", hu.pivots(J), tex=1024)
    skin = sm.skin("orc_skin", (.27, .37, .17), (.20, .29, .13), (.36, .45, .22), scars=.7, paint=(.5, .06, .04), veins=(.18, .28, .16), pore=1.4, wrinkle=1.6, nstr=1.4)
    hu.skin_pieces(M, f, hd, J, skin, (A(-.8, -.65, -.02), A(.8, .6, 2.25)), hb=.0185, hf=.0078)
    F = J["F"]; hc = J["headc"]; segs = J["segs"]
    eye = sm.eye("orc_eye", (hc[0] + .036 * k, hc[1] - .088 * k, hc[2] + .008 * k), (0, -1, 0), (.95, .62, .06), slit=False, glow=.9)
    hu.eyes_teeth(M, J, eye, k, True)
    bone = sm.bone("orc_bone"); hide = sm.leather("orc_hide", (.30, .18, .10), wear=1.6); dark = sm.leather("orc_leather", (.12, .08, .06)); iron = sm.metal("orc_iron", (.42, .43, .45), rough=.5, rust=.8)
    hair = sm.leather("orc_hair", (.04, .035, .03), rough=.7)
    for sx in (-1, 1):   # underbite tusks + mohawk spikes
        b0 = A(hc[0] + sx * .034 * k, hc[1] - .090 * k, hc[2] - .068 * k); b1 = b0 + A(sx * .006 * k, -.012 * k, .105 * k); b2 = b1 + A(-sx * .008 * k, -.004 * k, .03 * k)
        M.add(extract(U([cap(b0, b1, .0125 * k, .0085 * k), cap(b1, b2, .0085 * k, .0016 * k)], .004), *hu.bb([b0, b1, b2], .02 * k), .0048 * k), bone, part="head")
    for i in range(9):
        p0 = A(hc[0], hc[1] + .11 * k - i * .027 * k, hc[2] + .095 * k + .004 * k * i * 0 - abs(i - 3) * .004 * k); p1 = p0 + A(0, .035 * k * (1 + i * .05), .05 * k * (1 - abs(i - 3) * .05))
        M.add(extract(cap(p0, p1, .011 * k, .0015 * k), *hu.bb([p0, p1], .02 * k), .0055 * k), hair, part="head")
    jj = lambda z0, z1: (lambda c: (c[:, 2] > z0 * s) & (c[:, 2] < z1 * s))
    fray = lambda c: c[:, 2] > (.62 + .07 * noise(c, 9, 40) + .03 * np.sin(c[:, 0] * 90)) * s
    M.add(hu.shell(F, .016, A(-.4, -.34, .5) * s, A(.4, .34, 1.12) * s, .0135, lambda c: fray(c) & (c[:, 2] < 1.0 * s) & (np.abs(c[:, 1]) < .32 * s * 1.3)), hide, segs=segs)   # hide trousers
    M.add(hu.shell(F, .026, A(-.4, -.3, .94) * s, A(.4, .3, 1.1) * s, .012, jj(.965, 1.045), ridges=lambda P: np.sin(P[:, 0] * 120 + P[:, 1] * 40) * .5 + .5, amp=.002), dark, segs=segs)   # belt
    for sd in (-1, 1): M.add(hu.shell(F, .02, A(sd * .2, -.3, -.02) * s - .12 * s, A(sd * .2, .15, .34) * s + .12 * s, .0135, lambda c, sd=sd: (c[:, 2] < .31 * s) & (c[:, 0] * sd > 0)), dark, segs=segs)   # boots
    for sd, sn in ((1, "l"), (-1, "r")):
        S_, E, W = J["sh_" + sn], J["el_" + sn], J["wr_" + sn]; ax = W - E; L2 = float(ax @ ax)
        for n_, (t0, t1, dd, mt) in enumerate(((.38, .94, .018, iron),)):
            M.add(hu.shell(F, dd, *hu.bb([E, W], .14 * s), .011, lambda c, E=E, ax=ax, L2=L2, t0=t0, t1=t1: (((c - E) @ ax) / L2 > t0) & (((c - E) @ ax) / L2 < t1) & (np.linalg.norm(c - E, axis=1) < .36 * s)), mt, segs=segs)
        pk = lambda c, S_=S_, sd=sd: (np.linalg.norm(c - S_, axis=1) < .17 * s) & (c[:, 2] > S_[2] - .01 * s) & ((c[:, 0] - S_[0]) * sd > -.04 * s)
        M.add(hu.shell(F, .042 * s, *hu.bb([S_], .26 * s), .012, pk, ridges=lambda P: np.sin(P[:, 2] * 85) * .5 + .5, amp=.006), iron, segs=segs)
        sp0 = S_ + A(sd * .075, 0, .105) * s; sp1 = sp0 + A(sd * .05, 0, .26) * s
        M.add(extract(cap(sp0, sp1, .034 * s, .003 * s), *hu.bb([sp0, sp1], .06 * s), .0075), bone, part="arm_" + sn)
    ch = J["waist"][1] + A(0, 0, 0)[1]
    M.add(hu.shell(F, .019, A(-.4, -.35, .98) * s, A(.4, .1, 1.62) * s, .0125, lambda c: (np.abs((c[:, 2] - 1.28 * s) + 1.25 * c[:, 0]) < .06 * s) & (c[:, 1] < J["waist"][1] - .02 * s) & (c[:, 2] > 1.0 * s) & (c[:, 2] < 1.6 * s)), dark, segs=segs)   # chest strap
    sk0 = A(0, hc[1] * 0 - .20 * s, 1.30 * s)
    M.add(extract(U([ell(A(0, -.205 * s - .02, 1.32 * s), (.05 * s, .022 * s, .06 * s))]), *hu.bb([A(0, -.2 * s, 1.32 * s)], .09 * s), .0065), bone, part="torso")   # skull medallion
    G = J["wr_r"] + J["lo_r"] * .125 * s + A(.022 * s, 0, 0); dh = hu.unit((0, -.42, .9))
    haft = lambda p: cap((0, 0, -.30 * s), (0, 0, .86 * s), .024 * s, .02 * s)(p)
    blade = lambda p: sub(ell((0, .30 * s, .66 * s), (.011 * s, .27 * s, .25 * s))(p) * 1 + 0 * p[:, 0], 0 * p[:, 0] + ell((0, -.10 * s, .66 * s), (.12 * s, .26 * s, .34 * s))(p), .004) if False else sub(ell((0, .31 * s, .66 * s), (.024 * s, .28 * s, .26 * s)), ell((0, -.12 * s, .66 * s), (.2 * s, .30 * s, .36 * s)), .006)(p)
    spike = lambda p: cap((0, 0, .84 * s), (0, 0, 1.06 * s), .02 * s, .002 * s)(p)
    wf = hu.frame(U([haft, blade, spike, lambda p: cap((0, 0, -.30 * s), (0, 0, -.38 * s), .03 * s, .02 * s)(p)], .012), G, dh, (1, 0, 0)); pts = [G - dh * .5 * s, G + dh * 1.3 * s]
    lo_, hi_ = hu.bb(pts, .45 * s); M.add(extract(wf, lo_, hi_, .0135), iron, part="weapon_r")
    wg = hu.frame(lambda p: cap((0, 0, -.28 * s), (0, 0, .30 * s), .0275 * s, .0275 * s)(p), G, dh, (1, 0, 0)); M.add(extract(wg, *hu.bb(pts, .1 * s), .011), dark, part="weapon_r")
    M.export(out)

if __name__ == "__main__":
    build(os.path.join(ROOT, "assets/models/monsters/mon_orc_warlord_berserker.glb"))
