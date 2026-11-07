#!/usr/bin/env python3
"""Garrick - royal paladin.  Base: VRoid Studio 'AvatarSample_C' (free-use, pixiv Inc.) -> engine part-rig (vrm_forge), then heavy silver plate,
four-layer pauldrons, greaves, royal-blue cloak, crest heater shield and Aetherblade sword added in Blender."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, anatomy_core as ac, vrm_forge as vf, armor_kit as ak
ROOT = ac.ROOT
def tint(name, im):
    if "HAIR" in name: return ak.hue_ramp((.20, .12, .03), (.98, .80, .38), 1.0)(name, im)
    if "Tops" in name or "Bottoms" in name: return ak.hue_ramp((.015, .02, .07), (.16, .24, .55), 1.1)(name, im)
    return im
def build(out):
    ch = vf.convert(vf.ensure_vrm("AvatarSample_C"), 1.92, "garr", tint=tint, skirt_leg=.55)
    sil = ac.material("g_plate", "steel", (.84, .86, .90), seed=21, nstr=.45); gold = ac.material("g_gold", "gold", (.96, .76, .28), seed=22, nstr=1.0)
    lea = ac.material("g_leather", "leather", (.20, .11, .06), seed=23); blue = ac.material("g_cloak", "cloth", (.05, .12, .46), seed=24, nstr=4, double=True); wh = ac.material("g_lining", "cloth", (.86, .84, .78), seed=25, nstr=4, double=True)
    B = ch.bones; k = ch.height / 1.8
    ak.cuirass(ch, "torso_cuirass", sil, B["J_Bip_C_Spine"][2] - .02 * k, B["J_Bip_C_UpperChest"][2] + .10 * k, pad=.028 * k, bulge=1.6)
    ak.cuirass(ch, "torso_beltplate", gold, B["J_Bip_C_Hips"][2] + .08 * k, B["J_Bip_C_Hips"][2] + .14 * k, pad=.024 * k, n=3, solid=.006)
    ak.cuirass(ch, "torso_gorget", sil, B["J_Bip_C_Neck"][2] - .035 * k, B["J_Bip_C_Neck"][2] + .015 * k, pad=-.012 * k, n=3, bulge=0)
    for s in "lr":
        ak.pauldron(ch, s, sil, gold, layers=4, size=1.22)
        E, W = B["J_Bip_%s_LowerArm" % s.upper()], B["J_Bip_%s_Hand" % s.upper()]
        ak.plate(ch, "forearm_%s_vambrace" % s, sil, "forearm_" + s, E, W, .12, .90, ["forearm_" + s], pad=.014 * k, n=4, rmax=.07 * k, flare=1.25)
        ak.plate(ch, "forearm_%s_vambrace_trim" % s, gold, "forearm_" + s, E, W, .12, .16, ["forearm_" + s], pad=.020 * k, n=2, solid=.004, rmax=.07 * k)
        Hh, K, A = B["J_Bip_%s_UpperLeg" % s.upper()], B["J_Bip_%s_LowerLeg" % s.upper()], B["J_Bip_%s_Foot" % s.upper()]
        ak.plate(ch, "leg_%s_cuisse" % s, sil, "leg_" + s, Hh, K, .30, .92, ["leg_" + s], pad=.016 * k, n=4, ref=(1, 0, 0), rmax=.12 * k)
        ak.plate(ch, "shin_%s_greave" % s, sil, "shin_" + s, K, A, .02, .72, ["shin_" + s], pad=.016 * k, n=5, ref=(1, 0, 0), rmax=.09 * k)
        ak.knee(ch, s, sil, gold, 1.15)
    ak.cloak(ch, blue, wh, spread=.55, z_bot=ch.height * .2)
    d = np.array([0, -.50, .86]); hand = B["J_Bip_R_Hand"] + (B["J_Bip_R_Hand"] - B["J_Bip_R_LowerArm"]) * .22
    ak.import_prop(os.path.join(ROOT, "assets/models/weapons/wpn_aetherblade_longsword.glb"), "weapon_r", ch, hand - d * .13 * k, d, 1.12 * k, tag="sword")
    mid = (B["J_Bip_L_LowerArm"] + B["J_Bip_L_Hand"]) / 2
    ak.import_prop(os.path.join(ROOT, "assets/models/weapons/wpn_royal_crest_heater_shield.glb"), "forearm_l", ch, mid + np.array([.075 * k, -.03, -.36 * k]), (0, 0, 1), .86 * k, roll=np.pi / 2, tag="shield")
    vf.export_char(out, ch)
if __name__ == "__main__": build(os.path.join(ROOT, "assets/models/characters/chr_ally_garrick_royal_paladin.glb"))
