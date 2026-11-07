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
};

inline Mat4 aroundPivot(Vec3 piv, const Mat4& R, Vec3 shift = {}) {
  return mMul(mTrans(piv + shift), mMul(R, mTrans(piv * -1.f)));
}

inline Mat4 partTransform(const AnimState& a, int partId, Vec3 pivot) {
  if (a.rig == RIG_STATIC || partId == PART_ROOT) return mIdent();
  float sp = std::clamp(a.speed / 6.5f, 0.f, 1.f);
  float breathe = std::sin(a.time * 2.3f);

  if (a.rig == RIG_QUADRUPED) {
    float gallop = std::sin(a.walkPhase) * 0.62f * sp;
    float spinePitch = std::cos(a.walkPhase) * 0.08f * sp + 0.02f * breathe;
    float bite = std::sin(a.attackProgress * kPi);
    if (partId == PART_TORSO) return aroundPivot(pivot, mRotX(spinePitch));
    if (partId == PART_HEAD) return aroundPivot(pivot, mRotX(spinePitch - 0.35f * bite + 0.04f * breathe), {0.f, 0.05f * bite, 0.14f * bite});
    if (partId == PART_LEG_L) return aroundPivot(pivot, mRotX(gallop - 0.3f * bite));
    if (partId == PART_LEG_R) return aroundPivot(pivot, mRotX(-gallop + 0.2f * bite));
    if (partId == PART_JAW_OR_TAIL) return aroundPivot(pivot, mMul(mRotY(std::sin(a.time * 4.2f) * 0.28f), mRotX(0.18f * std::cos(a.time * 3.1f))));
    return mIdent();
  }

  // Biped & Hero rigs
  float stride = std::sin(a.walkPhase) * 0.68f * sp;
  float torsoPitch = 0.025f * breathe + sp * 0.20f;
  float torsoYaw = std::sin(a.walkPhase) * 0.08f * sp;
  float headPitch = -0.02f * breathe - sp * 0.10f, headYaw = -torsoYaw * 0.5f;
  float cloakPitch = 0.04f + 0.03f * std::sin(a.time * 2.7f) + sp * 0.18f + 0.04f * std::sin(a.walkPhase * 2.f) * sp;
  float cloakSway = 0.025f * std::cos(a.time * 2.1f);
  float legLPitch = stride, legRPitch = -stride;
  float armLPitch = -stride * 0.75f + 0.03f * breathe;
  float armRPitch = stride * 0.65f - 0.08f + 0.03f * breathe, armRYaw = 0.f, armRZ = 0.f;

  if (a.airborne) {
    legLPitch = -0.48f; legRPitch = 0.32f; armLPitch = -0.45f; armRPitch = -0.35f; cloakPitch += 0.35f;
  }
  if (a.rollProgress > 0.f) {
    torsoPitch += 0.35f; legLPitch = -0.65f; legRPitch = -0.65f; armLPitch = -0.7f; armRPitch = -0.7f;
  }
  if (a.slashing) {
    float k = std::clamp(a.slashProgress, 0.f, 1.f), e = k * k * (3.f - 2.f * k);
    if (a.combo == 0) {
      torsoYaw += lerpf(-0.42f, 0.48f, e); torsoPitch += 0.14f;
      armRPitch = lerpf(-1.25f, 0.55f, e); armRYaw = lerpf(-0.55f, 0.65f, e); armRZ = -0.28f;
    } else if (a.combo == 1) {
      torsoYaw += lerpf(0.52f, -0.52f, e); torsoPitch += 0.16f;
      armRPitch = -0.72f; armRYaw = lerpf(0.90f, -0.90f, e); armRZ = 0.25f;
    } else {
      torsoPitch += lerpf(-0.28f, 0.42f, e);
      armRPitch = lerpf(-2.15f, 0.65f, e); armRYaw = 0.f;
    }
    cloakPitch += 0.24f;
  }
  if (a.attackProgress > 0.f) {
    float s = std::sin(a.attackProgress * kPi);
    torsoYaw += 0.38f * s; torsoPitch += 0.18f * s;
    armRPitch = lerpf(armRPitch, -1.35f + 1.85f * a.attackProgress, s);
  }
  if (a.castWeight > 0.f) {
    float cw = std::clamp(a.castWeight, 0.f, 1.f);
    torsoYaw -= 0.22f * cw;
    armLPitch = lerpf(armLPitch, -1.38f, cw);
    cloakPitch += 0.12f * cw;
  }

  Mat4 Rtorso = mMul(mRotY(torsoYaw), mRotX(torsoPitch));
  if (partId == PART_TORSO) return aroundPivot(pivot, Rtorso);
  if (partId == PART_LEG_L) return aroundPivot(pivot, mRotX(legLPitch));
  if (partId == PART_LEG_R) return aroundPivot(pivot, mRotX(legRPitch));
  if (partId == PART_HEAD) return aroundPivot(pivot, mMul(Rtorso, mMul(mRotY(headYaw), mRotX(headPitch))));
  if (partId == PART_CLOAK) return aroundPivot(pivot, mMul(mRotY(torsoYaw * 0.35f), mMul(mRotZ(cloakSway), mRotX(cloakPitch))));
  if (partId == PART_ARM_L) return aroundPivot(pivot, mMul(Rtorso, mRotX(armLPitch)));
  if (partId == PART_ARM_R || partId == PART_WEAPON_R) {
    Mat4 Rarm = mMul(Rtorso, mMul(mRotY(armRYaw), mMul(mRotZ(armRZ), mRotX(armRPitch))));
    return aroundPivot(pivot, Rarm);
  }
  return mIdent();
}
}  // namespace isekai
