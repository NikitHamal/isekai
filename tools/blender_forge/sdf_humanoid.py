#!/usr/bin/env python3
"""Parametric SDF humanoid anatomy (orcs, goblins, knights ...).  All absolute lengths are for h=1.8 m and scaled by s=h/1.8."""
import numpy as np
from sdf_core import *

def unit(v): v = A(v); return v / np.linalg.norm(v)

def muscle(a, b, t, rx, ry, rl, ox=0., oy=0.):
    a, b = A(a), A(b); return ellz(a + (b - a) * t + A(ox, oy, 0), (rx, ry, rl), b - a)

def hand(wr, d, s, fist=False, side=1, grip_axis=(0, 0, 1)):
    """fingered hand at wrist wr pointing along d (side +1 = left/+X)."""
    d = unit(d); f = []; pc = wr + d * .055 * s
    f.append(ellz(pc, (.040 * s, .019 * s, .052 * s), d))
    inward = A(-side, 0, 0); fw = A(0, -1, 0)
    for i in range(4):
        o = (i - 1.5) * .0215 * s; base = wr + d * .098 * s + A(o, 0, 0); ln = (.040 - abs(i - 1.5) * .0035) * s
        if fist:
            p1 = base + (d * .9 + inward * .25) * ln; p2 = p1 + (d * .2 + inward * .95) * ln * .85; p3 = p2 + (-d * .7 + inward * .6) * ln * .6
        else:
            p1 = base + (d * .95 + fw * .30) * ln * 1.05; p2 = p1 + (d * .75 + fw * .65) * ln * .8; p3 = p2 + (d * .55 + fw * .8) * ln * .6
        f += [cap(base, p1, .0105 * s, .0095 * s), cap(p1, p2, .0095 * s, .0088 * s), cap(p2, p3, .0085 * s, .0075 * s)]
    t0 = wr + d * .045 * s + inward * .012 * s + fw * .015 * s; t1 = t0 + (d * .5 + inward * .45 + fw * .75) * .04 * s; t2 = t1 + (d * .4 + fw * .9 + inward * .1) * .035 * s
    f += [cap(t0, t1, .0125 * s, .0105 * s), cap(t1, t2, .0105 * s, .009 * s)]
    return U(f, .006)

def head(c, s, hs=1.0, jaw=1.0, brow=1.0, nose=1.0, cheek=1.0, ear=0.0, ear_up=.35, chin=1.0, snout=0.0, brow_drop=0.0):
    x, y, z = c; k = s * hs; f = [ell((x, y + .012 * k, z + .008 * k), (.088 * k, .106 * k, .108 * k))]
    f += [ell((x, y - .030 * k, z - .030 * k), (.080 * k, .088 * k, .092 * k))]
    for sx in (-1, 1):
        f += [cap((x + sx * .052 * k * jaw, y - .006 * k, z - .062 * k), (x + sx * .012 * k, y - .088 * k * (1 + snout), z - .082 * k), .037 * k, .030 * k * jaw)]
        f += [ell((x + sx * .056 * k, y - .070 * k, z - .018 * k), (.026 * k * cheek, .028 * k, .024 * k))]
    f += [ell((x, y - .098 * k * (1 + snout * .5), z - .092 * k), (.030 * k * chin, .026 * k, .026 * k * chin))]
    g = U(f, .02 * k)
    g = U([g, cap((x - .060 * k, y - .088 * k, z + .030 * k - brow_drop * k), (x + .060 * k, y - .088 * k, z + .030 * k - brow_drop * k), .015 * k * brow),
           ell((x, y - .105 * k * (1 + snout * .4), z - .026 * k), (.015 * k * nose, .028 * k * nose, .033 * k * nose)),
           ell((x, y - .120 * k * (1 + snout * .4), z - .040 * k), (.020 * k * nose, .014 * k * nose, .012 * k * nose))], .012 * k)
    for sx in (-1, 1):
        g = sub(g, ell((x + sx * .036 * k, y - .086 * k, z + .008 * k), (.0185 * k, .020 * k, .0165 * k)), .004 * k)
        g = sub(g, ell((x + sx * .027 * k, y - .122 * k * (1 + snout * .4), z - .040 * k), (.0042 * k, .010 * k, .0055 * k)), .003 * k)
        if ear > 0:
            d = unit((sx * 1.0, .25, ear_up)); L = .09 * k * ear; p = A(x + sx * .085 * k, y + .012 * k, z - .004 * k)
            g = U([g, ellz(p + d * L * .5, (.011 * k, .034 * k, L * .55), d, up=(0, 1, 0)), cap(p, p + d * L * .3, .02 * k, .012 * k)], .012 * k)
    return sub(g, ell((x, y - .098 * k * (1 + snout * .4), z - .060 * k), (.028 * k, .014 * k, .0055 * k)), .003 * k)

