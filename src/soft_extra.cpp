#include "soft_extra.hpp"
#include <algorithm>
#include <cmath>
#include "math3d.hpp"
#include "terrain.hpp"
namespace isekai {
SoftEnv gEnv;
static void splat(Framebuffer& fb, float sx, float sy, float rad, Vec3 c, float a) {
  int x0 = std::max(0, int(sx - rad)), x1 = std::min(fb.w - 1, int(sx + rad)), y0 = std::max(0, int(sy - rad)), y1 = std::min(fb.h - 1, int(sy + rad));
  for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) { float d = std::hypot(x - sx, y - sy) / rad; if (d >= 1) continue; float k = std::pow(1 - d, 1.6f) * a; uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3];
    p[0] = uint8_t(std::min(255.f, p[0] + 255 * c.x * k)); p[1] = uint8_t(std::min(255.f, p[1] + 255 * c.y * k)); p[2] = uint8_t(std::min(255.f, p[2] + 255 * c.z * k)); } }
static void rect(Framebuffer& fb, int x0, int y0, int x1, int y1, Vec3 c, float a = 1.f) {
  for (int y = std::max(0, y0); y < std::min(fb.h, y1); y++) for (int x = std::max(0, x0); x < std::min(fb.w, x1); x++) { uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3];
    p[0] = uint8_t(p[0] * (1 - a) + 255 * c.x * a); p[1] = uint8_t(p[1] * (1 - a) + 255 * c.y * a); p[2] = uint8_t(p[2] * (1 - a) + 255 * c.z * a); } }
float softShadow(const ShadowMap& sm, Vec3 wp, Vec3 n, Vec3 L) {
  Vec3 q = wp + n * 0.06f - sm.focus; float u = dot(q, sm.lx) / sm.ext * .5f + .5f, v = dot(q, sm.ly) / sm.ext * .5f + .5f, d = dot(q, sm.S); (void)L;
  if (u < 0 || v < 0 || u >= 1 || v >= 1) return 1.f; int cx = int(u * sm.n), cy = int(v * sm.n); float lit = 0; int cnt = 0;
  for (int dy = -1; dy <= 1; dy++) for (int dx = -1; dx <= 1; dx++) { int x = std::clamp(cx + dx, 0, sm.n - 1), y = std::clamp(cy + dy, 0, sm.n - 1); lit += sm.d[size_t(y) * sm.n + x] > d + 0.12f ? 0.f : 1.f; cnt++; }
  return lit / cnt; }
Vec3 softPointLights(Vec3 wp, Vec3 n, Vec3 alb) {
  Vec3 o{}; if (!gEnv.lights) return o; for (const Light& l : *gEnv.lights) { Vec3 d = l.pos - wp; float dist = vlen(d); if (dist > l.radius || dist < 1e-3f) continue;
    float att = std::clamp(1.f - (dist / l.radius) * (dist / l.radius), 0.f, 1.f); att = att * att / (1.f + dist * dist * 0.2f); float nl = std::max(0.f, dot(n, d * (1.f / dist))) * att * 0.55f;
    o = o + Vec3{alb.x * l.color.x, alb.y * l.color.y, alb.z * l.color.z} * nl; } return o; }
