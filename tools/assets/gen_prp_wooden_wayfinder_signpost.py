from common import *
import numpy as np
r = np.random.RandomState(3)
post = spline_tube([(0, 0, 0), (.04, 1.3, .02), (-.03, 2.6, 0)], [.22, .17, .15], twist=.8, rings=40, sides=22, bark_disp=.05, seed=4)
def board(y, ang, ln, tip):
    b = box((ln, .34, .07), (ln/2 + .1, 0, 0), seg=14); pts = b.V.copy(); k = pts[:, 0] > ln*.8 + .1; pts[k, 1] *= np.clip(1 - (pts[k, 0] - (ln*.8 + .1)) / (ln*.2) * .9, .1, 1) if tip else 1
    b.V = pts + r.randn(*pts.shape) * .006; return node(f"board_{y}", b, TIMBER, [node("nail_a", sphere(.03, (.2, 0, .05), rings=8, sides=10), IRON), node("nail_b", sphere(.03, (.2, 0, -.05), rings=8, sides=10), IRON),
        node("rune", merge([box((.05, .15 + .1*(i % 2), .02), (.45 + .2*i, 0, .045), (0, 0, 20*i), seg=3) for i in range(3)]), AMBER)], pos=(.1, y, .15 if ang else -.15), rot=(0, ang, 0))
boards = [board(2.2, 0, 1.1, True), board(1.8, 180, 1.0, True), board(1.4, -25, .9, True)]
moss = merge([sphere(1, (r.randn()*.15, .3 + r.rand()*.8, r.randn()*.1), (.17, .25, .17), 12, 16) for _ in range(5)] + [sphere(1, (0, .05, 0), (.6, .15, .6), 14, 22)])
stones = merge([sphere(1, (np.cos(a)*.45, .08, np.sin(a)*.45), (.2 + r.rand()*.1, .14, .2), 10, 14) for a in np.linspace(0, 6.28, 7)[:-1]])
root_node = node("prp_wooden_wayfinder_signpost", None, None, [node("post", post, BARK), *boards, node("moss", moss, MOSS), node("stones", stones, STONE),
    node("finial", sphere(.14, (-.03, 2.68, 0), rings=14, sides=16), TIMBER)])
if __name__ == "__main__": print(compile_glb(root_node, out("props", "prp_wooden_wayfinder_signpost"), 256))
