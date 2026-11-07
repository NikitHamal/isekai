// Scene assembly: Valoria Kingdom Frontier instances, skeletal animations, 3 switchable spells, runic circles, curved sword ribbons & sky lightning.
#include <algorithm>
#include "game_world.hpp"
#include "kingdom.hpp"
namespace isekai {
static float enemyHeight(int k) { return k == EK_ORC ? 3.4f : k == EK_WOLF ? 1.7f : 1.3f; }
static Vec3 spellColor(int k) { return k == 1 ? Vec3{.28f, .88f, 1.f} : k == 2 ? Vec3{.88f, .48f, 1.f} : Vec3{1.f, .42f, .14f}; }
Scene GameWorld::buildScene() const {
  Scene s; s.time = time; s.heroYaw = heroYaw; s.camYaw = camYaw; s.hp = std::clamp(hp / 100.f, 0.f, 1.f); s.mana = std::clamp(mana / 100.f, 0.f, 1.f);
  s.casting = castFlash > 0; s.activeSpell = activeSpell; s.focus = hero;
  s.cam.eye = camOverride ? ovEye : camEye; s.cam.target = camOverride ? ovTgt : hero + Vec3{0, 1.55f + yOff, 0}; s.cam.fovDeg = 55;
  auto add = [&](const char* k, Mat4 m, float em = 1.f, Vec3 tint = {1, 1, 1}, bool sway = false, AnimState anim = {}, bool shad = true) {
    Instance i; i.model = M(k); i.M = m; i.emissive = em; i.tint = tint; i.windSway = sway; i.anim = anim; i.castShadow = shad; s.inst.push_back(i);
  };
  { Instance g; g.model = M("terrain"); g.M = mIdent(); g.ground = true; g.castShadow = false; s.inst.push_back(g); }
  if (M("grass")) {
    float swayX = std::sin(time * 2.2f) * 0.04f;
    Instance gr; gr.model = M("grass"); gr.M = mTrans({swayX, 0.f, 0.f}); gr.castShadow = false; gr.windSway = true; s.inst.push_back(gr);
  }
  auto place = [&](Vec3 p, float yaw) { return mMul(mTrans(p), mRotY(yaw)); };
  add("guild", place(guildPos(), kPi / 2)); add("keep", place(keepPos(), kPi)); add("wagon", place(wagonPos(), 0.12f));
  if (M("forge")) add("forge", place(forgePos(), -kPi / 2));
  if (M("tower")) add("tower", place(towerPos(), kPi / 3));
  if (M("tavern")) add("tavern", place(tavernPos(), -kPi / 2));
  { float sx = roadCenterX(2.f) + 3.6f; add("sign", fit(M("sign"), 2.9f, {sx, terrainHeight(sx, 2.f), 2.f}, 0.35f)); }
  { Vec3 w = wagonPos(); float cx = w.x + 3.4f, cz = w.z - 1.f; add("chest", fit(M("chest"), 0.9f, {cx, terrainHeight(cx, cz), cz}, -0.5f)); }
  { AnimState pa; pa.rig = RIG_BIPED; pa.time = time; pa.walkPhase = time * 2.f; add("paladin", fit(M("paladin"), 2.3f, paladinPos(), kPi + 0.25f), 1.f, {1, 1, 1}, false, pa); }
  for (int i = 0; i < 10; i++) {
    float z = -18.f - i * 9.5f, side = (i % 2 ? 1.f : -1.f), x = roadCenterX(z) + side * (17.5f + (i % 3) * 4.5f);
    add("cliff", fit(M("cliff"), 7.5f + (i % 4) * 1.8f, {x, terrainHeight(x, z) - 0.5f, z}, i * 1.1f));
  }
  for (int i = 0; i < 18; i++) {
    float z = 4.f - i * 4.2f, side = (i % 2 ? 1.f : -1.f), dist = 7.8f + (i % 4) * 3.4f + ((i * 7) % 3) * 1.8f;
    float x = roadCenterX(z) + side * dist; if (z > 6.f && side < 0.f && dist < 21.f) x -= 9.f;
    const char* tk = (i % 3 == 0) ? "tree" : "pine"; float h = (i % 3 == 0) ? (8.2f + (i % 4) * 1.1f) : (6.8f + (i % 5) * 0.9f);
    add(tk, fit(M(tk), h, {x, terrainHeight(x, z) - 0.15f, z}, i * 1.7f), 1.f, {1, 1, 1}, true);
  }
  for (int i = 0; i < 16; i++) {
    float z = 5.f - i * 4.5f, side = (i % 2 ? -1.f : 1.f), x = roadCenterX(z) + side * (5.2f + (i % 5) * 2.3f);
    if (z > 6.f && side < 0.f) continue;
    add("boulder", fit(M("boulder"), 1.0f + (i % 4) * 0.45f, {x, terrainHeight(x, z) - 0.18f, z}, i * 2.1f));
  }
  // Hero with hierarchical skeletal animation
  float roll = rollT > 0 ? (1.f - rollT / 0.5f) * 2 * kPi : 0.f, bob = std::fabs(std::sin(runPhase)) * 0.04f; Vec3 hp3 = hero + Vec3{0, yOff + bob, 0};
  Mat4 hm = mMul(mTrans(hp3), mMul(mRotY(heroYaw), mMul(mTrans({0, .9f, 0}), mMul(mRotX(roll), mTrans({0, -.9f, 0}))))); Vec3 ht{1.f, 1 - hurtFlash, 1 - hurtFlash};
  AnimState ha; ha.rig = RIG_HERO; ha.time = time; ha.walkPhase = runPhase; ha.speed = vlen({heroVel.x, 0.f, heroVel.z});
  ha.slashProgress = slashProgress(); ha.combo = combo; ha.slashing = slashT > 0.f;
  ha.castWeight = std::clamp(castFlash / 0.35f, 0.f, 1.f); ha.rollProgress = rollT > 0.f ? 1.f - rollT / 0.5f : 0.f; ha.airborne = !onGround;
  add("hero", hm, 1.f, ht, false, ha);
  // Rotating 3D Runic Circle at the caster's feet while casting
  if (castFlash > 0.f && M("rune")) {
    Vec3 sc = spellColor(activeSpell);
    Mat4 rm = mMul(mTrans({hero.x, hero.y + 0.03f, hero.z}), mMul(mRotY(time * 3.6f), mScale(1.1f)));
    add("rune", rm, 2.2f, sc, false, {}, false);
  }
  std::vector<Light> L; auto flick = [&](float i) { return 1.f + 0.15f * std::sin(time * 13 + i * 2.f) + 0.08f * std::sin(time * 31 + i * 5.f); };
  { Vec3 g = guildPos(); for (int i = 0; i < 3; i++) { Vec3 p = g + Vec3{6.4f, 2.6f, -4.f + i * 4.f}; L.push_back({p, Vec3{3.2f, 1.7f, .6f} * flick(i), 9.f}); s.fx.push_back({p, .55f, {1, .6f, .2f}, .5f * flick(i)}); } }
  { Vec3 k = keepPos(); for (int i = 0; i < 2; i++) { Vec3 p = k + Vec3{i ? 6.f : -6.f, 4.5f, 8.8f}; L.push_back({p, Vec3{3.4f, 1.8f, .6f} * flick(i + 4.f), 12.f}); s.fx.push_back({p, .7f, {1, .6f, .2f}, .55f * flick(i + 4.f)}); } }
  for (auto& e : enemies) {
    if (!e.alive && e.deadT > 0.9f) continue;
    float sc = e.alive ? 1.f : 1.f - e.deadT / 0.9f; const char* key = e.kind == EK_ORC ? "orc" : e.kind == EK_WOLF ? "wolf" : "goblin";
    AnimState ea; ea.rig = (e.kind == EK_WOLF) ? RIG_QUADRUPED : RIG_BIPED; ea.time = time; ea.walkPhase = e.walkPhase; ea.speed = e.moveSpeed;
    ea.attackProgress = (e.atkCd > 0.f && e.atkCd < 0.65f) ? (1.f - e.atkCd / 0.65f) : 0.f;
    Vec3 etint = (e.freezeT > 0.f) ? Vec3{.45f, .88f, 1.35f} : Vec3{1.f + e.flash * 2, 1.f + e.flash, 1.f + e.flash};
    add(key, fit(M(key), enemyHeight(e.kind) * std::max(sc, .05f), e.pos, e.yaw), 1.f, etint, false, ea);
    if (e.alive) { Vec3 eye = e.pos + transformDir(mRotY(e.yaw), {0, enemyHeight(e.kind) * (e.kind == EK_WOLF ? .62f : .88f), enemyHeight(e.kind) * (e.kind == EK_WOLF ? .62f : .15f)}); Vec3 c = e.kind == EK_WOLF ? Vec3{.5f, .8f, 1.f} : Vec3{1, .5f, .1f}; s.fx.push_back({eye, .16f, c, .8f}); }
  }
  for (auto& b : bolts) {
    float f = flick(b.pos.x); Vec3 bc = spellColor(b.kind);
    L.insert(L.begin(), {b.pos, bc * (6.5f * f), 16.f});
    s.fx.push_back({b.pos, b.kind == 1 ? 0.65f : 1.05f, bc, .82f});
    s.fx.push_back({b.pos, .42f, {1.f, .95f, .8f}, .95f});
  }
  for (auto& f : flashes) {
    float k = std::clamp(f.t / 0.65f, 0.f, 1.f); Vec3 fc = spellColor(f.kind);
    L.insert(L.begin(), {f.pos + Vec3{0, .6f, 0}, fc * (12.f * k), 22.f});
    s.fx.push_back({f.pos, 2.8f * (1.2f - k * .4f), fc, .55f * k});
    if (M("rune")) {
      float gy0 = terrainHeight(f.pos.x, f.pos.z) + 0.04f;
      Mat4 rm = mMul(mTrans({f.pos.x, gy0, f.pos.z}), mMul(mRotY(-time * 4.2f), mScale(1.4f + (1.f - k) * 0.8f)));
      add("rune", rm, 2.4f, fc, false, {}, false);
    }
    if (f.kind == 2) {  // Aether Judgment sky-to-ground jagged lightning bolt
      Vec3 prev = f.pos + Vec3{0.f, 14.5f, 0.f};
      for (int seg = 1; seg <= 10; seg++) {
        float u = float(seg) / 10.f, jx = (seg < 10) ? std::sin(seg * 17.3f + time * 35.f) * 0.42f : 0.f, jz = (seg < 10) ? std::cos(seg * 23.1f + time * 31.f) * 0.42f : 0.f;
        Vec3 cur = f.pos + Vec3{jx, (1.f - u) * 14.5f, jz}, w{0.16f, 0.f, 0.f};
        s.ribbons.push_back({prev - w, prev + w, cur - w, cur + w, {.88f, .68f, 1.f}, k * 0.92f, k * 0.92f});
        prev = cur;
      }
    }
  }
  if (castFlash > 0.f) {
    Vec3 hp = handPos(), sc = spellColor(activeSpell);
    L.insert(L.begin(), {hp, sc * (4.f * (castFlash / .35f)), 7.f});
    s.fx.push_back({hp, .42f, sc, (castFlash / .35f) * 0.7f});
  }
  for (auto& p : parts) s.fx.push_back({p.p, p.size * 1.6f, p.col, std::min(1.f, p.life * 1.6f)});
  if (slashT > 0.f && slashRibbon.size() >= 2) {
    for (size_t i = 0; i + 1 < slashRibbon.size(); i++) {
      float a0 = std::clamp(slashRibbon[i].t / 0.30f, 0.f, 1.f) * (float(i + 1) / slashRibbon.size());
      float a1 = std::clamp(slashRibbon[i + 1].t / 0.30f, 0.f, 1.f) * (float(i + 2) / slashRibbon.size());
      s.ribbons.push_back({slashRibbon[i].base, slashRibbon[i].tip, slashRibbon[i + 1].base, slashRibbon[i + 1].tip, {.55f, .85f, 1.f}, a0 * 0.78f, a1 * 0.85f});
    }
  }
  std::sort(L.begin(), L.end(), [&](const Light& a, const Light& b) { float da = vlen(a.pos - hero) - a.radius * .5f, db = vlen(b.pos - hero) - b.radius * .5f; return da < db; }); if (L.size() > 8) L.resize(8); s.lights = L; return s; }
void GameWorld::stageShowcase() {
  float rx = roadCenterX(12.f); hero = {rx, terrainHeight(rx, 12.f), 12.f}; heroYaw = kPi + 0.18f; Input in; in.focused = true; camYaw = kPi; camInit = false;
  for (auto& e : enemies) e.alive = false; enemies.clear();
  spawn(EK_WOLF, {rx + 2.3f, 0, 7.4f}); spawn(EK_GOBLIN, {rx - 2.1f, 0, 6.4f}); spawn(EK_ORC, {rx + 1.6f, 0, 2.2f});
  for (int i = 0; i < 4; i++) update(in, 0.016f, 1.78f);
  slashDur = 0.38f; slashT = 0.22f; combo = 0; castFlash = 0.28f; activeSpell = 0; runPhase = 1.15f; heroVel = {0.f, 0.f, -5.2f};
  slashRibbon.clear();
  for (int i = 0; i < 9; i++) {
    float t = float(i) / 8.f, ang = heroYaw + lerpf(0.95f, -0.55f, t);
    Mat4 R = mMul(mRotY(ang), mRotX(1.38f)); Vec3 sd = transformDir(R, {0, 1, 0}), hp0 = handPos();
    slashRibbon.push_back({hp0 + sd * 0.28f, hp0 + sd * 1.42f, 0.12f + 0.18f * t});
  }
  enemies[0].pos = {rx + 2.3f, terrainHeight(rx + 2.3f, 7.4f), 7.4f}; enemies[0].walkPhase = 0.9f; enemies[0].moveSpeed = 5.8f; enemies[0].atkCd = 0.32f;
  enemies[1].pos = {rx - 2.1f, terrainHeight(rx - 2.1f, 6.4f), 6.4f}; enemies[1].walkPhase = 1.4f; enemies[1].moveSpeed = 3.4f; enemies[1].atkCd = 0.25f; enemies[1].freezeT = 2.0f;
  enemies[2].pos = {rx + 1.6f, terrainHeight(rx + 1.6f, 2.2f), 2.2f}; enemies[2].walkPhase = 0.8f; enemies[2].moveSpeed = 2.6f; enemies[2].atkCd = 0.30f;
  for (auto& e : enemies) e.vel = {}; enemies[0].yaw = -0.35f; enemies[1].yaw = 0.28f; enemies[2].yaw = -0.45f;
  bolts.clear(); bolts.push_back({{rx + 0.7f, 1.35f, 8.8f}, {2.2f, -.5f, -26.f}, 1.f, 0});
  flashes.clear(); flashes.push_back({enemies[2].pos, 0.52f, 2});
  for (int i = 0; i < 8; i++) { Vec3 p = Vec3{rx + 0.7f, 1.35f, 8.8f} + Vec3{2.2f, -.5f, -26.f} * (i * .012f); parts.push_back({p, {0, .3f, 0}, .5f, 1.f, .1f, {1.f, .45f, .12f}}); }
  camOverride = true; ovEye = {rx + 4.2f, 2.3f, 19.5f}; ovTgt = {rx - 1.5f, 2.3f, 4.f}; }
}  // namespace isekai
