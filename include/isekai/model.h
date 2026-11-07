#pragma once
#include <array>
#include <cstdint>
#include <string>
#include <vector>
namespace isekai {
using Mat4 = std::array<float, 16>;  // column-major
struct Vec3 { float x = 0, y = 0, z = 0; };
inline Vec3 operator+(Vec3 a, Vec3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
inline Vec3 operator-(Vec3 a, Vec3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
inline Vec3 operator*(Vec3 a, float s) { return {a.x * s, a.y * s, a.z * s}; }
inline float dot(Vec3 a, Vec3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
inline Vec3 cross(Vec3 a, Vec3 b) { return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x}; }
Vec3 normalize(Vec3 v);
Vec3 transformPoint(const Mat4& m, Vec3 p);
Vec3 transformDir(const Mat4& m, Vec3 p);

struct Texture { int w = 0, h = 0; std::vector<uint8_t> rgba; bool valid() const { return w > 0; } };
struct Material {
  std::string name; int base = -1, normal = -1, mr = -1, emissive = -1;
  float baseFactor[4] = {1, 1, 1, 1}; float emissiveFactor[3] = {0, 0, 0}; bool blend = false;
};
struct Primitive {
  std::vector<Vec3> pos, nrm; std::vector<float> uv; std::vector<float> tan;  // tan: xyzw
  std::vector<uint32_t> idx; int material = -1; std::string node;
};
struct Model {
  std::string path, name; std::vector<Texture> textures; std::vector<Material> materials; std::vector<Primitive> prims;
  int nodeCount = 0; Vec3 bmin{1e9f, 1e9f, 1e9f}, bmax{-1e9f, -1e9f, -1e9f};
  size_t triangles() const { size_t t = 0; for (auto& p : prims) t += p.idx.size() / 3; return t; }
};
// Loads a .glb: world-space baked primitives, embedded PNG textures decoded to RGBA8. Returns false + err on failure.
bool loadGlb(const std::string& path, Model& out, std::string& err);

struct Framebuffer { int w, h; std::vector<uint8_t> rgb; std::vector<float> depth; Framebuffer(int W, int H) : w(W), h(H), rgb(W * H * 3), depth(W * H) {} };
struct Camera { Vec3 eye, target{0, 0, 0}; float fovDeg = 45; };
void clearFrame(Framebuffer& fb, Vec3 skyTop, Vec3 skyBottom);
// Renders a model (uniformly scaled/offset into world) with PBR-lite shading: albedo, normal map, emissive, warm key light, fog, ACES.
void drawModel(Framebuffer& fb, const Camera& cam, const Model& m, Vec3 offset, float scale);
bool writePng(const std::string& path, const Framebuffer& fb);
}  // namespace isekai
