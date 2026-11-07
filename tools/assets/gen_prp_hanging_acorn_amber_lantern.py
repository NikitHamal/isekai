from common import *
import numpy as np
glass = lathe([(.001, -.3), (.12, -.29), (.22, -.16), (.27, .02), (.22, .2), (.12, .3), (.001, .32)], segments=48)
cap = lathe([(.001, .3), (.2, .3), (.24, .33), (.14, .42), (.06, .5), (.001, .52)], 48)
base = lathe([(.001, -.42), (.1, -.42), (.13, -.34), (.2, -.3), (.001, -.3)], 36)
ribs = merge([spline_tube([(np.cos(a)*.1, -.3, np.sin(a)*.1), (np.cos(a)*.29, .0, np.sin(a)*.29), (np.cos(a)*.1, .32, np.sin(a)*.1)], [.02, .022, .02], rings=18, sides=8, bark_disp=0) for a in np.linspace(0, 6.283, 9)[:-1]])
rope = spline_tube([(0, .5, 0), (.04, .8, 0), (-.03, 1.1, 0), (0, 1.4, 0)], [.03]*4, twist=12, rings=40, sides=10, bark_disp=.03)
loops = merge([torus(.09, .022, (0, 1.4 + i*.04, 0), rot=(90, 0, 0), seg=24, sides=8) for i in range(2)])
flame = sphere(.1, (0, -.05, 0), (1, 1.6, 1), 16, 20)
root_node = node("prp_hanging_acorn_amber_lantern", None, None, [node("glass", glass, AMBER), node("flame", flame, AMBER), node("cap", cap, TIMBER), node("base", base, TIMBER),
    node("ribs", ribs, IRON), node("rope", rope, ROPE), node("rope_loops", loops, ROPE)])
if __name__ == "__main__": print(compile_glb(root_node, out("props", "prp_hanging_acorn_amber_lantern"), 256))
