// Renderer-agnostic scene description produced by GameWorld each frame and consumed by the GL renderer or software fallback.
#pragma once
#include <string>
#include <vector>
#include <isekai/model.h>
#include "animator.hpp"
namespace isekai {
struct Instance {
  const Model* model = nullptr; Mat4 M{}; float emissive = 1.f; Vec3 tint{1, 1, 1};
  bool ground = false;      // splat-mapped terrain
  bool castShadow = true;
  bool windSway = false;    // vertex wind sway for grass tufts, wildflowers & tree canopies
  AnimState anim{};         // per-part hierarchical skeletal animation state
};
struct Light { Vec3 pos; Vec3 color; float radius = 8; };
struct Fx { Vec3 pos; float size = 0.2f; Vec3 color{1, .8f, .3f}; float alpha = 1.f; };   // additive glow sprite
struct RibbonSeg { Vec3 a0, b0, a1, b1; Vec3 color{0.75f, 0.9f, 1.f}; float alpha0 = 1.f, alpha1 = 1.f; };
struct Scene {
  Camera cam; float time = 0, heroYaw = 0, camYaw = 0;
  float hp = 1.f, mana = 1.f; bool casting = false;       // HUD: fractions 0..1
  int activeSpell = 0;                                    // 0=Crimson Flare, 1=Glacial Fang, 2=Aether Judgment
  std::vector<Instance> inst; std::vector<Light> lights; std::vector<Fx> fx;
  std::vector<RibbonSeg> ribbons;                         // 3D triangle-strip sword trails & lightning bolts
  Vec3 sunDir{0.62f, 0.38f, 0.30f};                        // golden-hour sun (unnormalised, points toward the sun)
  Vec3 focus{0, 0, 0};                                     // shadow-map centre (hero)
  Vec3 skyTop{.16f, .34f, .72f}, skyHorizon{1.0f, .66f, .36f};
};
}  // namespace isekai
