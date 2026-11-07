// HUD + glow FX batching for the GL renderer. The HUD is deliberately minimal: a slim HP bar and Mana bar (top-left) and a casting dot.
#ifdef _WIN32
#include "gl_renderer.hpp"
#include <cmath>
#include <cstdio>
#include "math3d.hpp"
#include "stb_easy_font.h"
namespace isekai {
void GLRenderer::quad(float x0, float y0, float x1, float y1, const float* c) {
  HV a{x0, y0, 2, 2, c[0], c[1], c[2], c[3]}, b = a, d = a, e = a; b.x = x1; d.x = x1; d.y = y1; e.y = y1; hv.insert(hv.end(), {a, b, d, a, d, e}); }
void GLRenderer::glow(float x, float y, float r, const float* c) {
  auto v = [&](float dx, float dy) { return HV{x + dx * r, y + dy * r, dx, dy, c[0], c[1], c[2], c[3]}; };
  hv.insert(hv.end(), {v(-1, -1), v(1, -1), v(1, 1), v(-1, -1), v(1, 1), v(-1, 1)}); }
void GLRenderer::fan(float cx, float cy, const std::vector<float>& p, const float* c) {
  HV o{cx, cy, 2, 2, c[0], c[1], c[2], c[3]}; for (size_t i = 0; i + 3 < p.size(); i += 2) { HV a = o, b = o; a.x = p[i]; a.y = p[i+1]; b.x = p[i+2]; b.y = p[i+3]; hv.insert(hv.end(), {o, a, b}); } }
void GLRenderer::disc(float cx, float cy, float r, const float* c, int seg) {
  std::vector<float> p; for (int i = 0; i <= seg; i++) { float t = i * 2 * kPi / seg; p.push_back(cx + std::cos(t) * r); p.push_back(cy + std::sin(t) * r); } fan(cx, cy, p, c); }
void GLRenderer::ring(float cx, float cy, float r, float t, const float* c) {
  for (int i = 0; i < 48; i++) { float a0 = i * 2 * kPi / 48, a1 = (i + 1) * 2 * kPi / 48; HV p[4]; float rr[4] = {r - t, r, r - t, r}, aa[4] = {a0, a0, a1, a1};
    for (int k = 0; k < 4; k++) p[k] = HV{cx + std::cos(aa[k]) * rr[k], cy + std::sin(aa[k]) * rr[k], 2, 2, c[0], c[1], c[2], c[3]}; hv.insert(hv.end(), {p[0], p[1], p[3], p[0], p[3], p[2]}); } }
void GLRenderer::text(float x, float y, const std::string& s, float sc, const float* c) {
  static char buf[60000]; unsigned char col[4] = {255, 255, 255, 255}; int nq = stb_easy_font_print(0, 0, (char*)s.c_str(), col, buf, sizeof(buf));
  for (int q = 0; q < nq; q++) { float* v[4]; for (int k = 0; k < 4; k++) v[k] = (float*)(buf + (q * 4 + k) * 16); HV h[4];
    for (int k = 0; k < 4; k++) h[k] = HV{x + v[k][0] * sc, y + v[k][1] * sc, 2, 2, c[0], c[1], c[2], c[3]}; hv.insert(hv.end(), {h[0], h[1], h[2], h[0], h[2], h[3]}); } }
void GLRenderer::flush(int w, int h, bool additive) {
  (void)additive; if (hv.empty()) return; glUseProgram(hud); glUniform2f(U(hud, "uRes"), (float)w, (float)h); glBindVertexArray(hudVao); glBindBuffer(GL_ARRAY_BUFFER, hudVbo);
  glBufferData(GL_ARRAY_BUFFER, hv.size() * sizeof(HV), hv.data(), GL_DYNAMIC_DRAW); glDrawArrays(GL_TRIANGLES, 0, (GLsizei)hv.size()); glBindVertexArray(0); hv.clear(); }
bool GLRenderer::project(const Mat4& m, Vec3 p, int w, int h, float& sx, float& sy, float& depth) {
  float cx = m[0]*p.x + m[4]*p.y + m[8]*p.z + m[12], cy = m[1]*p.x + m[5]*p.y + m[9]*p.z + m[13], cw = m[3]*p.x + m[7]*p.y + m[11]*p.z + m[15]; if (cw < 0.1f) return false;
  sx = (cx / cw * .5f + .5f) * w; sy = (.5f - cy / cw * .5f) * h; depth = cw; return true; }
void GLRenderer::drawHud(const Scene& s, int w, int h) {
  float ui = std::max(0.75f, h / 900.f), x0 = 34 * ui, y0 = 30 * ui, bw = 300 * ui, bh = 10 * ui;
  const float frame[4] = {.62f, .56f, .45f, .95f}, frameDk[4] = {.2f, .17f, .13f, .95f}, back[4] = {.04f, .02f, .03f, .82f}, hi[4] = {1, 1, 1, .22f};
  auto bar = [&](float y, float v, const float* c0, const float* c1) {
    quad(x0 - 3 * ui, y - 3 * ui, x0 + bw + 3 * ui, y + bh + 3 * ui, frameDk); quad(x0 - 2 * ui, y - 2 * ui, x0 + bw + 2 * ui, y + bh + 2 * ui, frame); quad(x0, y, x0 + bw, y + bh, back);
    v = std::max(0.f, std::min(1.f, v)); const int seg = 24; for (int i = 0; i < seg; i++) { float a = float(i) / seg, b = float(i + 1) / seg; if (a >= v) break; float t = a; float c[4] = {c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t, c0[2] + (c1[2] - c0[2]) * t, 1};
      quad(x0 + bw * a, y, x0 + bw * std::min(b, v), y + bh, c); }
    quad(x0, y, x0 + bw * v, y + 2 * ui, hi); };
  const float r0[4] = {.4f, .02f, .06f, 1}, r1[4] = {.92f, .12f, .16f, 1}, b0[4] = {.05f, .2f, .55f, 1}, b1[4] = {.3f, .7f, 1.f, 1};
  bar(y0, s.hp, r0, r1); bar(y0 + bh + 10 * ui, s.mana, b0, b1);
  const float sc[3][4] = {{1.f, .38f, .12f, .95f}, {.25f, .88f, 1.f, .95f}, {.86f, .45f, 1.f, .95f}};
  int sp = std::max(0, std::min(2, s.activeSpell));
  float sx = x0 + bw + 14 * ui, sy = y0 + bh + 10 * ui + bh * 0.5f;
  disc(sx, sy, 6.5f * ui, frameDk, 16); disc(sx, sy, 5.0f * ui, sc[sp], 16);
  if (s.casting) { const float dot[4] = {1.f, .85f, .6f, .9f}; disc(w * .5f, h * .5f, 2.5f * ui, dot, 12); } }
}  // namespace isekai
#endif
