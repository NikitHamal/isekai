#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <isekai/model.h>
#include "math3d.hpp"
#include "soft_extra.hpp"
#include "terrain.hpp"
namespace isekai {
static Vec3 sample(const Texture& t, float u, float v) {
  if (!t.valid()) return {1, 1, 1};
  u -= std::floor(u); v -= std::floor(v); int x = std::min(t.w - 1, int(u * t.w)), y = std::min(t.h - 1, int(v * t.h)); const uint8_t* p = &t.rgba[(size_t(y) * t.w + x) * 4];
  return {p[0] / 255.f, p[1] / 255.f, p[2] / 255.f};
}
static float aces(float x) { x *= 0.6f; return std::clamp((x * (2.51f * x + 0.03f)) / (x * (2.43f * x + 0.59f) + 0.14f), 0.f, 1.f); }

void clearFrame(Framebuffer& fb, Vec3 top, Vec3 bot) {
  for (int y = 0; y < fb.h; y++) { float t = float(y) / fb.h; Vec3 c = top * (1 - t) + bot * t;
    for (int x = 0; x < fb.w; x++) { uint8_t* p = &fb.rgb[(size_t(y) * fb.w + x) * 3]; p[0] = uint8_t(255 * aces(c.x)); p[1] = uint8_t(255 * aces(c.y)); p[2] = uint8_t(255 * aces(c.z)); } }
  std::fill(fb.depth.begin(), fb.depth.end(), 1e30f);
}

struct SV { float sx, sy, z; Vec3 wp, n, t; float u, v, tw; };

void drawInstance(Framebuffer& fb, const Camera& cam, const Model& m, const Mat4& MM, Vec3 tint, bool ground, const AnimState& anim) {
  Vec3 f = normalize(cam.target - cam.eye), r = normalize(cross(f, {0, 1, 0})), up = cross(r, f);
  float tanH = std::tan(cam.fovDeg * 0.5f * 3.14159265f / 180.f), aspect = float(fb.w) / fb.h; Vec3 L = gEnv.sm ? gEnv.sun : normalize({0.5f, 0.8f, 0.45f});
  for (const Primitive& P : m.prims) {
    Mat4 PM = (anim.rig == RIG_STATIC) ? MM : mMul(MM, partTransform(anim, P.partId, P.pivot));
    const Material* mat = P.material >= 0 ? &m.materials[P.material] : nullptr; auto tex = [&](int i) -> const Texture* { return i >= 0 ? &m.textures[i] : nullptr; };
    const Texture *A = mat ? tex(mat->base) : nullptr, *NM = mat ? tex(mat->normal) : nullptr, *EM = mat ? tex(mat->emissive) : nullptr, *MR = mat ? tex(mat->mr) : nullptr;
    std::vector<SV> V(P.pos.size()); std::vector<char> ok(P.pos.size());
    for (size_t i = 0; i < V.size(); i++) {
      Vec3 w = transformPoint(PM, P.pos[i]), d = w - cam.eye; float cz = dot(d, f); ok[i] = cz > 0.05f; if (!ok[i]) continue;
      V[i] = {(dot(d, r) / (cz * tanH * aspect) * 0.5f + 0.5f) * fb.w, (0.5f - dot(d, up) / (cz * tanH) * 0.5f) * fb.h, cz, w, normalize(transformDir(PM, P.nrm[i])),
              P.tan.empty() ? Vec3{1, 0, 0} : normalize(transformDir(PM, Vec3{P.tan[i*4], P.tan[i*4+1], P.tan[i*4+2]})), P.uv[i*2], P.uv[i*2+1], P.tan.empty() ? 1.f : P.tan[i*4+3]};
    }
    for (size_t k = 0; k + 2 < P.idx.size(); k += 3) {
      uint32_t ia = P.idx[k], ib = P.idx[k+1], ic = P.idx[k+2]; if (!ok[ia] || !ok[ib] || !ok[ic]) continue;
      const SV &a = V[ia], &b = V[ib], &c = V[ic]; float area = (b.sx - a.sx) * (c.sy - a.sy) - (c.sx - a.sx) * (b.sy - a.sy); if (std::fabs(area) < 1e-6f) continue;
      int x0 = std::max(0, int(std::floor(std::min({a.sx, b.sx, c.sx})))), x1 = std::min(fb.w - 1, int(std::ceil(std::max({a.sx, b.sx, c.sx}))));
      int y0 = std::max(0, int(std::floor(std::min({a.sy, b.sy, c.sy})))), y1 = std::min(fb.h - 1, int(std::ceil(std::max({a.sy, b.sy, c.sy}))));
      for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) {
        float px = x + .5f, py = y + .5f;
        float w0 = ((b.sx - px) * (c.sy - py) - (c.sx - px) * (b.sy - py)) / area, w1 = ((c.sx - px) * (a.sy - py) - (a.sx - px) * (c.sy - py)) / area, w2 = 1 - w0 - w1;
        if (w0 < 0 || w1 < 0 || w2 < 0) continue;
        float pa = w0 / a.z, pb = w1 / b.z, pc = w2 / c.z, inv = 1.f / (pa + pb + pc); float z = inv; size_t di = size_t(y) * fb.w + x; if (z >= fb.depth[di]) continue;
        pa *= inv; pb *= inv; pc *= inv; float u = a.u * pa + b.u * pb + c.u * pc, v = a.v * pa + b.v * pb + c.v * pc;
        Vec3 n = normalize(a.n * pa + b.n * pb + c.n * pc); if (!ground && dot(n, (a.wp * pa + b.wp * pb + c.wp * pc) - cam.eye) > 0) n = n * -1.f;  // double-sided
        Vec3 wp0 = a.wp * pa + b.wp * pb + c.wp * pc; Vec3 alb = ground ? terrainAlbedo(wp0.x, wp0.z, wp0.y) : A ? sample(*A, u, v) : (mat ? Vec3{mat->baseFactor[0], mat->baseFactor[1], mat->baseFactor[2]} * .6f : Vec3{.6f, .6f, .6f}); alb = {alb.x * tint.x, alb.y * tint.y, alb.z * tint.z};
        if (NM) { Vec3 t = normalize(a.t * pa + b.t * pb + c.t * pc); Vec3 s = sample(*NM, u, v); Vec3 tn = {s.x * 2 - 1, s.y * 2 - 1, s.z * 2 - 1}; Vec3 bt = cross(n, t) * a.tw; Vec3 nn = normalize(t * tn.x + bt * tn.y + n * tn.z); if (dot(nn, n) > 0.2f) n = nn; }
        float rough = MR ? sample(*MR, u, v).y : 0.7f, metal = MR ? sample(*MR, u, v).z : 0.f; Vec3 wp = a.wp * pa + b.wp * pb + c.wp * pc; Vec3 vd = normalize(cam.eye - wp), hv = normalize(L + vd);
        float sh = gEnv.sm ? softShadow(*gEnv.sm, wp, n, L) : 1.f; float ndl = std::max(0.f, dot(n, L)) * sh, spec = std::pow(std::max(0.f, dot(n, hv)), 2.f / (rough * rough + .02f)) * (0.1f + 0.9f * metal) * (1 - rough * .6f);
        spec *= sh; float ao = ground ? 1.f : (gEnv.sm ? std::clamp(0.55f + 0.45f * sstep(0.f, 2.2f, wp.y - terrainHeight(wp.x, wp.z)), 0.f, 1.f) : 1.f); float amb = (0.26f + 0.14f * n.y) * ao; Vec3 lit = {alb.x * (1 - metal * .8f) * (amb * .8f + ndl * 1.25f) + spec * (0.9f + metal * (alb.x - .9f)), alb.y * (1 - metal * .8f) * (amb + ndl * 1.1f) + spec * (0.85f + metal * (alb.y - .85f)), alb.z * (1 - metal * .8f) * (amb * 1.2f + ndl * .85f) + spec * (0.75f + metal * (alb.z - .75f))};
        if (!ground) {
          float rim = std::pow(1.f - std::max(0.f, dot(n, vd)), 3.0f), sb = std::clamp(dot(n, L) * 0.5f + 0.5f, 0.f, 1.f);
          lit = lit + Vec3{1.15f, 0.72f, 0.35f} * (rim * sb * (0.35f + 0.65f * sh) * ao * 0.55f);
        }
        if (gEnv.lights) lit = lit + softPointLights(wp, n, alb);
        if (EM && mat) { Vec3 e = sample(*EM, u, v); lit = lit + Vec3{e.x * mat->emissiveFactor[0] * tint.x, e.y * mat->emissiveFactor[1] * tint.y, e.z * mat->emissiveFactor[2] * tint.z} * 1.4f; }
        float fog = 1.f - std::exp(-z * gEnv.fogDen); lit = lit * (1 - fog) + gEnv.fogCol * fog;
        fb.depth[di] = z; uint8_t* o = &fb.rgb[di * 3]; o[0] = uint8_t(255 * aces(lit.x)); o[1] = uint8_t(255 * aces(lit.y)); o[2] = uint8_t(255 * aces(lit.z));
      }
    }
  }
}
void drawModel(Framebuffer& fb, const Camera& cam, const Model& m, Vec3 off, float scale) {
  Mat4 M = mIdent(); M[0] = M[5] = M[10] = scale; M[12] = off.x; M[13] = off.y; M[14] = off.z; drawInstance(fb, cam, m, M, {1, 1, 1}, false); }
bool writePng(const std::string& path, const Framebuffer& fb) { return stbi_write_png(path.c_str(), fb.w, fb.h, 3, fb.rgb.data(), fb.w * 3) != 0; }
}  // namespace isekai
