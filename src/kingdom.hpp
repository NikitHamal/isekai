// Valoria Kingdom Frontier layout: landmark placements and collision footprints shared by gameplay and scene assembly.
#pragma once
#include <vector>
#include "terrain.hpp"
namespace isekai {
struct Footprint { float cx, cz, hx, hz; };
inline Vec3 guildPos() { return {roadCenterX(16.f) - 15.5f, terrainHeight(roadCenterX(16.f) - 15.5f, 16.f), 16.f}; }   // door faces the road (yaw = +pi/2)
inline Vec3 wagonPos() { return {roadCenterX(8.f) + 6.2f, terrainHeight(roadCenterX(8.f) + 6.2f, 8.f), 8.f}; }
inline Vec3 keepPos() { return {0.f, terrainHeight(0.f, 60.f), 60.f}; }
inline Vec3 paladinPos() { return {roadCenterX(44.f) + 4.f, terrainHeight(roadCenterX(44.f) + 4.f, 44.f), 44.f}; }
inline Vec3 forgePos() { return {roadCenterX(22.f) + 14.5f, terrainHeight(roadCenterX(22.f) + 14.5f, 22.f), 22.f}; }
inline Vec3 towerPos() { return {roadCenterX(38.f) - 14.0f, terrainHeight(roadCenterX(38.f) - 14.0f, 38.f), 38.f}; }
inline Vec3 tavernPos() { return {roadCenterX(36.f) + 15.8f, terrainHeight(roadCenterX(36.f) + 15.8f, 36.f), 36.f}; }
// Buildings are authored in metres (origin at building centre): placed 1:1 with a yaw. Keep faces the plaza (yaw = pi).
inline std::vector<Footprint> obstacles() {
  Vec3 g = guildPos(), w = wagonPos(), k = keepPos(); std::vector<Footprint> o;
  Vec3 fg = forgePos(), tw = towerPos(), tv = tavernPos();
  o.push_back({g.x, g.z, 5.9f, 8.1f}); o.push_back({w.x, w.z + 1.f, 1.5f, 3.3f});
  o.push_back({fg.x, fg.z, 3.8f, 4.8f}); o.push_back({tw.x, tw.z, 3.6f, 3.6f}); o.push_back({tv.x, tv.z, 4.2f, 5.7f});
  for (float s : {-1.f, 1.f}) { o.push_back({s * 6.25f, k.z, 2.75f, 8.f}); o.push_back({s * 9.f, k.z - 8.6f, 4.1f, 4.1f}); o.push_back({s * 13.5f, k.z, 4.5f, 2.5f}); o.push_back({s * 16.5f, k.z, 4.1f, 4.1f}); }
  return o; }
// Pushes a circle (x,z,r) out of every footprint; returns true if it moved.
inline bool pushOut(float& x, float& z, float r) {
  bool moved = false;
  for (const Footprint& f : obstacles()) {
    float dx = x - f.cx, dz = z - f.cz, ox = f.hx + r - std::fabs(dx), oz = f.hz + r - std::fabs(dz);
    if (ox > 0 && oz > 0) { if (ox < oz) x += (dx < 0 ? -ox : ox); else z += (dz < 0 ? -oz : oz); moved = true; } }
  return moved; }
}  // namespace isekai
