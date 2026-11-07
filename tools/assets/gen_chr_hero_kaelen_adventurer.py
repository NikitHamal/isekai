from kingdom_lib import *
r = np.random.RandomState(21); HAND = np.array([-.34, 1.08, .22])
def limb(pts, rad, sides=18): return merge([tube(pts[i], pts[i + 1], rad[i], sides, 3, rad[i + 1]) for i in range(len(pts) - 1)])
# legs: dark trousers, knee-high leather boots
legs, boots, cuffs = [], [], []
for s in (-1, 1):
    legs.append(limb([(s * .1, .95, 0), (s * .105, .52, .02)], [.1, .075], 22)); legs.append(ell((s * .1, .93, 0), (.105, .09, .11), 14, 22))
    boots.append(limb([(s * .105, .54, .02), (s * .1, .1, 0)], [.085, .063], 22)); boots.append(ell((s * .1, .045, .075), (.068, .048, .15), 14, 22)); boots.append(cyl_tri(.098, .07, (s * .105, .56, .02), 3, 22, r2=.092))
    boots.append(box_tri((.12, .02, .3), (s * .1, .01, .06), d=3)); cuffs.append(torus(.085, .014, (s * .1, .27, .0), seg=22, sides=6)); cuffs.append(torus(.09, .014, (s * .1, .42, .01), seg=22, sides=6))
# gambeson torso with quilting rings, belt, pouches, bandolier
gam = [ell((0, 1.24, 0), (.185, .28, .12), 22, 34), ell((0, 1.0, 0), (.17, .13, .11), 16, 28), ell((0, .9, 0), (.2, .1, .13), 16, 28)] + [torus(.18 - abs(y - 1.25) * .1, .013, (0, y, 0), seg=32, sides=6, scale=(1, 1, .68)) for y in np.linspace(1.04, 1.46, 8)]
skirt = [folded([(.2, .94), (.215, .8), (.23, .66)], 11, .06, 48, .72)]
belt = [torus(.175, .03, (0, 1.0, 0), seg=36, sides=8, scale=(1, 1, .72)), box_tri((.07, .06, .03), (0, 1.0, .125), d=6)] + [ell((x, 1.0, z), (.05, .06, .04), 8, 10) for x, z in ((.19, .02), (-.2, -.03), (.12, -.1))]
strap = [tube((-.16, 1.52, .05), (.17, 1.0, .1), .017, 8, 4)]
# steel cuirass + layered pauldrons + gorget
steel = [ell((0, 1.36, .008), (.2, .2, .135), 26, 40), ell((0, 1.16, .02), (.17, .07, .115), 14, 28), ell((0, 1.62, 0), (.1, .035, .09), 12, 22)]
for s in (-1, 1):
    for k, (dx, dy, rz, sc) in enumerate(((.255, 1.58, -24, 1.0), (.285, 1.53, -30, 1.1), (.31, 1.47, -36, 1.2))): steel.append(ell((s * dx, dy, 0), (.095 * sc, .035, .125 * sc), 14, 26, 1, (0, 0, s * rz)))
    steel.append(ell((s * .265, 1.6, 0), (.06, .028, .07), 10, 16, 1, (0, 0, -s * 20)))
rivets = [ell((s * x, y, .13 - abs(x) * .3), (.008, .008, .008), 5, 6) for s in (-1, 1) for x, y in ((.08, 1.46), (.14, 1.35), (.1, 1.25), (.05, 1.5))]
# arms: gambeson sleeves, leather bracers, gloved hands
arms, brac, hands = [], [], []
for s, P in ((-1, [(-.27, 1.53, 0), (-.33, 1.26, .07), tuple(HAND + np.array([0, .0, -.02]))]), (1, [(.27, 1.53, 0), (.33, 1.26, .04), (.3, 1.04, .12)])):
    arms.append(limb(P[:2], [.06, .052], 20)); arms.append(ell(P[1], (.056, .056, .056), 10, 16)); brac.append(limb([P[1], P[2]], [.052, .04], 20))
    brac.append(cyl_tri(.047, .11, tuple((np.array(P[1]) * .35 + np.array(P[2]) * .65)), 3, 20)); brac += [tube(np.array(P[1]) * (1 - f) + np.array(P[2]) * f - np.array([.06, 0, 0]), np.array(P[1]) * (1 - f) + np.array(P[2]) * f + np.array([.06, 0, 0]), .006, 6) for f in (.2, .5, .8)]
    hands.append(ell(P[2], (.043, .05, .052), 12, 18)); hands += [ell(np.array(P[2]) + np.array([s * .004 + (k - 1.5) * .017 * 0, -.045, .02 + k * .0]), (.011, .03, .011), 6, 8) for k in range(1)]
