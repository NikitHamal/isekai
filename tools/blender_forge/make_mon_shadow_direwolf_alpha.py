#!/usr/bin/env python3
"""Shadow Direwolf Alpha: real-Blender quadruped anatomy (lofted ribcage/neck/skull/muzzle, digitigrade legs, tail, fur strands)."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anatomy_core import *

def build(path):
    reset(); random.seed(6)
    fur = material("wolf_fur", "fur", (.13, .12, .16), seed=2, nstr=4); fur2 = material("wolf_fur_light", "fur", (.30, .28, .32), seed=3, nstr=4)
    nose = material("wolf_nose", "plain", (.02, .02, .02), n=64, rough=.3); tooth = material("wolf_tooth", "bone", (.92, .9, .8), seed=4)
    eye = material("wolf_eye", "glow", (1, .55, .1), n=64, emit=(1, .5, .08), emit_str=3.0); gum = material("wolf_gum", "plain", (.35, .08, .1), n=64)
    piv = V((0, -.1, .8)); R = (0, 0, 1)
    loft("torso_body", [(V((0, -.36, .76)), .10, .20), (V((0, -.30, .80)), .14, .25), (V((0, -.18, .83)), .165, .275), (V((0, 0, .80)), .155, .255), (V((0, .2, .77)), .125, .21), (V((0, .36, .77)), .14, .23), (V((0, .5, .75)), .10, .18), (V((0, .56, .74)), .04, .08)], fur, segs=22, ref=R, tile=.5, sub=2, pivot=piv)
    for i in range(14):   # raised hackles along the spine
        y = -.3 + i * .06; z = .83 + .27 * math.cos((y + .1) * 2.2) * .4 + .02
        tube("torso_hackle%d" % i, [V((0, y, z + .04)), V((0, y + .045, z + .11 + .02 * (i % 3))), V((0, y + .08, z + .15))], [.016, .012, .002], fur2, segs=5, flat=.5, sub=0, pivot=piv)
    hp = V((0, -.5, .98))
    loft("head_neck", [(V((0, -.28, .90)), .12, .17), (V((0, -.40, .98)), .10, .15), (V((0, -.50, 1.03)), .085, .115)], fur, segs=16, ref=R, sub=2, pivot=hp, caps=(False, False))
    loft("head_skull", [(V((0, -.50, 1.03)), .085, .11), (V((0, -.58, 1.04)), .10, .115), (V((0, -.66, 1.03)), .09, .10), (V((0, -.74, 1.00)), .062, .07), (V((0, -.84, .975)), .048, .052), (V((0, -.90, .965)), .036, .04)], fur, segs=18, ref=R, tile=.3, sub=2, pivot=hp)
    prim("head_nose", "sphere", nose, (.032, .028, .026), (0, -.915, .975), sub=1, pivot=hp, segs=12)
    loft("head_jaw", [(V((0, -.60, .955)), .06, .04), (V((0, -.74, .93)), .05, .032), (V((0, -.86, .935)), .034, .025), (V((0, -.89, .94)), .02, .018)], fur2, segs=12, ref=R, sub=1, pivot=V((0, -.6, .96)))
    for sx in (-1, 1):
        sd = "l" if sx > 0 else "r"
        tube("head_ear" + sd, [V((sx * .06, -.56, 1.11)), V((sx * .075, -.55, 1.19)), V((sx * .07, -.545, 1.26))], [.04, .028, .004], fur, segs=8, flat=.45, sub=1, pivot=hp, ref=(1, 0, 0))
        prim("head_eye" + sd, "sphere", eye, (.014, .011, .011), (sx * .062, -.735, 1.045), sub=1, pivot=hp, segs=10)
        for k, y in enumerate((-.80, -.755)): tube("head_fang%s%d" % (sd, k), [V((sx * .034, y, .955)), V((sx * .034, y, .91 - k * .0)), V((sx * .034, y, .885))], [.011, .008, .001], tooth, segs=6, sub=0, pivot=hp)
    shp = V((0, -.28, .72)); hip = V((0, .38, .72))
    for sx in (-1, 1):
        x = sx * .11; sd = "l" if sx > 0 else "r"
        tube("leg_l_front" + sd, [V((x, -.28, .74)), V((x, -.26, .55)), V((x, -.29, .36)), V((x, -.31, .20)), V((x, -.36, .05)), V((x, -.40, .03))], [.075, .06, .04, .03, .035, .035], fur, segs=10, flat=.9, sub=1, pivot=shp, ref=(1, 0, 0))
        tube("leg_r_hind" + sd, [V((x, .38, .76)), V((x, .30, .55)), V((x, .42, .36)), V((x, .46, .22)), V((x, .43, .05)), V((x, .38, .03))], [.095, .065, .038, .028, .035, .035], fur, segs=10, flat=.9, sub=1, pivot=hip, ref=(1, 0, 0))
    tube("tail", [V((0, .52, .78)), V((0, .72, .74)), V((0, .92, .62)), V((0, 1.06, .46))], [.05, .052, .042, .012], fur, segs=10, flat=.9, sub=1, pivot=V((0, .5, .78)), ref=(1, 0, 0))
    export(path)
if __name__ == "__main__":
    build(os.path.join(ROOT, "assets", "models", "monsters", "mon_shadow_direwolf_alpha.glb"))
