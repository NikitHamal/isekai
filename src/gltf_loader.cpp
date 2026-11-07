#define CGLTF_IMPLEMENTATION
#include "cgltf.h"
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#include <algorithm>
#include <cmath>
#include <isekai/model.h>
namespace isekai {
Vec3 normalize(Vec3 v) { float l = std::sqrt(dot(v, v)); return l > 1e-12f ? v * (1.f / l) : Vec3{0, 1, 0}; }
Vec3 transformPoint(const Mat4& m, Vec3 p) { return {m[0] * p.x + m[4] * p.y + m[8] * p.z + m[12], m[1] * p.x + m[5] * p.y + m[9] * p.z + m[13], m[2] * p.x + m[6] * p.y + m[10] * p.z + m[14]}; }
Vec3 transformDir(const Mat4& m, Vec3 p) { return {m[0] * p.x + m[4] * p.y + m[8] * p.z, m[1] * p.x + m[5] * p.y + m[9] * p.z, m[2] * p.x + m[6] * p.y + m[10] * p.z}; }

static int texIndex(const cgltf_data* d, const cgltf_texture_view& v) { return v.texture ? int(v.texture->image - d->images) : -1; }
static bool hasSub(const std::string& s, const char* k) { return s.find(k) != std::string::npos; }

static void rigCharacterParts(Model& out) {
  bool isChar = hasSub(out.name, "chr_") || hasSub(out.name, "mon_") || hasSub(out.name, "enm_") || hasSub(out.name, "warhorse") || hasSub(out.name, "griffon");
  if (!isChar || hasSub(out.name, "slime")) return;
  bool quad = hasSub(out.name, "wolf") || hasSub(out.name, "warhorse") || hasSub(out.name, "griffon");
  float H = std::max(out.bmax.y - out.bmin.y, 0.01f), W = std::max(out.bmax.x - out.bmin.x, 0.01f), L = std::max(out.bmax.z - out.bmin.z, 0.01f);
  float zc = 0.5f * (out.bmin.z + out.bmax.z), wSide = -1.f, wxSum = 0.f; int wCnt = 0;
  auto isWpnNode = [&](const std::string& n) {
    return hasSub(n, "sword") || hasSub(n, "blade") || hasSub(n, "grip") || hasSub(n, "runes") || hasSub(n, "axe") || hasSub(n, "cleaver") || hasSub(n, "hammer") || hasSub(n, "staff") || hasSub(n, "bow") || hasSub(n, "halberd") || hasSub(n, "crossbow");
  };
  for (auto& P : out.prims) if (isWpnNode(P.node)) for (auto& v : P.pos) { wxSum += v.x; wCnt++; }
  if (wCnt > 0) wSide = (wxSum / wCnt >= 0.f) ? 1.f : -1.f;
  auto pivotFor = [&](int pid) -> Vec3 {
    if (quad) {
      if (pid == PART_HEAD) return {0.f, out.bmin.y + 0.65f * H, zc + 0.24f * L};
      if (pid == PART_LEG_L) return {0.f, out.bmin.y + 0.50f * H, zc + 0.24f * L};
      if (pid == PART_LEG_R) return {0.f, out.bmin.y + 0.50f * H, zc - 0.24f * L};
      if (pid == PART_JAW_OR_TAIL) return {0.f, out.bmin.y + 0.58f * H, zc - 0.30f * L};
      return {0.f, out.bmin.y + 0.52f * H, zc};
    }
    if (pid == PART_HEAD) return {0.f, out.bmin.y + 0.80f * H, 0.f};
    if (pid == PART_CLOAK) return {0.f, out.bmin.y + 0.82f * H, -0.05f * L};
    if (pid == PART_ARM_R || pid == PART_WEAPON_R) return {wSide * 0.19f * W, out.bmin.y + 0.76f * H, 0.f};
    if (pid == PART_ARM_L) return {-wSide * 0.19f * W, out.bmin.y + 0.76f * H, 0.f};
    if (pid == PART_LEG_L) return {0.08f * W, out.bmin.y + 0.46f * H, 0.f};
    if (pid == PART_LEG_R) return {-0.08f * W, out.bmin.y + 0.46f * H, 0.f};
    return {0.f, out.bmin.y + 0.46f * H, 0.f};
  };
  std::vector<Primitive> rigged;
  for (auto& P : out.prims) {
    int fixed = -1; const std::string& n = P.node;
    if (hasSub(n, "cloak") || hasSub(n, "cape") || hasSub(n, "lining")) fixed = PART_CLOAK;
    else if (isWpnNode(n)) fixed = PART_WEAPON_R;
    else if (hasSub(n, "buckler") || hasSub(n, "shield") || hasSub(n, "glyph")) fixed = PART_ARM_L;
    else if (hasSub(n, "hair") || hasSub(n, "eyes") || hasSub(n, "helm") || hasSub(n, "visor") || hasSub(n, "crest") || hasSub(n, "plume") || hasSub(n, "horns") || hasSub(n, "tusks") || hasSub(n, "ears")) fixed = PART_HEAD;
    if (fixed >= 0) { P.partId = fixed; P.pivot = pivotFor(fixed); rigged.push_back(std::move(P)); continue; }
    std::vector<uint32_t> buckets[PART_COUNT];
    for (size_t k = 0; k + 2 < P.idx.size(); k += 3) {
      uint32_t ia = P.idx[k], ib = P.idx[k + 1], ic = P.idx[k + 2];
      Vec3 c = (P.pos[ia] + P.pos[ib] + P.pos[ic]) * (1.f / 3.f);
      float ny = (c.y - out.bmin.y) / H, nz = (c.z - zc) / L; int pid = PART_TORSO;
      if (quad) {
        if (nz < -0.28f) pid = PART_JAW_OR_TAIL;
        else if (ny < 0.48f) pid = (nz >= 0.f) ? PART_LEG_L : PART_LEG_R;
        else if (nz > 0.25f) pid = PART_HEAD;
      } else {
        if (ny < 0.45f) pid = (c.x >= 0.f) ? PART_LEG_L : PART_LEG_R;
        else if (ny >= 0.81f) pid = PART_HEAD;
        else if (std::fabs(c.x) > 0.20f * W) pid = (c.x * wSide > 0.f) ? PART_ARM_R : PART_ARM_L;
      }
      buckets[pid].push_back(ia); buckets[pid].push_back(ib); buckets[pid].push_back(ic);
    }
    for (int pid = 0; pid < PART_COUNT; pid++) {
      if (buckets[pid].empty()) continue;
      Primitive sub; sub.material = P.material; sub.node = P.node; sub.partId = pid; sub.pivot = pivotFor(pid);
      std::vector<int> remap(P.pos.size(), -1);
      for (uint32_t vi : buckets[pid]) {
        if (remap[vi] < 0) {
          remap[vi] = (int)sub.pos.size(); sub.pos.push_back(P.pos[vi]); sub.nrm.push_back(P.nrm[vi]);
          sub.uv.push_back(P.uv[vi * 2]); sub.uv.push_back(P.uv[vi * 2 + 1]);
          if (P.tan.size() >= (vi + 1) * 4) for (int t = 0; t < 4; t++) sub.tan.push_back(P.tan[vi * 4 + t]);
        }
        sub.idx.push_back((uint32_t)remap[vi]);
      }
      rigged.push_back(std::move(sub));
    }
  }
  out.prims = std::move(rigged);
}

bool loadGlb(const std::string& path, Model& out, std::string& err) {
  cgltf_options opt{}; cgltf_data* d = nullptr;
  if (cgltf_parse_file(&opt, path.c_str(), &d) != cgltf_result_success) { err = "cgltf_parse_file failed"; return false; }
  if (cgltf_load_buffers(&opt, d, path.c_str()) != cgltf_result_success) { err = "cgltf_load_buffers failed"; cgltf_free(d); return false; }
  if (cgltf_validate(d) != cgltf_result_success) { err = "cgltf_validate failed"; cgltf_free(d); return false; }
  out.path = path; out.name = path.substr(path.find_last_of("/\\") == std::string::npos ? 0 : path.find_last_of("/\\") + 1);
  out.nodeCount = int(d->nodes_count);
  for (size_t i = 0; i < d->images_count; i++) {
    Texture t; const cgltf_image& im = d->images[i];
    if (im.buffer_view) {
      const uint8_t* p = static_cast<const uint8_t*>(im.buffer_view->buffer->data) + im.buffer_view->offset; int c;
      uint8_t* px = stbi_load_from_memory(p, int(im.buffer_view->size), &t.w, &t.h, &c, 4);
      if (px) { t.rgba.assign(px, px + size_t(t.w) * t.h * 4); stbi_image_free(px); } else { err = "image decode failed"; cgltf_free(d); return false; }
    }
    out.textures.push_back(std::move(t));
  }
  for (size_t i = 0; i < d->materials_count; i++) {
    const cgltf_material& m = d->materials[i]; Material mt; mt.name = m.name ? m.name : "mat";
    if (m.has_pbr_metallic_roughness) {
      auto& pb = m.pbr_metallic_roughness; mt.base = texIndex(d, pb.base_color_texture); mt.mr = texIndex(d, pb.metallic_roughness_texture);
      for (int k = 0; k < 4; k++) mt.baseFactor[k] = pb.base_color_factor[k];
    }
    mt.normal = texIndex(d, m.normal_texture); mt.emissive = texIndex(d, m.emissive_texture);
    for (int k = 0; k < 3; k++) mt.emissiveFactor[k] = m.emissive_factor[k];
    mt.blend = m.alpha_mode == cgltf_alpha_mode_blend; out.materials.push_back(mt);
  }
  for (size_t ni = 0; ni < d->nodes_count; ni++) {
    const cgltf_node& n = d->nodes[ni]; if (!n.mesh) continue;
    Mat4 W; cgltf_node_transform_world(&n, W.data());
    for (size_t pi = 0; pi < n.mesh->primitives_count; pi++) {
      const cgltf_primitive& pr = n.mesh->primitives[pi]; if (pr.type != cgltf_primitive_type_triangles || !pr.indices) continue;
      Primitive P; P.node = n.name ? n.name : ""; P.material = pr.material ? int(pr.material - d->materials) : -1;
      for (size_t ai = 0; ai < pr.attributes_count; ai++) {
        const cgltf_attribute& a = pr.attributes[ai]; size_t cnt = a.data->count, nc = cgltf_num_components(a.data->type);
        std::vector<float> buf(cnt * nc); cgltf_accessor_unpack_floats(a.data, buf.data(), buf.size());
        if (a.type == cgltf_attribute_type_position) for (size_t v = 0; v < cnt; v++) P.pos.push_back(transformPoint(W, {buf[v*3], buf[v*3+1], buf[v*3+2]}));
        else if (a.type == cgltf_attribute_type_normal) for (size_t v = 0; v < cnt; v++) P.nrm.push_back(normalize(transformDir(W, {buf[v*3], buf[v*3+1], buf[v*3+2]})));
        else if (a.type == cgltf_attribute_type_texcoord && a.index == 0) P.uv = buf;
        else if (a.type == cgltf_attribute_type_tangent) { P.tan = buf; for (size_t v = 0; v < cnt; v++) { Vec3 t = normalize(transformDir(W, {buf[v*4], buf[v*4+1], buf[v*4+2]})); P.tan[v*4] = t.x; P.tan[v*4+1] = t.y; P.tan[v*4+2] = t.z; } }
      }
      P.idx.resize(pr.indices->count); for (size_t k = 0; k < P.idx.size(); k++) P.idx[k] = uint32_t(cgltf_accessor_read_index(pr.indices, k));
      if (P.pos.empty() || P.nrm.size() != P.pos.size() || P.uv.size() != P.pos.size() * 2) { err = "primitive missing POSITION/NORMAL/TEXCOORD_0 in node " + P.node; cgltf_free(d); return false; }
      for (auto& v : P.pos) { out.bmin = {std::fmin(out.bmin.x, v.x), std::fmin(out.bmin.y, v.y), std::fmin(out.bmin.z, v.z)}; out.bmax = {std::fmax(out.bmax.x, v.x), std::fmax(out.bmax.y, v.y), std::fmax(out.bmax.z, v.z)}; }
      out.prims.push_back(std::move(P));
    }
  }
  cgltf_free(d); if (out.prims.empty()) { err = "no triangle primitives"; return false; }
  rigCharacterParts(out);
  return true;
}
}  // namespace isekai