# neck, head, face, hair
skin = [tube((0, 1.6, 0), (0, 1.69, .01), .045, 16), ell((0, 1.755, .012), (.083, .105, .098), 28, 40), ell((0, 1.7, .05), (.06, .055, .05), 14, 24), ell((0, 1.745, .1), (.012, .02, .018), 8, 10)] + [ell((s * .084, 1.745, .0), (.014, .03, .02), 8, 10) for s in (-1, 1)]
eyes = [ell((s * .033, 1.77, .092), (.012, .008, .008), 8, 10) for s in (-1, 1)]; brows = [box_tri((.034, .006, .008), (s * .035, 1.795, .094), (0, 0, -s * 8), 20) for s in (-1, 1)]
hair = [ell((0, 1.78, -.015), (.094, .1, .108), 24, 36)]
for i in range(120):
    th = r.rand() * 2 * np.pi; ph = np.arccos(r.rand() * .95 + .02) if True else 0; d = np.array([np.sin(ph) * np.cos(th), np.cos(ph), np.sin(ph) * np.sin(th)])
    if d[2] > .35 and d[1] < .5: continue
    base = np.array([0, 1.775, -.01]) + d * np.array([.09, .1, .1]); tip = base + d * (.07 + .08 * r.rand()) + np.array([.0, -.03 * r.rand(), -.02]) + (np.array([.0, .0, .04]) if d[2] > 0 and d[1] > .6 else 0)
    hair.append(tube(base, tip, .017 + .01 * r.rand(), 6, 3, .002))
for k in range(9): hair.append(tube((-.07 + k * .0175, 1.83, .07), (-.07 + k * .0175 + (r.rand() - .5) * .03, 1.79 - .02 * r.rand(), .13), .012, 6, 3, .002))
# flowing midnight-blue cloak (outer) with crimson lining, clasp + chain
nr, nc = 36, 40; P = np.zeros((nr, nc, 3)); Q = np.zeros((nr, nc, 3))
for i in range(nr):
    v = i / (nr - 1)
    for j in range(nc):
        u = j / (nc - 1) * 2 - 1; hw = .19 + .3 * v ** .9; fold = .045 * v * np.sin(u * 3.2 * np.pi + v * 2) ; sweep = -.14 - .26 * v ** 1.3 + .05 * np.sin(v * 5 + u)
        x = u * hw; y = 1.6 - v * 1.27 + .03 * abs(u) * v; z = sweep + fold - .05 * u * u * (1 - v * .3)
        P[i, j] = (x, y, z); Q[i, j] = (x * .985, y + .004, z + .016)
cloak = grid(P, closed_u=False); lining = grid(Q, closed_u=False, flip=True)
collar = [torus(.1, .028, (0, 1.6, -.02), seg=28, sides=8, scale=(1, 1, .95))]; clasp = [ell((0, 1.57, .095), (.025, .025, .015), 10, 14)] + [tube((-.07, 1.585, .08), (.07, 1.585, .08), .006, 6)]
# Aetherblade longsword (node names contain "sword"): grip at HAND, blade along +Y
G = HAND
grip = [tube(G + [0, -.12, 0], G + [0, .1, 0], .017, 12)] + [torus(.018, .004, G + [0, y, 0], rot=(90, 0, 0), seg=12, sides=4) for y in np.linspace(-.1, .08, 7)]
guard = [box_tri((.3, .028, .04), G + [0, .12, 0], d=4), ell(G + [.15, .12, 0], (.02, .02, .02), 8, 10), ell(G + [-.15, .12, 0], (.02, .02, .02), 8, 10)]; pom = [ell(G + [0, -.14, 0], (.03, .03, .03), 12, 16)]
blade = poly_prism([(-.03, 0), (.03, 0), (.028, .82), (.0, .95), (-.028, .82)], .014, G + [0, .14, 0], d=2.5); fuller = poly_prism([(-.009, .05), (.009, .05), (.007, .8), (-.007, .8)], .018, G + [0, .14, 0], d=2.5)
runes = [box_tri((.014, .03, .02), G + [0, .3 + k * .1, 0], d=1) for k in range(5)]
glyph = [torus(.048, .006, (.3, 1.04, .12), rot=(0, 0, 90), seg=24, sides=6)] + [box_tri((.006, .02, .02), (.345, 1.04 + .0, .12 + np.sin(a) * .05), (0, 0, 0), 1) for a in np.linspace(0, 6.28, 6)[:5]]
root = node("chr_hero_kaelen_adventurer", None, None, [node("trousers_gambeson", merge(legs + gam + skirt + arms), GAMBE), node("leather_boots_bracers_belt", merge(boots + cuffs + brac + belt + strap), LEATHERS),
    node("steel_cuirass_pauldrons", merge(steel + rivets + clasp), DAMASK), node("skin", merge(skin + hands), FLESH), node("eyes", merge(eyes + brows), DARKHAIR), node("tousled_dark_hair", merge(hair), DARKHAIR),
    node("midnight_cloak", merge([cloak] + collar), CLOAKB), node("crimson_cloak_lining", lining, CLOAKR), node("sword_grip_guard", merge(grip + guard + pom), GOLDM), node("sword_blade", merge([blade]), DAMASK),
    node("sword_runes", merge(runes + [fuller]), CRYSTAL), node("spell_glyph_ring", merge(glyph), RUBY)])
if __name__ == "__main__": print(compile_glb(root, out("characters", "chr_hero_kaelen_adventurer"), 512))
