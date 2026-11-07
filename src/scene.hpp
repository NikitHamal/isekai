// Renderer-agnostic scene description produced by GameWorld each frame and consumed by the GL renderer or software fallback.
#pragma once
#include <string>
#include <vector>
#include <isekai/model.h>
namespace isekai {
struct Instance {
  const Model* model = nullptr; Mat4 M{}; float emissive = 1.f; Vec3 tint{1, 1, 1};
  bool ground = false;      // splat-mapped terrain
  bool castShadow = true;
};
struct Light { Vec3 pos; Vec3 color; float radius = 8; };
struct Fx { Vec3 pos; float size = 0.2f; Vec3 color{1, .8f, .3f}; float alpha = 1.f; };   // additive glow sprite
struct Scene {
  Camera cam; float time = 0, heroYaw = 0, camYaw = 0;
  float hp = 1.f, mana = 1.f; bool casting = false;       // HUD: fractions 0..1
  std::vector<Instance> inst; std::vector<Light> lights; std::vector<Fx> fx;
  Vec3 sunDir{0.62f, 0.38f, 0.30f};                        // golden-hour sun (unnormalised, points toward the sun)
  Vec3 focus{0, 0, 0};                                     // shadow-map centre (hero)
  Vec3 skyTop{.16f, .34f, .72f}, skyHorizon{1.0f, .66f, .36f};
};
}  // namespace isekai
