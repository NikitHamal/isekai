// Shared terrain description: height field, winding kingdom road and splat weights (used by game logic, soft raster bake and mirrored in GLSL).
#pragma once
#include <cmath>
#include <algorithm>
#include "math3d.hpp"
namespace isekai {
inline float roadCenterX(float z) { return 3.5f * std::sin(z * 0.045f) + 1.5f * std::sin(z * 0.11f + 1.f); }
inline float tHash(float x, float y) { float s = std::sin(x * 127.1f + y * 311.7f) * 43758.5453f; return s - std::floor(s); }
inline float tNoise(float x, float y) {
  float ix = std::floor(x), iy = std::floor(y), fx = x - ix, fy = y - iy; fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
  return lerpf(lerpf(tHash(ix, iy), tHash(ix + 1, iy), fx), lerpf(tHash(ix, iy + 1), tHash(ix + 1, iy + 1), fx), fy); }
inline float sstep(float a, float b, float x) { float t = std::clamp((x - a) / (b - a), 0.f, 1.f); return t * t * (3 - 2 * t); }
// Cobblestone kingdom road (winding) widening into the Valoria town plaza south of z=10.
inline float roadMask(float x, float z) {
  float d = std::fabs(x - roadCenterX(z)), road = std::clamp((3.2f - d) / 1.2f, 0.f, 1.f);
  float plaza = sstep(8.f, 14.f, z) * (1.f - sstep(16.f, 22.f, d)); return std::max(road, plaza); }
inline float terrainHeight(float x, float z) {
  float rm = roadMask(x, z);
  float rolling = (tNoise(x * 0.04f, z * 0.04f) - 0.5f) * 3.0f + (tNoise(x * 0.12f, z * 0.12f) - 0.5f) * 0.7f;
  float foothill = std::clamp((-z - 18.f) / 40.f, 0.f, 1.f); foothill *= foothill;                 // frontier rises to the north (-z)
  float ridge = foothill * (14.f * tNoise(x * 0.03f + 7.f, z * 0.03f) + 5.f * tNoise(x * 0.09f, z * 0.09f));
  float townFlat = std::clamp((z - 8.f) / 20.f, 0.f, 1.f);                                          // flatten near the city
  float h = (rolling * (1.f - townFlat * 0.85f) + ridge) * (1.f - rm * 0.92f);
  return h; }
inline Vec3 vmix(Vec3 a, Vec3 b, float t) { return a * (1 - t) + b * t; }
// Splat-mapped terrain colour: lush grass / dry meadow, rocky foothills, mud verge and mortared cobblestone road (mirrored in the GLSL ground shader).
inline Vec3 terrainAlbedo(float x, float z, float h) {
  float rm = roadMask(x, z), n1 = tNoise(x * .9f, z * .9f), n2 = tNoise(x * 4.f, z * 4.f), n3 = tNoise(x * .12f, z * .12f), n4 = tNoise(x * 18.f, z * 18.f);
  Vec3 grass = vmix(vmix({.09f, .21f, .04f}, {.27f, .40f, .09f}, n1 * .6f + n2 * .4f), {.42f, .37f, .16f}, sstep(.55f, .9f, n3) * .6f) * (.85f + .3f * n4);
  float rk = std::clamp((h - 3.5f) / 5.f + (n3 - .5f) * .9f + (n2 - .5f) * .25f, 0.f, 1.f);
  Vec3 col = vmix(grass, vmix({.33f, .31f, .28f}, {.55f, .52f, .46f}, n2) * (.8f + .4f * n4), sstep(.25f, .7f, rk));
  Vec3 mud = vmix({.20f, .14f, .08f}, {.34f, .25f, .15f}, n2) * (.8f + .4f * n4);
  col = vmix(col, mud, sstep(.05f, .45f, rm));
  if (rm > .45f) {
    float rowH = .42f, row = std::floor(z / rowH), cu = (x - roadCenterX(z)) / .55f + (std::fmod(row, 2.f) != 0.f ? .5f : 0.f), fu = cu - std::floor(cu), fv = z / rowH - row;
    float edge = std::min(std::min(fu, 1 - fu) * .55f, std::min(fv, 1 - fv) * rowH), stone = tHash(std::floor(cu), row), bev = sstep(.0f, .06f, edge);
    Vec3 c = vmix({.38f, .36f, .33f}, {.62f, .59f, .52f}, stone) * (.85f + .3f * n4) * (.6f + .4f * bev); Vec3 mort = mud * .55f;
    col = vmix(col, vmix(mort, c, sstep(.015f, .045f, edge)), sstep(.45f, .8f, rm)); }
  return col; }
}  // namespace isekai
