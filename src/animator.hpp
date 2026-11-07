// Hierarchical multi-part procedural skeletal animation for Hero, Allies, Biped Enemies, and Quadruped Monsters.
#pragma once
#include <algorithm>
#include <cmath>
#include "math3d.hpp"
namespace isekai {
enum AnimRig : int { RIG_STATIC = 0, RIG_HERO = 1, RIG_BIPED = 2, RIG_QUADRUPED = 3 };

struct AnimState {
  int rig = RIG_STATIC;
  float time = 0.f;
  float walkPhase = 0.f;
  float speed = 0.f;           // movement speed (m/s)
  float slashProgress = 0.f;   // 0..1 during 3-hit sword combo
  int combo = 0;               // 0 = diagonal cleave, 1 = reverse horizontal slash, 2 = overhead slam
  bool slashing = false;
  float castWeight = 0.f;      // 0..1 during magic cast
  float rollProgress = 0.f;    // 0..1 during dodge roll
  bool airborne = false;
  float attackProgress = 0.f;  // 0..1 for ally/monster melee swing or wolf bite
  const Vec3* pv = nullptr; const bool* pvHas = nullptr;   // per-part joint pivots of the model (waist, shoulders, elbows, hips, knees)
};


inline Mat4 aroundPivot(Vec3 piv, const Mat4& R, Vec3 shift = {}) {
  return mMul(mTrans(piv + shift), mMul(R, mTrans(piv * -1.f)));
}
inline Vec3 jointOf(const AnimState& a, int pid, Vec3 fb) { return (a.pv && a.pvHas && a.pvHas[pid]) ? a.pv[pid] : fb; }
inline float sstep01(float x) { x = std::clamp(x, 0.f, 1.f); return x * x * (3.f - 2.f * x); }

// Hierarchical pose: waist -> torso -> (neck/head, shoulder -> elbow), hip -> knee. Positive X-pitch swings a hanging limb backward, negative raises it forward.
inline Mat4 partTransform(const AnimState& a, int partId, Vec3 pivot) {
  if (a.rig == RIG_STATIC) return mIdent();
  float sp = std::clamp(a.speed / 6.5f, 0.f, 1.f), breathe = std::sin(a.time * 2.3f);
  Vec3 waist = jointOf(a, PART_TORSO, pivot);
  Mat4 G = mIdent();   // whole-body transform (dodge roll tumble)
  if (a.rollProgress > 0.f) { float k = std::clamp(a.rollProgress, 0.f, 1.f); Vec3 c = waist + Vec3{0.f, 0.05f, 0.f}; G = aroundPivot(c, mRotX(k * 2.f * kPi), {0.f, -0.18f * std::sin(k * kPi), 0.f}); }
  if (a.rig == RIG_QUADRUPED) {
    float gallop = std::sin(a.walkPhase) * 0.62f * sp, spinePitch = std::cos(a.walkPhase) * 0.08f * sp + 0.02f * breathe, bite = std::sin(a.attackProgress * kPi);
    Mat4 L = mIdent();
    if (partId == PART_TORSO) L = aroundPivot(pivot, mRotX(spinePitch));
    else if (partId == PART_HEAD) L = aroundPivot(pivot, mRotX(spinePitch - 0.35f * bite + 0.04f * breathe), {0.f, 0.05f * bite, 0.14f * bite});
    else if (partId == PART_LEG_L) L = aroundPivot(pivot, mRotX(gallop - 0.3f * bite));
    else if (partId == PART_LEG_R) L = aroundPivot(pivot, mRotX(-gallop + 0.2f * bite));
    else if (partId == PART_JAW_OR_TAIL) L = aroundPivot(pivot, mMul(mRotY(std::sin(a.time * 4.2f) * 0.28f), mRotX(0.18f * std::cos(a.time * 3.1f) - 0.2f * sp)));
    return mMul(G, L);
  }
  float ph = a.walkPhase, s1 = std::sin(ph);
  float bob = (std::fabs(std::cos(ph)) - 0.5f) * 0.035f * sp + 0.004f * breathe;
  float torsoPitch = 0.02f * breathe + sp * 0.17f, torsoYaw = s1 * 0.10f * sp, torsoRoll = std::cos(ph) * 0.03f * sp;
  float headPitch = -0.02f * breathe - sp * 0.10f, headYaw = -torsoYaw * 0.6f;
  float cloakPitch = 0.04f + 0.03f * std::sin(a.time * 2.7f) + sp * 0.22f + 0.05f * std::sin(ph * 2.f) * sp, cloakSway = 0.025f * std::cos(a.time * 2.1f);
  float hipL = s1 * 0.72f * sp, hipR = -hipL;
  float kneeL = std::max(0.f, -std::cos(ph)) * 1.05f * sp, kneeR = std::max(0.f, std::cos(ph)) * 1.05f * sp;
  float armLP = -s1 * 0.60f * sp + 0.03f * breathe, armLZ = 0.f, elbL = -0.22f - 0.55f * sp * std::max(0.f, std::cos(ph)) - 0.04f * breathe;
  float armRP = s1 * 0.38f * sp - 0.05f + 0.03f * breathe, armRY = 0.f, armRZ = 0.f, elbR = -0.10f - 0.08f * sp - 0.03f * breathe;
  float crouch = 0.f;
  if (a.airborne) { hipL = -0.55f; hipR = 0.30f; kneeL = 0.9f; kneeR = 0.5f; armLP = -0.5f; armRP = -0.45f; elbL = -0.7f; elbR = -0.5f; cloakPitch += 0.45f; torsoPitch += 0.05f; }
  if (a.slashing) {
    float k = std::clamp(a.slashProgress, 0.f, 1.f), e = sstep01(k), wind = sstep01(k * 3.f) * (1.f - sstep01((k - 0.25f) * 4.f)), lunge = std::sin(std::min(k * 1.4f, 1.f) * kPi);
    if (a.combo == 0) { torsoYaw += lerpf(-0.55f, 0.65f, e); torsoPitch += 0.14f; armRP = lerpf(-1.6f, 0.15f, e); armRY = lerpf(-0.7f, 0.85f, e); armRZ = lerpf(-0.45f, -0.05f, e); elbR = lerpf(-1.25f, -0.15f, e); }
    else if (a.combo == 1) { torsoYaw += lerpf(0.75f, -0.75f, e); torsoPitch += 0.12f; armRP = lerpf(-1.05f, -0.80f, e); armRY = lerpf(1.25f, -1.1f, e); armRZ = lerpf(0.3f, -0.2f, e); elbR = lerpf(-1.0f, -0.12f, e); }
    else { float up = sstep01(k / 0.38f), dn = sstep01((k - 0.38f) / 0.30f); torsoPitch += lerpf(-0.30f, 0.50f, dn) * (k > 0.38f ? 1.f : up * 0.6f); armRP = k < 0.38f ? lerpf(-0.4f, -2.6f, up) : lerpf(-2.6f, 0.25f, dn); elbR = k < 0.38f ? lerpf(-0.5f, -1.0f, up) : lerpf(-1.0f, -0.1f, dn); crouch = dn * (1.f - sstep01((k - 0.7f) * 3.f)) * 0.7f; }
    hipL = -0.55f * lunge - 0.15f * crouch; hipR = 0.35f * lunge + 0.5f * crouch; kneeL = 0.35f * lunge + 0.9f * crouch; kneeR = 0.5f * lunge + 0.5f * crouch;
    armLP = 0.55f * e - 0.2f; armLZ = 0.35f; elbL = -0.5f; cloakPitch += 0.30f + wind * 0.1f;
  }
  if (a.attackProgress > 0.f) {   // monster / ally melee: heavy overhead chop
    float k = std::clamp(a.attackProgress, 0.f, 1.f), up = sstep01(k / 0.45f), dn = sstep01((k - 0.45f) / 0.3f), s = std::sin(k * kPi);
    armRP = k < 0.45f ? lerpf(armRP, -2.5f, up) : lerpf(-2.5f, 0.35f, dn); elbR = k < 0.45f ? lerpf(elbR, -1.1f, up) : lerpf(-1.1f, -0.15f, dn);
    torsoPitch += (k < 0.45f ? -0.28f * up : lerpf(-0.28f, 0.45f, dn)); torsoYaw += 0.25f * s; armLP = -0.8f * s; elbL = -0.8f * s;
  }
  if (a.castWeight > 0.f) {
    float cw = std::clamp(a.castWeight, 0.f, 1.f), r = 1.f - 0.18f * std::sin((1.f - cw) * kPi);   // recoil
    torsoYaw -= 0.30f * cw; armLP = lerpf(armLP, -1.52f * r, cw); armLZ = lerpf(armLZ, -0.10f, cw); elbL = lerpf(elbL, -0.06f, cw); cloakPitch += 0.14f * cw; headYaw += 0.15f * cw;
  }
  if (a.rollProgress > 0.f) { torsoPitch += 0.55f; hipL = -1.45f; hipR = -1.45f; kneeL = 1.9f; kneeR = 1.9f; armLP = -1.3f; armRP = -1.3f; elbL = -1.5f; elbR = -1.5f; headPitch += 0.4f; }
  Mat4 Rt = mMul(mRotY(torsoYaw), mMul(mRotZ(torsoRoll), mRotX(torsoPitch)));
  Mat4 Tt = mMul(mTrans({0.f, bob - crouch * 0.12f, 0.f}), aroundPivot(waist, Rt));   // torso chain base
  auto armChain = [&](int sPart, int ePart, float ap, float ay, float az, float el, bool forearm) {
    Vec3 sh = jointOf(a, sPart, pivot); Mat4 R = mMul(mRotY(ay), mMul(mRotZ(az), mRotX(ap)));
    Mat4 M = mMul(Tt, aroundPivot(sh, R));
    if (forearm) { Vec3 el3 = jointOf(a, ePart, pivot); M = mMul(M, aroundPivot(el3, mRotX(el))); }
    return mMul(G, M); };
  auto legChain = [&](int hPart, int kPart, float hp, float kn, bool shin) {
    Vec3 hp3 = jointOf(a, hPart, pivot); Mat4 M = mMul(mTrans({0.f, bob * 0.5f - crouch * 0.12f, 0.f}), aroundPivot(hp3, mRotX(hp)));
    if (shin) M = mMul(M, aroundPivot(jointOf(a, kPart, pivot), mRotX(kn)));
    return mMul(G, M); };
  switch (partId) {
    case PART_ROOT: return G;
    case PART_TORSO: return mMul(G, Tt);
    case PART_HEAD: return mMul(G, mMul(Tt, aroundPivot(pivot, mMul(mRotY(headYaw), mRotX(headPitch)))));
    case PART_CLOAK: return mMul(G, mMul(Tt, aroundPivot(pivot, mMul(mRotY(torsoYaw * 0.35f), mMul(mRotZ(cloakSway), mRotX(cloakPitch))))));
    case PART_ARM_L: return armChain(PART_ARM_L, PART_FOREARM_L, armLP, 0.f, armLZ, 0.f, false);
    case PART_FOREARM_L: return armChain(PART_ARM_L, PART_FOREARM_L, armLP, 0.f, armLZ, elbL, true);
    case PART_ARM_R: { bool fr = !(a.pvHas && a.pvHas[PART_FOREARM_R]); if (fr) return armChain(PART_ARM_R, PART_ARM_R, armRP, armRY, armRZ, 0.f, false); return armChain(PART_ARM_R, PART_FOREARM_R, armRP, armRY, armRZ, 0.f, false); }
    case PART_FOREARM_R: case PART_WEAPON_R:
      if (a.pvHas && a.pvHas[PART_FOREARM_R]) return armChain(PART_ARM_R, PART_FOREARM_R, armRP, armRY, armRZ, elbR, true);
      return armChain(PART_ARM_R, PART_ARM_R, armRP, armRY, armRZ, 0.f, false);
    case PART_JAW_OR_TAIL: return mMul(G, mMul(Tt, aroundPivot(pivot, mMul(mRotY(std::sin(a.time * 3.1f) * (0.22f + 0.2f * sp) - torsoYaw * 0.8f), mRotX(0.10f + 0.30f * sp + 0.06f * std::sin(a.time * 2.2f))))));
    case PART_LEG_L: return legChain(PART_LEG_L, PART_SHIN_L, hipL, kneeL, false);
    case PART_SHIN_L: return legChain(PART_LEG_L, PART_SHIN_L, hipL, kneeL, true);
    case PART_LEG_R: return legChain(PART_LEG_R, PART_SHIN_R, hipR, kneeR, false);
    case PART_SHIN_R: return legChain(PART_LEG_R, PART_SHIN_R, hipR, kneeR, true);
    default: return G;
  }
}
// CPU part-blend skinning: each vertex stores (part0, part1 + blend) in TEXCOORD_1; position = lerp(M[part0] p, M[part1] p, blend) with the hierarchical part poses above.
inline void skinPrimitive(const Primitive& P, const AnimState& a, std::vector<Vec3>& pos, std::vector<Vec3>& nrm) {
  Mat4 pm[PART_COUNT];
  for (int k = 0; k < PART_COUNT; k++) pm[k] = partTransform(a, k, (a.pv && a.pvHas && a.pvHas[k]) ? a.pv[k] : P.pivot);
  size_t n = P.pos.size(); pos.resize(n); nrm.resize(n);
  for (size_t i = 0; i < n; i++) {
    int j0 = std::clamp(int(P.uv2[i * 2] + 0.5f), 0, PART_COUNT - 1); float v = P.uv2[i * 2 + 1]; int j1 = std::clamp(int(std::floor(v + 1e-3f)), 0, PART_COUNT - 1); float wb = std::clamp(v - float(j1), 0.f, 1.f);
    if (wb < 1e-3f || j0 == j1) { pos[i] = transformPoint(pm[j0], P.pos[i]); nrm[i] = transformDir(pm[j0], P.nrm[i]); continue; }
    pos[i] = transformPoint(pm[j0], P.pos[i]) * (1.f - wb) + transformPoint(pm[j1], P.pos[i]) * wb;
    nrm[i] = normalize(transformDir(pm[j0], P.nrm[i]) * (1.f - wb) + transformDir(pm[j1], P.nrm[i]) * wb);
  }
}
}  // namespace isekai