def humanoid(h=1.8, sh=.20, chest=(.17, .115), belly=0., arm=1.0, leg=1.0, mus=1.0, hunch=0., hs=1.0, armL=1.0, neck=1.0, hip=.095, fist_r=True, **hk):
    s = h / 1.8
    def Yo(z): return -hunch * s * max(0., (z / s - .95) / .85) ** 1.4
    J = {}; ang1, ang2 = .42, .30; up = unit((np.sin(ang1), -.03, -np.cos(ang1))); lo = unit((np.sin(ang2), -.12, -np.cos(ang2)))
    J["waist"] = A(0, Yo(.99 * s), .99 * s); J["neck"] = A(0, Yo(1.52 * s) - .005 * s, 1.52 * s); J["headc"] = A(0, Yo(1.68 * s) - .014 * s, 1.675 * s * (1 - .04 * (hs - 1) * 0)); J["top"] = J["headc"] + A(0, 0, .11 * s * hs)
    f, segs = [], dict(torso=[], head=[(J["neck"], J["top"])], arm_l=[], arm_r=[], forearm_l=[], forearm_r=[], leg_l=[], leg_r=[], shin_l=[], shin_r=[])
    segs["torso"] = [(A(0, 0, .93 * s), J["waist"]), (J["waist"], J["neck"])]; segs["head"] = [(J["neck"] + A(0, 0, .03 * s), J["top"]), (J["headc"] + A(0, -.05 * s, -.07 * s), J["headc"] + A(0, -.11 * s, -.085 * s)), (J["headc"] + A(0, -.1 * s, -.02 * s), J["headc"] + A(0, -.13 * s, -.04 * s))]
    ch = Yo(1.33 * s)
    f += [ell((0, 0, .93 * s), (.165 * leg ** .3, .115, .09 * s)), ell((0, Yo(1.08 * s) - .02 * belly * s, 1.07 * s), (.145 + .02 * belly, .105 + .06 * belly, .095 * s)),
          ell((0, ch, 1.33 * s), (chest[0], chest[1], .125 * s)), ell((0, ch - .01 * s, 1.43 * s), (chest[0] * 1.05, chest[1] * .9, .08 * s))]
    for sx in (-1, 1):
        f += [ell((sx * .085 * mus ** .6, ch - .075 * s * mus ** .5, 1.37 * s), (.088 * mus, .055 * mus ** .7, .052 * s * mus)), ell((sx * .125, ch + .035, 1.32 * s), (.055, .07, .12 * s)),
              cap((sx * .03, J["neck"][1], 1.55 * s), (sx * (sh - .05), Yo(1.48 * s), 1.47 * s), .042 * neck * mus ** .3, .035)]
    f += [cap(A(0, Yo(.95 * s), .95 * s), A(0, ch + .01, 1.30 * s), .125 * (chest[0] / .17) ** .6, .15 * (chest[0] / .17) ** .6 * s), cap(J["neck"] + A(0, 0, -.04 * s), J["neck"] + A(0, -.012 * s, .1 * s), .056 * s * neck, .048 * s * neck)]
    for side, sx in (("l", 1), ("r", -1)):
        S_ = A(sx * sh, Yo(1.46 * s), 1.46 * s); E = S_ + up * A(sx, 1, 1) * .31 * s * armL; W = E + lo * A(sx, 1, 1) * .27 * s * armL; segs["arm_" + side] = [(S_, E)]
        segs["forearm_" + side] = [(E, W), (W, W + lo * A(sx, 1, 1) * .2 * s)]; segs["torso"].append((J["neck"], S_ + A(-sx * .02, 0, 0)))
        J["sh_" + side], J["el_" + side], J["wr_" + side], J["lo_" + side] = S_, E, W, lo * A(sx, 1, 1)
        f += [ell(S_ + A(sx * .012, .0, -.02 * s), (.068 * s * mus, .066 * s * mus, .08 * s * mus)), cap(S_, E, .056 * s * arm, .043 * s * arm), muscle(S_, E, .38, .05 * s * arm * mus, .053 * s * arm * mus, .1 * s, 0, -.012 * s),
              muscle(S_, E, .45, .045 * s * arm, .05 * s * arm, .1 * s, 0, .015 * s), cap(E, W, .043 * s * arm, .029 * s * arm), muscle(E, W, .2, .042 * s * arm * mus, .046 * s * arm, .085 * s, 0, -.008 * s), ell(E, (.044 * s * arm, .044 * s * arm, .044 * s * arm))]
        H_ = hip * s * (1 if sx > 0 else -1); Hp = A(sx * hip * s, Yo(.93 * s), .92 * s); K = A(sx * .092 * s, -.012 * s, .50 * s); An = A(sx * .09 * s, .012 * s, .085 * s)
        segs["leg_" + side] = [(Hp, K)]; segs["shin_" + side] = [(K, An), (An, A(sx * .095 * s, -.13 * s, .03 * s))]; J["hip_" + side], J["kn_" + side], J["an_" + side] = Hp, K, An
        f += [cap(Hp, K, .098 * s * leg, .064 * s * leg), muscle(Hp, K, .4, .082 * s * leg * mus ** .4, .088 * s * leg, .17 * s, 0, -.012 * s), muscle(Hp, K, .45, .07 * s * leg, .075 * s * leg, .16 * s, 0, .02 * s), ell(K, (.062 * s * leg, .064 * s * leg, .062 * s * leg)),
              cap(K, An, .06 * s * leg, .034 * s), muscle(K, An, .25, .056 * s * leg * mus ** .3, .062 * s * leg, .11 * s, 0, .028 * s), muscle(K, An, .6, .04 * s, .036 * s, .13 * s, 0, -.018 * s),
              ell(A(sx * .092 * s, -.075 * s, .042 * s), (.05 * s, .125 * s, .042 * s)), ell(A(sx * .092 * s, -.16 * s, .028 * s), (.044 * s, .06 * s, .026 * s)), ell(An + A(0, .02 * s, -.02 * s), (.048 * s, .05 * s, .05 * s))]
    J["segs"] = segs; J["s"] = s
    return U(f, .035 * s), J, head(J["headc"], s, hs, **hk)

