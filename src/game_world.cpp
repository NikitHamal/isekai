#include "game_world.hpp"
#include <algorithm>
#include <filesystem>
#include "terrain.hpp"
namespace isekai {
static const struct { const char* key; const char* path; } kAssets[] = {
  {"hero", "characters/chr_hero_kaelen_adventurer"}, {"paladin", "characters/chr_ally_garrick_royal_paladin"},
  {"guild", "buildings/bld_valoria_adventurer_guild"}, {"keep", "buildings/bld_royal_citadel_keep"}, {"wagon", "vehicles/veh_merchant_covered_wagon"},
  {"orc", "monsters/mon_orc_warlord_berserker"}, {"wolf", "monsters/mon_shadow_direwolf_alpha"}, {"goblin", "monsters/mon_forest_goblin_raider"},
  {"slime", "monsters/mon_emerald_mana_slime_king"}, {"cliff", "environment/env_mossy_forest_cliff_modular"},
  {"tree", "environment/env_sacred_world_tree_canopy"}, {"sign", "props/prp_wooden_wayfinder_signpost"},
  {"chest", "props/prp_ornate_treasure_chest"}, {"sword", "weapons/wpn_aetherblade_longsword"}, {"shield", "weapons/wpn_royal_crest_heater_shield"}};
static float gy(float x, float z) { return terrainHeight(x, z); }
GameWorld::GameWorld(const std::string& root) {
  loadAll(root); hero = {roadCenterX(12.f), gy(roadCenterX(12.f), 12.f), 12.f};
  for (int i = 0; i < 4; i++) { float z = -14.f - i * 7.f; spawn(EK_GOBLIN, {roadCenterX(z) + (i % 2 ? 5.f : -5.f), 0, z}); }
  spawn(EK_ORC, {roadCenterX(-30.f) - 7.f, 0, -30.f}); spawn(EK_ORC, {roadCenterX(-46.f) + 6.f, 0, -46.f});
  spawn(EK_WOLF, {roadCenterX(-22.f) + 9.f, 0, -22.f}); spawn(EK_WOLF, {roadCenterX(-38.f) - 10.f, 0, -38.f}); spawn(EK_WOLF, {roadCenterX(-54.f) + 3.f, 0, -54.f}); }
void GameWorld::loadAll(const std::string& root) {
  namespace fs = std::filesystem; found = fs::exists(root + "/assets/models");
  for (auto& a : kAssets) { std::string p = root + "/assets/models/" + a.path + ".glb"; auto m = std::make_unique<Model>(); std::string err;
    if (fs::exists(p) && loadGlb(p, *m, err)) { loaded++; models[a.key] = std::move(m); } }
  auto ph = [&](const char* k, Vec3 half, Vec3 c, Vec3 col) { if (!models.count(k)) models[k] = std::make_unique<Model>(makeBoxModel(half, c, col)); };
  ph("hero", {.3f, .9f, .2f}, {0, .9f, 0}, {.12f, .14f, .3f}); ph("paladin", {.4f, 1.f, .3f}, {0, 1.f, 0}, {.6f, .6f, .65f}); ph("guild", {7.5f, 5.f, 5.5f}, {0, 5.f, 0}, {.5f, .42f, .32f});
  ph("keep", {18.f, 12.f, 8.f}, {0, 12.f, 0}, {.5f, .5f, .48f}); ph("wagon", {1.1f, 1.3f, 2.2f}, {0, 1.3f, 0}, {.45f, .33f, .2f}); ph("orc", {.7f, 1.4f, .5f}, {0, 1.4f, 0}, {.3f, .4f, .2f});
  ph("wolf", {.5f, .65f, 1.f}, {0, .65f, 0}, {.12f, .12f, .15f}); ph("goblin", {.35f, .6f, .3f}, {0, .6f, 0}, {.35f, .5f, .15f}); ph("cliff", {4.f, 3.f, 6.f}, {0, 3.f, 0}, {.4f, .45f, .35f});
  ph("tree", {2.5f, 4.5f, 2.5f}, {0, 4.5f, 0}, {.18f, .42f, .12f});
  ph("slime", {.7f, .6f, .7f}, {0, .6f, 0}, {.2f, .9f, .5f}); ph("sign", {.4f, 1.3f, .1f}, {0, 1.3f, 0}, {.3f, .2f, .1f}); ph("chest", {.5f, .35f, .35f}, {0, .35f, 0}, {.4f, .25f, .1f});
  models["terrain"] = std::make_unique<Model>(makeTerrainModel(110.f, 1.0f));
  models["pine"] = std::make_unique<Model>(makePineTreeModel());
  models["boulder"] = std::make_unique<Model>(makeMossyBoulderModel());
  models["grass"] = std::make_unique<Model>(makeGrassFieldModel());
  models["rune"] = std::make_unique<Model>(makeRuneCircleModel()); }
Mat4 GameWorld::fit(const Model* m, float height, Vec3 pos, float yaw) const {
  float ext = std::max(m->bmax.y - m->bmin.y, 0.01f), s = height / ext; Vec3 c = (m->bmin + m->bmax) * 0.5f;
  return mMul(mTrans(pos), mMul(mRotY(yaw), mMul(mScale(s), mTrans({-c.x, -m->bmin.y, -c.z})))); }
void GameWorld::burst(Vec3 p, int n, Vec3 col, float speed, float size) {
  for (int i = 0; i < n; i++) { float a = (rand() % 1000) / 1000.f * 2 * kPi, e = ((rand() % 1000) / 1000.f - .2f) * 1.6f, sp = speed * (.4f + (rand() % 1000) / 1000.f);
    parts.push_back({p, {std::cos(a) * std::cos(e) * sp, std::sin(e) * sp + speed * .4f, std::sin(a) * std::cos(e) * sp}, 0.6f + (rand() % 500) / 1000.f, 1.f, size, col}); } }
void GameWorld::spawn(int kind, Vec3 p) {
  Enemy e; e.kind = kind; p.y = gy(p.x, p.z); e.pos = e.home = p; e.patrolT = (rand() % 100) / 10.f; e.hp = e.maxHp = kind == EK_ORC ? 9.f : kind == EK_WOLF ? 4.f : 3.f; enemies.push_back(e); }
void GameWorld::update(const Input& in, float dt, float) {
  dt = std::min(dt, 0.05f); time += dt;
  cameraUpdate(in, dt);
  for (auto& p : parts) { p.life -= dt; p.v.y -= 5.f * dt; p.p = p.p + p.v * dt; } parts.erase(std::remove_if(parts.begin(), parts.end(), [](const Particle& p) { return p.life <= 0; }), parts.end());
  for (auto& f : flashes) f.t -= dt; flashes.erase(std::remove_if(flashes.begin(), flashes.end(), [](const Flash& f) { return f.t <= 0; }), flashes.end());
  if (hitStop > 0.f) { hitStop = std::max(0.f, hitStop - dt); return; }
  heroUpdate(in, dt); enemiesUpdate(dt); boltsUpdate(dt);
  if (slashT <= 0.f) { trail.clear(); slashRibbon.clear(); }
  else {
    for (auto& t : trail) t.second -= dt;
    trail.erase(std::remove_if(trail.begin(), trail.end(), [](auto& t) { return t.second <= 0; }), trail.end());
    for (auto& s : slashRibbon) s.t -= dt;
    slashRibbon.erase(std::remove_if(slashRibbon.begin(), slashRibbon.end(), [](const SlashPt& s) { return s.t <= 0; }), slashRibbon.end());
  }
  mana = std::min(100.f, mana + dt * 6.f); }
}  // namespace isekai
