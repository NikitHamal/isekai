#ifdef _WIN32
#include "gl_renderer.hpp"
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
  const char* r = (const char*)glGetString(GL_RENDERER); const char* v = (const char*)glGetString(GL_VERSION); gpuName = r ? r : "unknown GPU"; glVersion = v ? v : "?";
  pbr = link(kPbrVS, kPbrFS, err); sky = link(kSkyVS, kSkyFS, err); hud = link(kHudVS, kHudFS, err); if (!pbr || !sky || !hud) return false;
  glGenVertexArrays(1, &skyVao); glGenVertexArrays(1, &hudVao); glGenBuffers(1, &hudVbo); glBindVertexArray(hudVao); glBindBuffer(GL_ARRAY_BUFFER, hudVbo);
  glEnableVertexAttribArray(0); glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 32, (void*)0); glEnableVertexAttribArray(1); glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, (void*)8);
  glEnableVertexAttribArray(2); glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 32, (void*)16); glBindVertexArray(0); return true; }
GLint GLRenderer::U(GLuint prog, const char* n) { std::string k = std::to_string(prog) + n; auto it = uloc.find(k); if (it != uloc.end()) return it->second; return uloc[k] = glGetUniformLocation(prog, n); }
GLRenderer::GPUModel& GLRenderer::upload(const Model* m) {
  auto it = models.find(m); if (it != models.end()) return it->second; GPUModel g;
  for (const Texture& t : m->textures) { GLuint id = 0; glGenTextures(1, &id); glBindTexture(GL_TEXTURE_2D, id);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, t.w, t.h, 0, GL_RGBA, GL_UNSIGNED_BYTE, t.rgba.data()); glGenerateMipmap(GL_TEXTURE_2D);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT); g.tex.push_back(id); }
  for (const Primitive& P : m->prims) { GPUPrim gp; gp.mat = P.material; gp.count = (GLsizei)P.idx.size(); std::vector<float> vb; vb.reserve(P.pos.size() * 12);
    for (size_t i = 0; i < P.pos.size(); i++) { vb.insert(vb.end(), {P.pos[i].x, P.pos[i].y, P.pos[i].z, P.nrm[i].x, P.nrm[i].y, P.nrm[i].z});
      if (P.uv.size() > i * 2 + 1) vb.insert(vb.end(), {P.uv[i*2], P.uv[i*2+1]}); else vb.insert(vb.end(), {0.f, 0.f});
      if (P.tan.size() > i * 4 + 3) vb.insert(vb.end(), {P.tan[i*4], P.tan[i*4+1], P.tan[i*4+2], P.tan[i*4+3]}); else vb.insert(vb.end(), {1.f, 0.f, 0.f, 1.f}); }
    glGenVertexArrays(1, &gp.vao); glGenBuffers(1, &gp.vbo); glGenBuffers(1, &gp.ebo); glBindVertexArray(gp.vao);
    glBindBuffer(GL_ARRAY_BUFFER, gp.vbo); glBufferData(GL_ARRAY_BUFFER, vb.size() * 4, vb.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gp.ebo); glBufferData(GL_ELEMENT_ARRAY_BUFFER, P.idx.size() * 4, P.idx.data(), GL_STATIC_DRAW);
    const int off[4] = {0, 12, 24, 32}, n[4] = {3, 3, 2, 4}; for (int a = 0; a < 4; a++) { glEnableVertexAttribArray(a); glVertexAttribPointer(a, n[a], GL_FLOAT, GL_FALSE, 48, (void*)(size_t)off[a]); }
    g.prims.push_back(gp); }
  glBindVertexArray(0); return models[m] = std::move(g); }
void GLRenderer::drawModel(const Instance& in, const Model& m, GPUModel& g) {
  glUniformMatrix4fv(U(pbr, "uM"), 1, GL_FALSE, in.M.data()); glUniform3f(U(pbr, "uTint"), in.tint.x, in.tint.y, in.tint.z); glUniform1f(U(pbr, "uEmBoost"), in.emissive);
  glUniform1i(U(pbr, "uGround"), in.ground ? 1 : 0);
  for (const GPUPrim& p : g.prims) { float has[4] = {0, 0, 0, 0}, base[4] = {.6f, .6f, .6f, 1}, ef[3] = {0, 0, 0}; GLuint ids[4] = {0, 0, 0, 0};
    if (p.mat >= 0) { const Material& mt = m.materials[p.mat]; int ti[4] = {mt.base, mt.normal, mt.mr, mt.emissive};
      for (int k = 0; k < 4; k++) if (ti[k] >= 0 && ti[k] < (int)g.tex.size()) { has[k] = 1; ids[k] = g.tex[ti[k]]; }
      for (int k = 0; k < 4; k++) base[k] = mt.baseFactor[k]; for (int k = 0; k < 3; k++) ef[k] = mt.emissiveFactor[k]; }
    for (int k = 0; k < 4; k++) { glActiveTexture(GL_TEXTURE0 + k); glBindTexture(GL_TEXTURE_2D, ids[k]); }
    glUniform4f(U(pbr, "uHas"), has[0], has[1], has[2], has[3]); glUniform4f(U(pbr, "uBase"), base[0], base[1], base[2], base[3]); glUniform3f(U(pbr, "uEmF"), ef[0], ef[1], ef[2]);
    glBindVertexArray(p.vao); glDrawElements(GL_TRIANGLES, p.count, GL_UNSIGNED_INT, nullptr); } }
