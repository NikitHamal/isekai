from kingdom_lib import *
W, D, H1, H2 = 15.0, 11.0, 4.2, 3.5; hx, hz = W / 2, D / 2; rise = 4.2; r = np.random.RandomState(9)
# ---- ground floor: cut-stone core + individually modelled ashlar relief, plinth, quoins ----
core = box_tri((W - .1, H1, D - .1), (0, H1 / 2, 0), d=.32); plinth = box_tri((W + .5, .55, D + .5), (0, .27, 0), d=.5)
FH = [(x - .62, x + .62, 1.2, 2.8) for x in (-5.3, -2.9, 2.9, 5.3)]; SH = [(z - .56, z + .56, 1.2, 2.8) for z in (-3.0, 0.0, 3.0)]
blocks = [block_wall(-hx, -1.5, .5, H1, hz, .14, seed=1, holes=FH), block_wall(1.5, hx, .5, H1, hz, .14, seed=2, holes=FH), block_wall(-1.5, 1.5, 3.9, H1, hz, .14, seed=3),
          block_wall(-hz, hz, .5, H1, hx, .14, seed=4, axis=1, holes=SH), block_wall(-hz, hz, .5, H1, -hx - .14, .14, seed=5, axis=1, holes=SH), block_wall(-hx, hx, .5, H1, -hz - .14, .14, seed=6)]
quoins = [box_tri((.9, .42, .9), (sx * (hx + .02), .6 + k * .42, sz * (hz + .02)), (0, 0, 0), .5) for sx in (-1, 1) for sz in (-1, 1) for k in range(9) if (k % 2 == 0 or True)]
stone = core; relief = merge(blocks)
# ---- door: arched oak double doors with iron straps, voussoir ring ----
door = [box_tri((1.2, 2.5, .14), (s * .62, 1.55, hz + .1), d=.5) for s in (-1, 1)]
straps = [box_tri((1.1, .1, .05), (s * .62, y, hz + .2), d=1) for s in (-1, 1) for y in (.7, 1.5, 2.3)] + [torus(.12, .02, (s * .15, 1.2, hz + .22), rot=(0, 0, 0), seg=14, sides=6) for s in (-1, 1)]
fan = poly_prism([(np.cos(a) * 1.3, 2.8 + np.sin(a) * 1.3) for a in np.linspace(0, np.pi, 14)], .14, (0, 0, hz + .1), d=.5)
arch = arch_opening(0, 0, 2.6, 2.8, hz + .02, .3, n=15)
# ---- ground windows (warm lit leaded glass) + stone sills ----
gl, fr = [], []
for x in (-5.3, -2.9, 2.9, 5.3):
    gl.append(box_tri((.95, 1.35, .06), (x, 2.0, hz + .09), d=1)); fr.append(box_tri((1.15, 1.55, .1), (x, 2.0, hz + .04), d=.8)); fr.append(box_tri((.06, 1.35, .09), (x, 2.0, hz + .12), d=1)); fr.append(box_tri((.95, .06, .09), (x, 2.0, hz + .12), d=1))
    fr.append(box_tri((1.4, .14, .4), (x, 1.2, hz + .18), d=.5))
for z in (-3.0, 0.0, 3.0):
    for sx in (-1, 1): gl.append(box_tri((.06, 1.3, .9), (sx * (hx + .1), 2.0, z), d=1)); fr.append(box_tri((.1, 1.5, 1.1), (sx * (hx + .05), 2.0, z), d=.8))
