#!/usr/bin/env python3
"""Shadow Direwolf Alpha - SDF-sculpted quadruped: deep ribcage, muscular neck, sculpted skull/snout, digitigrade legs (shoulder-elbow-wrist / hip-knee-hock),
bushy tail, ~6000 tapered fur cards (mane, ruff, tail plume) + baked fur PBR.  Engine rig: torso, head, arm_l/r + forearm_l/r (front legs),
leg_l/r + shin_l/r (hind legs), tail.  Blender space: front = -Y."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sdf_core import *
import sdf_humanoid as hu, sdf_mats as sm
from sdf_bake import Model
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fur_cards(V, F, N, wfn, n, rng, Lr=(.07, .12), width=.03, flow=(0, 1, -.15), flowk=.9, upk=0.):
    ar = np.linalg.norm(np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]), axis=1); cen = V[F].mean(1); cn = N[F].mean(1)
    w = ar * wfn(cen, cn); w /= w.sum(); ti = rng.choice(len(F), n, p=w); b = rng.dirichlet([1, 1, 1], n); P = np.einsum("ni,nij->nj", b, V[F[ti]]); Nn = np.einsum("ni,nij->nj", b, N[F[ti]])
    Nn /= np.linalg.norm(Nn, axis=1, keepdims=True); fl = A(flow) / np.linalg.norm(A(flow)); d = Nn * .55 + fl * flowk + A(0, 0, 1) * upk + rng.normal(0, .18, (n, 3)); d /= np.linalg.norm(d, axis=1, keepdims=True)
    L = rng.uniform(*Lr, n)[:, None] * wfn(P, Nn)[:, None] ** .25; side = np.cross(d, Nn); side /= np.linalg.norm(side, axis=1, keepdims=True) + 1e-9; hw = width * .5 * rng.uniform(.8, 1.2, n)[:, None]
    mid = P + d * L * .5 + Nn * L * .08; tip = P + d * L + Nn * L * .04 - A(0, 0, 1) * L * .18
    Vs = np.concatenate([P - side * hw, P + side * hw, mid - side * hw * .7, mid + side * hw * .7, tip], 0).reshape(5, n, 3).transpose(1, 0, 2).reshape(-1, 3)
    Fi = (np.arange(n)[:, None, None] * 5 + np.array([[0, 1, 3], [0, 3, 2], [2, 3, 4]])[None]).reshape(-1, 3).astype(np.int64)
    Ns = np.repeat(Nn, 5, axis=0); uv = np.tile(np.array([[0, 0], [1, 0], [.12, .5], [.88, .5], [.5, 1.]]), (n, 1))
    return Vs.astype(np.float32), Fi, Ns.astype(np.float32), uv

def build(out):
    rng = np.random.default_rng(7); sd = (-1, 1)
    def L(x, y, z): return A(x, y, z)
    body = [ell(L(0, .40, .86), (.17, .20, .19)), ell(L(0, -.24, .90), (.20, .34, .30)), ell(L(0, .06, .85), (.16, .26, .22)), cap(L(0, -.55, .98), L(0, -.78, 1.06), .165, .125),
            ell(L(0, -.46, 1.02), (.15, .20, .20)), cap(L(0, .5, .88), L(0, 1.0, .66), .075, .03), cap(L(0, 1.0, .66), L(0, 1.32, .42), .05, .016)]
    head = [ell(L(0, -.86, 1.07), (.105, .15, .105)), cap(L(0, -.92, 1.05), L(0, -1.12, 1.0), .078, .047), ell(L(0, -1.13, 1.0), (.04, .035, .03)), ell(L(0, -.95, .98), (.08, .10, .05))]
    for s in sd:
        head += [ellz(L(s * .068, -.80, 1.20), (.03, .013, .075), (s * .25, -.15, 1), up=(1, 0, 0)), ell(L(s * .062, -.95, 1.13), (.035, .045, .028)), ell(L(s * .08, -.86, 1.04), (.04, .06, .06))]
        sh, el, wr, pw = L(s * .14, -.28, .86), L(s * .125, -.31, .54), L(s * .115, -.28, .17), L(s * .115, -.40, .035)
        hp, kn, hk, hpw = L(s * .15, .40, .84), L(s * .16, .27, .56), L(s * .125, .45, .27), L(s * .125, .36, .035)
        body += [cap(sh, el, .085, .062), ellz((sh + el) / 2 + L(0, .02, .02), (.07, .09, .17), el - sh), ell(sh, (.095, .12, .12)), cap(el, wr, .05, .033), cap(wr, pw, .033, .03), ell(pw + L(0, -.04, 0), (.04, .07, .03)),
                 cap(hp, kn, .105, .075), ellz((hp + kn) / 2 + L(s * .02, .03, 0), (.095, .12, .2), kn - hp), ell(hp, (.12, .13, .14)), cap(kn, hk, .062, .04), ell(kn, (.07, .075, .075)), cap(hk, hpw, .036, .03), ell(hpw + L(0, -.04, 0), (.042, .075, .03))]
        head_ = None
    F = U(body + head, .05); jar = F
    piv = dict(torso=L(0, .08, .88), head=L(0, -.60, 1.0), cloak=L(0, -.4, 1.0), tail=L(0, .52, .88), weapon_r=L(-.1, -.3, .5))
    segs = dict(torso=[(L(0, .40, .86), L(0, -.45, .95))], head=[(L(0, -.60, 1.0), L(0, -.86, 1.07)), (L(0, -.9, 1.05), L(0, -1.12, 1.0))], tail=[(L(0, .52, .86), L(0, 1.0, .66)), (L(0, 1.0, .66), L(0, 1.34, .42))])
    for s, n in ((1, "l"), (-1, "r")):
        sh, el, wr, pw = L(s * .14, -.28, .86), L(s * .125, -.31, .54), L(s * .115, -.28, .17), L(s * .115, -.40, .035); hp, kn, hk, hpw = L(s * .15, .40, .84), L(s * .16, .27, .56), L(s * .125, .45, .27), L(s * .125, .36, .035)
        piv.update({"arm_" + n: sh, "forearm_" + n: el, "leg_" + n: hp, "shin_" + n: kn}); segs.update({"arm_" + n: [(sh, el)], "forearm_" + n: [(el, wr), (wr, pw)], "leg_" + n: [(hp, kn)], "shin_" + n: [(kn, hk), (hk, hpw)]})
    M = Model("wolf", piv, tex=1024)
    fm = sm.fur("wolf_fur", (.10, .095, .12), (.52, .5, .56), belly=(.3, .27, .26), saddle=(.24, .24, .3), along=(1, 3, 1), nstr=1.6, dirt=.4)
    nose = sm.skin("wolf_nose", (.03, .025, .03), (.01, .01, .01), pore=1.5, rough=.3)
    bnd = (L(-.5, -1.25, -.02), L(.5, 1.45, 1.4)); hy = -.6
    Vb, Fb, Nb = extract(F, *bnd, .0175, keep=lambda c: c[:, 1] > hy + .02)
    M.add((Vb, Fb, Nb), fm, segs=segs, tau=.045)
    M.add(extract(F, L(-.25, -1.25, .75), L(.25, hy + .03, 1.4), .0075, keep=lambda c: c[:, 1] < hy, push=.0004), fm, segs=segs, tau=.045)
    eye = sm.eye("wolf_eye", (.056, -.955, 1.115), (0, -1, 0), (1.0, .5, .05), glow=1.3, emit_str=1.4); bone = sm.bone("wolf_bone", (.9, .88, .8)); claw = sm.bone("wolf_claw", (.12, .1, .09))
    for s in sd:
        c = L(s * .056, -.955, 1.115); M.add(extract(ell(c, (.0155, .0155, .0155)), c - .03, c + .03, .0035), eye, part="head")
        for dz, dy, r in ((0, 0, .0085),):
            b0 = L(s * .034, -1.08, .975); b1 = b0 + L(s * .002, -.012, -.05); M.add(extract(cap(b0, b1, .0095, .0012), *hu.bb([b0, b1], .02), .0035), bone, part="head")
            b0 = L(s * .026, -1.10, .96); b1 = b0 + L(0, -.004, -.03); M.add(extract(cap(b0, b1, .006, .001), *hu.bb([b0, b1], .02), .0035), bone, part="head")
    M.add(extract(ell(L(0, -1.158, 1.012), (.028, .022, .02)), L(-.05, -1.2, .96), L(.05, -1.11, 1.06), .004), nose, part="head")
    for s, n in ((1, "l"), (-1, "r")):
        for fr in (True, False):
            pw = L(s * (.115 if fr else .125), -.40 if fr else .36, .035)
            for i in (-1, 0, 1):
                b0 = pw + L(i * .022, -.095, .006); b1 = b0 + L(i * .004, -.045, -.022); M.add(extract(cap(b0, b1, .0095, .0012), *hu.bb([b0, b1], .02), .0035), claw, part=("forearm_" if fr else "shin_") + n)
    def wfn(c, nrm):
        w = np.full(len(c), .35); z, y = c[:, 2], c[:, 1]
        w += 3.0 * ((z > .93) & (y < -.1) & (y > -.72)) + 2.0 * ((np.abs(c[:, 0]) < .13) & (nrm[:, 2] > .3) & (y > -.1)) + 2.6 * (y > .5) + 1.8 * ((y < -.45) & (z < 1.0) & (y > -.78)) + 1.0 * ((c[:, 0] ** 2 > .02) & (y > .2) & (z > .5))
        w *= np.where(nrm[:, 2] < -.5, .15, 1.) * np.where(y < -.9, .12, 1.) * np.where(z < .5, .5, 1.); return w
    cards = sm.fur_card("wolf_fur_cards", (.08, .075, .1), (.58, .56, .62), .3)
    Vc, Fc, Nc, uv = fur_cards(Vb, Fb, Nb, wfn, 5200, rng, Lr=(.07, .14), width=.034, flowk=.85, upk=.35)
    M.add((Vc, Fc, Nc), cards, segs=segs, tau=.045, uv=uv)
    tv = lambda c, nrm: np.where(c[:, 1] > .5, 1., 0.) * 1.0
    Vt, Ft, Nt, uvt = fur_cards(Vb, Fb, Nb, lambda c, nrm: .02 + 3.0 * (c[:, 1] > .85), 1200, rng, Lr=(.12, .24), width=.05, flow=(0, 1, -.5), flowk=.9, upk=0)
    M.add((Vt, Ft, Nt), cards, segs=segs, tau=.045, uv=uvt)
    M.export(out)

if __name__ == "__main__":
    build(os.path.join(ROOT, "assets/models/monsters/mon_shadow_direwolf_alpha.glb"))
