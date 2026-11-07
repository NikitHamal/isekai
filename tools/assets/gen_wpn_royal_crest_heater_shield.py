from common import *
import numpy as np
def hw(t): return .42 * (1 - max(0, (t - .3) / .7) ** 1.7) ** .65     # half-width: flat top (t=0) to point (t=1)
def face(front, n=44, m=40):
    P = np.zeros((n, m, 3))
    for i in range(n):
        t = i / (n - 1); w = hw(t) + 1e-3
        for j in range(m):
            x = (j / (m - 1) * 2 - 1); X = x * w; P[i, j] = (X, .5 - t * 1.05, (.13 * (1 - (X / .42) ** 2) * (1 - .3 * t) + (.04 if front else -.0)) * (1 if front else .55) - (0 if front else .03) + .02 * (1 - t) ** 2)
    return grid(P, closed_u=False, flip=not front)
ts = np.linspace(0, 1, 90); out_pts = [(-.44, .5, .09)] + [(.44 * 0 + s * hw(t) * 1.04, .5 - t * 1.05, .075 * (1 - t * .6) + .002) for t in ts for s in (1,)][:] + [(-s * hw(t) * 1.04, .5 - t * 1.05, .075 * (1 - t * .6) + .002) for t in ts[::-1] for s in (1,)]
out_pts = [(-hw(0) * 1.04, .5, .08)] + [(hw(t) * 1.04 * (-1 if False else 1), .5 - t * 1.05, .075 * (1 - t * .55)) for t in ts] + [(-hw(t) * 1.04, .5 - t * 1.05, .075 * (1 - t * .55)) for t in ts[::-1]]
rim = spline_tube(out_pts, [.022], rings=180, sides=14, bark_disp=0, cap=False)
planks = merge([face(True), face(False)])
bands = merge([box((.04, 1.08, .02), (0, -.03, .125), seg=10)] + [box((.84 - .1 * k, .04, .02), (0, .42 - k * .32, .122 + .0), seg=12) for k in range(2)])
rivets = merge([sphere(.016, (x, y, .13 - .13 * (x / .42) ** 2 * 1.0 + .02), rings=8, sides=10) for y in (.4, .1) for x in np.linspace(-.34, .34, 7)] + [sphere(.016, (0, y, .135), rings=8, sides=10) for y in (-.2, -.35)])
boss = merge([sphere(.1, (0, .18, .16), (1, 1, .55), 18, 24), torus(.11, .018, (0, .18, .155), rot=(90, 0, 0), seg=32, sides=10)])
mane = merge([torus(.14 + .018 * k, .014, (0, .18, .15), rot=(90, 0, 0), seg=32, sides=8) for k in range(3)] + [box((.03, .06, .02), (np.cos(a) * .17, .18 + np.sin(a) * .17, .162), (0, 0, np.degrees(a) - 90), seg=2) for a in np.linspace(0, 2 * np.pi, 16, endpoint=False)])
lion = merge([sphere(.065, (0, .18, .205), (1, 1.05, .7), 14, 18), sphere(.03, (0, .155, .255), (1, .8, 1), 8, 10), sphere(.013, (-.028, .2, .25), rings=6, sides=8), sphere(.013, (.028, .2, .25), rings=6, sides=8), sphere(.03, (-.055, .245, .2), (1, 1, .5), 8, 10), sphere(.03, (.055, .245, .2), (1, 1, .5), 8, 10)])
crown = merge([cylinder(.05, .035, (0, .33, .15), sides=16, rings=1, rot=(80, 0, 0))] + [cone for k in (-1, 0, 1) for cone in [cylinder(.014, .06, (k * .04, .37 + (.012 if k == 0 else 0), .152), r2=.001, sides=8, rings=2)]])
straps = merge([spline_tube([(-.2, .25 - k * .35, -.03), (0, .3 - k * .35, -.075), (.2, .25 - k * .35, -.03)], [.02, .022, .02], rings=14, sides=8, bark_disp=0) for k in range(2)] + [torus(.045, .01, (0, .08, -.07), seg=16, sides=6)])
root_node = node("wpn_royal_crest_heater_shield", None, None, [node("oak_face_and_back", planks, OAK), node("steel_rim", rim, STEEL), node("steel_bands", bands, STEEL), node("rivets", rivets, IRON),
    node("crest_boss", boss, GOLD), node("lion_mane", mane, GOLD), node("lion_face", lion, GOLD), node("crest_crown", crown, GOLD), node("arm_straps", straps, LEATHER, [node("grip_attach", None, pos=(0, .08, -.07))])])
if __name__ == "__main__": print(compile_glb(root_node, out("weapons", "wpn_royal_crest_heater_shield"), 256))
