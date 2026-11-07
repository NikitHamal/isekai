// Platform abstraction: input snapshot + native window interface (implemented in win32_gl_window.cpp).
#pragma once
#include <cstdint>
namespace isekai {
enum Key { KEY_BACK = 0x08, KEY_TAB = 0x09, KEY_ENTER = 0x0D, KEY_SHIFT = 0x10, KEY_ESC = 0x1B, KEY_SPACE = 0x20,
           KEY_LEFT = 0x25, KEY_UP = 0x26, KEY_RIGHT = 0x27, KEY_DOWN = 0x28, KEY_F11 = 0x7A };
struct Input {
  bool down[256] = {}, pressed[256] = {};   // pressed = went down this frame
  bool lmb = false, rmb = false, lmbPressed = false;
  float mdx = 0, mdy = 0; int wheel = 0;                   // mouse delta in pixels this frame (only while mouse is captured)
  int width = 1600, height = 900; bool quit = false, resized = false, focused = true;
};
class Window {
 public:
  Window(); ~Window();
  bool create(int w, int h, const char* title);   // native window (no GL yet)
  bool initGL(char* errBuf, int errLen);          // WGL 3.3 core context + dynamic loader
  bool pollEvents(Input& in);                     // false once the window closed
  void swap(); void toggleFullscreen(); void setMouseCapture(bool on); bool mouseCaptured() const;
  void presentSoftware(const uint8_t* rgb, int w, int h);  // StretchDIBits blit (software fallback)
  void setTitle(const char* t); void messageBox(const char* title, const char* text);
  struct Impl; Impl* p;
};
}  // namespace isekai
