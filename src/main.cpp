// Chronicles of Aetheria: Isekai — entry point. Modes: --verify-headless (CI/QA), default interactive (see ROADMAP E3+).
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <isekai/model.h>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <direct.h>
extern "C" { __declspec(dllexport) unsigned long NvOptimusEnablement = 0x00000001; __declspec(dllexport) int AmdPowerXpressRequestHighPerformance = 1; }
#endif
#include "game_world.hpp"
#include "soft_extra.hpp"
namespace isekai { int runInteractive(const std::string& root); }
namespace fs = std::filesystem;
using namespace isekai;

static int verifyHeadless(const std::string& root) {
  std::vector<std::string> files;
  if (fs::exists(root + "/assets/models"))
    for (auto& e : fs::recursive_directory_iterator(root + "/assets/models")) if (e.path().extension() == ".glb") files.push_back(e.path().string());
  std::sort(files.begin(), files.end());
  std::vector<Model> models; size_t totalTris = 0; int failed = 0;
  for (auto& f : files) {
    Model m; std::string err; auto t0 = std::chrono::steady_clock::now();
    if (!loadGlb(f, m, err)) { std::printf("[FAIL] %s: %s\n", f.c_str(), err.c_str()); failed++; continue; }
    int ms = int(std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0).count());
    bool texOk = !m.materials.empty(); for (auto& mt : m.materials) texOk &= mt.base >= 0 && mt.normal >= 0 && mt.mr >= 0;
    std::printf("[%s] %s tris=%zu nodes=%d prims=%zu materials=%zu textures=%zu (%d ms)\n", texOk ? " OK " : "WARN", m.name.c_str(), m.triangles(), m.nodeCount, m.prims.size(), m.materials.size(), m.textures.size(), ms);
    if (!texOk) failed++; totalTris += m.triangles(); models.push_back(std::move(m));
  }
  Framebuffer fb(1280, 720); clearFrame(fb, {.35f, .55f, .8f}, {.9f, .8f, .6f});
  int n = int(models.size()), cols = std::max(1, int(std::ceil(std::sqrt(double(std::max(n, 1)))))); float cell = 7.f;
  for (int i = 0; i < n; i++) {
    const Model& m = models[i]; float ext = std::max({m.bmax.x - m.bmin.x, m.bmax.y - m.bmin.y, m.bmax.z - m.bmin.z}); float s = (cell * 0.8f) / std::max(ext, 0.01f);
    Vec3 c = (m.bmin + m.bmax) * 0.5f; Vec3 off = {(i % cols) * cell - (cols - 1) * cell * .5f - c.x * s, -m.bmin.y * s - 1.f, -(i / cols) * cell - c.z * s};
    drawModel(fb, Camera{{0, 3.f + cols * 1.2f, 4.f + cols * 3.5f}, {0, 0.f, -(n / cols) * cell * .3f}, 45}, m, off, s);
  }
  fs::create_directories(root + "/docs/previews");
  bool png = writePng(root + "/docs/previews/asset_contact_sheet.png", fb);
  { GameWorld w(root); w.stageShowcase(); Framebuffer sf(1600, 900); renderSceneSoft(sf, w.buildScene()); png &= writePng(root + "/docs/previews/engine_headless_frame.png", sf); std::printf("scene: %d of 14 catalog models loaded into the playable world\n", w.modelCount()); }
  std::printf("headless: %d model(s), %zu triangles, frame %s, %d failure(s)\n", n, totalTris, png ? "written" : "WRITE-FAILED", failed);
  return (failed == 0 && png) ? 0 : 1;
}

int main(int argc, char** argv) {
  std::string root = "."; bool headless = false;
  for (int i = 1; i < argc; i++) { if (!std::strcmp(argv[i], "--verify-headless")) headless = true; else if (!std::strcmp(argv[i], "--root") && i + 1 < argc) root = argv[++i]; }
  if (headless) return verifyHeadless(root);
#ifdef _WIN32
  char exe[MAX_PATH]; if (GetModuleFileNameA(nullptr, exe, MAX_PATH)) {  // find assets/ next to isekai.exe (or one level up if inside bin/)
    fs::path d = fs::path(exe).parent_path(); if (!fs::exists(d / "assets" / "models") && fs::exists(d.parent_path() / "assets" / "models")) d = d.parent_path();
    SetCurrentDirectoryA(d.string().c_str()); root = d.string(); }
  return runInteractive(root);
#else
  std::printf("Chronicles of Aetheria: Isekai\nThe interactive 3D window is implemented for Windows (Win32 + OpenGL 3.3). Use --verify-headless on this platform.\n");
  return 0;
#endif
}
#ifdef _WIN32
int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {
  if (__argc > 1 && AttachConsole(ATTACH_PARENT_PROCESS)) { freopen("CONOUT$", "w", stdout); freopen("CONOUT$", "w", stderr); }
  return main(__argc, __argv);
}
#endif
