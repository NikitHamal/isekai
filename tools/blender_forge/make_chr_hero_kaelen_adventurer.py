#!/usr/bin/env python3
"""Kaelen - spellsword hero.  Base: VRoid Studio sample 'Sakurada Fumiriya' (CC0, pixiv Inc.) converted to the engine part-rig by vrm_forge,
then customised in Blender: raven-blue hair retint, steel cuirass + layered pauldrons + bracers + greaves + belt, crimson cloak, Aetherblade longsword.
Run: python3 make_chr_hero_kaelen_adventurer.py [vrm_path]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import anatomy_core as ac, vrm_forge as vf, armor_kit as ak
ROOT = ac.ROOT; VRM = vf.ensure_vrm("Sakurada_Fumiriya")

def tint(name, im):
    if "HAIR" in name: return ak.hue_ramp((.01, .012, .04), (.20, .27, .52), 1.6)(name, im)
    return im

def build(out):
    ch = vf.convert(VRM, 1.80, "kael", tint=tint, skirt_leg=0)
    steel = ac.material("k_steel", "steel", (.62, .67, .75), seed=7, nstr=.5); gold = ac.material("k_gold", "gold", (.95, .72, .25), seed=8, nstr=1.2)
    leather = ac.material("k_leather", "leather", (.30, .17, .08), seed=5); dleather = ac.material("k_dleather", "leather", (.13, .08, .05), seed=6)
    red = ac.material("k_cloak", "cloth", (.50, .04, .07), seed=9, nstr=4, double=True); blue = ac.material("k_cloak_in", "cloth", (.05, .07, .22), seed=10, nstr=4, double=True)
    P = ch.pivots; B = ch.bones; k = ch.height / 1.8
    ak.cuirass(ch, "torso_cuirass", steel, B["J_Bip_C_Spine"][2] + .02 * k, B["J_Bip_C_UpperChest"][2] + .09 * k, pad=.016 * k)
    ak.cuirass(ch, "torso_belt", leather, B["J_Bip_C_Hips"][2] + .07 * k, B["J_Bip_C_Hips"][2] + .13 * k, pad=.012 * k, n=3, solid=.006)
    ak.cuirass(ch, "torso_gorget", steel, B["J_Bip_C_Neck"][2] - .03 * k, B["J_Bip_C_Neck"][2] + .01 * k, pad=-.015 * k, n=3, bulge=0)
    for s in "lr":
        ak.pauldron(ch, s, steel, gold)
        E, W = B["J_Bip_%s_LowerArm" % s.upper()], B["J_Bip_%s_Hand" % s.upper()]
        ak.plate(ch, "forearm_%s_bracer" % s, dleather, "forearm_" + s, E, W, .30, .92, ["forearm_" + s], pad=.008 * k, n=4, rmax=.07 * k)
        ak.plate(ch, "forearm_%s_bracer_trim" % s, gold, "forearm_" + s, E, W, .30, .34, ["forearm_" + s], pad=.014 * k, n=2, solid=.004, rmax=.07 * k)
        K, A = B["J_Bip_%s_LowerLeg" % s.upper()], B["J_Bip_%s_Foot" % s.upper()]
        ak.plate(ch, "shin_%s_greave" % s, steel, "shin_" + s, K + (A - K) * .02, A, .02, .70, ["shin_" + s], pad=.014 * k, n=5, ref=(1, 0, 0), rmax=.09 * k)
        ak.knee(ch, s, steel, gold); ak.plate(ch, "shin_%s_cuff" % s, gold, "shin_" + s, K, A, -.03, .02, ["shin_" + s], pad=.026 * k, n=2, solid=.004)
    ak.cloak(ch, red, blue, spread=.5)
    d = np.array([0, -.55, .83]); d /= np.linalg.norm(d); hand = B["J_Bip_R_Hand"] + (B["J_Bip_R_Hand"] - B["J_Bip_R_LowerArm"]) * .22
    ak.import_prop(os.path.join(ROOT, "assets/models/weapons/wpn_aetherblade_longsword.glb"), "weapon_r", ch, hand - d * .13 * k, d, 1.08 * k, tag="sword")
    vf.export_char(out, ch)

if __name__ == "__main__":
    build(os.path.join(ROOT, "assets/models/characters/chr_hero_kaelen_adventurer.glb"))
