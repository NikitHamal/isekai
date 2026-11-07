// Procedural placeholder / ground meshes (used when an optional .glb is missing, and for the forest floor).
#include "game_world.hpp"
namespace isekai {
Model makeBoxModel(Vec3 h, Vec3 c, Vec3 rgb) {
  Model m; m.name = "box"; Primitive P; const Vec3 N[6] = {{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
  for (int f = 0; f < 6; f++) { Vec3 n = N[f], u = std::fabs(n.y) > .5f ? Vec3{1, 0, 0} : Vec3{0, 1, 0}, v = cross(n, u); u = cross(v, n); uint32_t b = (uint32_t)P.pos.size();
    for (int k = 0; k < 4; k++) { float su = (k == 1 || k == 2) ? 1.f : -1.f, sv = k >= 2 ? 1.f : -1.f; Vec3 d = n + u * su + v * sv;
      P.pos.push_back({c.x + d.x * h.x, c.y + d.y * h.y, c.z + d.z * h.z}); P.nrm.push_back(n); P.uv.push_back(su * .5f + .5f); P.uv.push_back(sv * .5f + .5f); }
    for (uint32_t i : {0u, 1u, 2u, 0u, 2u, 3u}) P.idx.push_back(b + i); }
  Material mt; mt.name = "placeholder"; mt.baseFactor[0] = rgb.x; mt.baseFactor[1] = rgb.y; mt.baseFactor[2] = rgb.z; m.materials.push_back(mt); P.material = 0; m.prims.push_back(P);
  m.bmin = {c.x - h.x, c.y - h.y, c.z - h.z}; m.bmax = {c.x + h.x, c.y + h.y, c.z + h.z}; return m; }
Model makeGroundModel(float h, float y) {  // tessellated so near-plane clipping in the software path never drops the whole floor
  Model m; m.name = "ground"; Primitive P; const int N = 24; for (int j = 0; j <= N; j++) for (int i = 0; i <= N; i++) { P.pos.push_back({(i / float(N) * 2 - 1) * h, y - 0.02f, (j / float(N) * 2 - 1) * h}); P.nrm.push_back({0, 1, 0}); P.uv.push_back(i * 2.f); P.uv.push_back(j * 2.f); }
  for (int j = 0; j < N; j++) for (int i = 0; i < N; i++) { uint32_t a = j * (N + 1) + i, b = a + 1, c = a + N + 1, d = c + 1; for (uint32_t k : {a, c, b, b, c, d}) P.idx.push_back(k); }
  Material mt; mt.name = "ground"; m.materials.push_back(mt); P.material = 0; m.prims.push_back(P); m.bmin = {-h, y, -h}; m.bmax = {h, y, h}; return m; }
}  // namespace isekai
