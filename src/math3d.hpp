// Small column-major matrix helpers shared by the GL renderer, software fallback and game logic.
#pragma once
#include <cmath>
#include <isekai/model.h>
namespace isekai {
constexpr float kPi = 3.14159265358979f;
inline Mat4 mIdent() { return {1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1}; }
inline Mat4 mMul(const Mat4& a, const Mat4& b) {
  Mat4 r{}; for (int c = 0; c < 4; c++) for (int rw = 0; rw < 4; rw++) { float s = 0; for (int k = 0; k < 4; k++) s += a[k * 4 + rw] * b[c * 4 + k]; r[c * 4 + rw] = s; } return r; }
inline Mat4 mTrans(Vec3 t) { Mat4 m = mIdent(); m[12] = t.x; m[13] = t.y; m[14] = t.z; return m; }
inline Mat4 mScale(float s) { Mat4 m = mIdent(); m[0] = m[5] = m[10] = s; return m; }
inline Mat4 mRotY(float a) { Mat4 m = mIdent(); float c = std::cos(a), s = std::sin(a); m[0] = c; m[2] = -s; m[8] = s; m[10] = c; return m; }
inline Mat4 mRotX(float a) { Mat4 m = mIdent(); float c = std::cos(a), s = std::sin(a); m[5] = c; m[6] = s; m[9] = -s; m[10] = c; return m; }
inline Mat4 mRotZ(float a) { Mat4 m = mIdent(); float c = std::cos(a), s = std::sin(a); m[0] = c; m[1] = s; m[4] = -s; m[5] = c; return m; }
inline Mat4 mPersp(float fovDeg, float aspect, float n, float f) {
  float t = 1.f / std::tan(fovDeg * 0.5f * kPi / 180.f); Mat4 m{}; m[0] = t / aspect; m[5] = t; m[10] = (f + n) / (n - f); m[11] = -1; m[14] = 2 * f * n / (n - f); return m; }
inline Mat4 mLookAt(Vec3 e, Vec3 c) {
  Vec3 f = normalize(c - e), r = normalize(cross(f, {0, 1, 0})), u = cross(r, f); Mat4 m = mIdent();
  m[0] = r.x; m[4] = r.y; m[8] = r.z; m[1] = u.x; m[5] = u.y; m[9] = u.z; m[2] = -f.x; m[6] = -f.y; m[10] = -f.z;
  m[12] = -dot(r, e); m[13] = -dot(u, e); m[14] = dot(f, e); return m; }
inline float vlen(Vec3 v) { return std::sqrt(dot(v, v)); }
inline float lerpf(float a, float b, float t) { return a + (b - a) * t; }
inline float wrapPi(float a) { while (a > kPi) a -= 2 * kPi; while (a < -kPi) a += 2 * kPi; return a; }
}  // namespace isekai
