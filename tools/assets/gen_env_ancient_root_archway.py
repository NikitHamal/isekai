from common import *
import numpy as np
r = np.random.RandomState(7); H = 4.2; W = 2.6
def root(side, k):  # twisted root column rising from the ground and arching over the passage
    x = side * (W + .1 * k); pts = [(x + side*1.4, 0, .9*(k-1)), (x + side*.3, 1.0, .5*(k-1)), (x - side*.3, 2.4, .3*(k-1)), (side*1.5, H-.3, .1*(k-1)), (side*.2, H+.1, 0)]
    return spline_tube(pts, [.85, .6, .45, .38, .3], twist=2.5 + k, rings=44, sides=24, bark_disp=.06, seed=10*k + (side > 0))
roots = [node(f"root_{s}_{k}", root(s, k), BARK) for s in (-1, 1) for k in (0, 1, 2)]
stones = [node(f"base_{s}", merge([box((1.5, .7, 1.7), (s*(W+1.0), .35, 0), (0, r.randn()*5, 0), seg=4), box((1.1, .5, 1.3), (s*(W+1.0), .95, 0), (0, 8, 0), seg=4)]), STONE) for s in (-1, 1)]
path = node("path_slabs", merge([box((1.4, .12, 1.0), (x*1.45 - 2.9 + 1.45, -.06, z*1.0), (0, r.randn()*3, 0), seg=5) for x in range(0, 3) for z in (-1, 0, 1)] + [box((7, .12, 5), (0, -.15, 0), seg=6)]), STONE)
lintel = node("lintel", timber_frame([((-W-.4, H-.4, 0), (W+.4, H-.4, 0)), ((-W-.4, H-1.0, .4), (W+.4, H-1.0, .4)), ((-W-.4, H-1.0, -.4), (W+.4, H-1.0, -.4)),
                        ((-W, H-1.0, 0), (-W+.9, H-.1, 0)), ((W, H-1.0, 0), (W-.9, H-.1, 0))], beam_w=.34), TIMBER)
ropes = node("rope_bindings", merge([spline_tube([(x, H-.5, -.45), (x, H-.5, 0), (x, H-.5, .45)], [.28, .28, .28], rings=6, sides=14, bark_disp=.05).tf(rot=(0, 0, 0)) for x in (-W+.3, -1, 1, W-.3)]), ROPE)
moss = node("moss", merge([sphere(1, (s*(W+1.0)+r.randn()*.4, 1.15+r.rand()*.2, r.randn()*.4), (.55+r.rand()*.3, .22, .5+r.rand()*.3), rings=14, sides=22) for s in (-1, 1) for _ in range(4)] +
                          [sphere(1, (x, H-.05, 0), (.45, .16, .4), 12, 20) for x in (-1.5, .2, 1.4)]), MOSS)
def lantern(x, z, drop):
    body = lathe([(.001, -.28), (.1, -.27), (.2, -.12), (.24, .05), (.2, .2), (.1, .28), (.05, .33), (.001, .34)], segments=36)
    cap = lathe([(.001, .3), (.12, .3), (.1, .36), (.04, .42), (.001, .43)], 24)
    return node(f"lantern_{x}", None, None, [node("glass", body, AMBER), node("cap", cap, TIMBER),
        node("rope", spline_tube([(0, .4, 0), (.02, .4 + drop/2, 0), (0, .4 + drop, 0)], [.025]*3, rings=10, sides=8, bark_disp=0), ROPE),
        node("ring", torus(.07, .015, (0, .46, 0), rot=(90, 0, 0), seg=16, sides=6), IRON),
        node("cage", merge([cylinder(.018, .6, (np.cos(a)*.215, .03, np.sin(a)*.215), sides=6) for a in np.linspace(0, 6.28, 7)[:-1]]), IRON)], pos=(x, H-1.3-drop, z))
lanterns = [lantern(-1.6, .5, .5), lantern(0, .45, .9), lantern(1.7, .5, .6)]
hearts = []
root_node = node("env_ancient_root_archway", None, None, roots + stones + [path, lintel, ropes, moss] + lanterns)
if __name__ == "__main__":
    print(compile_glb(root_node, out("environment", "env_ancient_root_archway")))