# ---- upper jetty floor: plaster infill + oak timber frame ----
UW, UD = W + .8, D + .8; plaster = [box_tri((UW - .2, H2, UD - .2), (0, H1 + H2 / 2 + .3, 0), d=.28)]
y0, y1 = H1 + .3, H1 + H2 + .3; tb = []; uhx, uhz = UW / 2, UD / 2
for y in (y0, (y0 + y1) / 2, y1): tb += [box_tri((UW + .1, .26, .26), (0, y, sz * uhz), d=.8) for sz in (-1, 1)] + [box_tri((.26, .26, UD + .1), (sx * uhx, y, 0), d=.8) for sx in (-1, 1)]
for x in np.linspace(-uhx, uhx, 9): tb += [box_tri((.22, H2, .22), (x, (y0 + y1) / 2, sz * uhz), d=.8) for sz in (-1, 1)]
for z in np.linspace(-uhz, uhz, 7): tb += [box_tri((.22, H2, .22), (sx * uhx, (y0 + y1) / 2, z), d=.8) for sx in (-1, 1)]
for x in np.linspace(-uhx, uhx, 9)[:-1:2]: tb += [beam((x, y0, uhz + .02), (x + 1.88, y1, uhz + .02), .16), beam((x + 1.88, y0, -uhz - .02), (x, y1, -uhz - .02), .16)]
for k in range(10): tb.append(box_tri((.3, .3, 1.1), (-uhx + k * (UW / 9.), H1 - .1, uhz - .4), (0, 0, 0), .8)) if False else None
corbels = [box_tri((.28, .28, .9), (x, H1 - .05, uhz - .4), d=.8) for x in np.linspace(-uhx + .5, uhx - .5, 10)]
ugl, ushut = [], []
for x in (-5.5, -3.0, 3.0, 5.5):
    ugl.append(box_tri((.9, 1.3, .06), (x, y0 + 1.7, uhz + .02), d=1)); tb.append(box_tri((1.1, 1.5, .1), (x, y0 + 1.7, uhz - .02), d=.8)); ushut += [box_tri((.5, 1.35, .05), (x + s * .75, y0 + 1.7, uhz + .06), d=.9) for s in (-1, 1)]
ugl.append(box_tri((1.8, 1.5, .06), (0, y0 + 1.75, uhz + .02), d=1)); tb.append(box_tri((2.1, 1.8, .1), (0, y0 + 1.75, uhz - .02), d=.8))
for z in (-3.0, 0.0, 3.0):
    for sx in (-1, 1): ugl.append(box_tri((.06, 1.3, .9), (sx * (uhx + .02), y0 + 1.7, z), d=1))
# ---- porch: oak deck, posts, lean-to slate roof, hanging guild sign ----
deck = box_tri((7.4, .3, 3.4), (0, .15, hz + 1.9), d=.4); posts = [cyl_tri(.16, 3.6, (x, 2.05, hz + 3.35), .8, 12) for x in (-3.5, -1.2, 1.2, 3.5)]
steps = [box_tri((3.2, .2, .45), (0, .1 - k * .1 + .1, hz + 3.8 + k * .45), d=.5) for k in range(2)]
pr = box_tri((8.0, .22, 4.2), (0, 3.85, hz + 1.95), (12.8, 0, 0), .26); pr_b = [beam((x, 3.55, hz + 3.35), (x, 4.1, hz + .1), .18) for x in (-3.5, -1.2, 1.2, 3.5)]
sign = [box_tri((1.4, .9, .08), (-5.3, 3.4, hz + 3.1), d=.8), tube((-5.3, 3.9, hz + .1), (-5.3, 3.9, hz + 3.1), .05, 8)]
emblem = [poly_prism([(-.45, .0), (.45, .0), (.45, .3), (0, .55), (-.45, .3)], .05, (-5.3, 3.3, hz + 3.17), d=1), torus(.28, .035, (-5.3, 3.4, hz + 3.2), rot=(0, 0, 0), seg=20, sides=6)]
# ---- gable roof (ridge along X), gable-end infill, dormers, chimney ----
roof, ridge = gable_roof(W + 1.8, uhz + .1, rise, (0, y1 + .05, 0), over=.55, lip_rows=16)
gab = [poly_prism([(-uhz, 0), (uhz, 0), (0, rise)], .3, (sx * (uhx - .05), y1 + .02, 0), d=.28, rot=(0, 90, 0)) for sx in (-1, 1)]
gabt = [beam((sx * (uhx + .1), y1, 0), (sx * (uhx + .1), y1 + rise - .2, 0), .22) for sx in (-1, 1)] + [beam((sx * (uhx + .1), y1 + .1, -uhz + .3), (sx * (uhx + .1), y1 + rise * .55, -.5), .18) for sx in (-1, 1)] + [beam((sx * (uhx + .1), y1 + .1, uhz - .3), (sx * (uhx + .1), y1 + rise * .55, .5), .18) for sx in (-1, 1)]
dpl, dgl, dtb, drf, drg = [], [], [], [], []
for x in (-3.6, 3.6):
    zz = uhz * .5; ry = y1 + rise * .5; dpl.append(box_tri((1.9, 1.7, 1.7), (x, ry + .5, zz), d=.28)); dgl.append(box_tri((1.0, 1.0, .06), (x, ry + .55, zz + .88), d=1))
    dtb += [box_tri((1.25, 1.25, .1), (x, ry + .55, zz + .85), d=.8), box_tri((.2, 1.9, .2), (x - .95, ry + .6, zz + .85), d=.8), box_tri((.2, 1.9, .2), (x + .95, ry + .6, zz + .85), d=.8)]
    a, b = gable_roof(2.0, 1.15, .95, (x, ry + 1.3, zz - .1), over=.3, lip_rows=5); drf.append(a.tf(rot=(0, 90, 0), pos=(0, 0, 0)) if False else a); drg.append(b)
