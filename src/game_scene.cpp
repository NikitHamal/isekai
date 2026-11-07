// Scene assembly: turns world state into renderer-agnostic instances, lights, glow sprites and minimap dots.
#include <algorithm>
#include "game_world.hpp"
namespace isekai {
Scene GameWorld::buildScene() const {
  Scene s; s.time = time; s.hearts = hearts; s.maxHearts = maxHearts; s.kills = kills; s.heroYaw = heroYaw; s.camYaw = camYaw;
  s.cam.eye = camOverride ? ovEye : camEye; s.cam.target = camOverride ? ovTgt : hero + Vec3{0, 1.4f, 0}; s.cam.fovDeg = 55;
  auto add = [&](const char* k, Mat4 m, float em = 1.f, Vec3 tint = {1, 1, 1}) { Instance i; i.model = M(k); i.M = m; i.emissive = em; i.tint = tint; s.inst.push_back(i); };
  { Instance g; g.model = M("ground"); g.M = mIdent(); g.ground = true; s.inst.push_back(g); }
  add("arch", mIdent());
  const float cx[6] = {-11.5f, 11.5f, -11.5f, 11.5f, -11.5f, 11.5f}, cz[6] = {12.f, 12.f, -4.f, -4.f, -20.f, -20.f};
  for (int i = 0; i < 6; i++) add("cliff", fit(M("cliff"), 9.f, {cx[i], -0.5f, cz[i]}, (i % 2 ? -1.f : 1.f) * kPi / 2));
  add("sign", fit(M("sign"), 2.9f, signPos, 0.35f));
  float lift = chestOpen ? 1.f + 0.04f * std::sin(chestAnim * kPi) : 1.f; add("chest", fit(M("chest"), 1.0f * lift, chestPos, 0.6f), 1.f + chestGlow * 2.5f, {1 + chestGlow * .4f, 1 + chestGlow * .3f, 1});
  std::vector<Light> L; auto flick = [&](int i) { return 1.f + 0.18f * std::sin(time * 13 + i * 2.f) + 0.1f * std::sin(time * 31 + i * 5.f); };
  const Vec3 archL[3] = {{-2.9f, 2.9f, 0.2f}, {0.f, 3.2f, 0.2f}, {2.9f, 2.9f, 0.2f}}; for (int i = 0; i < 3; i++) { L.push_back({archL[i], Vec3{3.2f, 1.7f, .55f} * flick(i), 9.f}); s.fx.push_back({archL[i], .45f, {1, .6f, .2f}, 0.55f * flick(i)}); }
  for (int i = 0; i < 2; i++) { float sx = i ? 3.f : -3.f; Vec3 post{sx, -0.5f, 9.5f}; add("post", mTrans(post)); add("beam", mMul(mTrans({sx, 2.1f, 9.5f}), mRotY(i ? kPi : 0.f)));
    float lx = sx + (i ? -0.8f : 0.8f); add("lantern", fit(M("lantern"), 0.75f, {lx, 1.35f, 9.5f}, 0)); Vec3 lp{lx, 1.7f, 9.5f}; L.push_back({lp, Vec3{3.f, 1.6f, .5f} * flick(i + 3), 8.f}); s.fx.push_back({lp, .4f, {1, .6f, .2f}, .6f * flick(i + 3)}); }
  if (chestGlow > 0.01f) L.push_back({chestPos + Vec3{0, 1, 0}, Vec3{3, 2.4f, .8f} * chestGlow, 7.f});
  Vec3 hp = hero + Vec3{0, std::fabs(std::sin(runPhase)) * 0.05f, 0}; add("hero", fit(M("hero"), 1.8f, hp, heroYaw), 1.f, {1.f, 1 - hurtFlash, 1 - hurtFlash});
  float k = slashT > 0 ? 1.f - slashT / 0.45f : 0.f, sw = slashT > 0 ? slashDir * lerpf(1.25f, -1.25f, k) : 0.f, pitch = slashT > 0 ? 1.45f : 0.35f;
  add("sword", mMul(mTrans(handPos()), mMul(mRotY(heroYaw + sw), mMul(mRotX(pitch), mScale(0.85f)))), 1.6f);
  add("shield", fit(M("shield"), 0.9f, hero + transformDir(mRotY(heroYaw), {0, 0.85f, -0.3f}), heroYaw + kPi));
  float ft = time * 1.2f; Vec3 fp = hero + transformDir(mRotY(heroYaw), {std::sin(ft) * 1.1f, 2.0f + 0.2f * std::sin(ft * 2), std::sin(2 * ft) * 0.6f - 0.2f});
  add("fairy", fit(M("fairy"), 0.5f, fp - Vec3{0, .25f, 0}, camYaw + kPi + 0.4f * std::sin(time * 3)), 2.f); L.insert(L.begin(), {fp, Vec3{.5f, 1.4f, 1.5f} * (1.6f + .3f * std::sin(time * 9)), 8.f});
  s.fx.push_back({fp, .7f, {.5f, 1.f, 1.f}, .8f}); s.fx.push_back({fp, 1.1f, {1.f, .85f, .4f}, .25f});
  for (int i = 1; i <= 7; i++) { float tt = ft - i * 0.14f; Vec3 q = hero + transformDir(mRotY(heroYaw), {std::sin(tt) * 1.1f, 2.0f + 0.2f * std::sin(tt * 2), std::sin(2 * tt) * 0.6f - 0.2f}); s.fx.push_back({q, .22f * (1.f - i / 8.f), {.6f, 1.f, .9f}, .7f * (1.f - i / 8.f)}); }
  for (auto& p : pickups) if (!p.taken) { Vec3 q = p.pos + Vec3{0, 0.9f + 0.15f * std::sin(p.phase * 2.f), 0}; add("heart", fit(M("heart"), 0.7f, q - Vec3{0, .35f, 0}, p.phase * 1.5f), 1.4f);
    s.fx.push_back({q + Vec3{0, .1f, 0}, .5f, {1, .25f, .3f}, .45f}); L.push_back({q, Vec3{2.2f, .35f, .4f}, 4.5f}); s.dots.push_back({p.pos.x, p.pos.z, 2}); }
  for (auto& g : goblins) { if (!g.alive && g.deadT > 0.6f) continue; float sc = g.alive ? 1.f : 1.f - g.deadT / 0.6f; add("goblin", fit(M("goblin"), 1.35f * std::max(sc, 0.05f), g.pos, g.yaw), 1.f, {1.f + g.flash * 2, 1.f + g.flash, 1.f + g.flash});
    if (g.alive) { Vec3 e = g.pos + transformDir(mRotY(g.yaw), {0, 1.05f, 0.18f}); s.fx.push_back({e, .16f, {1, .65f, .1f}, .9f}); s.dots.push_back({g.pos.x, g.pos.z, 3}); } }
  { Vec3 sp{6.5f, -0.5f, -4.5f}; float w = std::sin(time * 3.f); add("slime", fit(M("slime"), 1.5f * (1.f + .06f * w), sp, time * 0.2f), 1.6f); s.fx.push_back({sp + Vec3{0, .8f, 0}, .8f, {.3f, 1.f, .6f}, .35f}); L.push_back({sp + Vec3{0, .9f, 0}, Vec3{.4f, 1.6f, .8f}, 5.f}); }
  for (auto& p : parts) s.fx.push_back({p.p, p.size * 1.6f, p.col, std::min(1.f, p.life * 1.6f)});
  for (auto& t : trail) s.fx.push_back({t.first, .3f * (t.second / .38f + .3f), {.6f, 1.f, 1.f}, t.second / .38f * 0.9f}), s.fx.push_back({t.first, .55f, {1.f, .85f, .4f}, t.second / .38f * 0.25f});
  if (!chestOpen) s.dots.push_back({chestPos.x, chestPos.z, 4}); s.dots.push_back({signPos.x, signPos.z, 5}); s.dots.push_back({0, 0, 1}); s.dots.push_back({hero.x, hero.z, 0});
  std::sort(L.begin() + 1, L.end(), [&](const Light& a, const Light& b) { return vlen(a.pos - hero) < vlen(b.pos - hero); }); if (L.size() > 8) L.resize(8); s.lights = L;
  s.hint = hint; if (s.hint.empty() && nearChest() && !chestOpen) s.hint = "Press E or slash to open the chest"; return s; }
void GameWorld::stageShowcase() {
  hero = {0.9f, groundY, 8.0f}; heroYaw = kPi + 0.55f; goblins[0].pos = {-1.3f, groundY, 6.2f}; goblins[0].yaw = 0.9f; hearts = 3; Input in; in.lmbPressed = true; in.focused = true;
  for (int i = 0; i < 12; i++) { update(in, 0.016f, 1.78f); in.lmbPressed = false; heroYaw = kPi + 0.55f; }
  goblins[0].hp = 3; camOverride = true; ovEye = {1.4f, 2.9f, 13.2f}; ovTgt = {-0.2f, 1.7f, 3.5f}; }
}  // namespace isekai
