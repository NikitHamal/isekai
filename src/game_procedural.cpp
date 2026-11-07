// Procedural placeholder / ground meshes (used when an optional .glb is missing, and for the forest floor).
#include "game_world.hpp"
#include "terrain.hpp"
namespace isekai {
Model makeBoxModel(Vec3 h, Vec3 c, Vec3 rgb) {
  Model m; m.name = "box"; Primitive P; const Vec3 N[6] = {{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
  for (int f = 0; f < 6; f++) { Vec3 n = N[f], u = std::fabs(n.y) > .5f ? Vec3{1, 0, 0} : Vec3{0, 1, 0}, v = cross(n, u); u = cross(v, n); uint32_t b = (uint32_t)P.pos.size();
    for (int k = 0; k < 4; k++) { float su = (k == 1 || k == 2) ? 1.f : -1.f, sv = k >= 2 ? 1.f : -1.f; Vec3 d = n + u * su + v * sv;
      P.pos.push_back({c.x + d.x * h.x, c.y + d.y * h.y, c.z + d.z * h.z}); P.nrm.push_back(n); P.uv.push_back(su * .5f + .5f); P.uv.push_back(sv * .5f + .5f); }
    for (uint32_t i : {0u, 1u, 2u, 0u, 2u, 3u}) P.idx.push_back(b + i); }
  Material mt; mt.name = "placeholder"; mt.baseFactor[0] = rgb.x; mt.baseFactor[1] = rgb.y; mt.baseFactor[2] = rgb.z; m.materials.push_back(mt); P.material = 0; m.prims.push_back(P);
  m.bmin = {c.x - h.x, c.y - h.y, c.z - h.z}; m.bmax = {c.x + h.x, c.y + h.y, c.z + h.z}; return m; }
Model makeTerrainModel(float h, float step) {  // sculpted height-field (rolling meadows, flat cobble road/plaza, rising frontier foothills)
  Model m; m.name = "terrain"; Primitive P; const int N = int(2 * h / step); float lo = 1e9f, hi = -1e9f;
  for (int j = 0; j <= N; j++) for (int i = 0; i <= N; i++) {
    float x = -h + i * step, z = -h + j * step, y = terrainHeight(x, z); lo = std::min(lo, y); hi = std::max(hi, y);
    float dx = terrainHeight(x + .5f, z) - terrainHeight(x - .5f, z), dz = terrainHeight(x, z + .5f) - terrainHeight(x, z - .5f);
    P.pos.push_back({x, y, z}); P.nrm.push_back(normalize({-dx, 1.f, -dz})); P.uv.push_back(x * .25f); P.uv.push_back(z * .25f); }
  for (int j = 0; j < N; j++) for (int i = 0; i < N; i++) { uint32_t a = j * (N + 1) + i, b = a + 1, c = a + N + 1, d = c + 1; for (uint32_t k : {a, c, b, b, c, d}) P.idx.push_back(k); }
  Material mt; mt.name = "terrain"; m.materials.push_back(mt); P.material = 0; m.prims.push_back(P); m.bmin = {-h, lo, -h}; m.bmax = {h, hi, h}; return m; }
}  // namespace isekai
