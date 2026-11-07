// HUD + glow FX batching for the GL renderer: hearts, FPS/GPU text, minimap, controls strip.
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
void GLRenderer::heart(float cx, float cy, float s, const float* c) {
  std::vector<float> pts; for (int i = 0; i <= 40; i++) { float t = i / 40.f * 2 * kPi; float x = 16 * std::pow(std::sin(t), 3), y = 13 * std::cos(t) - 5 * std::cos(2 * t) - 2 * std::cos(3 * t) - std::cos(4 * t);
    pts.push_back(cx + x * s / 34.f); pts.push_back(cy - y * s / 34.f); } fan(cx, cy, pts, c); }
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
void GLRenderer::drawHud(const Scene& s, int w, int h, float fps) {
  const float red[4] = {.86f, .1f, .16f, 1}, dark[4] = {.12f, .02f, .04f, .85f}, gold[4] = {1, .8f, .3f, 1}, white[4] = {1, 1, 1, .95f}, soft[4] = {1, 1, 1, .6f}, shadow[4] = {0, 0, 0, .7f}; float ui = std::max(0.75f, h / 900.f);
  for (int i = 0; i < s.maxHearts; i++) { float cx = (34 + i * 38) * ui, cy = 40 * ui; heart(cx, cy + 2, 32 * ui, shadow); heart(cx, cy, 30 * ui, i < s.hearts ? red : dark);
    if (i < s.hearts) { const float hl[4] = {1, .7f, .7f, .8f}; disc(cx - 6 * ui, cy - 6 * ui, 3.5f * ui, hl, 12); } }
  char b[160]; std::snprintf(b, sizeof b, "FPS %d", (int)(fps + .5f)); text(18 * ui + 1, 78 * ui + 1, b, 2.f * ui, shadow); text(18 * ui, 78 * ui, b, 2.f * ui, gold);
  std::snprintf(b, sizeof b, "%s | OpenGL %s", gpuName.c_str(), glVersion.c_str()); text(18 * ui, 100 * ui, b, 1.3f * ui, soft);
  std::snprintf(b, sizeof b, "Goblins slain: %d", s.kills); text(18 * ui, 118 * ui, b, 1.3f * ui, soft);
  float R = 95 * ui, mx = w - R - 24 * ui, my = h - R - 24 * ui; const float bg[4] = {.04f, .09f, .05f, .72f}, rim[4] = {.95f, .75f, .3f, .95f}; disc(mx, my, R, bg); ring(mx, my, R, 3 * ui, rim);
  Vec3 hero{0, 0, 0}; for (auto& d : s.dots) if (d.kind == 0) hero = {d.x, 0, d.z}; float fx = std::sin(s.camYaw), fz = std::cos(s.camYaw), scale = R / 28.f;
  for (auto& d : s.dots) { float dx = d.x - hero.x, dz = d.z - hero.z, right = dx * -fz + dz * fx, fwd = dx * fx + dz * fz, px = mx + right * scale, py = my - fwd * scale;
    if (std::hypot(px - mx, py - my) > R - 5 * ui) continue; static const float cols[6][4] = {{.3f, 1, .5f, 1}, {.4f, .7f, 1, 1}, {1, .2f, .3f, 1}, {1, .45f, .1f, 1}, {1, .85f, .3f, 1}, {.8f, .7f, .5f, 1}};
    float r = (d.kind == 1 ? 6.f : d.kind == 0 ? 5.f : 4.f) * ui; if (d.kind == 2) heart(px, py, 11 * ui, cols[2]); else if (d.kind == 1) quad(px - 8 * ui, py - 4 * ui, px + 8 * ui, py + 4 * ui, cols[1]); else disc(px, py, r, cols[d.kind], 14); }
  if (!s.hint.empty()) { float tw = s.hint.size() * 8.f * 1.6f * ui; text(w * .5f - tw * .5f + 1, h * .78f + 1, s.hint, 1.6f * ui, shadow); text(w * .5f - tw * .5f, h * .78f, s.hint, 1.6f * ui, white); }
  const std::string ctl = "WASD: Move | Mouse/Arrows: Camera | Space: Jump/Roll | LMB/F: Sword Slash | E: Interact | F11: Fullscreen | Esc: Free Mouse"; float cw = ctl.size() * 6.2f * ui;
  quad(w * .5f - cw * .5f - 14 * ui, h - 34 * ui, w * .5f + cw * .5f + 14 * ui, h - 8 * ui, dark); text(w * .5f - cw * .5f, h - 28 * ui, ctl, 1.0f * ui, soft); }
}  // namespace isekai
#endif