chx, chz = -4.8, -1.6; ch0, ch1 = y1 - 1.0, y1 + rise + 1.7
chim = [box_tri((1.2, ch1 - ch0, 1.2), (chx, (ch0 + ch1) / 2, chz), d=.45), block_wall(chx - .6, chx + .6, ch0, ch1, chz + .6, .1, .3, .6, 11, .5), block_wall(chx - .6, chx + .6, ch0, ch1, chz - .7, .1, .3, .6, 12, .5),
        block_wall(chz - .6, chz + .6, ch0, ch1, chx + .6, .1, .3, .6, 13, .5, axis=1), block_wall(chz - .6, chz + .6, ch0, ch1, chx - .7, .1, .3, .6, 14, .5, axis=1), box_tri((1.6, .3, 1.6), (chx, ch1 + .15, chz), d=.5)] + [cyl_tri(.14, .5, (chx + dx, ch1 + .55, chz + dz), .8, 10) for dx in (-.3, .3) for dz in (-.3, .3)]
lantern = [tube((x, 3.4, hz + 3.35), (x, 3.0, hz + 3.35), .02, 6) for x in (-2.35, 2.35)] + [box_tri((.25, .35, .25), (x, 2.8, hz + 3.35), d=1) for x in (-2.35, 2.35)]
M = lambda *l: merge([m for m in l if m is not None])
flat = lambda l: [m for g in l for m in (g if isinstance(g, list) else [g])]
root = node("bld_valoria_adventurer_guild", None, None, [
    node("plinth_stone", merge([plinth, quoins and merge(quoins)]), DARKSTONE), node("ashlar_walls", stone, CASTLE), node("hewn_relief", relief, STONEF),
    node("arch_voussoirs", merge([arch, fan]), STONEF), node("oak_double_doors", merge(door + [box_tri((.1, 2.5, .15), (0, 1.55, hz + .1), d=.5)]), OAKP), node("door_iron", merge(straps), DARKSTEEL),
    node("lit_glass_ground", merge(gl + [m for m in lantern[2:]]), GLASSLIT), node("window_frames", merge(fr + dtb + tb + corbels + posts + pr_b + sign[:2] + gabt + steps[:0]), BEAM),
    node("upper_plaster", merge(plaster + gab + dpl), PLASTER), node("lit_glass_upper", merge(ugl + dgl), GLASSLIT), node("shutters_deck", merge(ushut + [deck] + steps + [sign[0]]), OAKP),
    node("slate_roof", merge([roof, pr] + drf), SLATE), node("ridge_caps", merge([ridge] + drg), DARKSTEEL), node("chimney_stone", merge(chim), CASTLE), node("sign_emblem", merge(emblem), GOLDM)])
if __name__ == "__main__": print(compile_glb(root, out("buildings", "bld_valoria_adventurer_guild"), 1024))
