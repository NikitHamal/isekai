#!/usr/bin/env python3
"""Humanoid body: lofted muscular torso, 2-segment arms & legs (separate articulated objects with joint pivots), fingered hands."""
import math
from mathutils import Vector as V
from anatomy_core import *

JOINT = dict(waist=V((0, 0, 1.06)), neck=V((0, 0, 1.53)), hip=V((0.092, 0, 0.93)), knee=V((0.092, -0.006, 0.505)), ankle=V((0.092, 0.01, 0.085)),
             sho=V((0.208, 0.0, 1.455)), elbow=V((0.272, 0.035, 1.145)), wrist_l=V((0.292, -0.045, 0.875)), wrist_r=V((-0.296, -0.135, 0.975)))

def mx(p): return V((-p.x, p.y, p.z))

def torso(skin, bulk=1.0, nm="torso", female=0.0, belly=0.0):
    b = bulk
    S = [(V((0, 0.006, 0.88)), .150 * b, .105 * b), (V((0, 0.004, 0.94)), .172 * b, .118 * b), (V((0, 0.0, 1.02)), .160 * b, .112 * b),
         (V((0, -0.002 - belly * .02, 1.10)), (.142 - female * .01) * b, (.102 + belly * .035) * b), (V((0, -0.004, 1.19)), .158 * b, .112 * b),
         (V((0, -0.010, 1.29)), .186 * b, .125 * b, 2.3), (V((0, -0.012, 1.38)), .202 * b, .122 * b, 2.4), (V((0, -0.004, 1.44)), .196 * b, .105 * b, 2.3),
         (V((0, 0.002, 1.485)), .125 * b, .082 * b), (V((0, 0.004, 1.52)), .066 * b, .066 * b)]
    t = loft(nm + "_body", S, skin, segs=24, tile=.45, sub=1, pivot=JOINT["waist"])
    def pecs(p):   # chest / abdominal definition sculpted with bmesh
        d = V((0, 0, 0))
        if p.y < -0.02:
            for sx in (-1, 1):
                f = max(0, 1 - ((p.x - sx * .08 * b) / (.075 * b)) ** 2 - ((p.z - 1.33) / .065) ** 2); d.y -= .016 * f * b
            if p.z < 1.20 and p.z > 0.98 and abs(p.x) < .09 * b: d.y -= .006 * max(0, math.cos((p.z - 1.09) / .11 * math.pi)) * (1 + (abs(p.x) < .02) * -.5)
        return d
    sculpt(t, pecs); return t

def leg(side, skin, bulk=1.0, nm="leg"):
    sx = 1 if side == "l" else -1; hp, kn, an = V((sx * .092, 0, .93)), V((sx * .092, -.006, .505)), V((sx * .092, .01, .085)); b = bulk
    th = loft("%s_%s_thigh" % (nm, side), [(hp + V((0, 0, .03)), .084 * b, .092 * b), (V((sx * .092, -.002, .80)), .090 * b, .094 * b, 2.1), (V((sx * .090, -.006, .66)), .078 * b, .082 * b), (kn + V((0, -.002, .02)), .056 * b, .062 * b), (kn - V((0, 0, .03)), .054 * b, .058 * b)],
              skin, segs=16, tile=.45, sub=1, pivot=hp)
    th.name = "%s_%s" % (nm, side); return th

def shin(side, skin, bulk=1.0, nm="shin"):
    sx = 1 if side == "l" else -1; kn = V((sx * .092, -.006, .505)); b = bulk
    S = [(kn + V((0, .004, .03)), .054 * b, .058 * b), (V((sx * .092, -.004, .45)), .056 * b, .063 * b), (V((sx * .092, .012, .37)), .060 * b, .070 * b), (V((sx * .092, .010, .26)), .048 * b, .054 * b), (V((sx * .092, .008, .14)), .036 * b, .040 * b), (V((sx * .092, .010, .085)), .037 * b, .040 * b)]
    return loft("%s_%s_calf" % (nm, side), S, skin, segs=14, tile=.4, sub=1, pivot=kn)

def foot(side, mat, bulk=1.0, nm="shin", long=1.0):
    sx = 1 if side == "l" else -1; b = bulk; kn = V((sx * .092, -.006, .505))
    P = [V((sx * .092, .062, .045)), V((sx * .092, .02, .042)), V((sx * .092, -.05, .035)), V((sx * .092, -.115 * long, .028)), V((sx * .092, -.158 * long, .024))]
    S = [(P[0], .036 * b, .036 * b), (P[1], .046 * b, .050 * b), (P[2], .048 * b, .042 * b), (P[3], .043 * b, .028 * b), (P[4], .030 * b, .018 * b)]
    return loft("%s_%s_foot" % (nm, side), S, mat, segs=12, ref=(1, 0, 0), tile=.3, sub=1, pivot=kn)

def upper_arm(side, skin, bulk=1.0, nm="arm", S=None, E=None):
    sx = 1 if side == "l" else -1; S = S or V((sx * .208, 0, 1.455)); E = E or V((sx * .272, .035, 1.145)); b = bulk; d = (E - S).normalized()
    secs = [(S - d * .030 + V((-sx * .01, 0, .0)), .056 * b, .056 * b), (S + d * .02, .062 * b, .060 * b, 2.1), (S + d * .09, .060 * b, .058 * b), (S + (E - S) * .55, .050 * b, .052 * b), (S + (E - S) * .82, .043 * b, .046 * b), (E + d * .02, .040 * b, .042 * b)]
    return loft("%s_%s" % (nm, side), secs, skin, segs=14, ref=(0, 1, 0), tile=.4, sub=1, pivot=S)

