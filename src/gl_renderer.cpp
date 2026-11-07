#ifdef _WIN32
#include "gl_renderer.hpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include "gl_shaders.hpp"
#include "math3d.hpp"
namespace isekai {
static GLuint compile(GLenum type, const char* src, std::string& err) {
  GLuint s = glCreateShader(type); glShaderSource(s, 1, &src, nullptr); glCompileShader(s); GLint ok = 0; glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
  if (!ok) { char log[1024]; glGetShaderInfoLog(s, 1024, nullptr, log); err += log; return 0; } return s; }
static GLuint link(const char* vs, const char* fs, std::string& err) {
  GLuint v = compile(GL_VERTEX_SHADER, vs, err), f = compile(GL_FRAGMENT_SHADER, fs, err); if (!v || !f) return 0;
  GLuint p = glCreateProgram(); glAttachShader(p, v); glAttachShader(p, f); glLinkProgram(p); glDeleteShader(v); glDeleteShader(f); GLint ok = 0; glGetProgramiv(p, GL_LINK_STATUS, &ok);
  if (!ok) { char log[1024]; glGetProgramInfoLog(p, 1024, nullptr, log); err += log; return 0; } return p; }
bool GLRenderer::init(std::string& err) {
  pbr = link(kPbrVS, kPbrFS, err); sky = link(kSkyVS, kSkyFS, err); hud = link(kHudVS, kHudFS, err); shadowProg = link(kShadowVS, kShadowFS, err);
  bloomProg = link(kSkyVS, kBloomFS, err); postProg = link(kSkyVS, kPostFS, err);
  if (!pbr || !sky || !hud || !shadowProg || !bloomProg || !postProg) return false;
  glGenTextures(1, &shadowTex); glBindTexture(GL_TEXTURE_2D, shadowTex); glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, kShadowRes, kShadowRes, 0, GL_DEPTH_COMPONENT, GL_FLOAT, nullptr);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
  { const GLfloat border[4] = {1, 1, 1, 1}; glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border); }
  glGenFramebuffers(1, &shadowFbo); glBindFramebuffer(GL_FRAMEBUFFER, shadowFbo); glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, shadowTex, 0); glDrawBuffer(GL_NONE); glReadBuffer(GL_NONE);
  bool fboOk = glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE; glBindFramebuffer(GL_FRAMEBUFFER, 0); if (!fboOk) { err += "shadow framebuffer incomplete"; return false; }
  glGenFramebuffers(1, &sceneFbo); glGenTextures(1, &sceneColorTex); glGenTextures(1, &sceneDepthTex);
  glGenFramebuffers(2, bloomFbo); glGenTextures(2, bloomTex);
  glGenVertexArrays(1, &skyVao); glGenVertexArrays(1, &hudVao); glGenBuffers(1, &hudVbo); glBindVertexArray(hudVao); glBindBuffer(GL_ARRAY_BUFFER, hudVbo);
  glEnableVertexAttribArray(0); glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 32, (void*)0); glEnableVertexAttribArray(1); glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, (void*)8);
  glEnableVertexAttribArray(2); glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 32, (void*)16); glBindVertexArray(0); return true; }
