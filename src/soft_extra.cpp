#include "soft_extra.hpp"
#include <algorithm>
#include <cmath>
#include "math3d.hpp"
namespace isekai {
static void splat(Framebuffer& fb, float sx, float sy, float rad, Vec3 c, float a) {
  int x0 = std::max(0, int(sx - rad)), x1 = std::min(fb.w - 1, int(sx + rad)), y0 = std::max(0, int(sy - rad)), y1 = std::min(fb.h - 1, int(sy + rad));
  for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) { float d = std::hypot(x - sx, y - sy) / rad; if (d >= 1) continue; float k = std::pow(1 - d, 1.6f) * a; uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3];
    p[0] = uint8_t(std::min(255.f, p[0] + 255 * c.x * k)); p[1] = uint8_t(std::min(255.f, p[1] + 255 * c.y * k)); p[2] = uint8_t(std::min(255.f, p[2] + 255 * c.z * k)); } }
static void rect(Framebuffer& fb, int x0, int y0, int x1, int y1, Vec3 c) { for (int y = std::max(0, y0); y < std::min(fb.h, y1); y++) for (int x = std::max(0, x0); x < std::min(fb.w, x1); x++) { uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3]; p[0] = uint8_t(255 * c.x); p[1] = uint8_t(255 * c.y); p[2] = uint8_t(255 * c.z); } }
void renderSceneSoft(Framebuffer& fb, const Scene& s) {
  clearFrame(fb, s.skyTop * 1.3f, s.skyHorizon * 1.1f);
  for (const Instance& in : s.inst) if (in.model) drawInstance(fb, s.cam, *in.model, in.M, in.ground ? Vec3{.28f, .5f, .15f} : in.tint);
  Vec3 f = normalize(s.cam.target - s.cam.eye), r = normalize(cross(f, {0, 1, 0})), up = cross(r, f); float tanH = std::tan(s.cam.fovDeg * .5f * kPi / 180.f), asp = float(fb.w) / fb.h;
  for (const Fx& fx : s.fx) { Vec3 d = fx.pos - s.cam.eye; float cz = dot(d, f); if (cz < .3f) continue; float sx = (dot(d, r) / (cz * tanH * asp) * .5f + .5f) * fb.w, sy = (.5f - dot(d, up) / (cz * tanH) * .5f) * fb.h;
    splat(fb, sx, sy, std::min(160.f, fx.size * fb.h * .9f / cz), fx.color, fx.alpha); }
  int u = std::max(1, fb.h / 90);   // minimal HUD: hearts + minimap (full text HUD is GL-only)
  for (int i = 0; i < s.maxHearts; i++) rect(fb, (6 + i * 9) * u, 6 * u, (13 + i * 9) * u, 12 * u, i < s.hearts ? Vec3{.86f, .1f, .16f} : Vec3{.2f, .05f, .08f});
  int R = 22 * u, mx = fb.w - R - 4 * u, my = fb.h - R - 4 * u; for (int y = -R; y <= R; y++) for (int x = -R; x <= R; x++) if (x * x + y * y <= R * R) { uint8_t* p = &fb.rgb[(size_t(my + y) * fb.w + mx + x) * 3]; p[0] /= 3; p[1] = uint8_t(p[1] / 3 + 20); p[2] /= 3; }
  float fx = std::sin(s.camYaw), fz = std::cos(s.camYaw), hx = 0, hz = 0; for (auto& d : s.dots) if (d.kind == 0) { hx = d.x; hz = d.z; }
  for (auto& d : s.dots) { float dx = d.x - hx, dz = d.z - hz, px = mx + (dx * -fz + dz * fx) * R / 28.f, py = my - (dx * fx + dz * fz) * R / 28.f; if (std::hypot(px - mx, py - my) > R - 2) continue;
    Vec3 c = d.kind == 0 ? Vec3{.3f, 1, .5f} : d.kind == 1 ? Vec3{.4f, .7f, 1} : d.kind == 2 ? Vec3{1, .2f, .3f} : d.kind == 3 ? Vec3{1, .45f, .1f} : Vec3{1, .85f, .3f}; rect(fb, int(px) - u, int(py) - u, int(px) + u, int(py) + u, c); }
}
}  // namespace isekai
