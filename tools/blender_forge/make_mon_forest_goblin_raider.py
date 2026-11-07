#!/usr/bin/env python3
"""Forest Goblin Raider - SDF-sculpted lanky goblin: oversized head, huge swept ears, hooked nose, pointed fangs, rusty cap, ragged hide tunic and a jagged cleaver.
Same pipeline as the orc (smooth-union anatomy -> marching cubes -> Blender Smart UV -> PBR bake -> official glTF export, engine part-blend rig)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sdf_core import *
import sdf_humanoid as hu, sdf_mats as sm
from sdf_bake import Model, noise
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def build(out):
    f, J, hd = hu.humanoid(h=1.28, sh=.175, chest=(.145, .105), belly=.12, arm=.78, leg=.8, mus=.45, hunch=.24, hs=1.4, armL=1.2, neck=.8, jaw=1.15, brow=1.2, nose=2.8, chin=1.5, cheek=.8, ear=2.5, ear_up=.12, brow_drop=.002)
    s = J["s"]; k = s * 1.4; M = Model("gob", hu.pivots(J), tex=1024)
    skin = sm.skin("gob_skin", (.42, .52, .17), (.25, .34, .10), (.55, .62, .25), scars=.5, pore=1.2, wrinkle=1.3, nstr=1.3, veins=(.3, .42, .12))
    hu.skin_pieces(M, f, hd, J, skin, (A(-.6, -.5, -.02), A(.6, .45, 1.55)), hb=.0142, hf=.0068)
    F = J["F"]; hc = J["headc"]; segs = J["segs"]
    eye = sm.eye("gob_eye", (hc[0] + .036 * k, hc[1] - .088 * k, hc[2] + .008 * k), (0, -1, 0), (1.0, .85, .05), slit=True, glow=1.0)
    hu.eyes_teeth(M, J, eye, k * 1.12, True)
    bone = sm.bone("gob_bone"); hide = sm.leather("gob_hide", (.28, .20, .11), wear=1.8); dark = sm.leather("gob_leather", (.14, .09, .06)); iron = sm.metal("gob_iron", (.45, .42, .40), rough=.55, rust=1.0)
    for sx in (-1, 1):
        for dx in (0, .022):
            b0 = A(hc[0] + sx * (.024 + dx) * k, hc[1] - .104 * k, hc[2] - .071 * k); b1 = b0 + A(0, -.004 * k, .042 * k)
            M.add(extract(cap(b0, b1, .006 * k, .0008 * k), *hu.bb([b0, b1], .01 * k), .0035 * k), bone, part="head")
    cp = lambda c: (c[:, 2] > hc[2] + .035 * k) & (c[:, 1] > hc[1] - .1 * k)
    M.add(hu.shell(F, .016 * k, *hu.bb([hc], .2 * k), .009, cp), iron, segs=segs)   # rusty cap
    fray = lambda z: (lambda c: c[:, 2] > (z + .05 * noise(c, 9, 41) + .02 * np.sin(c[:, 0] * 70)) * s)
    M.add(hu.shell(F, .013, A(-.3, -.3, .6) * s, A(.3, .25, 1.55) * s, .0125, lambda c: fray(.78)(c) & (c[:, 2] < 1.5 * s) & (np.abs(c[:, 0]) < J["sh_l"][0] - .02 * s * 0 + .0) | False), hide, segs=segs)
    for sd in (-1, 1): M.add(hu.shell(F, .015, A(sd * .15, -.2, -.02) * s - .1 * s, A(sd * .15, .12, .36) * s + .1 * s, .0115, lambda c, sd=sd: (c[:, 2] < .30 * s) & (c[:, 0] * sd > 0)), dark, segs=segs)
    M.add(hu.shell(F, .02, A(-.3, -.3, .9) * s, A(.3, .3, 1.07) * s, .011, lambda c: (c[:, 2] > .93 * s) & (c[:, 2] < 1.0 * s)), dark, segs=segs)
    G = J["wr_r"] + J["lo_r"] * .125 * s + A(.022 * s, 0, 0); dh = hu.unit((0, -.5, .85))
    blade = sub(ell((0, .05 * s, .52 * s), (.009 * s, .06 * s, .34 * s)), ell((0, -.05 * s, .6 * s), (.06 * s, .04 * s, .14 * s)), .005)
    wf = hu.frame(U([lambda p: cap((0, 0, -.22 * s), (0, 0, .2 * s), .02 * s, .018 * s)(p), blade, lambda p: rbox((0, 0, .21 * s), (.015 * s, .06 * s, .01 * s), .006)(p)], .01), G, dh, (1, 0, 0))
    pts = [G - dh * .3 * s, G + dh * .95 * s]; M.add(extract(wf, *hu.bb(pts, .3 * s), .011), iron, part="weapon_r")
    M.export(out)

if __name__ == "__main__":
    build(os.path.join(ROOT, "assets/models/monsters/mon_forest_goblin_raider.glb"))
