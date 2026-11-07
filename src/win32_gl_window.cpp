// Native Win32 window + WGL OpenGL 3.3 core context. Links only system libs: opengl32 gdi32 user32 kernel32 shell32 winmm.
#ifdef _WIN32
#include "gl_loader.hpp"
#include "platform.hpp"
#include <cstdio>
#include <cstring>
#include <vector>
#define WGL_CONTEXT_MAJOR_VERSION_ARB 0x2091
#define WGL_CONTEXT_MINOR_VERSION_ARB 0x2092
#define WGL_CONTEXT_PROFILE_MASK_ARB 0x9126
#define WGL_CONTEXT_CORE_PROFILE_BIT_ARB 0x00000001
namespace isekai {
struct Window::Impl {
  HWND hwnd = nullptr; HDC dc = nullptr; HGLRC rc = nullptr; Input* in = nullptr; bool fullscreen = false, capture = false, closed = false;
  WINDOWPLACEMENT prev{}; DWORD prevStyle = 0; int w = 1600, h = 900; Input pend;
  void recenter() { RECT r; GetClientRect(hwnd, &r); POINT c{(r.right) / 2, (r.bottom) / 2}; ClientToScreen(hwnd, &c); SetCursorPos(c.x, c.y); }
};
static LRESULT CALLBACK wndProc(HWND h, UINT m, WPARAM wp, LPARAM lp) {
  auto* I = (Window::Impl*)GetWindowLongPtrA(h, GWLP_USERDATA); if (!I) return DefWindowProcA(h, m, wp, lp);
  Input& in = I->pend;
  switch (m) {
    case WM_CLOSE: I->closed = true; in.quit = true; return 0;
    case WM_DESTROY: return 0;
    case WM_SIZE: in.width = LOWORD(lp); in.height = HIWORD(lp); in.resized = true; return 0;
    case WM_SETFOCUS: in.focused = true; return 0;
    case WM_KILLFOCUS: in.focused = false; memset(in.down, 0, sizeof(in.down)); in.lmb = in.rmb = false; return 0;
    case WM_KEYDOWN: case WM_SYSKEYDOWN: if (wp < 256) { if (!(lp & (1 << 30))) in.pressed[wp] = true; in.down[wp] = true; } return 0;
    case WM_KEYUP: case WM_SYSKEYUP: if (wp < 256) in.down[wp] = false; return 0;
    case WM_LBUTTONDOWN: in.lmb = true; in.lmbPressed = true; return 0;
    case WM_LBUTTONUP: in.lmb = false; return 0;
    case WM_RBUTTONDOWN: in.rmb = true; return 0;
    case WM_RBUTTONUP: in.rmb = false; return 0;
    case WM_ERASEBKGND: return 1;
    case WM_SETCURSOR: if (I->capture && LOWORD(lp) == HTCLIENT) { SetCursor(nullptr); return TRUE; } break;
  }
  return DefWindowProcA(h, m, wp, lp);
}
Window::Window() : p(new Impl) {}
Window::~Window() { if (p->rc) { wglMakeCurrent(nullptr, nullptr); wglDeleteContext(p->rc); } if (p->hwnd) DestroyWindow(p->hwnd); delete p; }
bool Window::create(int w, int h, const char* title) {
  timeBeginPeriod(1); WNDCLASSA wc{}; wc.style = CS_OWNDC | CS_HREDRAW | CS_VREDRAW; wc.lpfnWndProc = wndProc; wc.hInstance = GetModuleHandleA(nullptr);
  wc.hCursor = LoadCursorA(nullptr, IDC_ARROW); wc.lpszClassName = "IsekaiWnd"; wc.hIcon = LoadIconA(nullptr, IDI_APPLICATION); RegisterClassA(&wc);
  RECT r{0, 0, w, h}; AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
  p->hwnd = CreateWindowExA(0, "IsekaiWnd", title, WS_OVERLAPPEDWINDOW | WS_VISIBLE, CW_USEDEFAULT, CW_USEDEFAULT, r.right - r.left, r.bottom - r.top, nullptr, nullptr, wc.hInstance, nullptr);
  if (!p->hwnd) return false; SetWindowLongPtrA(p->hwnd, GWLP_USERDATA, (LONG_PTR)p); p->dc = GetDC(p->hwnd);
  p->w = w; p->h = h; p->pend.width = w; p->pend.height = h; ShowWindow(p->hwnd, SW_SHOW); SetForegroundWindow(p->hwnd); return true;
}
bool Window::initGL(char* err, int errLen) {
  PIXELFORMATDESCRIPTOR pfd{}; pfd.nSize = sizeof(pfd); pfd.nVersion = 1; pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
  pfd.iPixelType = PFD_TYPE_RGBA; pfd.cColorBits = 32; pfd.cDepthBits = 24; pfd.cStencilBits = 8; pfd.iLayerType = PFD_MAIN_PLANE;
  int fmt = ChoosePixelFormat(p->dc, &pfd); if (!fmt || !SetPixelFormat(p->dc, fmt, &pfd)) { snprintf(err, errLen, "SetPixelFormat failed"); return false; }
  HGLRC tmp = wglCreateContext(p->dc); if (!tmp || !wglMakeCurrent(p->dc, tmp)) { snprintf(err, errLen, "wglCreateContext failed"); return false; }
  typedef HGLRC(WINAPI * CCA)(HDC, HGLRC, const int*); typedef BOOL(WINAPI * SI)(int);
  auto cca = (CCA)wglGetProcAddress("wglCreateContextAttribsARB"); int at[] = {WGL_CONTEXT_MAJOR_VERSION_ARB, 3, WGL_CONTEXT_MINOR_VERSION_ARB, 3, WGL_CONTEXT_PROFILE_MASK_ARB, WGL_CONTEXT_CORE_PROFILE_BIT_ARB, 0};
  p->rc = cca ? cca(p->dc, nullptr, at) : nullptr;
  if (p->rc) { wglMakeCurrent(nullptr, nullptr); wglDeleteContext(tmp); wglMakeCurrent(p->dc, p->rc); } else { p->rc = tmp; }  // compat context still exposes GL3.3 on NVIDIA
  const char* miss; if (!loadGLFunctions(&miss)) { snprintf(err, errLen, "OpenGL 3.3 entry point missing: %s", miss); return false; }
  if (auto si = (SI)wglGetProcAddress("wglSwapIntervalEXT")) si(1); return true;
}
bool Window::pollEvents(Input& in) {
  Input& q = p->pend; memset(q.pressed, 0, sizeof(q.pressed)); q.lmbPressed = false; q.resized = false; q.mdx = q.mdy = 0;
  MSG msg; while (PeekMessageA(&msg, nullptr, 0, 0, PM_REMOVE)) { TranslateMessage(&msg); DispatchMessageA(&msg); }
  if (p->capture && q.focused) { POINT c; GetCursorPos(&c); RECT r; GetClientRect(p->hwnd, &r); POINT m{r.right / 2, r.bottom / 2}; ClientToScreen(p->hwnd, &m);
    q.mdx = float(c.x - m.x); q.mdy = float(c.y - m.y); p->recenter(); }
  in = q; return !p->closed;
}
void Window::swap() { SwapBuffers(p->dc); }
void Window::setMouseCapture(bool on) { p->capture = on; if (on) { p->recenter(); ShowCursor(FALSE); } else { while (ShowCursor(TRUE) < 0) {} } }
bool Window::mouseCaptured() const { return p->capture; }
void Window::toggleFullscreen() {
  if (!p->fullscreen) { p->prev.length = sizeof(p->prev); GetWindowPlacement(p->hwnd, &p->prev); p->prevStyle = GetWindowLongA(p->hwnd, GWL_STYLE);
    MONITORINFO mi{sizeof(mi)}; GetMonitorInfoA(MonitorFromWindow(p->hwnd, MONITOR_DEFAULTTONEAREST), &mi);
    SetWindowLongA(p->hwnd, GWL_STYLE, WS_POPUP | WS_VISIBLE); SetWindowPos(p->hwnd, HWND_TOP, mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right - mi.rcMonitor.left, mi.rcMonitor.bottom - mi.rcMonitor.top, SWP_FRAMECHANGED | SWP_SHOWWINDOW);
  } else { SetWindowLongA(p->hwnd, GWL_STYLE, p->prevStyle | WS_VISIBLE); SetWindowPlacement(p->hwnd, &p->prev); SetWindowPos(p->hwnd, nullptr, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED); }
  p->fullscreen = !p->fullscreen;
}
void Window::presentSoftware(const uint8_t* rgb, int w, int h) {
  std::vector<uint8_t> bgra(size_t(w) * h * 4); for (size_t i = 0; i < size_t(w) * h; i++) { bgra[i*4] = rgb[i*3+2]; bgra[i*4+1] = rgb[i*3+1]; bgra[i*4+2] = rgb[i*3]; bgra[i*4+3] = 255; }
  BITMAPINFO bi{}; bi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER); bi.bmiHeader.biWidth = w; bi.bmiHeader.biHeight = -h; bi.bmiHeader.biPlanes = 1; bi.bmiHeader.biBitCount = 32; bi.bmiHeader.biCompression = BI_RGB;
  RECT r; GetClientRect(p->hwnd, &r); StretchDIBits(p->dc, 0, 0, r.right, r.bottom, 0, 0, w, h, bgra.data(), &bi, DIB_RGB_COLORS, SRCCOPY);
}
void Window::setTitle(const char* t) { SetWindowTextA(p->hwnd, t); }
void Window::messageBox(const char* t, const char* x) { MessageBoxA(p->hwnd, x, t, MB_OK | MB_ICONINFORMATION); }
}  // namespace isekai
#endif
