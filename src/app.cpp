// Interactive game loop (Windows): OpenGL 3.3 PBR path with automatic software-framebuffer fallback.
#ifdef _WIN32
#include <chrono>
#include <cstdio>
#include <memory>
#include "game_world.hpp"
#include "gl_renderer.hpp"
#include "platform.hpp"
#include "soft_extra.hpp"
namespace isekai {
int runInteractive(const std::string& root) {
  Window win; if (!win.create(1600, 900, "Chronicles of Aetheria: Isekai")) return 2;
  GameWorld world(root); if (!world.assetsFound()) { win.messageBox("Chronicles of Aetheria: Isekai", "Could not find the 'assets/models' folder next to isekai.exe.\nPlease extract the whole zip and run isekai.exe from the extracted folder."); return 3; }
  std::unique_ptr<GLRenderer> gl; char err[256] = {0};
  if (win.initGL(err, sizeof err)) { gl = std::make_unique<GLRenderer>(); std::string e; if (!gl->init(e)) { std::fprintf(stderr, "GL init failed: %s\n", e.c_str()); gl.reset(); } }
  else std::fprintf(stderr, "GL context unavailable: %s\n", err);
  if (!gl) win.messageBox("Chronicles of Aetheria: Isekai", "OpenGL 3.3 is unavailable on this system, so the game will run with the built-in software renderer (lower resolution).");
  std::unique_ptr<Framebuffer> soft; Input in; win.setMouseCapture(true);
  auto last = std::chrono::steady_clock::now(); 
  while (win.pollEvents(in)) {
    auto now = std::chrono::steady_clock::now(); float dt = std::chrono::duration<float>(now - last).count(); last = now; if (dt <= 0) dt = 1e-4f;
    if (!in.focused && win.mouseCaptured()) win.setMouseCapture(false);
    if (in.pressed[KEY_ESC] && win.mouseCaptured()) { win.setMouseCapture(false); }
    else if (!win.mouseCaptured() && in.lmbPressed && in.focused) { win.setMouseCapture(true); in.lmbPressed = false; }
    if (in.pressed[KEY_F11]) win.toggleFullscreen();
    world.update(in, dt, float(in.width) / std::max(1, in.height)); Scene sc = world.buildScene();
    if (gl) { gl->draw(sc, in.width, in.height); win.swap(); }
    else { int sw = 480, sh = 270; if (!soft) soft = std::make_unique<Framebuffer>(sw, sh); renderSceneSoft(*soft, sc); win.presentSoftware(soft->rgb.data(), sw, sh); }
  }
  return 0;
}
}  // namespace isekai
#endif
