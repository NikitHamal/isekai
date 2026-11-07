#include "game_world.hpp"
#include <algorithm>
#include <filesystem>
namespace isekai {
static const struct { const char* key; const char* path; } kAssets[] = {
  {"arch", "environment/env_ancient_root_archway"}, {"heart", "props/prp_crimson_heart_container"}, {"sign", "props/prp_wooden_wayfinder_signpost"},
  {"lantern", "props/prp_hanging_acorn_amber_lantern"}, {"chest", "props/prp_ornate_treasure_chest"}, {"sword", "weapons/wpn_aetherblade_longsword"},
  {"hero", "characters/chr_hero_kaelen_adventurer"}, {"fairy", "characters/chr_ally_lumina_spirit_fairy"}, {"shield", "weapons/wpn_royal_crest_heater_shield"},
  {"cliff", "environment/env_mossy_forest_cliff_modular"}, {"goblin", "monsters/mon_forest_goblin_raider"}, {"slime", "monsters/mon_emerald_mana_slime_king"}};
GameWorld::GameWorld(const std::string& root) {
  loadAll(root); hero.y = groundY; pickups = {{{0.f, -0.5f, -0.2f}}, {{-2.2f, -0.5f, -8.f}}, {{2.6f, -0.5f, -13.f}}}; for (size_t i = 0; i < pickups.size(); i++) pickups[i].phase = i * 2.1f;
  spawnGoblin({-3.f, -0.5f, -7.5f}); spawnGoblin({4.f, -0.5f, -12.f}); spawnGoblin({-1.f, -0.5f, -17.f});
  hint = "Walk through the Ancient Root Archway"; hintT = 8; }
void GameWorld::loadAll(const std::string& root) {
  namespace fs = std::filesystem; found = fs::exists(root + "/assets/models");
  for (auto& a : kAssets) { std::string p = root + "/assets/models/" + a.path + ".glb"; auto m = std::make_unique<Model>(); std::string err;
    if (fs::exists(p) && loadGlb(p, *m, err)) { loaded++; models[a.key] = std::move(m); } }
  auto ph = [&](const char* k, Vec3 half, Vec3 c, Vec3 col) { if (!models.count(k)) models[k] = std::make_unique<Model>(makeBoxModel(half, c, col)); };
  ph("hero", {.3f, .85f, .2f}, {0, .85f, 0}, {.1f, .6f, .3f}); ph("fairy", {.12f, .12f, .12f}, {0, 0, 0}, {.5f, 1.f, 1.f}); ph("goblin", {.35f, .6f, .3f}, {0, .6f, 0}, {.35f, .5f, .15f});
  ph("shield", {.3f, .4f, .05f}, {0, 0, 0}, {.6f, .5f, .2f}); ph("cliff", {4.f, 3.f, 6.f}, {0, 3.f, 0}, {.4f, .5f, .2f}); ph("slime", {.7f, .6f, .7f}, {0, .6f, 0}, {.2f, .9f, .5f});
  models["post"] = std::make_unique<Model>(makeBoxModel({.08f, 1.3f, .08f}, {0, 1.3f, 0}, {.25f, .15f, .08f})); models["beam"] = std::make_unique<Model>(makeBoxModel({.5f, .06f, .06f}, {.5f, 0, 0}, {.25f, .15f, .08f}));
  models["ground"] = std::make_unique<Model>(makeGroundModel(120.f, -0.5f)); }
Mat4 GameWorld::fit(const Model* m, float height, Vec3 pos, float yaw, float pitch) const {
  float ext = std::max(m->bmax.y - m->bmin.y, 0.01f), s = height / ext; Vec3 c = (m->bmin + m->bmax) * 0.5f;
  return mMul(mTrans(pos), mMul(mRotY(yaw), mMul(mRotX(pitch), mMul(mScale(s), mTrans({-c.x, -m->bmin.y, -c.z}))))); }
void GameWorld::burst(Vec3 p, int n, Vec3 col, float speed, float size) {
  for (int i = 0; i < n; i++) { float a = (rand() % 1000) / 1000.f * 2 * kPi, e = ((rand() % 1000) / 1000.f - .2f) * 1.6f, sp = speed * (.4f + (rand() % 1000) / 1000.f);
    parts.push_back({p, {std::cos(a) * std::cos(e) * sp, std::sin(e) * sp + speed * .4f, std::sin(a) * std::cos(e) * sp}, 0.7f + (rand() % 500) / 1000.f, 1.f, size, col}); } }
void GameWorld::spawnGoblin(Vec3 p) { Goblin g; g.pos = g.home = p; g.patrolT = (rand() % 100) / 10.f; goblins.push_back(g); }
Vec3 GameWorld::handPos() const { Mat4 R = mRotY(heroYaw); return hero + transformDir(R, {0.42f, 1.05f, 0.25f}); }
Vec3 GameWorld::swordTip() const {
  float k = slashT > 0 ? 1.f - slashT / 0.45f : 0.f; float sw = slashT > 0 ? slashDir * lerpf(1.25f, -1.25f, k) : 0.f, pitch = slashT > 0 ? 1.45f : 0.35f;
  return handPos() + transformDir(mMul(mRotY(heroYaw + sw), mRotX(pitch)), {0, 1.15f, 0}); }
bool GameWorld::nearChest() const { return vlen(hero - chestPos) < 2.6f; }
void GameWorld::update(const Input& in, float dt, float aspect) {
  dt = std::min(dt, 0.05f); time += dt; wantFullscreenToggle = in.pressed[KEY_F11]; wantMouseFree = in.pressed[KEY_ESC];
  heroUpdate(in, dt); enemiesUpdate(dt); cameraUpdate(in, dt, aspect);
  for (auto& p : pickups) { p.phase += dt; if (!p.taken && vlen(p.pos - Vec3{hero.x, p.pos.y, hero.z}) < 1.3f) { p.taken = true; burst(p.pos + Vec3{0, .9f, 0}, 60, {1, .8f, .25f}, 4.5f, .14f);
      if (hearts < maxHearts) hearts++; else if (!p.fromDrop && maxHearts < 8) { maxHearts++; hearts = maxHearts; } hint = "Heart Container! Max hearts up"; hintT = 3; } }
  for (auto& p : parts) { p.life -= dt; p.v.y -= 5.f * dt; p.p = p.p + p.v * dt; } parts.erase(std::remove_if(parts.begin(), parts.end(), [](const Particle& p) { return p.life <= 0; }), parts.end());
  for (auto& t : trail) t.second -= dt; trail.erase(std::remove_if(trail.begin(), trail.end(), [](auto& t) { return t.second <= 0; }), trail.end());
  if (chestOpen) { chestAnim = std::min(1.f, chestAnim + dt * 2); chestGlow = std::max(0.f, chestGlow - dt * .3f); } hintT -= dt; if (hintT < 0) hint.clear();
  if (in.pressed['E'] && nearChest() && !chestOpen) { chestOpen = true; chestGlow = 1; burst(chestPos + Vec3{0, .8f, 0}, 80, {1, .85f, .3f}, 5.f); pickups.push_back({chestPos + Vec3{0, -0.f, 1.6f}, false, 0, true}); hint = "The chest bursts open!"; hintT = 3; }
}
}  // namespace isekai