void GLRenderer::draw(const Scene& s, int w, int h, float fps) {
  if (w < 2 || h < 2) return; glViewport(0, 0, w, h); glClearColor(.05f, .08f, .05f, 1); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  float aspect = float(w) / h; Mat4 P = mPersp(s.cam.fovDeg, aspect, 0.1f, 400.f), V = mLookAt(s.cam.eye, s.cam.target), VP = mMul(P, V);
  Vec3 f = normalize(s.cam.target - s.cam.eye), r = normalize(cross(f, {0, 1, 0})), u = cross(r, f); float tanH = std::tan(s.cam.fovDeg * .5f * kPi / 180.f);
  glDisable(GL_DEPTH_TEST); glDisable(GL_BLEND); glDisable(GL_CULL_FACE); glUseProgram(sky);
  glUniform3f(U(sky, "uF"), f.x, f.y, f.z); glUniform3f(U(sky, "uR"), r.x, r.y, r.z); glUniform3f(U(sky, "uU"), u.x, u.y, u.z); glUniform2f(U(sky, "uTan"), tanH * aspect, tanH);
  glUniform3f(U(sky, "uHoriz"), s.skyHorizon.x, s.skyHorizon.y, s.skyHorizon.z); glUniform3f(U(sky, "uZenith"), s.skyTop.x, s.skyTop.y, s.skyTop.z);
  glBindVertexArray(skyVao); glDrawArrays(GL_TRIANGLES, 0, 3); glEnable(GL_DEPTH_TEST); glDepthFunc(GL_LEQUAL);
  glUseProgram(pbr); glUniformMatrix4fv(U(pbr, "uVP"), 1, GL_FALSE, VP.data()); glUniform3f(U(pbr, "uCam"), s.cam.eye.x, s.cam.eye.y, s.cam.eye.z); glUniform1f(U(pbr, "uTime"), s.time);
  glUniform3f(U(pbr, "uHoriz"), s.skyHorizon.x, s.skyHorizon.y, s.skyHorizon.z); glUniform3f(U(pbr, "uZenith"), s.skyTop.x, s.skyTop.y, s.skyTop.z);
  float lp[24] = {}, lc[24] = {}, lr[8] = {}; int nl = (int)std::min<size_t>(8, s.lights.size());  // nearest-first order is provided by the world
  for (int i = 0; i < nl; i++) { const Light& L = s.lights[i]; lp[i*3] = L.pos.x; lp[i*3+1] = L.pos.y; lp[i*3+2] = L.pos.z; lc[i*3] = L.color.x; lc[i*3+1] = L.color.y; lc[i*3+2] = L.color.z; lr[i] = L.radius; }
  glUniform3fv(U(pbr, "uLP"), 8, lp); glUniform3fv(U(pbr, "uLC"), 8, lc); glUniform1i(U(pbr, "uNL"), nl); for (int i = 0; i < 8; i++) glUniform1f(U(pbr, ("uLR[" + std::to_string(i) + "]").c_str()), lr[i]);
  glUniform1i(U(pbr, "uAlb"), 0); glUniform1i(U(pbr, "uNrm"), 1); glUniform1i(U(pbr, "uMR"), 2); glUniform1i(U(pbr, "uEm"), 3);
  for (const Instance& in : s.inst) if (in.model) drawModel(in, *in.model, upload(in.model));
  glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBindVertexArray(0);
  for (const Fx& fx : s.fx) { float sx, sy, d; if (project(VP, fx.pos, w, h, sx, sy, d)) { float c[4] = {fx.color.x, fx.color.y, fx.color.z, fx.alpha}; glow(sx, sy, fx.size * h * 0.9f / std::max(d, .5f), c); } }
  glBlendFunc(GL_SRC_ALPHA, GL_ONE); flush(w, h, true); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); drawHud(s, w, h, fps); flush(w, h, false); glDisable(GL_BLEND); }
}  // namespace isekai
#endif