void GLRenderer::ensureFbos(int w, int h) {
  if (w == fboW && h == fboH) return;
  fboW = w; fboH = h;
  auto cfgTex = [&](GLuint t, int tw, int th, GLint ifmt, GLenum fmt, GLenum type, GLint filt) {
    glBindTexture(GL_TEXTURE_2D, t); glTexImage2D(GL_TEXTURE_2D, 0, ifmt, tw, th, 0, fmt, type, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filt); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filt);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
  };
  cfgTex(sceneColorTex, w, h, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT, GL_LINEAR);
  cfgTex(sceneDepthTex, w, h, GL_DEPTH_COMPONENT24, GL_DEPTH_COMPONENT, GL_FLOAT, GL_NEAREST);
  glBindFramebuffer(GL_FRAMEBUFFER, sceneFbo);
  glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, sceneColorTex, 0);
  glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, sceneDepthTex, 0);
  int bw = std::max(1, w / 2), bh = std::max(1, h / 2);
  for (int i = 0; i < 2; i++) {
    cfgTex(bloomTex[i], bw, bh, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT, GL_LINEAR);
    glBindFramebuffer(GL_FRAMEBUFFER, bloomFbo[i]);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, bloomTex[i], 0);
  }
  glBindFramebuffer(GL_FRAMEBUFFER, 0);
}
GLint GLRenderer::U(GLuint prog, const char* n) { std::string k = std::to_string(prog) + n; auto it = uloc.find(k); if (it != uloc.end()) return it->second; return uloc[k] = glGetUniformLocation(prog, n); }
GLRenderer::GPUModel& GLRenderer::upload(const Model* m) {
  auto it = models.find(m); if (it != models.end()) return it->second; GPUModel g;
  for (const Texture& t : m->textures) { GLuint id = 0; glGenTextures(1, &id); glBindTexture(GL_TEXTURE_2D, id);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, t.w, t.h, 0, GL_RGBA, GL_UNSIGNED_BYTE, t.rgba.data()); glGenerateMipmap(GL_TEXTURE_2D);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT); g.tex.push_back(id); }
  for (const Primitive& P : m->prims) { GPUPrim gp; gp.mat = P.material; gp.partId = P.partId; gp.pivot = P.pivot; gp.count = (GLsizei)P.idx.size(); std::vector<float> vb; vb.reserve(P.pos.size() * 12);
    for (size_t i = 0; i < P.pos.size(); i++) { vb.insert(vb.end(), {P.pos[i].x, P.pos[i].y, P.pos[i].z, P.nrm[i].x, P.nrm[i].y, P.nrm[i].z});
      if (P.uv.size() > i * 2 + 1) vb.insert(vb.end(), {P.uv[i*2], P.uv[i*2+1]}); else vb.insert(vb.end(), {0.f, 0.f});
      if (P.tan.size() > i * 4 + 3) vb.insert(vb.end(), {P.tan[i*4], P.tan[i*4+1], P.tan[i*4+2], P.tan[i*4+3]}); else vb.insert(vb.end(), {1.f, 0.f, 0.f, 1.f}); }
    glGenVertexArrays(1, &gp.vao); glGenBuffers(1, &gp.vbo); glGenBuffers(1, &gp.ebo); glBindVertexArray(gp.vao);
    glBindBuffer(GL_ARRAY_BUFFER, gp.vbo); glBufferData(GL_ARRAY_BUFFER, vb.size() * 4, vb.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gp.ebo); glBufferData(GL_ELEMENT_ARRAY_BUFFER, P.idx.size() * 4, P.idx.data(), GL_STATIC_DRAW);
    const int off[4] = {0, 12, 24, 32}, n[4] = {3, 3, 2, 4}; for (int a = 0; a < 4; a++) { glEnableVertexAttribArray(a); glVertexAttribPointer(a, n[a], GL_FLOAT, GL_FALSE, 48, (void*)(size_t)off[a]); }
    g.prims.push_back(gp); }
  glBindVertexArray(0); return models[m] = std::move(g); }
void GLRenderer::drawModel(const Instance& in, const Model& m, GPUModel& g, bool blendPass) {
  glUniform3f(U(pbr, "uTint"), in.tint.x, in.tint.y, in.tint.z); glUniform1f(U(pbr, "uEmBoost"), in.emissive);
  glUniform1i(U(pbr, "uGround"), in.ground ? 1 : 0); glUniform1i(U(pbr, "uWind"), in.windSway ? 1 : 0); glUniform1f(U(pbr, "uBaseY"), in.M[13]);
  for (const GPUPrim& p : g.prims) { if (blendPass != (p.mat >= 0 && m.materials[p.mat].blend)) continue;
    Mat4 PM = (in.anim.rig == RIG_STATIC) ? in.M : mMul(in.M, partTransform(in.anim, p.partId, p.pivot));
    glUniformMatrix4fv(U(pbr, "uM"), 1, GL_FALSE, PM.data());
    float has[4] = {0, 0, 0, 0}, base[4] = {.6f, .6f, .6f, 1}, ef[3] = {0, 0, 0}; GLuint ids[4] = {0, 0, 0, 0};
    if (p.mat >= 0) { const Material& mt = m.materials[p.mat]; int ti[4] = {mt.base, mt.normal, mt.mr, mt.emissive};
      for (int k = 0; k < 4; k++) if (ti[k] >= 0 && ti[k] < (int)g.tex.size()) { has[k] = 1; ids[k] = g.tex[ti[k]]; }
      for (int k = 0; k < 4; k++) base[k] = mt.baseFactor[k]; for (int k = 0; k < 3; k++) ef[k] = mt.emissiveFactor[k]; }
    for (int k = 0; k < 4; k++) { glActiveTexture(GL_TEXTURE0 + k); glBindTexture(GL_TEXTURE_2D, ids[k]); }
    glUniform4f(U(pbr, "uHas"), has[0], has[1], has[2], has[3]); glUniform4f(U(pbr, "uBase"), base[0], base[1], base[2], base[3]); glUniform3f(U(pbr, "uEmF"), ef[0], ef[1], ef[2]);
    glBindVertexArray(p.vao); glDrawElements(GL_TRIANGLES, p.count, GL_UNSIGNED_INT, nullptr); } }