def forearm(side, skin, bulk=1.0, nm="forearm", E=None, W=None):
    sx = 1 if side == "l" else -1; E = E or V((sx * .272, .035, 1.145)); W = W or (JOINT["wrist_l"] if side == "l" else JOINT["wrist_r"]); b = bulk; d = W - E
    secs = [(E - d.normalized() * .015, .040 * b, .042 * b), (E + d * .12, .046 * b, .046 * b), (E + d * .32, .048 * b, .044 * b), (E + d * .65, .037 * b, .035 * b), (E + d * .93, .029 * b, .028 * b), (W + d.normalized() * .01, .029 * b, .025 * b)]
    return loft("%s_%s_arm" % (nm, side), secs, skin, segs=14, ref=(0, 0, 1), tile=.35, sub=1, pivot=E)

def hand_relaxed(side, skin, W, bulk=1.0, nm="forearm", E=None):
    """Open relaxed hand (fingers gently curled, thumb forward) attached to the wrist; pivot = elbow (moves with forearm)."""
    sx = 1 if side == "l" else -1; E = E or V((sx * .272, .035, 1.145)); b = bulk; objs = []
    dn = V((0, 0, -1)); inw = V((-sx, 0, 0))
    palm = loft("%s_%s_palm" % (nm, side), [(W + dn * .005, .027 * b, .019 * b), (W + dn * .045, .036 * b, .018 * b), (W + dn * .088, .038 * b, .0155 * b)], skin, segs=10, ref=(sx, 0, 0), tile=.2, sub=1, pivot=E); objs.append(palm)
    for i, (yo, ln) in enumerate(((-.027, .046), (-.009, .050), (.009, .047), (.026, .038))):
        p = W + dn * .088 + V(0, yo * b, 0); pts = [p]; th = .12
        for seg in range(3):
            th += (.28 + .15 * seg + i * .03); p = p + V((-sx * math.sin(th), 0, -math.cos(th))) * (ln / 3 * b); pts.append(p.copy())
        objs.append(tube("%s_%s_finger%d" % (nm, side, i), pts, [.0092 * b, .0082 * b, .0072 * b, .0058 * b], skin, segs=8, flat=.92, sub=1, pivot=E))
    tp = [W + V(-sx * .002, -.026 * b, -.022), W + V(-sx * .012, -.044 * b, -.05), W + V(-sx * .020, -.056 * b, -.078), W + V(-sx * .024, -.058 * b, -.101)]
    objs.append(tube("%s_%s_thumb" % (nm, side), tp, [.0125 * b, .0105 * b, .0092 * b, .0075 * b], skin, segs=8, flat=.95, sub=1, pivot=E))
    return objs

def hand_grip(side, skin, W, G, bulk=1.0, nm="forearm", E=None, grip_r=.0165, spread=0.0):
    """Fist wrapped around a vertical sword/axe grip centred on G: palm block + 4 stacked fingers arcing round the grip + overlapping thumb."""
    b = bulk; E = E or V((0, 0, 1)); objs = []; sx = 1 if side == "l" else -1
    back = V(0, .026 * b, 0)
    palm = loft("%s_%s_palm" % (nm, side), [(W, .028 * b, .021 * b), (W.lerp(G + back, .6), .036 * b, .020 * b), (G + back + V(0, 0.002, 0), .040 * b, .018 * b)], skin, segs=10, ref=(0, 0, 1), tile=.2, sub=1, pivot=E); objs.append(palm)
    Rf = grip_r + .0085 * b
    for i in range(4):
        z = G.z + .034 * b - i * .0215 * b; r = (.0092 - i * .0004) * b; pts = []
        for k in range(8):
            a = math.radians(95 + k * 36); pts.append(V(G.x + math.cos(a) * Rf * (1 - .03 * k / 7), G.y + math.sin(a) * Rf, z - k * .0006))
        objs.append(tube("%s_%s_finger%d" % (nm, side, i), pts, [r] * 3 + [r * .92] * 3 + [r * .8] * 2, skin, segs=8, flat=1.0, sub=1, pivot=E))
    pts = [V(G.x + math.cos(math.radians(70 - k * 30)) * (Rf + .008 * b), G.y + math.sin(math.radians(70 - k * 30)) * (Rf + .008 * b), G.z + .052 * b - k * .0035) for k in range(6)]
    objs.append(tube("%s_%s_thumb" % (nm, side), [W.lerp(G + back, .85) + V(0, 0, .02)] + pts, [.0125 * b, .0115 * b, .011 * b, .010 * b, .0092 * b, .008 * b, .0065 * b], skin, segs=8, flat=1.0, sub=1, pivot=E))
    return objs

def scale_all(s, sx=1.0, sy=1.0):
    """Scale every object (vertex data + locations): s uniform, sx widens (bulk), sy deepens; solidify thickness unchanged."""
    M = Matrix.Diagonal((s * sx, s * sy, s, 1))
    for ob in OBJS:
        ob.data.transform(M); ob.location = V((ob.location.x * s * sx, ob.location.y * s * sy, ob.location.z * s))
