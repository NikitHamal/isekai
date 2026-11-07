// Hero controller (sword combo, Crimson Flare spell, dodge-roll), spring-arm camera, enemy AI.
#include <algorithm>
#include "game_world.hpp"
#include "kingdom.hpp"
namespace isekai {
static bool gPrevRmb = false;
struct Stats { float speed, detect, range, dmg, cd, height, radius, knock; };
static Stats statsFor(int k) { static const Stats s[3] = {{3.4f, 13.f, 1.5f, 8.f, 1.3f, 1.3f, .45f, 1.f}, {2.6f, 17.f, 2.7f, 22.f, 2.1f, 2.9f, .9f, .35f}, {6.4f, 22.f, 1.8f, 12.f, 1.1f, 1.6f, .6f, .8f}}; return s[k]; }
float GameWorld::slashProgress() const { return slashT > 0 ? 1.f - slashT / slashDur : 0.f; }
Vec3 GameWorld::handPos() const { return hero + Vec3{0, yOff, 0} + transformDir(mRotY(heroYaw), {-0.34f, 1.08f, 0.22f}); }
Mat4 GameWorld::swordRot() const {   // blade rests pointing down-forward; slashes sweep it (combo 0/1 horizontal, 2 overhead)
  float k = slashProgress(), yaw = heroYaw, pitch = 2.5f;
  if (slashT > 0) { float e = k * k * (3 - 2 * k); if (combo == 2) pitch = lerpf(-0.9f, 1.75f, e); else { float dir = combo == 0 ? 1.f : -1.f; yaw += dir * lerpf(1.3f, -1.3f, e); pitch = 1.45f; } }
  else if (castFlash > 0) pitch = 1.2f;
  return mMul(mRotY(yaw), mRotX(pitch)); }
Vec3 GameWorld::swordDir() const { return transformDir(swordRot(), {0, 1, 0}); }
void GameWorld::startSlash() {
  if (rollT > 0) return; if (slashT > 0) { queuedSlash = true; return; }
  combo = comboWindow > 0 ? (combo + 1) % 3 : 0; slashDur = combo == 2 ? 0.62f : 0.38f; slashT = slashDur; slashId += 1; comboWindow = 0; queuedSlash = false;
  float best = 6.f; for (auto& e : enemies) if (e.alive) { float d = vlen(e.pos - hero); if (d < best) { best = d; heroYaw = std::atan2(e.pos.x - hero.x, e.pos.z - hero.z); } }
  Vec3 fw{std::sin(heroYaw), 0, std::cos(heroYaw)}; heroVel = fw * (combo == 2 ? 7.f : 4.5f); }
void GameWorld::castSpell() {
  if (mana < 25.f || castCd > 0 || rollT > 0) return; mana -= 25.f; castCd = 0.55f; castFlash = 0.3f; heroYaw = camYaw;
  Vec3 fw{std::sin(camYaw), 0, std::cos(camYaw)}, o = handPos() + fw * 0.7f + Vec3{0, 0.1f, 0}, dir = fw; float best = 28.f;
  for (auto& e : enemies) if (e.alive) { Vec3 d = e.pos - hero; d.y = 0; float l = vlen(d); if (l < best && l > 0.1f && dot(d * (1.f / l), fw) > 0.82f) { best = l; Vec3 t = e.pos + Vec3{0, statsFor(e.kind).height * .5f, 0}; dir = normalize(t - o); } }
  bolts.push_back({o, dir * 28.f, 2.0f}); burst(o, 18, {1.f, .5f, .15f}, 2.5f, .1f); }
void GameWorld::damage(Enemy& e, float dmg, Vec3 from, float knock) {
  Vec3 d = e.pos - from; d.y = 0; float l = std::max(vlen(d), .2f); e.hp -= dmg; e.flash = 0.3f; e.vel = d * (knock * statsFor(e.kind).knock / l);
  burst(e.pos + Vec3{0, statsFor(e.kind).height * .5f, 0}, 26, {1.f, .45f, .15f}, 4.f);
  if (e.hp <= 0 && e.alive) { e.alive = false; burst(e.pos + Vec3{0, .8f, 0}, 60, {.7f, .25f, .9f}, 4.5f); } }
void GameWorld::boltsUpdate(float dt) {
  for (auto& b : bolts) {
    b.life -= dt; b.pos = b.pos + b.vel * dt; bool hit = b.life <= 0 || b.pos.y < terrainHeight(b.pos.x, b.pos.z) + 0.15f;
    for (auto& e : enemies) if (e.alive && vlen(b.pos - (e.pos + Vec3{0, statsFor(e.kind).height * .5f, 0})) < statsFor(e.kind).radius + .7f) hit = true;
    for (const Footprint& f : obstacles()) if (std::fabs(b.pos.x - f.cx) < f.hx && std::fabs(b.pos.z - f.cz) < f.hz && b.pos.y < 18.f) hit = true;
    parts.push_back({b.pos, {((rand() % 100) - 50) / 60.f, ((rand() % 100) - 20) / 70.f, ((rand() % 100) - 50) / 60.f}, .5f, 1.f, .09f, {1.f, .4f + (rand() % 40) / 100.f, .1f}});
    if (hit) { b.life = -1; flashes.push_back({b.pos, 0.6f}); burst(b.pos, 90, {1.f, .4f, .08f}, 7.f, .16f); burst(b.pos, 40, {.5f, .6f, 1.f}, 5.f, .12f);
      for (auto& e : enemies) if (e.alive && vlen(e.pos + Vec3{0, 1, 0} - b.pos) < 3.6f) damage(e, 3.f, b.pos - Vec3{0, 0, 0}, 11.f); } }
  bolts.erase(std::remove_if(bolts.begin(), bolts.end(), [](const Bolt& b) { return b.life < 0; }), bolts.end()); }
void GameWorld::heroUpdate(const Input& in, float dt) {
  Vec3 f{std::sin(camYaw), 0, std::cos(camYaw)}, r{-f.z, 0, f.x};
  float ix = (in.down['D'] ? 1.f : 0.f) - (in.down['A'] ? 1.f : 0.f), iy = (in.down['W'] ? 1.f : 0.f) - (in.down['S'] ? 1.f : 0.f);
  Vec3 dir = r * ix + f * iy; float l = vlen(dir); if (l > 1e-3f) dir = dir * (1.f / l);
  bool sprint = in.down[KEY_SHIFT]; float busy = (slashT > 0 ? 0.45f : 1.f) * (castFlash > 0 ? 0.6f : 1.f), sp = (sprint ? 7.4f : 4.4f) * busy;
  castCd = std::max(0.f, castCd - dt); castFlash = std::max(0.f, castFlash - dt); rollCd = std::max(0.f, rollCd - dt);
  if (rollT > 0) { rollT -= dt; heroVel = rollDir * 9.5f; if (rollT <= 0) rollCd = 0.25f; }
  else { Vec3 tv = dir * (l > 1e-3f ? sp : 0.f); float k = 1.f - std::exp(-12.f * dt); heroVel.x = lerpf(heroVel.x, tv.x, k); heroVel.z = lerpf(heroVel.z, tv.z, k); }
  hero.x += heroVel.x * dt; hero.z += heroVel.z * dt; pushOut(hero.x, hero.z, 0.45f); hero.x = std::clamp(hero.x, -95.f, 95.f); hero.z = std::clamp(hero.z, -95.f, 95.f);
  if (rollT > 0) heroYaw = std::atan2(rollDir.x, rollDir.z);
  else if (castFlash > 0) heroYaw += wrapPi(camYaw - heroYaw) * (1.f - std::exp(-20.f * dt));
  else if (l > 1e-3f && slashT <= 0) heroYaw += wrapPi(std::atan2(dir.x, dir.z) - heroYaw) * (1.f - std::exp(-14.f * dt));
  float gnd = terrainHeight(hero.x, hero.z);
  if (in.pressed[KEY_SPACE] && onGround && rollCd <= 0 && slashT <= 0) { if (l > 1e-3f) { rollT = 0.5f; rollDir = dir; invuln = std::max(invuln, 0.55f); } else { vy = 7.2f; onGround = false; } }
  if (!onGround) { vy -= 20.f * dt; yOff += vy * dt; if (yOff <= 0) { yOff = 0; vy = 0; onGround = true; } }
  hero.y = gnd; runPhase += dt * (l > 1e-3f ? (sprint ? 14.f : 9.f) : 0.f);
  bool rmb = in.rmb && in.focused; if (((rmb && !gPrevRmb) || in.pressed['Q'])) castSpell(); gPrevRmb = rmb;
  if ((in.lmbPressed && in.focused) || in.pressed['F']) startSlash();
  if (slashT > 0) { slashT -= dt; Vec3 tip = handPos() + swordDir() * 1.35f; trail.push_back({tip, 0.35f}); trail.push_back({handPos() + swordDir() * 0.9f, 0.3f});
    float k = slashProgress(); if (k > 0.2f && k < 0.8f) for (auto& e : enemies) if (e.alive && e.hitId != slashId) { Vec3 fw = swordDir(), dd = e.pos - hero; dd.y = 0; float dl = vlen(dd), reach = (combo == 2 ? 3.9f : 3.3f) + statsFor(e.kind).radius;
      Vec3 face{std::sin(heroYaw), 0, std::cos(heroYaw)}; (void)fw; if (dl < reach && (dl < 1.f || dot(dd * (1.f / dl), face) > (combo == 2 ? -0.1f : 0.15f))) { e.hitId = slashId; damage(e, combo == 2 ? 2.f : 1.f, hero, combo == 2 ? 14.f : 8.f); } }
    if (slashT <= 0) { comboWindow = 0.55f; if (queuedSlash) startSlash(); } }
  else comboWindow = std::max(0.f, comboWindow - dt);
  invuln = std::max(0.f, invuln - dt); hurtFlash = std::max(0.f, hurtFlash - dt);
  if (hp <= 0) { hp = 100; mana = 100; hero = {roadCenterX(12.f), 0, 12.f}; heroVel = {}; } }
void GameWorld::cameraUpdate(const Input& in, float dt) {
  float ro = (in.down[KEY_LEFT] ? 1.f : 0.f) - (in.down[KEY_RIGHT] ? 1.f : 0.f);
  camYaw += ro * 2.2f * dt - in.mdx * 0.0028f; camPitch = std::clamp(camPitch + ((in.down[KEY_UP] ? -1.f : 0.f) + (in.down[KEY_DOWN] ? 1.f : 0.f)) * 1.2f * dt + in.mdy * 0.0025f, -0.1f, 1.2f);
  Vec3 tgt = hero + Vec3{0, 1.55f + yOff, 0}, want = tgt + Vec3{-std::sin(camYaw) * std::cos(camPitch), std::sin(camPitch), -std::cos(camYaw) * std::cos(camPitch)} * camDist;
  want.y = std::max(want.y, terrainHeight(want.x, want.z) + 0.5f); if (!camInit) { camEye = want; camInit = true; } camEye = camEye + (want - camEye) * (1.f - std::exp(-9.f * dt)); }
void GameWorld::enemiesUpdate(float dt) {
  for (auto& e : enemies) {
    if (!e.alive) { e.deadT += dt; continue; } Stats s = statsFor(e.kind); e.flash = std::max(0.f, e.flash - dt); e.atkCd = std::max(0.f, e.atkCd - dt); e.patrolT += dt;
    Vec3 to = hero - e.pos; to.y = 0; float d = vlen(to), speed = 0; Vec3 mv{};
    if (d < s.detect && d > s.range * 0.8f) { mv = to * (1.f / d); speed = s.speed; }
    else if (d >= s.detect) { Vec3 pt = e.home + Vec3{std::sin(e.patrolT * .45f) * 3.2f, 0, std::cos(e.patrolT * .6f) * 2.4f}, pd = pt - e.pos; pd.y = 0; float pl = vlen(pd); if (pl > .1f) { mv = pd * (1.f / pl); speed = s.speed * .35f; } }
    if (speed > 0) e.yaw += wrapPi(std::atan2(mv.x, mv.z) - e.yaw) * (1.f - std::exp(-8.f * dt)); else if (d <= s.range) e.yaw = std::atan2(to.x, to.z);
    e.pos = e.pos + (mv * speed + e.vel) * dt; e.vel = e.vel * std::exp(-6.f * dt); pushOut(e.pos.x, e.pos.z, s.radius); e.pos.y = terrainHeight(e.pos.x, e.pos.z);
    if (d < s.range && e.atkCd <= 0) { e.atkCd = s.cd; if (invuln <= 0) { hp -= s.dmg; invuln = 0.9f; hurtFlash = 0.4f; heroVel = to * (7.f / std::max(d, .3f)); burst(hero + Vec3{0, 1.1f, 0}, 25, {.9f, .1f, .12f}, 3.f); } } } }
}  // namespace isekai