def skin_pieces(M, f, hd, J, mat, bnd, hb=.014, hf=.0065, fist_r=True, hands=True):
    """extract body / head / hands at different voxel sizes from one unified SDF and add them to Model M with automatic part weights."""
    s = J["s"]; zc = J["neck"][2] + .05 * s; hl = []; HC = {}
    for side, sx in (("l", 1), ("r", -1)):
        HC[side] = J["wr_" + side] + J["lo_" + side] * .085 * s; hl.append(hand(J["wr_" + side], J["lo_" + side], s, fist=(side == "r" and fist_r), side=sx))
    F = U([f, hd] + hl, .014 * s); R = .105 * s; J["F"] = F; J["HC"] = HC
    def nh(c): return np.minimum(np.linalg.norm(c - HC["l"], axis=1), np.linalg.norm(c - HC["r"], axis=1))
    M.add(extract(F, *bnd, hb, keep=lambda c: (c[:, 2] < zc + .012 * s) & (nh(c) > R)), mat, segs=J["segs"])
    hc = J["headc"]; M.add(extract(F, hc + A(-.2, -.26, zc - hc[2] - .01) * s, hc + A(.2, .2, .17) * s, hf * s, keep=lambda c: c[:, 2] >= zc, push=.0004), mat, segs=J["segs"])
    for side in "lr":
        c0 = HC[side]; M.add(extract(F, c0 - .15 * s, c0 + .15 * s, hf * s, keep=lambda c, c0=c0: np.linalg.norm(c - c0, axis=1) < R + .012 * s, push=.0004), mat, segs=J["segs"])

def shell(F, d, lo, hi, h, keep, ridges=None, amp=.004):
    g = off(F, d)
    if ridges is not None: g = add_noise(g, ridges, amp)
    return extract(g, lo, hi, h, keep=keep)

def pivots(J):
    p = dict(torso=J["waist"], head=J["neck"], cloak=J["neck"] - A(0, 0, .03), weapon_r=J["wr_r"], tail=J["waist"])
    for s_ in "lr": p.update({"arm_" + s_: J["sh_" + s_], "forearm_" + s_: J["el_" + s_], "leg_" + s_: J["hip_" + s_], "shin_" + s_: J["kn_" + s_]})
    return p

def frame(fn, origin, ez, ey=(1, 0, 0)):
    """SDF defined in a local frame: local z along ez, local y ~ ey (orthogonalised), x = y x z; origin is local (0,0,0)."""
    ez = unit(ez); ey = A(ey) - (A(ey) @ ez) * ez; ey = unit(ey); ex = np.cross(ey, ez); R = np.stack([ex, ey, ez], 1); o = A(origin)
    return lambda P: fn((P - o) @ R)

def bb(points, m):
    p = np.array([A(q) for q in points]); return p.min(0) - m, p.max(0) + m

def eyes_teeth(M, J, mats, k, glow_eye, hs_k=None):
    """Add eyeballs (own PBR eye material) at the head's sockets."""
    hc = J["headc"]; eb = []
    for sx in (-1, 1):
        c = A(hc[0] + sx * .036 * k, hc[1] - .088 * k, hc[2] + .008 * k); lo, hi = c - .03 * k, c + .03 * k
        M.add(extract(ell(c, (.0158 * k, .0158 * k, .0158 * k)), lo, hi, .0036 * k), mats, part="head")
