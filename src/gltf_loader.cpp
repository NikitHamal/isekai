#define CGLTF_IMPLEMENTATION
#include "cgltf.h"
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#include <cmath>
#include <isekai/model.h>
namespace isekai {
Vec3 normalize(Vec3 v) { float l = std::sqrt(dot(v, v)); return l > 1e-12f ? v * (1.f / l) : Vec3{0, 1, 0}; }
Vec3 transformPoint(const Mat4& m, Vec3 p) { return {m[0] * p.x + m[4] * p.y + m[8] * p.z + m[12], m[1] * p.x + m[5] * p.y + m[9] * p.z + m[13], m[2] * p.x + m[6] * p.y + m[10] * p.z + m[14]}; }
Vec3 transformDir(const Mat4& m, Vec3 p) { return {m[0] * p.x + m[4] * p.y + m[8] * p.z, m[1] * p.x + m[5] * p.y + m[9] * p.z, m[2] * p.x + m[6] * p.y + m[10] * p.z}; }

static int texIndex(const cgltf_data* d, const cgltf_texture_view& v) { return v.texture ? int(v.texture->image - d->images) : -1; }

bool loadGlb(const std::string& path, Model& out, std::string& err) {
  cgltf_options opt{}; cgltf_data* d = nullptr;
  if (cgltf_parse_file(&opt, path.c_str(), &d) != cgltf_result_success) { err = "cgltf_parse_file failed"; return false; }
  if (cgltf_load_buffers(&opt, d, path.c_str()) != cgltf_result_success) { err = "cgltf_load_buffers failed"; cgltf_free(d); return false; }
  if (cgltf_validate(d) != cgltf_result_success) { err = "cgltf_validate failed"; cgltf_free(d); return false; }
  out.path = path; out.name = path.substr(path.find_last_of("/\\") == std::string::npos ? 0 : path.find_last_of("/\\") + 1);
  out.nodeCount = int(d->nodes_count);
  for (size_t i = 0; i < d->images_count; i++) {  // embedded PNGs in bufferViews
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
  cgltf_free(d); if (out.prims.empty()) { err = "no triangle primitives"; return false; } return true;
}
}  // namespace isekai