static void shadowPass(ShadowMap& sm, const Scene& s) {
  sm.n = 2048; sm.d.assign(size_t(sm.n) * sm.n, -1e9f); sm.focus = s.focus; Vec3 S = normalize(s.sunDir); sm.S = S; sm.lx = normalize(cross({0, 1, 0}, S)); sm.ly = cross(S, sm.lx);
  for (const Instance& in : s.inst) { if (!in.model || !in.castShadow) continue;
    for (const Primitive& P : in.model->prims) { if (P.material >= 0 && (in.model->materials[P.material].blend || in.model->materials[P.material].mask)) continue;
      std::vector<Vec3> skP, skN; const std::vector<Vec3>* pPos = &P.pos; if (P.skinned && in.anim.rig != RIG_STATIC) { skinPrimitive(P, in.anim, skP, skN); pPos = &skP; }
      Mat4 PM = (in.anim.rig == RIG_STATIC || P.skinned) ? in.M : mMul(in.M, partTransform(in.anim, P.partId, P.pivot));
      std::vector<Vec3> V(P.pos.size()); for (size_t i = 0; i < V.size(); i++) { Vec3 q = transformPoint(PM, (*pPos)[i]) - sm.focus; V[i] = {(dot(q, sm.lx) / sm.ext * .5f + .5f) * sm.n, (dot(q, sm.ly) / sm.ext * .5f + .5f) * sm.n, dot(q, S)}; }
      for (size_t k = 0; k + 2 < P.idx.size(); k += 3) { const Vec3 &a = V[P.idx[k]], &b = V[P.idx[k + 1]], &c = V[P.idx[k + 2]]; float area = (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y); if (std::fabs(area) < 1e-9f) continue;
        int x0 = std::max(0, int(std::floor(std::min({a.x, b.x, c.x})))), x1 = std::min(sm.n - 1, int(std::ceil(std::max({a.x, b.x, c.x})))), y0 = std::max(0, int(std::floor(std::min({a.y, b.y, c.y})))), y1 = std::min(sm.n - 1, int(std::ceil(std::max({a.y, b.y, c.y}))));
        if (x1 - x0 > 600 || y1 - y0 > 600) continue;
        for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) { float px = x + .5f, py = y + .5f; float w0 = ((b.x - px) * (c.y - py) - (c.x - px) * (b.y - py)) / area, w1 = ((c.x - px) * (a.y - py) - (a.x - px) * (c.y - py)) / area, w2 = 1 - w0 - w1;
          if (w0 < -.02f || w1 < -.02f || w2 < -.02f) continue; float z = a.z * w0 + b.z * w1 + c.z * w2; float& dd = sm.d[size_t(y) * sm.n + x]; if (z > dd) dd = z; } } } } }
// Golden-hour atmospheric scattering (Rayleigh-ish zenith blue, Mie sun halo, warm horizon band, soft cloud streaks).
static Vec3 skyColor(Vec3 d, Vec3 sun, const Scene& s) {
  float h = std::clamp(d.y, 0.f, 1.f), mu = std::max(0.f, dot(d, sun)); Vec3 c = vmix(s.skyHorizon * 0.95f, s.skyTop, std::pow(h, 0.5f));
  float band = std::exp(-std::fabs(d.y) * 7.f); c = c + Vec3{1.0f, .45f, .18f} * (band * (0.25f + 0.9f * std::pow(mu, 3.f)));
  c = c + Vec3{1.f, .75f, .45f} * (std::pow(mu, 8.f) * .35f + std::pow(mu, 120.f) * 2.2f);
  if (d.y > 0.02f) { float u = d.x / (d.y + .25f) * 2.2f, v = d.z / (d.y + .25f) * 2.2f; float cl = std::clamp((tNoise(u * 1.3f, v * 2.5f) * .7f + tNoise(u * 3.f, v * 5.f) * .3f - .52f) * 3.f, 0.f, 1.f) * sstep(.02f, .3f, d.y) * .55f; c = vmix(c, Vec3{1.f, .78f, .6f} * 1.1f + Vec3{.1f, .05f, 0} * mu, cl); }
  if (d.y < 0) c = vmix(c, s.skyHorizon * .8f, std::clamp(1.f + d.y * 4.f, 0.f, 1.f)); return c; }
