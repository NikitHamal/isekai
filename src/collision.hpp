// Mesh-driven collision: every static model instance (buildings, cliffs, boulders, trees, wagon, props) is rasterised into a multi-level
// 0.2 m grid of walkable floors (up-facing triangles) and obstruction spans (walls / ceilings).  Gives enterable interiors, standable rocks,
// stairs, headroom checks, ledge mantling and camera collision from the SAME triangles that are rendered.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <unordered_map>
#include <vector>
#include <isekai/model.h>
#include "terrain.hpp"
namespace isekai {
struct CHit { float y0, y1; uint8_t kind; };   // kind 0: walkable floor (y0==y1)   kind 1: obstruction span [y0,y1]
struct CGrid { float x0 = 0, z0 = 0; int nx = 0, nz = 0; std::vector<std::vector<CHit>> cell; };
class Collision {
 public:
  static constexpr float kCell = 0.2f, kStep = 0.55f, kBody = 1.75f;
  void addModel(const Model& m, const Mat4& M) {
    std::vector<Vec3> P; float x0 = 1e9f, z0 = 1e9f, x1 = -1e9f, z1 = -1e9f; std::vector<std::pair<size_t, size_t>> ranges;
    for (const Primitive& pr : m.prims) { size_t b = P.size(); for (const Vec3& v : pr.pos) { Vec3 w = transformPoint(M, v); P.push_back(w); x0 = std::min(x0, w.x); x1 = std::max(x1, w.x); z0 = std::min(z0, w.z); z1 = std::max(z1, w.z); } ranges.push_back({b, pr.pos.size()}); }
    if (P.empty()) return; CGrid g; g.x0 = x0 - kCell; g.z0 = z0 - kCell; g.nx = int((x1 - x0) / kCell) + 3; g.nz = int((z1 - z0) / kCell) + 3; g.cell.resize(size_t(g.nx) * g.nz);
    size_t pi = 0; std::unordered_map<int, std::pair<float, float>> tmp;
    for (const Primitive& pr : m.prims) { size_t base = ranges[pi++].first;
      for (size_t k = 0; k + 2 < pr.idx.size(); k += 3) {
        Vec3 a = P[base + pr.idx[k]], b = P[base + pr.idx[k + 1]], c = P[base + pr.idx[k + 2]]; Vec3 n = cross(b - a, c - a); float nl = std::sqrt(dot(n, n)); if (nl < 1e-8f) continue; float ny = n.y / nl;
        if (std::min(a.y, std::min(b.y, c.y)) > 7.f) continue;
        if (std::fabs(ny) >= 0.7f) {   // floor (up-facing) or ceiling: z-buffer the triangle into cell centres
          int ix0 = int((std::min(a.x, std::min(b.x, c.x)) - g.x0) / kCell), ix1 = int((std::max(a.x, std::max(b.x, c.x)) - g.x0) / kCell) + 1, iz0 = int((std::min(a.z, std::min(b.z, c.z)) - g.z0) / kCell), iz1 = int((std::max(a.z, std::max(b.z, c.z)) - g.z0) / kCell) + 1;
          float det = (b.z - c.z) * (a.x - c.x) + (c.x - b.x) * (a.z - c.z); if (std::fabs(det) < 1e-9f) continue;
          for (int iz = std::max(iz0, 0); iz <= std::min(iz1, g.nz - 1); iz++) for (int ix = std::max(ix0, 0); ix <= std::min(ix1, g.nx - 1); ix++) {
            float px = g.x0 + (ix + .5f) * kCell, pz = g.z0 + (iz + .5f) * kCell;
            float l1 = ((b.z - c.z) * (px - c.x) + (c.x - b.x) * (pz - c.z)) / det, l2 = ((c.z - a.z) * (px - c.x) + (a.x - c.x) * (pz - c.z)) / det, l3 = 1.f - l1 - l2;
            if (l1 < -0.02f || l2 < -0.02f || l3 < -0.02f) continue; float y = l1 * a.y + l2 * b.y + l3 * c.y;
            g.cell[size_t(iz) * g.nx + ix].push_back(ny > 0 ? CHit{y, y, 0} : CHit{y, y + 0.06f, 1}); }
        } else {   // steep wall: conservative lattice sampling -> per-cell vertical span
          float e = std::max({vlen(b - a), vlen(c - b), vlen(a - c)}); int N = std::max(2, int(e / 0.08f)); if (N > 160) N = 160; tmp.clear();
          for (int i = 0; i <= N; i++) for (int j = 0; i + j <= N; j++) { float u = float(i) / N, v = float(j) / N, w = 1.f - u - v; Vec3 p = a * u + b * v + c * w;
            int ix = int((p.x - g.x0) / kCell), iz = int((p.z - g.z0) / kCell); if (ix < 0 || iz < 0 || ix >= g.nx || iz >= g.nz) continue; int key = iz * g.nx + ix;
            auto it = tmp.find(key); if (it == tmp.end()) tmp[key] = {p.y, p.y}; else { it->second.first = std::min(it->second.first, p.y); it->second.second = std::max(it->second.second, p.y); } }
          for (auto& kv : tmp) g.cell[kv.first].push_back({kv.second.first, kv.second.second, 1}); }
      } }
    grids.push_back(std::move(g)); }
  // tallest walkable floor at (x,z) not above yMax (terrain included)
  float floorAt(float x, float z, float yMax) const {
    float best = -1e9f, th = terrainHeight(x, z); if (th <= yMax) best = th;
    for (const CGrid& g : grids) { const std::vector<CHit>* c = cellAt(g, x, z); if (!c) continue; for (const CHit& h : *c) if (h.kind == 0 && h.y0 <= yMax && h.y0 > best) best = h.y0; }
    return best; }
  // any obstruction (wall / ceiling / overhead floor / rising terrain) intersecting the open span (lo,hi) at (x,z)
  bool blocked(float x, float z, float lo, float hi) const {
    if (terrainHeight(x, z) > lo) return true;
    for (const CGrid& g : grids) { const std::vector<CHit>* c = cellAt(g, x, z); if (!c) continue;
      for (const CHit& h : *c) { if (h.kind == 1) { if (h.y1 > lo && h.y0 < hi) return true; } else if (h.y0 > lo && h.y0 < hi) return true; } }
    return false; }
  bool blockedPoint(Vec3 p) const {   // projectile / camera ray test (thin surfaces, 12 cm tolerance)
    for (const CGrid& g : grids) { const std::vector<CHit>* c = cellAt(g, p.x, p.z); if (!c) continue; for (const CHit& h : *c) if (h.y1 > p.y - .12f && h.y0 < p.y + .12f) return true; }
    return false; }
  bool bodyFits(float x, float z, float y, float r) const {
    for (int i = -1; i < 8; i++) { float a = i * 0.7853982f, px = i < 0 ? x : x + std::cos(a) * r, pz = i < 0 ? z : z + std::sin(a) * r; if (blocked(px, pz, y + kStep, y + kBody)) return false; }
    return true; }
  float groundBelow(float x, float z, float y, float r, float step = kStep) const {
    float best = floorAt(x, z, y + step); for (int i = 0; i < 4; i++) { float a = i * 1.5707963f; best = std::max(best, floorAt(x + std::cos(a) * r * .7f, z + std::sin(a) * r * .7f, y + step)); } return best; }
  size_t gridCount() const { return grids.size(); }
 private:
  static const std::vector<CHit>* cellAt(const CGrid& g, float x, float z) {
    int ix = int(std::floor((x - g.x0) / kCell)), iz = int(std::floor((z - g.z0) / kCell)); if (ix < 0 || iz < 0 || ix >= g.nx || iz >= g.nz) return nullptr; const auto& c = g.cell[size_t(iz) * g.nx + ix]; return c.empty() ? nullptr : &c; }
  std::vector<CGrid> grids;
};
}  // namespace isekai