void GLRenderer::drawShadowCaster(const Instance& in, const Model& m, GPUModel& g) {
  for (const GPUPrim& p : g.prims) { if (p.mat >= 0 && m.materials[p.mat].blend) continue;
    Mat4 PM = (in.anim.rig == RIG_STATIC) ? in.M : mMul(in.M, partTransform(in.anim, p.partId, p.pivot));
    glUniformMatrix4fv(U(shadowProg, "uM"), 1, GL_FALSE, PM.data()); glBindVertexArray(p.vao); glDrawElements(GL_TRIANGLES, p.count, GL_UNSIGNED_INT, nullptr); } }
void GLRenderer::shadowPass(const Scene& s, const Mat4& lvp) {
  glBindFramebuffer(GL_FRAMEBUFFER, shadowFbo); glViewport(0, 0, kShadowRes, kShadowRes); glEnable(GL_DEPTH_TEST); glDepthMask(GL_TRUE); glClear(GL_DEPTH_BUFFER_BIT);
  glDisable(GL_CULL_FACE); glEnable(GL_POLYGON_OFFSET_FILL); glPolygonOffset(2.f, 4.f); glUseProgram(shadowProg); glUniformMatrix4fv(U(shadowProg, "uLVP"), 1, GL_FALSE, lvp.data());
  for (const Instance& in : s.inst) if (in.model && in.castShadow) drawShadowCaster(in, *in.model, upload(in.model));
  glDisable(GL_POLYGON_OFFSET_FILL); glBindVertexArray(0); glBindFramebuffer(GL_FRAMEBUFFER, 0); }
