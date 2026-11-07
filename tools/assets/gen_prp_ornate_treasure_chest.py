from common import *
import numpy as np
body = box((1.4, .7, .9), (0, .35, 0), seg=8)
lid = merge([cylinder(.45, 1.4, (0, 0, 0), sides=40, rings=8, rot=(0, 0, 90)).tf(scale=(1, 1, 1)), box((1.4, .02, .9), (0, 0, 0))]); lid.V[:, 1] = np.maximum(lid.V[:, 1], 0); lid = lid.tf(scale=(1, .62, 1))
straps = merge([box((.14, .74, .94), (x, .35, 0), seg=4) for x in (-.5, 0, .5)])
lid_straps = merge([cylinder(.46, .14, (x, 0, 0), sides=40, rings=2, rot=(0, 0, 90)) for x in (-.5, 0, .5)]); lid_straps.V[:, 1] = np.maximum(lid_straps.V[:, 1], 0); lid_straps = lid_straps.tf(scale=(1, .62 * 1.02, 1.03))
studs = merge([sphere(.035, (x + dx, y, .475), rings=8, sides=10) for x in (-.5, 0, .5) for dx in (-.045, .045) for y in (.1, .3, .6)])
padlock = merge([box((.2, .22, .08), (0, .05, 0), seg=4), torus(.07, .018, (0, .2, 0), rot=(0, 0, 0), seg=20, sides=8)])
lion = merge([sphere(.07, (0, .06, .05), (1, 1, .4), 12, 16), sphere(.04, (-.045, .09, .05), (1, 1, .5), 8, 10), sphere(.04, (.045, .09, .05), (1, 1, .5), 8, 10)])
gems = merge([sphere(.09, (x, .06, 0), (1, 1, 1), 12, 16) for x in (-.3, .3)])
root_node = node("prp_ornate_treasure_chest", None, None, [node("body", body, TIMBER), node("straps", straps, IRON), node("studs", studs, GOLD), node("lid", lid, TIMBER, [
    node("lid_straps", lid_straps, IRON)], pos=(0, .7, -.45), rot=(-15, 0, 0)), node("padlock", padlock, GOLD, [node("lion", lion, IRON, pos=(0, .0, .06))], pos=(0, .5, .5))])
if __name__ == "__main__": print(compile_glb(root_node, out("props", "prp_ornate_treasure_chest"), 256))
