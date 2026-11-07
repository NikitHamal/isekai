#!/usr/bin/env python3
"""Orc Warlord, Goblin Raider & Paladin Garrick: same real-Blender anatomical pipeline as the hero (lofted anatomy, sculpted face, fingered hands, armour)."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anatomy_core import *
from anatomy_face import *
from anatomy_body import *
EV = V((-.285, .05, 1.14)); G = V((-.305, -.215, .915))

def common(skin, top, bottom, boots, eye, face, bulk=1.0, bare_arms=False, bare_legs=False, grip=1.0):
    torso(top, bulk, "torso_body", belly=face.pop("belly", 0)); build_head(skin, eye_rgb=eye, nm="head", **face)
    upper_arm("l", skin if bare_arms else top, bulk, "arm"); upper_arm("r", skin if bare_arms else top, bulk, "arm", S=mx(JOINT["sho"]), E=EV)
    forearm("l", skin, bulk, "forearm"); forearm("r", skin, bulk, "forearm", E=EV); hand_relaxed("l", skin, JOINT["wrist_l"], bulk, "forearm")
    hand_grip("r", skin, JOINT["wrist_r"], G, bulk, "forearm", E=EV)
    for sd in "lr":
        leg(sd, skin if bare_legs else bottom, bulk, "leg"); shin(sd, skin if bare_legs else bottom, bulk, "shin"); sx = 1 if sd == "l" else -1; kn = V((sx * .092, -.006, .505))
        loft("shin_%s_boot" % sd, [(V((sx * .092, 0, .49)), .064 * bulk, .07 * bulk), (V((sx * .092, .012, .33)), .063 * bulk, .074 * bulk), (V((sx * .092, .01, .10)), .046 * bulk, .05 * bulk)], boots, segs=16, sub=1, pivot=kn, caps=(False, False), solid=.008)
        foot(sd, boots, 1.06 * bulk, "shin")

def pauldrons(mat, trim, spike=False, size=1.0):
    for sd in "lr":
        S = JOINT["sho"] if sd == "l" else mx(JOINT["sho"]); sx = 1 if sd == "l" else -1
        for k, (zz, sc) in enumerate(((.012, 1.0), (-.03, .94), (-.066, .86))):
            prim("arm_%s_pauldron%d" % (sd, k), "sphere", mat, (.102 * sc * size, .092 * sc * size, .062 * sc), (S.x + sx * k * .006, S.y, S.z + zz), sub=1, pivot=S, solid=.007, segs=18, keep=lambda c, zz=zz, S=S: c.z > S.z + zz - .02)
        if spike: prim("arm_%s_spike" % sd, "cone", trim, (.025, .025, .075), (S.x + sx * .03, S.y, S.z + .12), sub=0, pivot=S, segs=8)

def cloak_sheet(blue, red, w=.185):
    grid = []
    for i in range(24):
        t = i / 23; row = []
        for k in range(19):
            u = k / 18 * 2 - 1; wd = w + .17 * t ** 1.1
            row.append(V((u * wd, .088 + .11 * t ** 1.3 - .06 * u * u * (1 - t * .5) + math.sin(u * 4.4 + t * 1.2) * .02 * t, 1.50 - 1.0 * t + u * u * .035 * t)))
        grid.append(row)
    sheet("cloak", grid, blue, sub=1, pivot=V((0, .05, 1.50)), solid=.012, mat2=red)

def weapon_blade(kind, mat, gripm, trim):
    pv = EV; gp = G
    tube("weapon_r_grip", [gp + V(0, 0, -.12), gp + V(0, 0, .10)], [.0165, .0165], gripm, segs=12, sub=0, pivot=pv)
    if kind == "cleaver":
        loft("weapon_r_blade", [(gp + V(0, 0, .09), .035, .010, 2.4), (gp + V(0, 0, .22), .105, .011, 3.0), (gp + V(0, 0, .46), .150, .012, 3.0), (gp + V(0, 0, .62), .125, .010, 2.6), (gp + V(0, 0, .70), .03, .006, 2.0)], mat, segs=14, ref=(0, 1, 0), sub=1, pivot=pv)
        prim("weapon_r_spike", "cone", trim, (.02, .02, .09), gp + V(0, 0, -.2), rot=(math.pi, 0, 0), sub=0, pivot=pv, segs=8)
    elif kind == "dagger":
        loft("weapon_r_blade", [(gp + V(0, 0, .09), .016, .006, 1.0), (gp + V(.004, 0, .22), .022, .006, 1.0), (gp + V(.02, 0, .34), .012, .005, 1.0), (gp + V(.045, 0, .40), .002, .002, 1.0)], mat, segs=4, ref=(0, 1, 0), sub=0, pivot=pv)
    else:
        loft("weapon_r_blade", [(gp + V(0, 0, .094), .0125, .0095, 1.0), (gp + V(0, 0, .30), .0215, .0085, 1.0), (gp + V(0, 0, .75), .0200, .0075, 1.0), (gp + V(0, 0, 1.06), .004, .002, 1.0)], mat, segs=4, ref=(0, 1, 0), tile=.2, sub=0, pivot=pv)
    loft("weapon_r_guard", [(gp + V(-.08, 0, .09), .007, .011), (gp + V(0, 0, .09), .017, .022), (gp + V(.08, 0, .09), .007, .011)], trim, segs=8, ref=(0, 1, 0), sub=1, pivot=pv)
    prim("weapon_r_pommel", "sphere", trim, (.026, .026, .024), gp + V(0, 0, -.10), sub=1, pivot=pv)

def orc(path):
    reset(); random.seed(4)
    skin = material("orc_skin", "orc", (.30, .45, .20), seed=2, nstr=5); cloth = material("orc_hide", "leather", (.22, .13, .08), seed=3); fur = material("orc_fur", "fur", (.25, .17, .10), seed=4)
    iron = material("orc_iron", "plate", (.34, .35, .36), seed=5, nstr=4); bone = material("orc_bone", "bone", (.88, .82, .66), seed=6); dl = material("orc_boot", "leather", (.12, .08, .06), seed=7)
    common(skin, skin, cloth, dl, (.95, .65, .08), dict(hs=1.0, jaw=1.35, ear=.05, brow=1.8, nose=.8, tusk=.07, cheek=1.2, belly=.5), bulk=1.15, bare_arms=True)
    hair_clumps((.03, .03, .03), [dict(root=(0, -.06 + i * .03, 1.815 - abs(i - 2) * .004), dir=(0, .35, 1.0), length=.1 - abs(i - 2) * .01, r=.016, n=4, curl=(0, .5, -.2)) for i in range(5)] + [dict(root=(0, .09, 1.77), dir=(0, 1, .2), length=.2, r=.02, n=5, curl=(0, .4, -.6))], pivot=(0, 0, 1.53), cap=False, nm="head_mohawk")
    pauldrons(iron, bone, spike=True, size=1.15)
    loft("torso_harness_a", [(V((.17, -.13, 1.45)), .028, .01), (V((0, -.14, 1.3)), .03, .012), (V((-.15, -.115, 1.16)), .028, .01)], cloth, segs=8, ref=(0, 1, 0), sub=1, pivot=JOINT["waist"])
    loft("torso_harness_b", [(V((-.17, -.13, 1.45)), .028, .01), (V((0, -.14, 1.3)), .03, .012), (V((.15, -.115, 1.16)), .028, .01)], cloth, segs=8, ref=(0, 1, 0), sub=1, pivot=JOINT["waist"])
    prim("torso_plate", "sphere", iron, (.07, .02, .08), (0, -.152, 1.3), sub=1, pivot=JOINT["waist"], solid=.006)
    loft("torso_belt", [(V((0, .001, 1.05)), .17, .125), (V((0, .001, 1.12)), .172, .127)], cloth, segs=24, sub=1, pivot=JOINT["waist"], solid=.01, caps=(False, False))
    for k in range(7):
        a = math.radians(-120 + k * 40); prim("torso_fur%d" % k, "cone", fur, (.05, .02, .13), V((math.sin(a) * .17, -math.cos(a) * .13, .93)), rot=(math.pi, 0, 0), sub=1, pivot=JOINT["waist"], segs=8)
    for sd in "lr":
        sx = 1 if sd == "l" else -1; E = JOINT["elbow"] if sd == "l" else EV; W = JOINT["wrist_l"] if sd == "l" else JOINT["wrist_r"]; d = W - E
        loft("forearm_%s_bracer" % sd, [(E + d * .4, .056, .054), (E + d * .85, .042, .039)], iron, segs=14, ref=(0, 0, 1), sub=1, pivot=E, solid=.007)
    weapon_blade("cleaver", iron, cloth, bone)
    scale_all(1.0, 1.28, 1.15); export(path)

def goblin(path):
    reset(); random.seed(8)
    skin = material("gob_skin", "orc", (.50, .58, .20), seed=2, nstr=4); vest = material("gob_vest", "leather", (.27, .16, .08), seed=3); cloth = material("gob_rag", "cloth", (.30, .24, .12), seed=4)
    steel = material("gob_steel", "steel", (.55, .55, .5), seed=5, nstr=4); dl = material("gob_boot", "leather", (.16, .1, .06), seed=6)
    common(skin, vest, cloth, dl, (.95, .9, .1), dict(hs=1.35, jaw=.9, ear=.16, brow=1.5, nose=1.8, cheek=.9, lash=False), bulk=.85, bare_arms=True)
    hair_clumps((.12, .10, .05), [dict(root=(0, .0 + i * .02, 1.83), dir=(0, .2 * (i - 2), 1.0), length=.05, r=.01, n=3, curl=(0, .3, 0)) for i in range(4)], pivot=(0, 0, 1.53), cap=False, nm="head_tuft")
    loft("torso_belt", [(V((0, .001, 1.06)), .15, .112), (V((0, .001, 1.12)), .152, .114)], dl, segs=20, sub=1, pivot=JOINT["waist"], solid=.008, caps=(False, False))
    pauldrons(vest, steel, size=.8)
    weapon_blade("dagger", steel, dl, steel)
    scale_all(0.64, 1.0, 1.0); export(path)

def paladin(path):
    reset(); random.seed(2)
    skin = material("pal_skin", "skin", (.78, .56, .45), seed=2); under = material("pal_under", "cloth", (.12, .12, .2), seed=3)
    steel = material("pal_steel", "plate", (.82, .84, .88), seed=4, nstr=2); gold = material("pal_gold", "gold", (.95, .74, .26), seed=5, nstr=1.5)
    white = material("pal_cloak", "cloth", (.86, .85, .82), seed=6, double=True); blue = material("pal_blue", "cloth", (.08, .18, .55), seed=7, double=True); dl = material("pal_boot", "leather", (.2, .12, .07), seed=8)
    common(skin, under, under, dl, (.3, .55, .85), dict(jaw=1.1, brow=1.0), bulk=1.1)
    for sd in "lr":
        sx = 1 if sd == "l" else -1; E = JOINT["elbow"] if sd == "l" else EV; W = JOINT["wrist_l"] if sd == "l" else JOINT["wrist_r"]; d = W - E; S = JOINT["sho"] if sd == "l" else mx(JOINT["sho"])
        loft("forearm_%s_vambrace" % sd, [(E - d * .04, .052, .05), (E + d * .35, .058, .056), (E + d * .85, .045, .042), (E + d * 1.0, .047, .043)], steel, segs=16, ref=(0, 0, 1), sub=1, pivot=E, solid=.008)
        loft("arm_%s_rerebrace" % sd, [(S + (E - S) * .25, .066, .066), (S + (E - S) * .85, .052, .054)], steel, segs=16, sub=1, pivot=S, solid=.008, caps=(False, False))
        K = V((sx * .092, -.006, .505))
        loft("shin_%s_greave" % sd, [(V((sx * .092, 0, .52)), .066 * 1.1, .07 * 1.1), (V((sx * .092, .006, .40)), .068 * 1.1, .078 * 1.1), (V((sx * .092, .01, .13)), .05 * 1.1, .055 * 1.1)], steel, segs=18, sub=1, pivot=K, caps=(False, False), solid=.009)
        loft("leg_%s_cuisse" % sd, [(V((sx * .092, -.004, .88)), .098 * 1.1, .106 * 1.1), (V((sx * .090, -.006, .60)), .08 * 1.1, .086 * 1.1)], steel, segs=18, pivot=V((sx * .092, 0, .93)), sub=1, solid=.009, caps=(False, False))
        prim("shin_%s_poleyn" % sd, "sphere", gold, (.05, .035, .05), (sx * .092, -.05, .505), sub=1, pivot=K)
    pauldrons(steel, gold, size=1.25)
    cu = loft("torso_cuirass", [(V((0, 0, 1.12)), .16 * 1.1, .114 * 1.1), (V((0, -.01, 1.25)), .19 * 1.1, .13 * 1.1), (V((0, -.014, 1.35)), .215 * 1.1, .14 * 1.1, 2.3), (V((0, -.006, 1.43)), .21 * 1.1, .124 * 1.1, 2.4), (V((0, .002, 1.48)), .14 * 1.1, .095 * 1.1)], steel, segs=28, sub=1, pivot=JOINT["waist"], solid=.012, caps=(False, False))
    sculpt(cu, lambda p: V((0, -.016 * max(0, 1 - abs(p.x) / .02) - .02 * max(0, 1 - ((abs(p.x) - .09) / .07) ** 2) * (p.z > 1.27), 0)) if p.y < 0 else V((0, 0, 0)))
    for k in range(4): loft("torso_fauld%d" % k, [(V((0, 0, 1.13 - k * .035)), (.158 + k * .006) * 1.1, (.115 + k * .004) * 1.1), (V((0, 0, 1.115 - k * .035)), (.16 + k * .006) * 1.1, (.117 + k * .004) * 1.1)], gold if k == 0 else steel, segs=24, sub=1, pivot=JOINT["waist"], caps=(False, False), solid=.008)
    sheet("torso_tabard", [[V((u * (.12 - t * .015), -.135 - t * .03, 1.1 - t * .55 + 0)) for u in [i / 8 * 2 - 1 for i in range(9)]] for t in [j / 10 for j in range(11)]], blue, sub=1, pivot=JOINT["waist"], solid=.01)
    helm = loft("head_helm", [(V((0, .012, 1.575)), .056, .06), (V((0, .006, 1.62)), .092, .1), (V((0, .006, 1.70)), .105, .115), (V((0, .012, 1.78)), .094, .105), (V((0, .016, 1.835)), .05, .06), (V((0, .018, 1.85)), .02, .026)], steel, segs=28, pivot=V((0, 0, 1.53)), sub=1, solid=.008, keep=lambda c: not (c.y < -.025 and 1.625 < c.z < 1.745 and abs(c.x) < .066))
    hair_clumps((.8, .75, .62), [dict(root=(0, .03, 1.85), dir=(0, .5, 1.0), length=.22, r=.02, n=6, curl=(0, .5, -.5)) for _ in range(1)] + [dict(root=(i * .004, .03 + i * .004, 1.85), dir=(i * .15, .6, .8), length=.2, r=.014, n=6, curl=(0, .5, -.6)) for i in (-2, -1, 1, 2)], pivot=(0, 0, 1.53), cap=False, nm="head_plume")
    cloak_sheet(white, blue, .2); weapon_blade("sword", steel, dl, gold)
    scale_all(1.04, 1.0, 1.0); export(path)

if __name__ == "__main__":
    m = os.path.join(ROOT, "assets", "models")
    orc(m + "/monsters/mon_orc_warlord_berserker.glb"); goblin(m + "/monsters/mon_forest_goblin_raider.glb"); paladin(m + "/characters/chr_ally_garrick_royal_paladin.glb")