void GLRenderer::draw(const Scene& s, int w, int h) {
  if (w < 2 || h < 2) return;
  ensureFbos(w, h);
  Vec3 sun = normalize(s.sunDir); const float ext = 48.f;
  Mat4 lvp = mMul(mOrtho(-ext, ext, -ext, ext, 1.f, 260.f), mLookAt(s.focus + sun * 120.f, s.focus)); shadowPass(s, lvp);
  glBindFramebuffer(GL_FRAMEBUFFER, sceneFbo);
  glViewport(0, 0, w, h); glClearColor(.05f, .08f, .05f, 1); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  float aspect = float(w) / h; Mat4 P = mPersp(s.cam.fovDeg, aspect, 0.1f, 500.f), V = mLookAt(s.cam.eye, s.cam.target), VP = mMul(P, V);
  Vec3 f = normalize(s.cam.target - s.cam.eye), r = normalize(cross(f, {0, 1, 0})), u = cross(r, f); float tanH = std::tan(s.cam.fovDeg * .5f * kPi / 180.f);
  glDisable(GL_DEPTH_TEST); glDisable(GL_BLEND); glDisable(GL_CULL_FACE); glUseProgram(sky);
  glUniform3f(U(sky, "uF"), f.x, f.y, f.z); glUniform3f(U(sky, "uR"), r.x, r.y, r.z); glUniform3f(U(sky, "uU"), u.x, u.y, u.z); glUniform2f(U(sky, "uTan"), tanH * aspect, tanH); glUniform3f(U(sky, "uSun"), sun.x, sun.y, sun.z);
  glUniform3f(U(sky, "uHoriz"), s.skyHorizon.x, s.skyHorizon.y, s.skyHorizon.z); glUniform3f(U(sky, "uZenith"), s.skyTop.x, s.skyTop.y, s.skyTop.z);
  glBindVertexArray(skyVao); glDrawArrays(GL_TRIANGLES, 0, 3); glEnable(GL_DEPTH_TEST); glDepthFunc(GL_LEQUAL);
  glUseProgram(pbr); glUniformMatrix4fv(U(pbr, "uVP"), 1, GL_FALSE, VP.data()); glUniformMatrix4fv(U(pbr, "uLVP"), 1, GL_FALSE, lvp.data()); glUniform3f(U(pbr, "uSun"), sun.x, sun.y, sun.z);
  glUniform3f(U(pbr, "uCam"), s.cam.eye.x, s.cam.eye.y, s.cam.eye.z); glUniform1f(U(pbr, "uTime"), s.time);
  glUniform3f(U(pbr, "uHoriz"), s.skyHorizon.x, s.skyHorizon.y, s.skyHorizon.z); glUniform3f(U(pbr, "uZenith"), s.skyTop.x, s.skyTop.y, s.skyTop.z);
  float lp[24] = {}, lc[24] = {}, lr[8] = {}; int nl = (int)std::min<size_t>(8, s.lights.size());
  for (int i = 0; i < nl; i++) { const Light& L = s.lights[i]; lp[i*3] = L.pos.x; lp[i*3+1] = L.pos.y; lp[i*3+2] = L.pos.z; lc[i*3] = L.color.x; lc[i*3+1] = L.color.y; lc[i*3+2] = L.color.z; lr[i] = L.radius; }
  glUniform3fv(U(pbr, "uLP"), 8, lp); glUniform3fv(U(pbr, "uLC"), 8, lc); glUniform1i(U(pbr, "uNL"), nl); for (int i = 0; i < 8; i++) glUniform1f(U(pbr, ("uLR[" + std::to_string(i) + "]").c_str()), lr[i]);
  glUniform1i(U(pbr, "uAlb"), 0); glUniform1i(U(pbr, "uNrm"), 1); glUniform1i(U(pbr, "uMR"), 2); glUniform1i(U(pbr, "uEm"), 3); glUniform1i(U(pbr, "uShadow"), 4);
  glActiveTexture(GL_TEXTURE0 + 4); glBindTexture(GL_TEXTURE_2D, shadowTex);
  for (const Instance& in : s.inst) if (in.model) drawModel(in, *in.model, upload(in.model), false);
  glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE);
  for (const Instance& in : s.inst) if (in.model) drawModel(in, *in.model, upload(in.model), true);
  glDepthMask(GL_TRUE); glDisable(GL_BLEND); glDisable(GL_DEPTH_TEST);
  // Dual-pass Gaussian bloom on bright HDR pixels (> 1.1)
  int bw = std::max(1, w / 2), bh = std::max(1, h / 2);
  glUseProgram(bloomProg); glUniform1i(U(bloomProg, "uTex"), 0); glActiveTexture(GL_TEXTURE0); glBindVertexArray(skyVao);
  glBindFramebuffer(GL_FRAMEBUFFER, bloomFbo[0]); glViewport(0, 0, bw, bh);
  glBindTexture(GL_TEXTURE_2D, sceneColorTex); glUniform2f(U(bloomProg, "uDir"), 1.5f / bw, 0.f); glUniform1i(U(bloomProg, "uExtract"), 1);
  glDrawArrays(GL_TRIANGLES, 0, 3);
  glBindFramebuffer(GL_FRAMEBUFFER, bloomFbo[1]);
  glBindTexture(GL_TEXTURE_2D, bloomTex[0]); glUniform2f(U(bloomProg, "uDir"), 0.f, 1.5f / bh); glUniform1i(U(bloomProg, "uExtract"), 0);
  glDrawArrays(GL_TRIANGLES, 0, 3);
  // Composite SSAO + Dual-Pass Bloom + ACES to default framebuffer
  glBindFramebuffer(GL_FRAMEBUFFER, 0); glViewport(0, 0, w, h);
  glUseProgram(postProg);
  glUniform1i(U(postProg, "uScene"), 0); glUniform1i(U(postProg, "uDepth"), 1); glUniform1i(U(postProg, "uBloom"), 2);
  glUniform2f(U(postProg, "uInvRes"), 1.f / w, 1.f / h);
  glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_2D, sceneColorTex);
  glActiveTexture(GL_TEXTURE0 + 1); glBindTexture(GL_TEXTURE_2D, sceneDepthTex);
  glActiveTexture(GL_TEXTURE0 + 2); glBindTexture(GL_TEXTURE_2D, bloomTex[1]);
  glDrawArrays(GL_TRIANGLES, 0, 3);
  glEnable(GL_BLEND); glBindVertexArray(0);
  for (const RibbonSeg& rb : s.ribbons) {
    float x0, y0, d0, x1, y1, d1, x2, y2, d2, x3, y3, d3;
    if (project(VP, rb.a0, w, h, x0, y0, d0) && project(VP, rb.b0, w, h, x1, y1, d1) &&
        project(VP, rb.a1, w, h, x2, y2, d2) && project(VP, rb.b1, w, h, x3, y3, d3)) {
      HV v0{x0, y0, 2, 2, rb.color.x, rb.color.y, rb.color.z, rb.alpha0};
      HV v1{x1, y1, 2, 2, rb.color.x, rb.color.y, rb.color.z, rb.alpha0};
      HV v2{x2, y2, 2, 2, rb.color.x, rb.color.y, rb.color.z, rb.alpha1};
      HV v3{x3, y3, 2, 2, rb.color.x, rb.color.y, rb.color.z, rb.alpha1};
      hv.insert(hv.end(), {v0, v1, v3, v0, v3, v2});
    }
  }
  for (const Fx& fx : s.fx) { float sx, sy, d; if (project(VP, fx.pos, w, h, sx, sy, d)) { float c[4] = {fx.color.x, fx.color.y, fx.color.z, fx.alpha}; glow(sx, sy, fx.size * h * 0.9f / std::max(d, .5f), c); } }
  glBlendFunc(GL_SRC_ALPHA, GL_ONE); flush(w, h, true); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); drawHud(s, w, h); flush(w, h, false); glDisable(GL_BLEND); }
}  // namespace isekai
#endif
