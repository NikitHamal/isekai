// Renderer-agnostic scene description produced by GameWorld each frame and consumed by the GL renderer or software fallback.
#pragma once
#include <string>
#include <vector>
#include <isekai/model.h>
namespace isekai {
struct Instance { const Model* model = nullptr; Mat4 M{}; float emissive = 1.f; Vec3 tint{1, 1, 1}; bool ground = false; };
struct Light { Vec3 pos; Vec3 color; float radius = 8; };
struct Fx { Vec3 pos; float size = 0.2f; Vec3 color{1, .8f, .3f}; float alpha = 1.f; };   // additive glow sprite
struct MapDot { float x, z; int kind; };   // 0 hero, 1 archway, 2 heart, 3 enemy, 4 chest, 5 signpost
struct Scene {
  Camera cam; float time = 0, heroYaw = 0, camYaw = 0; int hearts = 3, maxHearts = 3; float heartFrac = 0;
  std::vector<Instance> inst; std::vector<Light> lights; std::vector<Fx> fx; std::vector<MapDot> dots; std::string hint; int kills = 0;
  Vec3 skyTop{.18f, .42f, .85f}, skyHorizon{.95f, .82f, .55f};
};
}  // namespace isekai
