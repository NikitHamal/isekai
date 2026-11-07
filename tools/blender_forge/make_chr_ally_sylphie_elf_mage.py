#!/usr/bin/env python3
"""Sylphie - high-elf archmage.  Base: VRoid Studio sample 'Victoria Rubin' (CC0, pixiv Inc.), customised in Blender with leaf-shaped elf ears,
a gold circlet + glowing gem, and an arcane crystal staff; hair and gown follow the cloak sway part."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, anatomy_core as ac, vrm_forge as vf, armor_kit as ak
ROOT = ac.ROOT
def build(out):
    ch = vf.convert(vf.ensure_vrm("Victoria_Rubin"), 1.76, "sylph", hair="cloak", skirt="cloak", skirt_leg=.55)
    skin = ac.material("s_skin", "skin", (.96, .80, .72), seed=31); gold = ac.material("s_gold", "gold", (.96, .78, .35), seed=32, nstr=1.0)
    wood = ac.material("s_wood", "leather", (.36, .24, .13), seed=33); glow = ac.material("s_gem", "glow", (.45, .85, 1.0), seed=34, emit=(.4, .85, 1.0), emit_str=3.2)
    B = ch.bones; k = ch.height / 1.8; H = B["J_Bip_C_Head"]
    for s in "lr": ak.ear(ch, s, skin, (np.sign(1 if s == "l" else -1) * .082 * k, H[1] + .005, H[2] + .075 * k), .105 * k, .022 * k)
    c = np.array([H[0], H[1] - .004, H[2] + .125 * k]); _, hx, hy = ak.section(ch, c[2], "head")
    ak._tag(ac.loft("head_circlet", [(ac.V(tuple(c)), hy + .012, hx + .012), (ac.V(tuple(c + [0, 0, .014 * k])), hy + .012, hx + .012)], gold, segs=30, ref=(0, 0, 1), caps=(False, False), pivot=ac.V(tuple(ch.pivots["head"])), solid=.004), "head")
    ak._tag(ac.prim("head_circlet_gem", "sphere", glow, (.014 * k, .01 * k, .022 * k), (c[0], c[1] - hy - .016, c[2] + .008), sub=1, pivot=ac.V(tuple(ch.pivots["head"])), segs=12), "head")
    hand = B["J_Bip_R_Hand"] + (B["J_Bip_R_Hand"] - B["J_Bip_R_LowerArm"]) * .22; base = hand + np.array([-.01, -.05, -.62 * k]); top = hand + np.array([-.02, -.16, 1.0 * k])
    ak.shaft(ch, "weapon_r_staff", wood, "weapon_r", base, top, .016 * k, .013 * k, 7)
    for t in (.12, .55, .93): ak.shaft(ch, "weapon_r_staff_ring%d" % int(t * 100), gold, "weapon_r", base + (top - base) * t, base + (top - base) * (t + .035), .024 * k, .024 * k, 2)
    ak._tag(ac.prim("weapon_r_staff_orb", "sphere", glow, (.055 * k,) * 3, tuple(top + np.array([0, -.012, .06 * k])), sub=2, pivot=ac.V(tuple(ch.pivots["weapon_r"])), segs=20), "weapon_r")
    for sx in (-1, 1): ak._tag(ac.prim("weapon_r_staff_prong%d" % sx, "cone", gold, (.012 * k, .008 * k, .085 * k), tuple(top + np.array([sx * .05 * k, 0, .035 * k])), rot=(0, -sx * .35, 0), sub=1, pivot=ac.V(tuple(ch.pivots["weapon_r"])), segs=8), "weapon_r")
    vf.export_char(out, ch)
if __name__ == "__main__": build(os.path.join(ROOT, "assets/models/characters/chr_ally_sylphie_elf_mage.glb"))
