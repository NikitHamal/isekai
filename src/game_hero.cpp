// Hero controller, spring-arm camera and goblin AI.
#include <algorithm>
#include "game_world.hpp"
namespace isekai {
void GameWorld::startSlash(const Input&) {
  slashT = 0.45f; slashDir = -slashDir; slashId += 1; float best = 5.f; for (auto& g : goblins) if (g.alive) { float d = vlen(g.pos - hero); if (d < best) { best = d; heroYaw = std::atan2(g.pos.x - hero.x, g.pos.z - hero.z); } } }
void GameWorld::heroUpdate(const Input& in, float dt) {
  Vec3 f{std::sin(camYaw), 0, std::cos(camYaw)}, r{-f.z, 0, f.x}; float ix = (in.down['D'] ? 1.f : 0.f) - (in.down['A'] ? 1.f : 0.f), iy = (in.down['W'] ? 1.f : 0.f) - (in.down['S'] ? 1.f : 0.f);
  Vec3 dir = r * ix + f * iy; float l = vlen(dir); if (l > 1e-3f) dir = dir * (1.f / l); bool sprint = in.down[KEY_SHIFT]; float sp = (sprint ? 7.2f : 4.4f) * (slashT > 0 ? 0.55f : 1.f);
  Vec3 tv = dir * (l > 1e-3f ? sp : 0.f); float k = 1.f - std::exp(-12.f * dt); heroVel.x = lerpf(heroVel.x, tv.x, k); heroVel.z = lerpf(heroVel.z, tv.z, k);
  Vec3 prev = hero; hero.x += heroVel.x * dt; hero.z += heroVel.z * dt;
  if (l > 1e-3f && slashT <= 0) heroYaw += wrapPi(std::atan2(dir.x, dir.z) - heroYaw) * (1.f - std::exp(-14.f * dt));
  if (std::fabs(hero.z) < 2.8f && std::fabs(hero.x) > 3.4f && std::fabs(hero.x) < 6.4f) { if (std::fabs(prev.x) <= 3.4f) hero.x = prev.x; else hero.z = prev.z; }
  hero.x = std::clamp(hero.x, -8.5f, 8.5f); hero.z = std::clamp(hero.z, -30.f, 16.f);
  if (onGround && in.pressed[KEY_SPACE]) { vy = 7.6f; onGround = false; } if (!onGround) { vy -= 20.f * dt; y += vy * dt; if (y <= 0) { y = 0; vy = 0; onGround = true; burst(hero, 6, {.8f, .7f, .5f}, 1.2f, .08f); } }
  hero.y = groundY + y; runPhase += dt * (l > 1e-3f ? (sprint ? 14.f : 9.f) : 0.f);
  if ((in.lmbPressed && in.focused) || in.pressed['F'] || in.pressed['J']) if (slashT <= 0.12f) startSlash(in);
  if (slashT > 0) { slashT -= dt; trail.push_back({swordTip(), 0.38f});
    if (!chestOpen && vlen(hero - chestPos) < 3.2f && slashT < 0.3f) { chestOpen = true; chestGlow = 1; burst(chestPos + Vec3{0, .8f, 0}, 80, {1, .85f, .3f}, 5.f); pickups.push_back({chestPos + Vec3{0, 0.f, 1.6f}, false, 0, true}); hint = "The chest bursts open!"; hintT = 3; } }
  invuln = std::max(0.f, invuln - dt); hurtFlash = std::max(0.f, hurtFlash - dt);
  if (hearts <= 0) { hearts = maxHearts; hero = {0, groundY, 11}; heroVel = {}; hint = "Defeated... the fairy revives you"; hintT = 3; }
  if (in.pressed['H']) { hearts = maxHearts; }
}
void GameWorld::cameraUpdate(const Input& in, float dt, float aspect) {
  (void)aspect; bool eFree = !(nearChest() && !chestOpen); float ro = (in.down[KEY_LEFT] ? 1.f : 0.f) - (in.down[KEY_RIGHT] ? 1.f : 0.f) + (in.down['Q'] ? 1.f : 0.f) - (eFree && in.down['E'] ? 1.f : 0.f);
  camYaw += ro * 2.2f * dt - in.mdx * 0.0028f; camPitch = std::clamp(camPitch + ((in.down[KEY_UP] ? -1.f : 0.f) + (in.down[KEY_DOWN] ? 1.f : 0.f)) * 1.2f * dt + in.mdy * 0.0025f, -0.15f, 1.25f);
  Vec3 tgt = hero + Vec3{0, 1.45f, 0}; Vec3 want = tgt + Vec3{-std::sin(camYaw) * std::cos(camPitch), std::sin(camPitch), -std::cos(camYaw) * std::cos(camPitch)} * camDist;
  want.y = std::max(want.y, groundY + 0.35f); if (!camInit) { camEye = want; camInit = true; } camEye = camEye + (want - camEye) * (1.f - std::exp(-9.f * dt));
}
void GameWorld::enemiesUpdate(float dt) {
  for (auto& g : goblins) {
    if (!g.alive) { g.deadT += dt; continue; } g.flash = std::max(0.f, g.flash - dt); g.atkCd = std::max(0.f, g.atkCd - dt); g.patrolT += dt; Vec3 to = hero - g.pos; to.y = 0; float d = vlen(to), speed = 0; Vec3 mv{};
    if (d < 9.f && d > 1.2f) { mv = to * (1.f / d); speed = 3.1f; } else if (d >= 9.f) { Vec3 pt = g.home + Vec3{std::sin(g.patrolT * .45f) * 3.2f, 0, std::cos(g.patrolT * .6f) * 2.4f}; Vec3 pd = pt - g.pos; pd.y = 0; float pl = vlen(pd); if (pl > .1f) { mv = pd * (1.f / pl); speed = 1.4f; } }
    if (speed > 0) g.yaw += wrapPi(std::atan2(mv.x, mv.z) - g.yaw) * (1.f - std::exp(-8.f * dt)); else if (d <= 1.2f) g.yaw = std::atan2(to.x, to.z);
    g.pos = g.pos + (mv * speed + g.vel) * dt; g.vel = g.vel * std::exp(-7.f * dt); g.pos.x = std::clamp(g.pos.x, -8.f, 8.f);
    if (d < 1.5f && g.atkCd <= 0) { g.atkCd = 1.4f; if (invuln <= 0) { hearts--; invuln = 1.3f; hurtFlash = 0.4f; heroVel = to * 8.f; burst(hero + Vec3{0, 1.1f, 0}, 25, {1, .2f, .2f}, 3.f); } }
    if (slashT > 0.08f && slashT < 0.36f && g.hitSwing != slashId) { Vec3 fw{std::sin(heroYaw), 0, std::cos(heroYaw)}, dd = g.pos - hero; dd.y = 0; float dl = vlen(dd);
      if (dl < 2.7f && (dl < 0.8f || dot(dd * (1.f / dl), fw) > 0.1f)) { g.hitSwing = slashId; g.hp -= 1; g.flash = 0.3f; g.vel = dd * (11.f / std::max(dl, .3f)); burst(g.pos + Vec3{0, 1, 0}, 30, {1, .6f, .15f}, 4.f);
        if (g.hp <= 0) { g.alive = false; kills++; pickups.push_back({g.pos, false, 0, true}); burst(g.pos + Vec3{0, .8f, 0}, 60, {.6f, 1, .4f}, 4.5f); hint = "Goblin defeated - it dropped a heart!"; hintT = 3; } } } }
}
}  // namespace isekai
