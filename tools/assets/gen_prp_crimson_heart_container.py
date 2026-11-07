from common import *
import numpy as np
heart = sdf_sculpt([('sphere', (-.3, .22, 0), .38), ('sphere', (.3, .22, 0), .38), ('sphere', (-.2, -.1, 0), .4), ('sphere', (.2, -.1, 0), .4),
                    ('sphere', (-.1, -.38, 0), .25), ('sphere', (.1, -.38, 0), .25), ('sphere', (0, -.6, 0), .13)], resolution=64, smooth_k=.07)
heart.V[:, 2] *= .85
# facet it: low-poly shading look by keeping sculpted mesh but adding an inner glowing core
core = sphere(.2, (0, .05, 0), rings=16, sides=24)
frame = merge([torus(.78, .045, (0, 0, -.3), rot=(90, 0, 0), seg=64, sides=14), torus(.62, .03, (0, 0, -.3), rot=(90, 0, 0), seg=64, sides=10)])
fil = merge([spline_tube([(np.cos(a)*.64, np.sin(a)*.64, -.3), (np.cos(a)*.71, np.sin(a)*.71, -.3), (np.cos(a)*.78, np.sin(a)*.78, -.3)], [.03, .025, .035], rings=14, sides=10, bark_disp=0) for a in np.linspace(0, 6.28, 9)[:-1]])
crown = merge([cylinder(.04, .22, (0, .84, 0), r2=.09, sides=12), sphere(.07, (0, 1.0, 0), rings=10, sides=12)])
root_node = node("prp_crimson_heart_container", None, None, [node("heart", heart, RUBY, pos=(0, 0, 0)), node("core", core, AMBER, pos=(0, .0, 0)),
    node("frame", frame, GOLD), node("filigree", fil, GOLD), node("crown", crown, GOLD)])
if __name__ == "__main__": print(compile_glb(root_node, out("props", "prp_crimson_heart_container"), 256))