static float acesF(float x) { x *= 0.62f; return std::clamp((x * (2.51f * x + 0.03f)) / (x * (2.43f * x + 0.59f) + 0.14f), 0.f, 1.f); }
void renderSceneSoft(Framebuffer& fb, const Scene& s) {
  Vec3 f = normalize(s.cam.target - s.cam.eye), r = normalize(cross(f, {0, 1, 0})), up = cross(r, f); float tanH = std::tan(s.cam.fovDeg * .5f * kPi / 180.f), asp = float(fb.w) / fb.h; Vec3 sun = normalize(s.sunDir);
  for (int y = 0; y < fb.h; y++) for (int x = 0; x < fb.w; x++) { Vec3 d = normalize(f + r * ((x + .5f) / fb.w * 2 - 1) * tanH * asp + up * (1 - (y + .5f) / fb.h * 2) * tanH); Vec3 c = skyColor(d, sun, s); uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3];
    p[0] = uint8_t(255 * std::pow(acesF(c.x), 1.f / 2.2f)); p[1] = uint8_t(255 * std::pow(acesF(c.y), 1.f / 2.2f)); p[2] = uint8_t(255 * std::pow(acesF(c.z), 1.f / 2.2f)); }
  std::fill(fb.depth.begin(), fb.depth.end(), 1e30f);
  static ShadowMap sm; shadowPass(sm, s); gEnv.sun = sun; gEnv.sm = &sm; gEnv.lights = &s.lights; gEnv.fogCol = vmix(s.skyHorizon, Vec3{.6f, .65f, .75f}, .35f) * .8f; gEnv.fogDen = 0.0085f;
  for (const Instance& in : s.inst) if (in.model) drawInstance(fb, s.cam, *in.model, in.M, in.tint, in.ground, in.anim);
  gEnv.sm = nullptr; gEnv.lights = nullptr;
  // Screen-Space Ambient Occlusion (SSAO) from depth neighborhood
  const int dx8[8] = {1, -1, 0, 0, 1, -1, 1, -1}, dy8[8] = {0, 0, 1, -1, 1, -1, -1, 1};
  for (int y = 0; y < fb.h; y++) for (int x = 0; x < fb.w; x++) {
    float zc = fb.depth[size_t(y) * fb.w + x]; if (zc > 400.f) continue;
    int rad = std::clamp(int(14.f / std::max(zc, 0.5f)), 2, 9); float occ = 0.f;
    for (int k = 0; k < 8; k++) {
      int sx = std::clamp(x + dx8[k] * rad, 0, fb.w - 1), sy = std::clamp(y + dy8[k] * rad, 0, fb.h - 1);
      float dz = zc - fb.depth[size_t(sy) * fb.w + sx];
      if (dz > 0.03f && dz < 1.35f) occ += sstep(0.03f, 0.24f, dz) * (1.f - sstep(0.45f, 1.35f, dz));
    }
    float ao = std::clamp(1.f - occ * (0.54f / 8.f), 0.42f, 1.f);
    uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3];
    p[0] = uint8_t(p[0] * ao); p[1] = uint8_t(p[1] * ao); p[2] = uint8_t(p[2] * ao);
  }
  auto proj = [&](Vec3 p, float& sx, float& sy, float& cz) {
    Vec3 d = p - s.cam.eye; cz = dot(d, f); if (cz < 0.2f) return false;
    sx = (dot(d, r) / (cz * tanH * asp) * .5f + .5f) * fb.w; sy = (.5f - dot(d, up) / (cz * tanH) * .5f) * fb.h; return true;
  };
  auto addTri = [&](float x0, float y0, float z0, float a0, float x1, float y1, float z1, float a1, float x2, float y2, float z2, float a2, Vec3 col) {
    float area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0); if (std::fabs(area) < 1e-4f) return;
    int ix0 = std::max(0, int(std::min({x0, x1, x2}))), ix1 = std::min(fb.w - 1, int(std::max({x0, x1, x2})) + 1);
    int iy0 = std::max(0, int(std::min({y0, y1, y2}))), iy1 = std::min(fb.h - 1, int(std::max({y0, y1, y2})) + 1);
    for (int y = iy0; y <= iy1; y++) for (int x = ix0; x <= ix1; x++) {
      float px = x + .5f, py = y + .5f;
      float w0 = ((x1 - px) * (y2 - py) - (x2 - px) * (y1 - py)) / area, w1 = ((x2 - px) * (y0 - py) - (x0 - px) * (y2 - py)) / area, w2 = 1.f - w0 - w1;
      if (w0 < 0 || w1 < 0 || w2 < 0) continue;
      float z = z0 * w0 + z1 * w1 + z2 * w2; if (z > fb.depth[size_t(y) * fb.w + x] + 0.15f) continue;
      float al = a0 * w0 + a1 * w1 + a2 * w2; uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3];
      p[0] = uint8_t(std::min(255.f, p[0] + 255.f * col.x * al)); p[1] = uint8_t(std::min(255.f, p[1] + 255.f * col.y * al)); p[2] = uint8_t(std::min(255.f, p[2] + 255.f * col.z * al));
    }
  };
  for (const RibbonSeg& rb : s.ribbons) {
    float x0, y0, z0, x1, y1, z1, x2, y2, z2, x3, y3, z3;
    if (proj(rb.a0, x0, y0, z0) && proj(rb.b0, x1, y1, z1) && proj(rb.a1, x2, y2, z2) && proj(rb.b1, x3, y3, z3)) {
      addTri(x0, y0, z0, rb.alpha0 * .5f, x1, y1, z1, rb.alpha0, x3, y3, z3, rb.alpha1, rb.color);
      addTri(x0, y0, z0, rb.alpha0 * .5f, x3, y3, z3, rb.alpha1, x2, y2, z2, rb.alpha1 * .5f, rb.color);
    }
  }
  for (const Fx& fx : s.fx) { Vec3 d = fx.pos - s.cam.eye; float cz = dot(d, f); if (cz < .3f) continue; float sx = (dot(d, r) / (cz * tanH * asp) * .5f + .5f) * fb.w, sy = (.5f - dot(d, up) / (cz * tanH) * .5f) * fb.h;
    splat(fb, sx, sy, std::min(160.f, fx.size * fb.h * .9f / cz), fx.color, fx.alpha); }
  // Dual-pass separable Gaussian bloom on bright emissive/spell pixels
  { int bw = std::max(1, fb.w / 4), bh = std::max(1, fb.h / 4);
  std::vector<Vec3> b0(size_t(bw) * bh), b1(size_t(bw) * bh);
  for (int y = 0; y < bh; y++) for (int x = 0; x < bw; x++) {
    const uint8_t* p = &fb.rgb[(size_t(y * 4) * fb.w + x * 4) * 3];
    Vec3 c{p[0] / 255.f, p[1] / 255.f, p[2] / 255.f}; float br = std::max({c.x, c.y, c.z});
    b0[size_t(y) * bw + x] = (br > 0.72f) ? c * ((br - 0.72f) / 0.28f) : Vec3{};
  }
  const float gw[5] = {0.227f, 0.195f, 0.122f, 0.054f, 0.016f};
  for (int y = 0; y < bh; y++) for (int x = 0; x < bw; x++) {
    Vec3 acc = b0[size_t(y) * bw + x] * gw[0];
    for (int i = 1; i <= 4; i++) acc = acc + (b0[size_t(y) * bw + std::min(bw - 1, x + i)] + b0[size_t(y) * bw + std::max(0, x - i)]) * gw[i];
    b1[size_t(y) * bw + x] = acc;
  }
  for (int y = 0; y < bh; y++) for (int x = 0; x < bw; x++) {
    Vec3 acc = b1[size_t(y) * bw + x] * gw[0];
    for (int i = 1; i <= 4; i++) acc = acc + (b1[size_t(std::min(bh - 1, y + i)) * bw + x] + b1[size_t(std::max(0, y - i)) * bw + x]) * gw[i];
    b0[size_t(y) * bw + x] = acc;
  }
  for (int y = 0; y < fb.h; y++) for (int x = 0; x < fb.w; x++) {
    Vec3 bl = b0[size_t(std::min(bh - 1, y / 4)) * bw + std::min(bw - 1, x / 4)] * 0.55f;
    uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3];
    p[0] = uint8_t(std::min(255.f, p[0] + bl.x * 255.f)); p[1] = uint8_t(std::min(255.f, p[1] + bl.y * 255.f)); p[2] = uint8_t(std::min(255.f, p[2] + bl.z * 255.f));
  } }
  // Minimal dark-fantasy HUD: slim metallic-framed HP (crimson) and Mana (azure) bars, top-left. Nothing else.
  int u = std::max(1, fb.h / 450), x0 = 24 * u, bw = 190 * u, bh = 7 * u; const Vec3 frame{.55f, .5f, .42f}, back{.05f, .03f, .04f};
  auto bar = [&](int y, float v, Vec3 c0, Vec3 c1) { rect(fb, x0 - u, y - u, x0 + bw + u, y + bh + u, frame, .9f); rect(fb, x0, y, x0 + bw, y + bh, back, .9f); int w = int(bw * std::clamp(v, 0.f, 1.f));
    for (int i = 0; i < w; i += 1) { float t = float(i) / bw; rect(fb, x0 + i, y, x0 + i + 1, y + bh, vmix(c0, c1, t)); } rect(fb, x0, y, x0 + w, y + u, Vec3{1, 1, 1}, .25f); };
  bar(22 * u, s.hp, {.45f, .02f, .06f}, {.9f, .12f, .15f}); bar(22 * u + bh + 6 * u, s.mana, {.05f, .2f, .55f}, {.25f, .65f, 1.f});
  Vec3 sc = s.activeSpell == 1 ? Vec3{.25f, .88f, 1.f} : s.activeSpell == 2 ? Vec3{.86f, .45f, 1.f} : Vec3{1.f, .38f, .12f};
  int sx = x0 + bw + 8 * u, sy = 22 * u + bh + 6 * u;
  rect(fb, sx - u, sy - u, sx + bh + u, sy + bh + u, frame, .9f); rect(fb, sx, sy, sx + bh, sy + bh, sc, .95f);
  if (s.casting) rect(fb, fb.w / 2 - u, fb.h / 2 - u, fb.w / 2 + u + 1, fb.h / 2 + u + 1, Vec3{1, .85f, .6f}, .9f);
}
}  // namespace isekai
