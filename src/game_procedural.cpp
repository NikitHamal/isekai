// Procedural ground, frontier pine trees, mossy boulders, and batched 3D meadow grass tufts & wildflowers.
#include "game_world.hpp"
#include <cmath>
#include "kingdom.hpp"
#include "terrain.hpp"
namespace isekai {
static Texture makeNoiseTex(Vec3 c0, Vec3 c1, float freq, int seed) {
  Texture t; t.w = t.h = 64; t.rgba.resize(64 * 64 * 4);
  for (int y = 0; y < 64; y++) for (int x = 0; x < 64; x++) {
    float n = 0.65f * tNoise(x * freq + seed * 7.f, y * freq + seed * 13.f) + 0.35f * tNoise(x * freq * 2.3f, y * freq * 2.3f);
    Vec3 c = vmix(c0, c1, std::clamp(n, 0.f, 1.f)); uint8_t* p = &t.rgba[(y * 64 + x) * 4];
    p[0] = uint8_t(std::clamp(c.x * 255.f, 0.f, 255.f)); p[1] = uint8_t(std::clamp(c.y * 255.f, 0.f, 255.f));
    p[2] = uint8_t(std::clamp(c.z * 255.f, 0.f, 255.f)); p[3] = 255;
  }
  return t;
}
static void updateBounds(Model& m) {
  m.bmin = {1e9f, 1e9f, 1e9f}; m.bmax = {-1e9f, -1e9f, -1e9f};
  for (auto& p : m.prims) for (auto& v : p.pos) {
    m.bmin = {std::min(m.bmin.x, v.x), std::min(m.bmin.y, v.y), std::min(m.bmin.z, v.z)};
    m.bmax = {std::max(m.bmax.x, v.x), std::max(m.bmax.y, v.y), std::max(m.bmax.z, v.z)};
  }
}
Model makeBoxModel(Vec3 h, Vec3 c, Vec3 rgb) {
  Model m; m.name = "box"; Primitive P; const Vec3 N[6] = {{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
  for (int f = 0; f < 6; f++) { Vec3 n = N[f], u = std::fabs(n.y) > .5f ? Vec3{1, 0, 0} : Vec3{0, 1, 0}, v = cross(n, u); u = cross(v, n); uint32_t b = (uint32_t)P.pos.size();
    for (int k = 0; k < 4; k++) { float su = (k == 1 || k == 2) ? 1.f : -1.f, sv = k >= 2 ? 1.f : -1.f; Vec3 d = n + u * su + v * sv;
      P.pos.push_back({c.x + d.x * h.x, c.y + d.y * h.y, c.z + d.z * h.z}); P.nrm.push_back(n); P.uv.push_back(su * .5f + .5f); P.uv.push_back(sv * .5f + .5f); }
    for (uint32_t i : {0u, 1u, 2u, 0u, 2u, 3u}) P.idx.push_back(b + i); }
  Material mt; mt.name = "placeholder"; mt.baseFactor[0] = rgb.x; mt.baseFactor[1] = rgb.y; mt.baseFactor[2] = rgb.z; m.materials.push_back(mt); P.material = 0; m.prims.push_back(P);
  updateBounds(m); return m;
}
Model makeTerrainModel(float h, float step) {
  Model m; m.name = "terrain"; Primitive P; const int N = int(2 * h / step);
  for (int j = 0; j <= N; j++) for (int i = 0; i <= N; i++) {
    float x = -h + i * step, z = -h + j * step, y = terrainHeight(x, z);
    float dx = terrainHeight(x + .5f, z) - terrainHeight(x - .5f, z), dz = terrainHeight(x, z + .5f) - terrainHeight(x, z - .5f);
    P.pos.push_back({x, y, z}); P.nrm.push_back(normalize({-dx, 1.f, -dz})); P.uv.push_back(x * .25f); P.uv.push_back(z * .25f); }
  for (int j = 0; j < N; j++) for (int i = 0; i < N; i++) { uint32_t a = j * (N + 1) + i, b = a + 1, c = a + N + 1, d = c + 1; for (uint32_t k : {a, c, b, b, c, d}) P.idx.push_back(k); }
  Material mt; mt.name = "terrain"; m.materials.push_back(mt); P.material = 0; m.prims.push_back(P); updateBounds(m); return m;
}
Model makePineTreeModel() {
  Model m; m.name = "pine_tree";
  m.textures.push_back(makeNoiseTex({.18f, .11f, .06f}, {.34f, .22f, .12f}, 0.25f, 1));
  m.textures.push_back(makeNoiseTex({.07f, .21f, .05f}, {.18f, .38f, .09f}, 0.30f, 2));
  Material mb; mb.name = "bark"; mb.base = 0; m.materials.push_back(mb);
  Material mf; mf.name = "pine_needles"; mf.base = 1; m.materials.push_back(mf);
  Primitive tr; tr.material = 0; tr.node = "trunk"; const int S = 12;
  for (int j = 0; j <= 6; j++) { float v = j / 6.f, y = v * 3.2f, r = lerpf(0.36f, 0.14f, v);
    for (int i = 0; i <= S; i++) { float a = i * 2 * kPi / S; tr.pos.push_back({std::cos(a) * r, y, std::sin(a) * r}); tr.nrm.push_back({std::cos(a), 0.1f, std::sin(a)}); tr.uv.push_back(float(i) / S); tr.uv.push_back(v); } }
  for (int j = 0; j < 6; j++) for (int i = 0; i < S; i++) { uint32_t a = j * (S + 1) + i, b = a + 1, c = a + S + 1, d = c + 1; for (uint32_t k : {a, c, b, b, c, d}) tr.idx.push_back(k); }
  m.prims.push_back(std::move(tr));
  Primitive lf; lf.material = 1; lf.node = "canopy"; const int CS = 18, CR = 6;
  const float y0s[4] = {1.6f, 3.0f, 4.3f, 5.5f}, hs[4] = {2.3f, 2.1f, 1.9f, 1.8f}, r0s[4] = {2.1f, 1.75f, 1.35f, 0.95f};
  for (int tier = 0; tier < 4; tier++) {
    uint32_t base = (uint32_t)lf.pos.size();
    for (int j = 0; j <= CR; j++) { float v = float(j) / CR, y = y0s[tier] + v * hs[tier];
      for (int i = 0; i <= CS; i++) { float u = float(i) / CS, a = u * 2 * kPi;
        float scall = 1.f + 0.18f * std::sin(a * 7.f + tier * 1.4f) * (1.f - v);
        float r = r0s[tier] * (1.f - 0.92f * v) * scall, droop = -0.18f * (1.f - v) * std::cos(a * 7.f);
        lf.pos.push_back({std::cos(a) * r, y + droop, std::sin(a) * r});
        lf.nrm.push_back(normalize({std::cos(a) * 0.8f, 0.55f, std::sin(a) * 0.8f})); lf.uv.push_back(u); lf.uv.push_back(v); } }
    for (int j = 0; j < CR; j++) for (int i = 0; i < CS; i++) { uint32_t a = base + j * (CS + 1) + i, b = a + 1, c = a + CS + 1, d = c + 1; for (uint32_t k : {a, c, b, b, c, d}) lf.idx.push_back(k); }
  }
  m.prims.push_back(std::move(lf)); updateBounds(m); return m;
}
Model makeMossyBoulderModel() {
  Model m; m.name = "mossy_boulder";
  m.textures.push_back(makeNoiseTex({.30f, .29f, .26f}, {.52f, .50f, .46f}, 0.28f, 5));
  m.textures.push_back(makeNoiseTex({.14f, .34f, .08f}, {.26f, .48f, .13f}, 0.32f, 6));
  Material mr; mr.name = "rock"; mr.base = 0; m.materials.push_back(mr);
  Material mm; mm.name = "moss"; mm.base = 1; m.materials.push_back(mm);
  Primitive pr, pm; pr.material = 0; pm.material = 1; const int R = 12, S = 18;
  auto buildSphere = [&](Primitive& P, float yOff, bool topOnly) {
    for (int j = 0; j <= R; j++) { float v = float(j) / R, th = v * kPi;
      for (int i = 0; i <= S; i++) { float u = float(i) / S, ph = u * 2 * kPi;
        Vec3 d{std::sin(th) * std::cos(ph), std::cos(th), std::sin(th) * std::sin(ph)};
        float n = 1.f + 0.22f * std::sin(ph * 3.f + th * 2.f) + 0.14f * std::cos(ph * 5.f - th * 3.f);
        Vec3 p{d.x * 1.35f * n, std::max(0.f, (d.y * 0.85f + 0.55f) * n) + yOff, d.z * 1.15f * n};
        P.pos.push_back(p); P.nrm.push_back(normalize({d.x, d.y + 0.25f, d.z})); P.uv.push_back(u * 2.f); P.uv.push_back(v * 2.f); } }
    for (int j = 0; j < R; j++) for (int i = 0; i < S; i++) {
      if (topOnly && j > R / 2) continue;
      uint32_t a = j * (S + 1) + i, b = a + 1, c = a + S + 1, d = c + 1; for (uint32_t k : {a, b, c, b, d, c}) P.idx.push_back(k); }
  };
  buildSphere(pr, 0.f, false); buildSphere(pm, 0.03f, true);
  m.prims.push_back(std::move(pr)); m.prims.push_back(std::move(pm)); updateBounds(m); return m;
}
Model makeGrassFieldModel() {
  Model m; m.name = "grass_field";
  m.textures.push_back(makeNoiseTex({.13f, .33f, .06f}, {.28f, .50f, .12f}, 0.35f, 9));
  m.textures.push_back(makeNoiseTex({.85f, .62f, .18f}, {.98f, .82f, .32f}, 0.40f, 10));
  Material mg; mg.name = "grass_blade"; mg.base = 0; m.materials.push_back(mg);
  Material mw; mw.name = "wildflower"; mw.base = 1; m.materials.push_back(mw);
  Primitive pg, pw; pg.material = 0; pw.material = 1;
  for (int idx = 0; idx < 680; idx++) {
    float h1 = std::sin(idx * 127.1f) * 43758.5453f; h1 -= std::floor(h1);
    float h2 = std::sin(idx * 311.7f) * 43758.5453f; h2 -= std::floor(h2);
    float x = (h1 * 2.f - 1.f) * 48.f, z = -55.f + h2 * 82.f;
    float rd = std::fabs(x - roadCenterX(z));
    if (rd < 4.2f || (z > 8.f && z < 24.f && rd < 18.f)) continue;
    bool hitObs = false; for (const Footprint& f : obstacles()) if (std::fabs(x - f.cx) < f.hx + 1.5f && std::fabs(z - f.cz) < f.hz + 1.5f) hitObs = true;
    if (hitObs) continue;
    float gy = terrainHeight(x, z);
    for (int b = 0; b < 4; b++) {
      float ang = idx * 1.7f + b * 1.57f, ca = std::cos(ang), sa = std::sin(ang);
      float bh = 0.42f + 0.28f * ((idx + b) % 5) * 0.2f, bw = 0.065f, lean = 0.16f;
      float bx = x + std::cos(ang * 2.f) * 0.22f, bz = z + std::sin(ang * 2.f) * 0.22f;
      uint32_t v0 = (uint32_t)pg.pos.size();
      Vec3 n = normalize({-sa, 0.45f, ca});
      pg.pos.push_back({bx - ca * bw, gy, bz - sa * bw}); pg.nrm.push_back(n); pg.uv.push_back(0.f); pg.uv.push_back(0.f);
      pg.pos.push_back({bx + ca * bw, gy, bz + sa * bw}); pg.nrm.push_back(n); pg.uv.push_back(1.f); pg.uv.push_back(0.f);
      pg.pos.push_back({bx - ca * bw * 0.5f - sa * lean * 0.4f, gy + bh * 0.55f, bz - sa * bw * 0.5f + ca * lean * 0.4f}); pg.nrm.push_back(n); pg.uv.push_back(0.2f); pg.uv.push_back(0.55f);
      pg.pos.push_back({bx + ca * bw * 0.5f - sa * lean * 0.4f, gy + bh * 0.55f, bz + sa * bw * 0.5f + ca * lean * 0.4f}); pg.nrm.push_back(n); pg.uv.push_back(0.8f); pg.uv.push_back(0.55f);
      pg.pos.push_back({bx - sa * lean, gy + bh, bz + ca * lean}); pg.nrm.push_back({0, 1, 0}); pg.uv.push_back(0.5f); pg.uv.push_back(1.f);
      for (uint32_t k : {0u, 1u, 2u, 1u, 3u, 2u, 2u, 3u, 4u}) pg.idx.push_back(v0 + k);
    }
    if (idx % 5 == 0) {
      uint32_t v0 = (uint32_t)pw.pos.size(); float fy = gy + 0.52f, r = 0.09f;
      pw.pos.push_back({x, fy + 0.04f, z}); pw.nrm.push_back({0, 1, 0}); pw.uv.push_back(0.5f); pw.uv.push_back(1.f);
      for (int p = 0; p < 5; p++) { float a = p * 2 * kPi / 5.f; pw.pos.push_back({x + std::cos(a) * r, fy, z + std::sin(a) * r}); pw.nrm.push_back({0, 1, 0}); pw.uv.push_back(0.8f); pw.uv.push_back(1.f); }
      for (uint32_t p = 0; p < 5; p++) { pw.idx.push_back(v0); pw.idx.push_back(v0 + 1 + p); pw.idx.push_back(v0 + 1 + (p + 1) % 5); }
    }
  }
  m.prims.push_back(std::move(pg)); m.prims.push_back(std::move(pw)); updateBounds(m); return m;
}
}  // namespace isekai
