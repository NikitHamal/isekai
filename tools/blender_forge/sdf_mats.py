#!/usr/bin/env python3
"""Procedural PBR material library for SDF creatures (3D-space textures: no seams on any UV island)."""
import numpy as np
from sdf_bake import Mat, noise, fbm

def C(*c): return np.array(c, float)
def mix(a, b, t): return a * (1 - t[:, None]) + b * t[:, None]
def ridge(x, w=.06): return np.clip(1 - np.abs(x - .5) / w, 0, 1)
def const(n, v): return np.full(n, v, float)

def skin(name, base, dark, light=None, pore=1.0, rough=.55, scars=0.0, paint=None, nstr=1.0, veins=None, wrinkle=1.0):
    base, dark = C(*base), C(*dark); light = C(*(light or base)) * 1.0
    def color(P, N):
        t = fbm(P, 1.2, 4, 3); a = mix(dark, base, np.clip(t * 1.6 - .2, 0, 1)); a = mix(a, light, np.clip(N[:, 2] * .5 + .1, 0, 1) * .5)
        a *= (.9 + .2 * noise(P, 22, 8))[:, None]
        if scars: s = ridge(fbm(P, 2.5, 3, 11), .025) * scars; a = mix(a, C(.62, .42, .38) * base / (base.max() + 1e-6) * 1.2, np.clip(s, 0, 1))
        if veins is not None: v = ridge(fbm(P, 3.5, 3, 19), .03); a = mix(a, C(*veins), v * .4)
        if paint is not None: pm = ridge(noise(P * [9, 1, 1], 1.7, 31), .028); a = mix(a, C(*paint), np.clip(pm * (P[:, 2] > 1.78), 0, 1))
        return np.clip(a, 0, 1), const(len(P), rough) - .1 * noise(P, 9, 5), const(len(P), 0), None
    def height(P, N): return .0016 * pore * noise(P, 38, 6) + .0035 * wrinkle * ridge(fbm(P, 3.0, 3, 21), .12) + .0022 * fbm(P, 9, 3, 2)
    return Mat(name, color, height, nstr)

def fur(name, base, tip, belly=None, saddle=None, rough=.85, along=(1, 1, 4), nstr=1.0, mask=(.0, 1.), dirt=.3):
    base, tip = C(*base), C(*tip); belly = C(*(belly or base)); saddle = C(*(saddle or base)); al = np.array(along, float)
    def color(P, N):
        st = noise(P * al, 38, 4) * .6 + noise(P * al, 90, 6) * .4; blot = fbm(P, 1.6, 4, 9)
        a = mix(base, tip, np.clip(st * 1.4 - .3, 0, 1) * .55 + .2 * blot); up = np.clip(N[:, 2] * 1.4, 0, 1); a = mix(a, saddle, up * np.clip(blot * 1.8 - .4, 0, 1) * .8)
        a = mix(a, belly, np.clip(-N[:, 2] * 1.6, 0, 1)); a *= (.55 + .6 * st)[:, None] * (1 - dirt * .5 * (noise(P, 6, 14)[:, None]))
        return np.clip(a, 0, 1), const(len(P), rough), const(len(P), 0), None
    def height(P, N): return .0045 * (noise(P * al, 38, 4) * .6 + noise(P * al, 90, 6) * .4)
    return Mat(name, color, height, nstr)

def leather(name, base, rough=.6, wear=1.0):
    base = C(*base)
    def color(P, N):
        t = fbm(P, 2, 4, 7); cr = ridge(fbm(P, 9, 3, 12), .05); a = base[None] * (.55 + .8 * t)[:, None] * (1 - .35 * cr)[:, None] * (1 - .25 * wear * noise(P, 4, 15))[:, None]
        return np.clip(a, 0, 1), np.clip(rough + .25 * (1 - t) + .1 * cr, 0, 1), const(len(P), 0), None
    def height(P, N): return .0022 * fbm(P, 24, 3, 8) - .0018 * ridge(fbm(P, 9, 3, 12), .05)
    return Mat(name, color, height, 1.0, double=True)

