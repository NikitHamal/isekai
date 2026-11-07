// Hero controller (3-hit sword combo, 3 switchable spells, ribbon trail, hit-stop, camera shake), spring-arm camera & enemy AI.
#include <algorithm>
#include "game_world.hpp"
#include "kingdom.hpp"
namespace isekai {
static bool gPrevRmb = false;
struct Stats { float speed, detect, range, dmg, cd, height, radius, knock; };
static Stats statsFor(int k) { static const Stats s[3] = {{3.4f, 13.f, 1.5f, 8.f, 1.3f, 1.3f, .45f, 1.f}, {2.6f, 17.f, 2.7f, 22.f, 2.1f, 2.9f, .9f, .35f}, {6.4f, 22.f, 1.8f, 12.f, 1.1f, 1.6f, .6f, .8f}}; return s[k]; }
bool GameWorld::tryMove(float nx, float nz) { if (!coll.bodyFits(nx, nz, hero.y, 0.38f)) return false; hero.x = nx; hero.z = nz; return true; }
void GameWorld::moveEntity(Vec3& p, Vec3 d, float r) {
  if (coll.bodyFits(p.x + d.x, p.z, p.y, r)) p.x += d.x; if (coll.bodyFits(p.x, p.z + d.z, p.y, r)) p.z += d.z;
  float g = coll.groundBelow(p.x, p.z, p.y, r, 0.6f); p.y = g > -1e8f ? g : terrainHeight(p.x, p.z); }
float GameWorld::slashProgress() const { return slashT > 0 ? 1.f - slashT / slashDur : 0.f; }
Vec3 GameWorld::handPos() const { return hero + Vec3{0, yOff, 0} + transformDir(mRotY(heroYaw), {-0.34f, 1.08f, 0.22f}); }
Mat4 GameWorld::swordRot() const {
  float k = slashProgress(), yaw = heroYaw, pitch = 2.5f;
  if (slashT > 0) { float e = k * k * (3 - 2 * k); if (combo == 2) pitch = lerpf(-0.9f, 1.75f, e); else { float dir = combo == 0 ? 1.f : -1.f; yaw += dir * lerpf(1.3f, -1.3f, e); pitch = 1.45f; } }
  else if (castFlash > 0) pitch = 1.2f;
  return mMul(mRotY(yaw), mRotX(pitch)); }
Vec3 GameWorld::swordDir() const { return transformDir(swordRot(), {0, 1, 0}); }
void GameWorld::startSlash() {
  if (rollT > 0) return; if (slashT > 0) { queuedSlash = true; return; }
  combo = comboWindow > 0 ? (combo + 1) % 3 : 0; slashDur = combo == 2 ? 0.62f : 0.38f; slashT = slashDur; slashId += 1; comboWindow = 0; queuedSlash = false;
  slashRibbon.clear();
  float best = 6.f; for (auto& e : enemies) if (e.alive) { float d = vlen(e.pos - hero); if (d < best) { best = d; heroYaw = std::atan2(e.pos.x - hero.x, e.pos.z - hero.z); } }
  Vec3 fw{std::sin(heroYaw), 0, std::cos(heroYaw)}; heroVel = fw * (combo == 2 ? 7.f : 4.5f); }
void GameWorld::castSpell() {
  if (mana < 22.f || castCd > 0 || rollT > 0) return;
  mana -= 22.f; castCd = 0.52f; castFlash = 0.35f; heroYaw = camYaw;
  Vec3 fw{std::sin(camYaw), 0, std::cos(camYaw)}, o = handPos() + fw * 0.7f + Vec3{0, 0.1f, 0}, dir = fw;
  float best = 28.f; Vec3 bestPos = hero + fw * 11.f; bestPos.y = terrainHeight(bestPos.x, bestPos.z);
  for (auto& e : enemies) if (e.alive) {
    Vec3 d = e.pos - hero; d.y = 0; float l = vlen(d);
    if (l < best && l > 0.1f && dot(d * (1.f / l), fw) > 0.78f) {
      best = l; bestPos = e.pos; Vec3 t = e.pos + Vec3{0, statsFor(e.kind).height * .5f, 0}; dir = normalize(t - o);
    }
  }
  if (activeSpell == 0) {  // Spell 1: Crimson Flare (Fireball + ember trail + knockback)
    bolts.push_back({o, dir * 28.f, 2.0f, 0});
    burst(o, 22, {1.f, .48f, .14f}, 2.8f, .11f);
  } else if (activeSpell == 1) {  // Spell 2: Glacial Fang (Fan of 5 crystalline ice lances + freeze/slow)
    for (int i = -2; i <= 2; i++) {
      Vec3 idir = normalize(transformDir(mRotY(i * 0.085f), dir));
      bolts.push_back({o + Vec3{0, 0.05f, 0}, idir * 30.f, 1.6f, 1});
    }
    burst(o, 26, {.3f, .88f, 1.f}, 3.2f, .10f);
  } else {  // Spell 3: Aether Judgment (Arcane ground circle + sky-to-ground lightning bolt + shockwave)
    flashes.push_back({bestPos, 0.65f, 2});
    camShake = std::max(camShake, 0.32f);
    burst(bestPos + Vec3{0, 0.4f, 0}, 75, {.85f, .52f, 1.f}, 7.5f, .15f);
    burst(bestPos + Vec3{0, 0.8f, 0}, 45, {1.f, .92f, .45f}, 6.0f, .13f);
    for (auto& e : enemies) if (e.alive && vlen(e.pos - bestPos) < 4.5f) damage(e, 4.2f, bestPos, 13.f);
  }
}
void GameWorld::damage(Enemy& e, float dmg, Vec3 from, float knock) {
  Vec3 d = e.pos - from; d.y = 0; float l = std::max(vlen(d), .2f); e.hp -= dmg; e.flash = 0.3f; e.vel = d * (knock * statsFor(e.kind).knock / l);
  Vec3 hc = e.pos + Vec3{0, statsFor(e.kind).height * .5f, 0};
  burst(hc, 28, {1.f, .86f, .38f}, 5.2f, .11f);  // metallic hit sparks
  burst(hc, 16, {.75f, .92f, 1.f}, 4.5f, .09f);
  hitStop = std::max(hitStop, combo == 2 ? 0.042f : 0.025f);
  camShake = std::max(camShake, combo == 2 ? 0.30f : 0.16f);
  if (e.hp <= 0 && e.alive) { e.alive = false; burst(e.pos + Vec3{0, .8f, 0}, 60, {.7f, .25f, .9f}, 4.5f); } }
void GameWorld::boltsUpdate(float dt) {
  for (auto& b : bolts) {
    b.life -= dt; b.pos = b.pos + b.vel * dt; bool hit = b.life <= 0 || b.pos.y < terrainHeight(b.pos.x, b.pos.z) + 0.15f;
    for (auto& e : enemies) if (e.alive && vlen(b.pos - (e.pos + Vec3{0, statsFor(e.kind).height * .5f, 0})) < statsFor(e.kind).radius + .7f) hit = true;
    if (coll.blockedPoint(b.pos)) hit = true;
    Vec3 tc = (b.kind == 1) ? Vec3{.35f, .88f, 1.f} : Vec3{1.f, .4f + (rand() % 40) / 100.f, .1f};
    parts.push_back({b.pos, {((rand() % 100) - 50) / 60.f, ((rand() % 100) - 20) / 70.f, ((rand() % 100) - 50) / 60.f}, .45f, 1.f, .09f, tc});
    if (hit) {
      b.life = -1; flashes.push_back({b.pos, 0.6f, b.kind}); camShake = std::max(camShake, 0.22f);
      if (b.kind == 1) {
        burst(b.pos, 55, {.35f, .90f, 1.f}, 6.2f, .14f); burst(b.pos, 25, {.85f, .96f, 1.f}, 4.5f, .11f);
        for (auto& e : enemies) if (e.alive && vlen(e.pos + Vec3{0, 1, 0} - b.pos) < 3.4f) { e.freezeT = 3.0f; damage(e, 1.8f, b.pos, 5.f); }
      } else {
        burst(b.pos, 90, {1.f, .4f, .08f}, 7.f, .16f); burst(b.pos, 40, {.5f, .6f, 1.f}, 5.f, .12f);
        for (auto& e : enemies) if (e.alive && vlen(e.pos + Vec3{0, 1, 0} - b.pos) < 3.6f) damage(e, 3.f, b.pos, 11.f);
      }
    }
  }
  bolts.erase(std::remove_if(bolts.begin(), bolts.end(), [](const Bolt& b) { return b.life < 0; }), bolts.end()); }
void GameWorld::heroUpdate(const Input& in, float dt) {
  if (in.pressed['1']) activeSpell = 0;
  if (in.pressed['2']) activeSpell = 1;
  if (in.pressed['3']) activeSpell = 2;
  if (in.wheel != 0) activeSpell = (activeSpell + (in.wheel > 0 ? 1 : 2)) % 3;
  Vec3 f{std::sin(camYaw), 0, std::cos(camYaw)}, r{-f.z, 0, f.x};
  float ix = (in.down['D'] ? 1.f : 0.f) - (in.down['A'] ? 1.f : 0.f), iy = (in.down['W'] ? 1.f : 0.f) - (in.down['S'] ? 1.f : 0.f);
  Vec3 dir = r * ix + f * iy; float l = vlen(dir); if (l > 1e-3f) dir = dir * (1.f / l);
  bool sprint = in.down[KEY_SHIFT]; float busy = (slashT > 0 ? 0.45f : 1.f) * (castFlash > 0 ? 0.6f : 1.f), sp = (sprint ? 7.4f : 4.4f) * busy;
  castCd = std::max(0.f, castCd - dt); castFlash = std::max(0.f, castFlash - dt); rollCd = std::max(0.f, rollCd - dt);
  if (rollT > 0) { rollT -= dt; heroVel = rollDir * 9.5f; if (rollT <= 0) rollCd = 0.25f; }
  else { Vec3 tv = dir * (l > 1e-3f ? sp : 0.f); float k = 1.f - std::exp(-12.f * dt); heroVel.x = lerpf(heroVel.x, tv.x, k); heroVel.z = lerpf(heroVel.z, tv.z, k); }
  { float ox = hero.x, oz = hero.z; bool bx = !tryMove(hero.x + heroVel.x * dt, hero.z), bz = !tryMove(hero.x, hero.z + heroVel.z * dt);
    if (bx) heroVel.x *= 0.2f; if (bz) heroVel.z *= 0.2f;
    if ((bx || bz) && !onGround && vy < 4.f && l > 1e-3f) {   // ledge mantle: climb onto rocks / crates / carts you jump into
      Vec3 pr = hero + dir * 0.62f; float ledge = coll.floorAt(pr.x, pr.z, hero.y + 1.35f);
      if (ledge > hero.y + 0.3f && coll.bodyFits(pr.x, pr.z, ledge, 0.34f)) { hero.x = pr.x; hero.z = pr.z; hero.y = ledge; vy = 0; onGround = true; heroVel = dir * 2.f; burst(hero + Vec3{0, .1f, 0}, 6, {.7f, .65f, .55f}, 1.5f, .07f); } }
    (void)ox; (void)oz; }
  hero.x = std::clamp(hero.x, -95.f, 95.f); hero.z = std::clamp(hero.z, -95.f, 95.f);
  if (rollT > 0) heroYaw = std::atan2(rollDir.x, rollDir.z);
  else if (castFlash > 0) heroYaw += wrapPi(camYaw - heroYaw) * (1.f - std::exp(-20.f * dt));
  else if (l > 1e-3f && slashT <= 0) heroYaw += wrapPi(std::atan2(dir.x, dir.z) - heroYaw) * (1.f - std::exp(-14.f * dt));
  float gnd = coll.groundBelow(hero.x, hero.z, hero.y, 0.32f);
  if (in.pressed[KEY_SPACE] && onGround && rollT <= 0 && slashT <= 0) { vy = 8.8f; onGround = false; burst(hero + Vec3{0, .05f, 0}, 5, {.65f, .6f, .5f}, 1.2f, .06f); }   // jump: ~1.6 m, mantles up to ~2.7 m ledges
  if ((in.pressed['C'] || in.pressed['V']) && onGround && rollCd <= 0 && slashT <= 0) { rollT = 0.5f; rollDir = l > 1e-3f ? dir : Vec3{std::sin(heroYaw), 0, std::cos(heroYaw)}; invuln = std::max(invuln, 0.55f); }
  if (onGround) { if (gnd > -1e8f && gnd >= hero.y - 0.75f) hero.y = gnd; else { onGround = false; vy = 0; } }
  else { vy -= 24.f * dt; hero.y += vy * dt; if (vy > 0 && coll.blocked(hero.x, hero.z, hero.y + 1.62f, hero.y + 1.95f)) vy = 0; if (vy <= 0 && hero.y <= gnd) { hero.y = gnd; vy = 0; onGround = true; } }
  yOff = 0.f; runPhase += dt * (l > 1e-3f ? (sprint ? 14.f : 9.f) : 0.f);
  bool rmb = in.rmb && in.focused; if (((rmb && !gPrevRmb) || in.pressed['Q'])) castSpell(); gPrevRmb = rmb;
  if ((in.lmbPressed && in.focused) || in.pressed['F']) startSlash();
  if (slashT > 0) {
    slashT -= dt; Vec3 hp0 = handPos(), sd = swordDir();
    slashRibbon.push_back({hp0 + sd * 0.25f, hp0 + sd * 1.42f, 0.30f});
    if (slashRibbon.size() > 10) slashRibbon.erase(slashRibbon.begin());
    float k = slashProgress();
    if (k > 0.2f && k < 0.8f) for (auto& e : enemies) if (e.alive && e.hitId != slashId) {
      Vec3 dd = e.pos - hero; dd.y = 0; float dl = vlen(dd), reach = (combo == 2 ? 3.9f : 3.3f) + statsFor(e.kind).radius;
      Vec3 face{std::sin(heroYaw), 0, std::cos(heroYaw)};
      if (dl < reach && (dl < 1.f || dot(dd * (1.f / dl), face) > (combo == 2 ? -0.1f : 0.15f))) {
        e.hitId = slashId; damage(e, combo == 2 ? 2.f : 1.f, hero, combo == 2 ? 14.f : 8.f);
      }
    }
    if (slashT <= 0) { comboWindow = 0.55f; if (queuedSlash) startSlash(); }
  } else comboWindow = std::max(0.f, comboWindow - dt);
  invuln = std::max(0.f, invuln - dt); hurtFlash = std::max(0.f, hurtFlash - dt);
  if (hp <= 0) { hp = 100; mana = 100; hero = {roadCenterX(12.f), terrainHeight(roadCenterX(12.f), 12.f), 12.f}; heroVel = {}; vy = 0; onGround = true; } }
void GameWorld::cameraUpdate(const Input& in, float dt) {
  float ro = (in.down[KEY_LEFT] ? 1.f : 0.f) - (in.down[KEY_RIGHT] ? 1.f : 0.f);
  camYaw += ro * 2.2f * dt - in.mdx * 0.0028f; camPitch = std::clamp(camPitch + ((in.down[KEY_UP] ? -1.f : 0.f) + (in.down[KEY_DOWN] ? 1.f : 0.f)) * 1.2f * dt + in.mdy * 0.0025f, -0.1f, 1.2f);
  camShake = std::max(0.f, camShake - dt * 1.4f);
  Vec3 shk = camShake > 0.f ? Vec3{std::sin(time * 47.f) * camShake * 0.22f, std::cos(time * 59.f) * camShake * 0.18f, 0.f} : Vec3{};
  Vec3 tgt = hero + Vec3{0, 1.55f + yOff, 0} + shk, want = tgt + Vec3{-std::sin(camYaw) * std::cos(camPitch), std::sin(camPitch), -std::cos(camYaw) * std::cos(camPitch)} * camDist;
  { Vec3 d = want - tgt; float len = vlen(d), safe = 1.f; for (int i = 1; i <= 28; i++) { float t = i / 28.f; Vec3 q = tgt + d * t; if (coll.blockedPoint(q) || q.y < terrainHeight(q.x, q.z) + 0.15f) { safe = std::max(0.12f, t - 0.07f); break; } } want = tgt + d * safe; (void)len; }
  want.y = std::max(want.y, terrainHeight(want.x, want.z) + 0.3f); if (!camInit) { camEye = want; camInit = true; } camEye = camEye + (want - camEye) * (1.f - std::exp(-9.f * dt)); }
void GameWorld::enemiesUpdate(float dt) {
  for (auto& e : enemies) {
    if (!e.alive) { e.deadT += dt; continue; }
    Stats s = statsFor(e.kind); e.flash = std::max(0.f, e.flash - dt); e.atkCd = std::max(0.f, e.atkCd - dt); e.freezeT = std::max(0.f, e.freezeT - dt);
    float chill = (e.freezeT > 0.f) ? 0.25f : 1.f; e.patrolT += dt * chill;
    Vec3 to = hero - e.pos; to.y = 0; float d = vlen(to), speed = 0; Vec3 mv{};
    if (d < s.detect && d > s.range * 0.8f) { mv = to * (1.f / d); speed = s.speed * chill; }
    else if (d >= s.detect) { Vec3 pt = e.home + Vec3{std::sin(e.patrolT * .45f) * 3.2f, 0, std::cos(e.patrolT * .6f) * 2.4f}, pd = pt - e.pos; pd.y = 0; float pl = vlen(pd); if (pl > .1f) { mv = pd * (1.f / pl); speed = s.speed * .35f * chill; } }
    e.moveSpeed = speed; e.walkPhase += dt * speed * 2.6f;
    if (speed > 0) e.yaw += wrapPi(std::atan2(mv.x, mv.z) - e.yaw) * (1.f - std::exp(-8.f * dt)); else if (d <= s.range) e.yaw = std::atan2(to.x, to.z);
    moveEntity(e.pos, (mv * speed + e.vel) * dt, std::min(s.radius, 0.6f)); e.vel = e.vel * std::exp(-6.f * dt);
    if (d < s.range && e.atkCd <= 0) { e.atkCd = s.cd; if (invuln <= 0) { hp -= s.dmg; invuln = 0.9f; hurtFlash = 0.4f; camShake = 0.28f; heroVel = to * (7.f / std::max(d, .3f)); burst(hero + Vec3{0, 1.1f, 0}, 25, {.9f, .1f, .12f}, 3.f); } } } }
// Party AI: Sylphie holds ~7 m and casts arcane frost bolts, Lyra dashes in for twin-dagger strikes; with no enemy near they trail the hero.
void GameWorld::alliesUpdate(float dt) {
  for (size_t i = 0; i < allies.size(); i++) {
    Ally& a = allies[i]; a.cd = std::max(0.f, a.cd - dt); a.atkT = std::max(0.f, a.atkT - dt);
    Enemy* tgt = nullptr; float bd = 18.f;
    for (auto& e : enemies) if (e.alive) { float d = vlen(e.pos - a.pos); if (d < bd && vlen(e.pos - hero) < 24.f) { bd = d; tgt = &e; } }
    Vec3 goal; float stop = 0.5f;
    if (tgt) {
      Vec3 d = tgt->pos - a.pos; d.y = 0; float L = std::max(vlen(d), .01f); Vec3 dn = d * (1.f / L);
      goal = a.kind == 0 ? tgt->pos - dn * 7.f : tgt->pos - dn * 1.25f; a.yaw = std::atan2(dn.x, dn.z);
      if (a.kind == 0 && bd < 13.f && a.cd <= 0.f) { Vec3 o = a.pos + Vec3{0, 1.45f, 0}, t = tgt->pos + Vec3{0, statsFor(tgt->kind).height * .5f, 0}; bolts.push_back({o, normalize(t - o) * 28.f, 1.6f, 1}); a.cd = 1.6f; a.atkT = .4f; }
      else if (a.kind == 1 && bd < 2.3f && a.cd <= 0.f) { damage(*tgt, 1.0f, a.pos, 3.5f); a.cd = .75f; a.atkT = .45f; }
    } else {
      Vec3 f = {std::sin(heroYaw), 0, std::cos(heroYaw)}, r = {std::cos(heroYaw), 0, -std::sin(heroYaw)}; float side = a.kind == 0 ? -1.f : 1.f;
      goal = hero + f * 2.6f + r * (side * 2.2f); stop = 0.9f;
    }
    Vec3 to = goal - a.pos; to.y = 0; float dist = std::max(vlen(to), .001f); float want = dist > stop ? std::min(6.4f, 1.6f + dist * 1.5f) : 0.f;
    a.speed += (want - a.speed) * std::min(1.f, dt * 8.f);
    if (want > 0.f) { Vec3 dn = to * (1.f / dist); Vec3 p = a.pos; moveEntity(p, dn * (a.speed * dt), .4f); a.pos = p; if (!tgt) a.yaw = std::atan2(dn.x, dn.z); }
    a.pos.y = terrainHeight(a.pos.x, a.pos.z); a.walkPhase += dt * a.speed * 1.9f;
  }
}
}  // namespace isekai
