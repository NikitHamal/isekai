// Scene assembly: Valoria Kingdom Frontier instances, forest trees, mossy boulders, wind-swaying 3D grass, dynamic lights and glow FX.
#include <algorithm>
#include "game_world.hpp"
#include "kingdom.hpp"
namespace isekai {
static float enemyHeight(int k) { return k == EK_ORC ? 3.4f : k == EK_WOLF ? 1.7f : 1.3f; }
Scene GameWorld::buildScene() const {
  Scene s; s.time = time; s.heroYaw = heroYaw; s.camYaw = camYaw; s.hp = std::clamp(hp / 100.f, 0.f, 1.f); s.mana = std::clamp(mana / 100.f, 0.f, 1.f); s.casting = castFlash > 0; s.focus = hero;
  s.cam.eye = camOverride ? ovEye : camEye; s.cam.target = camOverride ? ovTgt : hero + Vec3{0, 1.55f + yOff, 0}; s.cam.fovDeg = 55;
  auto add = [&](const char* k, Mat4 m, float em = 1.f, Vec3 tint = {1, 1, 1}, bool sway = false) {
    Instance i; i.model = M(k); i.M = m; i.emissive = em; i.tint = tint; i.windSway = sway; s.inst.push_back(i);
  };
  { Instance g; g.model = M("terrain"); g.M = mIdent(); g.ground = true; g.castShadow = false; s.inst.push_back(g); }
  if (M("grass")) {
    float swayX = std::sin(time * 2.2f) * 0.04f;
    Instance gr; gr.model = M("grass"); gr.M = mTrans({swayX, 0.f, 0.f}); gr.castShadow = false; gr.windSway = true; s.inst.push_back(gr);
  }
  auto place = [&](Vec3 p, float yaw) { return mMul(mTrans(p), mRotY(yaw)); };
  add("guild", place(guildPos(), kPi / 2)); add("keep", place(keepPos(), kPi)); add("wagon", place(wagonPos(), 0.12f));
  { float sx = roadCenterX(2.f) + 3.6f; add("sign", fit(M("sign"), 2.9f, {sx, terrainHeight(sx, 2.f), 2.f}, 0.35f)); }
  { Vec3 w = wagonPos(); float cx = w.x + 3.4f, cz = w.z - 1.f; add("chest", fit(M("chest"), 0.9f, {cx, terrainHeight(cx, cz), cz}, -0.5f)); }
  add("paladin", fit(M("paladin"), 2.3f, paladinPos(), kPi + 0.25f));
  // Sculpted mountain crags flanking the frontier valley
  for (int i = 0; i < 10; i++) {
    float z = -18.f - i * 9.5f, side = (i % 2 ? 1.f : -1.f), x = roadCenterX(z) + side * (17.5f + (i % 3) * 4.5f);
    add("cliff", fit(M("cliff"), 7.5f + (i % 4) * 1.8f, {x, terrainHeight(x, z) - 0.5f, z}, i * 1.1f));
  }
  // 3D Oak Canopy Trees & Frontier Pine Trees across the hills and road verges
  for (int i = 0; i < 18; i++) {
    float z = 4.f - i * 4.2f, side = (i % 2 ? 1.f : -1.f);
    float dist = 7.8f + (i % 4) * 3.4f + ((i * 7) % 3) * 1.8f;
    float x = roadCenterX(z) + side * dist;
    if (z > 6.f && side < 0.f && dist < 21.f) x -= 9.f;  // keep clear of guildhall courtyard
    float y = terrainHeight(x, z) - 0.15f;
    const char* tk = (i % 3 == 0) ? "tree" : "pine";
    float h = (i % 3 == 0) ? (8.2f + (i % 4) * 1.1f) : (6.8f + (i % 5) * 0.9f);
    add(tk, fit(M(tk), h, {x, y, z}, i * 1.7f), 1.f, {1, 1, 1}, true);
  }
  // Mossy Boulders nestled along road verges and foothills
  for (int i = 0; i < 16; i++) {
    float z = 5.f - i * 4.5f, side = (i % 2 ? -1.f : 1.f);
    float x = roadCenterX(z) + side * (5.2f + (i % 5) * 2.3f);
    if (z > 6.f && side < 0.f) continue;
    float y = terrainHeight(x, z) - 0.18f;
    add("boulder", fit(M("boulder"), 1.0f + (i % 4) * 0.45f, {x, y, z}, i * 2.1f));
  }
  // Hero + independently swinging Aetherblade
  float roll = rollT > 0 ? (1.f - rollT / 0.5f) * 2 * kPi : 0.f, bob = std::fabs(std::sin(runPhase)) * 0.04f; Vec3 hp3 = hero + Vec3{0, yOff + bob, 0};
  Mat4 hm = mMul(mTrans(hp3), mMul(mRotY(heroYaw), mMul(mTrans({0, .9f, 0}), mMul(mRotX(roll), mTrans({0, -.9f, 0}))))); Vec3 ht{1.f, 1 - hurtFlash, 1 - hurtFlash};
  add("hero", hm, 1.f, ht);
  if (models.count("hero_sword_part")) { Vec3 hl{-0.34f, 1.08f, 0.22f}; Mat4 sm = rollT > 0 ? hm : mMul(mTrans(handPos()), mMul(swordRot(), mTrans(hl * -1.f))); add("hero_sword_part", sm, 1.f, ht); }
  std::vector<Light> L; auto flick = [&](float i) { return 1.f + 0.15f * std::sin(time * 13 + i * 2.f) + 0.08f * std::sin(time * 31 + i * 5.f); };
  { Vec3 g = guildPos(); for (int i = 0; i < 3; i++) { Vec3 p = g + Vec3{6.4f, 2.6f, -4.f + i * 4.f}; L.push_back({p, Vec3{3.2f, 1.7f, .6f} * flick(i), 9.f}); s.fx.push_back({p, .55f, {1, .6f, .2f}, .5f * flick(i)}); } }
  { Vec3 k = keepPos(); for (int i = 0; i < 2; i++) { Vec3 p = k + Vec3{i ? 6.f : -6.f, 4.5f, 8.8f}; L.push_back({p, Vec3{3.4f, 1.8f, .6f} * flick(i + 4.f), 12.f}); s.fx.push_back({p, .7f, {1, .6f, .2f}, .55f * flick(i + 4.f)}); } }
  // Enemies
  for (auto& e : enemies) { if (!e.alive && e.deadT > 0.9f) continue; float sc = e.alive ? 1.f : 1.f - e.deadT / 0.9f; const char* key = e.kind == EK_ORC ? "orc" : e.kind == EK_WOLF ? "wolf" : "goblin";
    add(key, fit(M(key), enemyHeight(e.kind) * std::max(sc, .05f), e.pos, e.yaw), 1.f, {1.f + e.flash * 2, 1.f + e.flash, 1.f + e.flash});
    if (e.alive) { Vec3 eye = e.pos + transformDir(mRotY(e.yaw), {0, enemyHeight(e.kind) * (e.kind == EK_WOLF ? .62f : .88f), enemyHeight(e.kind) * (e.kind == EK_WOLF ? .62f : .15f)}); Vec3 c = e.kind == EK_WOLF ? Vec3{.5f, .8f, 1.f} : Vec3{1, .5f, .1f}; s.fx.push_back({eye, .16f, c, .8f}); } }
  // Spell bolts & impact flashes
  for (auto& b : bolts) { float f = flick(b.pos.x); L.insert(L.begin(), {b.pos, Vec3{7.f, 2.6f, .6f} * f, 18.f}); s.fx.push_back({b.pos, 1.1f, {1.f, .45f, .12f}, .8f}); s.fx.push_back({b.pos, .5f, {1.f, .9f, .6f}, 1.f}); s.fx.push_back({b.pos, 2.0f, {.5f, .6f, 1.f}, .22f}); }
  for (auto& f : flashes) { float k = f.t / 0.6f; L.insert(L.begin(), {f.pos + Vec3{0, .6f, 0}, Vec3{12.f, 4.f, .8f} * k, 22.f}); s.fx.push_back({f.pos, 3.2f * (1.2f - k * .4f), {1.f, .5f, .15f}, .6f * k}); }
  // Hand spell charge ONLY while actively casting
  if (castFlash > 0.f) { Vec3 hp = handPos(); L.insert(L.begin(), {hp, Vec3{4.f, 1.4f, .5f} * (castFlash / .3f), 7.f}); s.fx.push_back({hp, .45f, {1.f, .4f, .15f}, (castFlash / .3f) * 0.75f}); }
  for (auto& p : parts) s.fx.push_back({p.p, p.size * 1.6f, p.col, std::min(1.f, p.life * 1.6f)});
  // Sword slash arc ONLY renders while slashT > 0
  if (slashT > 0.f) {
    for (auto& t : trail) { float a = std::clamp(t.second / .35f, 0.f, 1.f); s.fx.push_back({t.first, .18f * (a + .25f), {.75f, .88f, 1.f}, a * .45f}); }
  }
  std::sort(L.begin(), L.end(), [&](const Light& a, const Light& b) { float da = vlen(a.pos - hero) - a.radius * .5f, db = vlen(b.pos - hero) - b.radius * .5f; return da < db; }); if (L.size() > 8) L.resize(8); s.lights = L; return s; }
void GameWorld::stageShowcase() {
  float rx = roadCenterX(12.f); hero = {rx, terrainHeight(rx, 12.f), 12.f}; heroYaw = kPi + 0.18f; Input in; in.focused = true; camYaw = kPi; camInit = false;
  for (auto& e : enemies) e.alive = false; enemies.clear();
  spawn(EK_WOLF, {rx + 2.6f, 0, 6.8f}); spawn(EK_GOBLIN, {rx - 2.4f, 0, 7.6f}); spawn(EK_ORC, {rx + 7.5f, 0, 1.5f});
  for (int i = 0; i < 4; i++) update(in, 0.016f, 1.78f);
  slashT = 0.f; trail.clear(); castFlash = 0.f;
  enemies[0].pos = {rx + 2.6f, terrainHeight(rx + 2.6f, 6.8f), 6.8f}; enemies[1].pos = {rx - 2.4f, terrainHeight(rx - 2.4f, 7.6f), 7.6f}; enemies[2].pos = {rx + 7.5f, terrainHeight(rx + 7.5f, 1.5f), 1.5f};
  for (auto& e : enemies) { e.vel = {}; e.atkCd = 99.f; } enemies[0].yaw = 0.25f; enemies[1].yaw = -0.2f; enemies[2].yaw = -0.35f;
  bolts.clear(); bolts.push_back({{rx + 0.8f, 1.35f, 9.2f}, {2.4f, -.5f, -26.f}, 1.f});
  for (int i = 0; i < 8; i++) { Vec3 p = Vec3{rx + 0.8f, 1.35f, 9.2f} + Vec3{2.4f, -.5f, -26.f} * (i * .012f); parts.push_back({p, {0, .3f, 0}, .5f, 1.f, .1f, {1.f, .45f, .12f}}); }
  camOverride = true; ovEye = {rx + 4.2f, 2.3f, 19.5f}; ovTgt = {rx - 1.5f, 2.3f, 4.f}; }
}  // namespace isekai
