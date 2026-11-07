// Valoria Kingdom Frontier layout: landmark placements and collision footprints shared by gameplay and scene assembly.
#pragma once
#include <vector>
#include "terrain.hpp"
namespace isekai {
struct Footprint { float cx, cz, hx, hz; };
constexpr float kGuildH = 11.5f, kKeepH = 26.f, kWagonH = 3.0f;
inline Vec3 guildPos() { return {roadCenterX(16.f) - 15.5f, terrainHeight(roadCenterX(16.f) - 15.5f, 16.f), 16.f}; }   // door faces the road (yaw = +pi/2)
inline Vec3 wagonPos() { return {roadCenterX(8.f) + 6.2f, terrainHeight(roadCenterX(8.f) + 6.2f, 8.f), 8.f}; }
inline Vec3 keepPos() { return {0.f, terrainHeight(0.f, 60.f), 60.f}; }
inline Vec3 paladinPos() { return {roadCenterX(44.f) + 4.f, terrainHeight(roadCenterX(44.f) + 4.f, 44.f), 44.f}; }
inline std::vector<Footprint> obstacles() {
  Vec3 g = guildPos(), w = wagonPos(), k = keepPos();
  return {{g.x, g.z, 5.8f, 8.f}, {w.x, w.z, 1.35f, 2.8f}, {-10.5f - 7.f, k.z, 11.5f, 8.f}, {10.5f + 7.f, k.z, 11.5f, 8.f}, {-14.f, k.z, 4.f, 8.f}, {14.f, k.z, 4.f, 8.f}}; }
// Pushes a circle (x,z,r) out of every footprint; returns true if it moved.
inline bool pushOut(float& x, float& z, float r) {
  bool moved = false;
  for (const Footprint& f : obstacles()) {
    float dx = x - f.cx, dz = z - f.cz, ox = f.hx + r - std::fabs(dx), oz = f.hz + r - std::fabs(dz);
    if (ox > 0 && oz > 0) { if (ox < oz) x += (dx < 0 ? -ox : ox); else z += (dz < 0 ? -oz : oz); moved = true; } }
  return moved; }
}  // namespace isekai
