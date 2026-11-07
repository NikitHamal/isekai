#!/usr/bin/env python3
"""Kaelen - spellsword hero. Real Blender build: lofted anatomy + sculpted face + fingered hands + layered steel armour + cloak. Run: python3 make_chr_hero_kaelen_adventurer.py"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anatomy_core import *
from anatomy_face import *
from anatomy_body import *

def build(out_path):
    reset(); random.seed(11)
    skin = material("kael_skin", "skin", (.80, .56, .43), seed=2)
    tunic = material("kael_tunic", "cloth", (.07, .08, .13), seed=3, nstr=4)
    pants = material("kael_pants", "cloth", (.10, .09, .09), seed=4, nstr=4)
    leather = material("kael_leather", "leather", (.30, .17, .08), seed=5)
    dleather = material("kael_dleather", "leather", (.14, .08, .05), seed=6)
    steel = material("kael_steel", "plate", (.66, .70, .76), seed=7, nstr=2.5)
    gold = material("kael_gold", "gold", (.95, .72, .25), seed=8, nstr=1.5)
    blue = material("kael_cloak_blue", "cloth", (.05, .07, .22), seed=9, nstr=5, double=True)
    red = material("kael_cloak_red", "cloth", (.46, .04, .06), seed=10, nstr=5, double=True)
    blade = material("kael_blade", "steel", (.78, .85, .95), seed=12, nstr=1.5, emit=(.15, .45, 1.0), emit_str=0.9)
    glow = material("kael_rune", "glow", (.3, .65, 1.0), seed=13, emit=(.3, .7, 1.0), emit_str=3.0)
    # --- body
    torso(tunic, 1.0, "torso_body")
    build_head(skin, eye_rgb=(.18, .60, .95), jaw=1.02, brow=1.1, pivot=(0, 0, 1.53), nm="head")
    random.seed(5); pv = (0, 0, 1.53); locks = []
    for i in range(9):  # top & crown spikes
        a = -math.pi * .5 + i / 8 * math.pi; locks.append(dict(root=(math.cos(a + math.pi) * .045, -.01 + math.sin(a) * .035 * 0 + (i - 4) * .0, 1.815), dir=(math.sin(a) * .8, -.2 + random.uniform(-.3, .3), 1.0), length=random.uniform(.11, .17), r=.017, n=5, curl=(0, .1, .5)))
    for i in range(7):  # bangs: short fringe swept sideways, clear of the eyes
        x = (i - 3) * .026; locks.append(dict(root=(x, -.082 - abs(i - 3) * .003, 1.786), dir=(x * 5 + (.2 if i >= 3 else -.2), -.30, -.35), length=random.uniform(.055, .075), r=.0125, n=4, curl=(0, .15, -.25)))
    for sx in (-1, 1):  # side locks framing the face over the ears
        for j in range(3): locks.append(dict(root=(sx * (.090 + j * .004), .0 + j * .02, 1.75 - j * .018), dir=(sx * .35, .1, -1.0), length=.09 - j * .012, r=.012, n=5, curl=(0, 0, -.3)))
    for i in range(10):  # back spikes
        a = i / 9 * 2 - 1; locks.append(dict(root=(a * .075, .085, 1.77 - abs(a) * .03), dir=(a * 1.0, .9, .3 + random.uniform(-.2, .3)), length=random.uniform(.13, .2), r=.017, n=5, curl=(0, .2, -.5)))
    hair_clumps((.025, .025, .035), locks, pivot=pv, nm="head_hair")
    # --- arms (left relaxed, right gripping sword) + pauldrons + bracers
    arm_l = upper_arm("l", tunic, 1.0, "arm"); mirror_r = upper_arm("r", tunic, 1.0, "arm", S=mx(JOINT["sho"]), E=V((-.285, .05, 1.14)))
    fl = forearm("l", skin, 1.0, "forearm"); fr = forearm("r", skin, 1.0, "forearm", E=V((-.285, .05, 1.14)))
    hand_relaxed("l", skin, JOINT["wrist_l"], 1.0, "forearm")
    G = V((-.305, -.215, .915)); hand_grip("r", skin, JOINT["wrist_r"], G, 1.0, "forearm", E=V((-.285, .05, 1.14)))
    for side, S, E, W in (("l", JOINT["sho"], JOINT["elbow"], JOINT["wrist_l"]), ("r", mx(JOINT["sho"]), V((-.285, .05, 1.14)), JOINT["wrist_r"])):
        sx = 1 if side == "l" else -1; d = W - E
        loft("forearm_%s_bracer" % side, [(E + d * .38, .047, .045), (E + d * .55, .045, .042), (E + d * .84, .035, .032), (E + d * .98, .0345, .031)], dleather, segs=16, ref=(0, 0, 1), sub=1, pivot=E, solid=.006)
        loft("forearm_%s_bracer_trim" % side, [(E + d * .385, .0485, .0465), (E + d * .405, .0485, .0465)], gold, segs=16, ref=(0, 0, 1), sub=1, pivot=E, caps=(False, False), solid=.004)
        for k, (zz, sc, dx) in enumerate(((0.012, 1.0, 0.0), (-0.030, .95, .006), (-0.066, .88, .012))):  # layered pauldron lames
            prim("arm_%s_pauldron%d" % (side, k), "sphere", steel, (.102 * sc, .092 * sc, .062 * sc), (S.x + sx * dx, S.y, S.z + zz), sub=1, pivot=S, solid=.007, segs=18, keep=lambda c, zz=zz, S=S: c.z > S.z + zz - .02)
        loft("arm_%s_pauldron_rim" % side, [(S + V((sx * .0, 0, 0.0)), .1, .09)], gold, segs=4, sub=0) if False else None
        loft("arm_%s_sleeve_cuff" % side, [(S + (E - S) * .62, .052, .054), (S + (E - S) * .70, .054, .056)], dleather, segs=14, sub=1, pivot=S, caps=(False, False), solid=.006)
    # --- legs: trousers, high boots
    for side in ("l", "r"):
        leg(side, pants, 1.0, "leg"); shin(side, pants, 1.0, "shin"); sx = 1 if side == "l" else -1
        kn = V((sx * .092, -.006, .505))
        loft("shin_%s_boot" % side, [(V((sx * .092, .0, .495)), .066, .072), (V((sx * .092, .006, .43)), .063, .072), (V((sx * .092, .012, .33)), .063, .074), (V((sx * .092, .012, .20)), .050, .056), (V((sx * .092, .010, .10)), .046, .050)], leather, segs=16, sub=1, pivot=kn, caps=(False, False), solid=.008)
        loft("shin_%s_boot_cuff" % side, [(V((sx * .092, .0, .525)), .074, .08), (V((sx * .092, -.002, .495)), .072, .078)], dleather, segs=16, sub=1, pivot=kn, caps=(False, True), solid=.007)
        foot(side, leather, 1.06, "shin")
        for kk in range(3): loft("shin_%s_strap%d" % (side, kk), [(V((sx * .092, .012, .43 - kk * .085)), .069, .078), (V((sx * .092, .012, .415 - kk * .085)), .069, .078)], dleather, segs=14, sub=0, pivot=kn, caps=(False, False), solid=.006)
        loft("shin_%s_knee" % side, [(V((sx * .092, -.052, .525)), .042, .028), (V((sx * .092, -.056, .505)), .046, .03), (V((sx * .092, -.05, .48)), .040, .026)], steel, segs=14, ref=(1, 0, 0), sub=1, pivot=kn)
    # --- cuirass, gorget, belt, tassets
    cu = loft("torso_cuirass", [(V((0, -.004, 1.18)), .148, .108), (V((0, -.008, 1.25)), .176, .124), (V((0, -.012, 1.34)), .196, .134, 2.3), (V((0, -.008, 1.42)), .198, .122, 2.4), (V((0, 0, 1.475)), .140, .092)], steel, segs=26, sub=1, pivot=JOINT["waist"], solid=.010, caps=(False, False))
    sculpt(cu, lambda p: V((0, -.012 * max(0, 1 - abs(p.x) / .018) - .020 * max(0, 1 - ((abs(p.x) - .085) / .07) ** 2) * (p.z > 1.27), 0)) if p.y < 0 else V((0, 0, 0)))
    loft("torso_gorget", [(V((0, .003, 1.485)), .098, .092), (V((0, .004, 1.525)), .068, .072)], steel, segs=20, sub=1, pivot=JOINT["waist"], solid=.008, caps=(False, False))
    loft("torso_collar", [(V((0, .004, 1.52)), .074, .078), (V((0, .004, 1.54)), .07, .074)], blue, segs=20, sub=1, pivot=JOINT["waist"], solid=.008, caps=(False, False))
    loft("torso_belt", [(V((0, .001, 1.075)), .150, .112), (V((0, .001, 1.125)), .152, .114)], dleather, segs=24, sub=1, pivot=JOINT["waist"], solid=.008, caps=(False, False))
    prim("torso_buckle", "cube", gold, (.026, .006, .022), (0, -.116, 1.10), sub=0, pivot=JOINT["waist"], bevel=.004)
    for k in range(9):  # tasset plates (skirt) hanging from the belt
        a = math.radians(-128 + k * 32); r = .17; c = V((math.sin(a) * r * .95, -math.cos(a) * r * .72, .98))
        prim("torso_tasset%d" % k, "cube", dleather if k % 2 else steel, (.034, .006, .095), c, rot=(0, 0, -a * 1.0 + math.pi * 0), sub=1, pivot=JOINT["waist"], bevel=.004, solid=None)
    # --- cloak (separate part): blue outside, crimson lining, wind-ready folds
    grid = []
    for i in range(24):
        t = i / 23; row = []
        for k in range(19):
            u = k / 18 * 2 - 1; wd = .185 + .17 * t ** 1.1
            y = .088 + .11 * t ** 1.3 - .06 * u * u * (1 - t * .5) + math.sin(u * 4.4 + t * 1.2) * .02 * t
            row.append(V((u * wd, y, 1.50 - 1.08 * t + (u * u) * .035 * t - math.sin(u * 7 + 1) * .008 * t)))
        grid.append(row)
    sheet("cloak", grid, blue, sub=1, pivot=V((0, .05, 1.50)), solid=.012, mat2=red)
    # --- Aetherblade longsword gripped in the right fist (vertical grip, blade up)
    gp = G
    tube("weapon_r_grip", [gp + V(0, 0, -.085), gp + V(0, 0, .075)], [.0155, .0155], dleather, segs=12, sub=0, pivot=V((-.285, .05, 1.14)))
    prim("weapon_r_pommel", "sphere", gold, (.026, .026, .024), gp + V(0, 0, -.100), sub=1, pivot=V((-.285, .05, 1.14)))
    loft("weapon_r_guard", [(gp + V(-.115, 0, .088), .007, .011), (gp + V(-.06, 0, .088), .013, .016), (gp + V(0, 0, .088), .017, .022), (gp + V(.06, 0, .088), .013, .016), (gp + V(.115, 0, .088), .007, .011)], gold, segs=8, ref=(0, 1, 0), sub=1, pivot=V((-.285, .05, 1.14)))
    loft("weapon_r_blade", [(gp + V(0, 0, .094), .0125, .0095, 1.0), (gp + V(0, 0, .30), .0215, .0085, 1.0), (gp + V(0, 0, .70), .0205, .0075, 1.0), (gp + V(0, 0, .96), .0160, .0055, 1.0), (gp + V(0, 0, 1.06), .004, .002, 1.0)], blade, segs=4, ref=(0, 1, 0), tile=.2, sub=0, pivot=V((-.285, .05, 1.14)))
    loft("weapon_r_runes", [(gp + V(0, -.0075, .16), .0055, .0016), (gp + V(0, -.0082, .55), .0055, .0016), (gp + V(0, -.0066, .90), .0030, .0012)], glow, segs=6, sub=0, pivot=V((-.285, .05, 1.14)))
    scale_all(1.0)
    return export(out_path)

if __name__ == "__main__":
    build(os.path.join(ROOT, "assets", "models", "characters", "chr_hero_kaelen_adventurer.glb"))
