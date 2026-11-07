#!/usr/bin/env python3
"""Lyra - beastkin rogue.  Base: VRoid Studio sample 'Vivi' (CC0, pixiv Inc.), customised in Blender with fox/cat ears, a swaying fur tail
(engine tail part), leather bracers + belt + scarf and twin daggers (Aetherblade re-scaled)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, anatomy_core as ac, vrm_forge as vf, armor_kit as ak
ROOT = ac.ROOT
def build(out):
    ch = vf.convert(vf.ensure_vrm("Vivi"), 1.60, "lyra", hair="cloak", skirt="cloak", skirt_leg=.55)
    fur = ac.material("l_fur", "fur", (.52, .31, .17), seed=41); pink = ac.material("l_ear", "skin", (.95, .62, .60), seed=42)
    lea = ac.material("l_leather", "leather", (.16, .09, .06), seed=43); red = ac.material("l_scarf", "cloth", (.55, .06, .08), seed=44, nstr=4, double=True); gold = ac.material("l_gold", "gold", (.9, .7, .3), seed=45)
    B = ch.bones; k = ch.height / 1.8; H = B["J_Bip_C_Head"]
    for s in "lr":
        sx = 1 if s == "l" else -1; ak.ear(ch, s, fur, (sx * .058 * k, H[1] - .01, H[2] + .11 * k), .115 * k, .05 * k, tilt=-.15, spread=.42, name="head_catear")
        ak.ear(ch, s, pink, (sx * .058 * k, H[1] - .028, H[2] + .112 * k), .085 * k, .033 * k, tilt=-.15, spread=.42, name="head_catear_in")
        E, W = B["J_Bip_%s_LowerArm" % s.upper()], B["J_Bip_%s_Hand" % s.upper()]
        ak.plate(ch, "forearm_%s_bracer" % s, lea, "forearm_" + s, E, W, .35, .92, ["forearm_" + s], pad=.008 * k, n=4, rmax=.06 * k)
    hz = B["J_Bip_C_Hips"][2]; ak.cuirass(ch, "torso_belt", lea, hz + .06 * k, hz + .11 * k, pad=.012 * k, n=3, solid=.006)
    ak.cuirass(ch, "torso_scarf", red, B["J_Bip_C_Neck"][2] - .045 * k, B["J_Bip_C_Neck"][2] + .0, pad=.0, n=3, bulge=0)
    hp = B["J_Bip_C_Hips"]; pts = [hp + np.array(v) * k for v in ((0, .08, -.02), (0, .17, -.03), (0, .27, .0), (0, .35, .1), (0, .37, .24), (0, .33, .36))]
    ak.swoosh("tail_fur", fur, "tail", ch, pts, [.040 * k, .045 * k, .042 * k, .036 * k, .028 * k, .014 * k], flat=1.0)
    d = np.array([0, -.62, .78]); d /= np.linalg.norm(d); sw = os.path.join(ROOT, "assets/models/weapons/wpn_aetherblade_longsword.glb")
    hr = B["J_Bip_R_Hand"] + (B["J_Bip_R_Hand"] - B["J_Bip_R_LowerArm"]) * .22; hl = B["J_Bip_L_Hand"] + (B["J_Bip_L_Hand"] - B["J_Bip_L_LowerArm"]) * .22
    ak.import_prop(sw, "weapon_r", ch, hr - d * .05 * k, d, .56 * k, tag="dagger")
    ak.import_prop(sw, "forearm_l", ch, hl - d * .05 * k, d, .56 * k, tag="dagger")
    vf.export_char(out, ch)
if __name__ == "__main__": build(os.path.join(ROOT, "assets/models/characters/chr_ally_lyra_beastkin_rogue.glb"))
