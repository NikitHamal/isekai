// OpenGL 3.3 renderer: offscreen HDR FBO, SSAO, dual-pass Gaussian bloom, Cook-Torrance GGX PBR + 3x3 PCF shadows, sky dome, glow FX and HUD.
#pragma once
#ifdef _WIN32
#include <string>
#include <unordered_map>
#include <vector>
#include "gl_loader.hpp"
#include "scene.hpp"
namespace isekai {
class GLRenderer {
 public:
  bool init(std::string& err);
  void draw(const Scene& s, int w, int h);
 private:
  struct HV { float x, y, u, v, r, g, b, a; };
  struct GPUPrim { GLuint vao = 0, vbo = 0, ebo = 0; GLsizei count = 0; int mat = -1, partId = 0; Vec3 pivot{}; };
  struct GPUModel { std::vector<GPUPrim> prims; std::vector<GLuint> tex; };
  GPUModel& upload(const Model* m);
  GLint U(GLuint prog, const char* n);
  void ensureFbos(int w, int h);
  void drawModel(const Instance& in, const Model& m, GPUModel& g, bool blendPass);
  void drawShadowCaster(const Instance& in, const Model& m, GPUModel& g);
  void shadowPass(const Scene& s, const Mat4& lvp);
  // HUD helpers (gl_hud.cpp)
  void quad(float x0, float y0, float x1, float y1, const float* c);
  void glow(float x, float y, float r, const float* c);
  void fan(float cx, float cy, const std::vector<float>& pts, const float* c);
  void disc(float cx, float cy, float r, const float* c, int seg = 40);
  void ring(float cx, float cy, float r, float t, const float* c);
  void text(float x, float y, const std::string& s, float scale, const float* c);
  void flush(int w, int h, bool additive);
  void drawHud(const Scene& s, int w, int h);
  bool project(const Mat4& vp, Vec3 p, int w, int h, float& sx, float& sy, float& depth);
  GLuint shadowProg = 0, shadowFbo = 0, shadowTex = 0; static constexpr int kShadowRes = 2048;
  GLuint sceneFbo = 0, sceneColorTex = 0, sceneDepthTex = 0;
  GLuint bloomFbo[2] = {0, 0}, bloomTex[2] = {0, 0}; int fboW = 0, fboH = 0;
  GLuint pbr = 0, sky = 0, bloomProg = 0, postProg = 0, hud = 0, skyVao = 0, hudVao = 0, hudVbo = 0; std::vector<HV> hv;
  std::unordered_map<const Model*, GPUModel> models; std::unordered_map<std::string, GLint> uloc;
};
}  // namespace isekai
#endif
