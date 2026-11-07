from common import *
import numpy as np
S = lambda sx: sx
def limb(pts, rad, **k): return spline_tube(pts, rad, rings=k.pop("rings", 16), sides=k.pop("sides", 16), bark_disp=0, **k)
legs, boots, cuffs, gaunt, arms, hands = [], [], [], [], [], []
for s in (-1, 1):
    legs.append(limb([(s*.11, .8, 0), (s*.11, .55, .02), (s*.11, .3, 0)], [.105, .085, .075], rings=20, sides=18))
    boots.append(merge([cylinder(.085, .3, (s*.11, .17, 0), r2=.098, sides=24, rings=6), sphere(.095, (s*.11, .06, .07), (1, .75, 1.7), 14, 20)]))
    cuffs.append(merge([cylinder(.115, .09, (s*.11, .34, 0), r2=.125, sides=28, rings=2), torus(.108, .012, (s*.11, .29, 0), seg=24, sides=8)]))
    arms.append(limb([(s*.23, 1.36, 0), (s*.3, 1.18, .02), (s*.31, .98, .1)], [.062, .052, .042], rings=20, sides=16))
    gaunt.append(merge([cylinder(.05, .17, (s*.31, 1.0, .09), r2=.062, sides=20, rings=4, rot=(25, 0, 0)), torus(.056, .01, (s*.31, 1.07, .06), rot=(25, 0, 0), seg=20, sides=6)]))
    hands.append(merge([sphere(.045, (s*.31, .9, .14), (1, 1, 1.1), 12, 16)] + [sphere(.014, (s*.31 + (k-1.5)*.015, .87, .18), (1, 1, 1.6), 6, 8) for k in range(4)]))
skirt = folded([(.36, .66), (.34, .7), (.3, .78), (.25, .88), (.2, .96)], 11, .09, 96, .8)
torso = folded([(.21, .94), (.2, 1.05), (.205, 1.2), (.21, 1.3), (.17, 1.38), (.08, 1.43)], 0, 0, 40, .68)
collar = torus(.1, .028, (0, 1.42, 0), seg=28, sides=10, scale=(1, 1, .9))
belt = merge([torus(.205, .026, (0, .96, 0), seg=40, sides=10, scale=(1, 1, .72)), box((.07, .06, .02), (0, .96, .155), seg=3), box((.035, .03, .024), (0, .96, .162), seg=2)])
cross = limb([(-.15, 1.4, .09), (-.02, 1.22, .15), (.1, 1.06, .16), (.2, .94, .13)], [.034, .032, .03, .03], rings=24, sides=10, flat=.4)
pouch = merge([box((.08, .09, .05), (.22, .9, .09), (0, 25, 0), seg=3), sphere(.03, (.22, .96, .115), (1, 1, .6), 8, 10)])
neck = cylinder(.04, .08, (0, 1.46, 0), sides=16, rings=2)
head = sphere(.115, (0, 1.58, 0), (1, 1.08, 1.04), 24, 32)
ears = merge([cylinder(.03, .16, (s*.13, 1.6, -.005), r2=.002, sides=10, rings=5, rot=(0, 0, -s*72)) for s in (-1, 1)])
eyes = merge([sphere(.016, (s*.042, 1.585, .105), (1, 1.3, .6), 8, 10) for s in (-1, 1)])
nose = sphere(.012, (0, 1.56, .118), (1, 1.2, 1.2), 8, 10)
lip = box((.04, .006, .01), (0, 1.52, .113), seg=2)
R = np.random.RandomState(7); locks = []
for i in range(16):  # layered spiky anime locks
    a = (i / 16) * 2 * np.pi; fr = np.cos(a) * .5 + .5; bx, bz = .11 * np.sin(a), .11 * np.cos(a); L = .13 + .1 * R.rand() + .06 * (1 - fr)
    locks.append(limb([(bx * .9, 1.66, bz * .9), (bx * 1.5, 1.7 + L * .5, bz * 1.5 + (.04 if fr > .5 else -.03)), (bx * 2.1, 1.68 + L * .55, bz * 2.1 + (.12 if fr > .6 else -.1) * 1)], [.03, .024, .004], rings=14, sides=10))
for k in range(5): locks.append(limb([(-.1 + k * .05, 1.68, .08), (-.1 + k * .05, 1.7, .13), (-.12 + k * .06, 1.63, .155)], [.02, .017, .003], rings=10, sides=8))
hair = merge(locks + [sphere(.12, (0, 1.605, -.012), (1.02, 1.0, 1.02), 18, 24)])
root_node = node("chr_hero_kaelen_adventurer", None, None, [node("legs", merge(legs), BEIGE), node("boots", merge(boots), LEATHER), node("boot_cuffs", merge(cuffs), LEATHER),
    node("tunic_skirt", skirt, EMERALD), node("tunic_torso", merge([torso, collar]), EMERALD), node("waist_belt", belt, LEATHER, [node("buckle_gold", box((.045, .04, .012), (0, .96, .175)), GOLD)]),
    node("cross_belt", cross, LEATHER), node("pouch", pouch, LEATHER), node("arm_L", arms[0], EMERALD, [node("hand_attach_L", None)]), node("arm_R", arms[1], EMERALD, [node("hand_attach_R", None, pos=(.31, .9, .14))]),
    node("gauntlets", merge(gaunt), LEATHER), node("hands", merge(hands), SKIN), node("neck", neck, SKIN), node("head", head, SKIN), node("pointed_ears", ears, SKIN),
    node("eyes", eyes, EYEG), node("nose", nose, SKIN), node("mouth", lip, LEATHER), node("hair", hair, HAIR), node("back_attach_shield", None, pos=(0, 1.2, -.22))])
if __name__ == "__main__": print(compile_glb(root_node, out("characters", "chr_hero_kaelen_adventurer"), 256))
