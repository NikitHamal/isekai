// Chronicles of Aetheria: Isekai — entry point. Modes: --verify-headless (CI/QA), default interactive (see ROADMAP E3+).
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <isekai/model.h>
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
  bool png = writePng(root + "/docs/previews/engine_headless_frame.png", fb);
  std::printf("headless: %d model(s), %zu triangles, frame %s, %d failure(s)\n", n, totalTris, png ? "written" : "WRITE-FAILED", failed);
  return (failed == 0 && png) ? 0 : 1;
}

int main(int argc, char** argv) {
  std::string root = "."; bool headless = false;
  for (int i = 1; i < argc; i++) { if (!std::strcmp(argv[i], "--verify-headless")) headless = true; else if (!std::strcmp(argv[i], "--root") && i + 1 < argc) root = argv[++i]; }
  if (headless) return verifyHeadless(root);
#ifdef ISEKAI_WINDOW
  std::printf("Interactive window mode: planned in milestone E3/E4.\n");
#else
  std::printf("Chronicles of Aetheria: Isekai\nBuilt without window support. Use --verify-headless, or configure with -DISEKAI_WINDOW=ON.\n");
#endif
  return 0;
}
