// Software rendering of a whole Scene (headless verifier + bullet-proof Windows fallback when GL 3.3 is unavailable):
// directional sun shadow map (PCF), golden-hour atmospheric sky, splat terrain, dynamic point lights and the minimal HP/Mana bars.
#pragma once
#include <vector>
#include <isekai/model.h>
#include "scene.hpp"
namespace isekai {
struct ShadowMap { int n = 0; std::vector<float> d; Vec3 focus, lx, ly, S; float ext = 90.f; };
struct SoftEnv { Vec3 sun{.5f, .8f, .45f}; const ShadowMap* sm = nullptr; const std::vector<Light>* lights = nullptr; Vec3 fogCol{.55f, .68f, .6f}; float fogDen = 0.025f; };
extern SoftEnv gEnv;
float softShadow(const ShadowMap& sm, Vec3 wp, Vec3 n, Vec3 L);
Vec3 softPointLights(Vec3 wp, Vec3 n, Vec3 alb);
void drawInstance(Framebuffer& fb, const Camera& cam, const Model& m, const Mat4& M, Vec3 tint, bool ground = false, const AnimState& anim = {});
void renderSceneSoft(Framebuffer& fb, const Scene& s);
}  // namespace isekai
