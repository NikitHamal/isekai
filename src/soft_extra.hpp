// Software rendering of a whole Scene (headless verifier + bullet-proof Windows fallback when GL 3.3 is unavailable).
#pragma once
#include <isekai/model.h>
#include "scene.hpp"
namespace isekai {
void drawInstance(Framebuffer& fb, const Camera& cam, const Model& m, const Mat4& M, Vec3 tint);
void renderSceneSoft(Framebuffer& fb, const Scene& s);
}  // namespace isekai