def cloth(name, base, base2=None, weave=60.0, rough=.9):
    base = C(*base); b2 = C(*(base2 or base)) * 1.0
    def wv(P): return np.sin(P[:, 0] * weave + np.sin(P[:, 2] * 3) * 2) * np.sin(P[:, 2] * weave + P[:, 1] * weave * .5) * .5 + .5
    def color(P, N):
        f = fbm(P, 1.8, 4, 17); a = mix(base, b2, np.clip(f * 1.5 - .25, 0, 1)); a *= (.82 + .25 * wv(P) + .15 * noise(P, 10, 18))[:, None]
        return np.clip(a, 0, 1), const(len(P), rough), const(len(P), 0), None
    def height(P, N): return .0012 * wv(P) + .002 * fbm(P, 5, 3, 19)
    return Mat(name, color, height, 1.0, double=True)

def metal(name, base, rough=.38, rust=0.0, metalness=.92, dent=1.0):
    base = C(*base)
    def color(P, N):
        br = noise(P * [1, 1, 12], 14, 22); sc = ridge(fbm(P, 18, 3, 23), .02); t = fbm(P, 4, 3, 24); a = base[None] * (.6 + .6 * br + .5 * sc * .6)[:, None] * (.85 + .3 * t)[:, None]
        rm = np.clip((fbm(P, 3, 4, 25) - .55) * 4, 0, 1) * rust; a = mix(a, C(.36, .16, .06), rm)
        return np.clip(a, 0, 1), np.clip(rough + .3 * (1 - br) + .35 * rm, 0, 1), np.clip(metalness * (1 - rm * .85), 0, 1), None
    def height(P, N): return .0014 * noise(P * [1, 1, 12], 14, 22) + .0025 * dent * fbm(P, 3, 3, 26) - .0012 * ridge(fbm(P, 18, 3, 23), .02)
    return Mat(name, color, height, 1.0)

def bone(name, base=(.86, .80, .64), rough=.6):
    base = C(*base)
    def color(P, N):
        g = noise(P * [1, 1, 5], 20, 30); a = base[None] * (.7 + .4 * g)[:, None] * (1 - .35 * np.clip(fbm(P, 3, 3, 31) - .5, 0, 1) * 2)[:, None]
        return np.clip(a, 0, 1), const(len(P), rough), const(len(P), 0), None
    def height(P, N): return .003 * noise(P * [1, 1, 5], 20, 30)
    return Mat(name, color, height)

def eye(name, center, fwd, iris, sclera=(.9, .86, .7), slit=False, glow=0.0, emit_str=1.0):
    c, f = C(*center), C(*fwd); f = f / np.linalg.norm(f); sx = np.cross([0, 0, 1.], f); sx /= np.linalg.norm(sx); iris, sclera = C(*iris), C(*sclera)
    def color(P, N):
        q = np.stack([np.abs(P[:, 0]), P[:, 1], P[:, 2]], 1) - c; q /= np.linalg.norm(q, axis=1, keepdims=True) + 1e-9; cs = q @ f; xs = q @ sx
        pup = ((np.abs(xs) < .07) & (cs > .55)) if slit else (cs > .965); ir = cs > .8
        a = np.tile(sclera, (len(P), 1)) * (.85 + .15 * noise(P, 60, 40))[:, None]; a = mix(a, iris * (.6 + .6 * noise(P, 90, 41))[:, None], ir.astype(float)); a[pup] = (.02, .02, .02)
        a = mix(a, a * C(1, .55, .5), np.clip(1 - cs * 1.3, 0, 1) * .5)
        em = (iris[None] * (ir & ~pup)[:, None] * glow) if glow > 0 else None
        return np.clip(a, 0, 1), const(len(P), .15), const(len(P), 0), em
    return Mat(name, color, None, 1.0, emit_str=emit_str)

def fur_card(name, root, tip, stripe=.25):
    root, tip = C(*root), C(*tip)
    def card(S):
        v = 1 - (np.arange(S) + .5) / S; u = (np.arange(S) + .5) / S; U_, V_ = np.meshgrid(u, v); st = np.sin(U_ * 55 + np.sin(V_ * 6) * 2) * .5 + .5
        a = root[None, None] * (1 - V_[..., None]) + tip[None, None] * V_[..., None]; a = a * (1 - stripe + stripe * st[..., None]) * (.6 + .5 * V_[..., None])
        nm = np.dstack([.5 + (U_ - .5) * .35, np.full_like(U_, .5), np.ones_like(U_)]); nm[..., :2] = np.clip(nm[..., :2], 0, 1)
        return np.clip(a, 0, 1), np.full((S, S), .9), np.zeros((S, S)), nm
    return Mat(name, None, None, 1.0, double=True, card=card)
