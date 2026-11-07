// Third-person gameplay: spellsword hero (sword combo, Crimson Flare spell, roll), kingdom frontier enemies, particles. Builds a Scene each frame.
#pragma once
#include <map>
#include <memory>
#include <string>
#include <vector>
#include "math3d.hpp"
#include "platform.hpp"
#include "scene.hpp"
namespace isekai {
enum EnemyKind { EK_GOBLIN = 0, EK_ORC = 1, EK_WOLF = 2 };
struct Particle { Vec3 p, v; float life, maxLife, size; Vec3 col; };
struct Enemy { int kind = EK_GOBLIN; Vec3 pos, vel, home; float yaw = 0, hp = 3, maxHp = 3, atkCd = 0, flash = 0, patrolT = 0, hitId = -1, deadT = 0; bool alive = true; };
struct Bolt { Vec3 pos, vel; float life = 2.f; };
struct Flash { Vec3 pos; float t = 0; };
class GameWorld {
 public:
  explicit GameWorld(const std::string& root);
  bool assetsFound() const { return found; }
  int modelCount() const { return loaded; }
  void update(const Input& in, float dt, float aspect);
  Scene buildScene() const;
  void stageShowcase();     // staged hero + combat frame for headless verification
  Vec3 heroPos() const { return hero; }
 private:
  const Model* M(const char* name) const { auto it = models.find(name); return it == models.end() ? nullptr : it->second.get(); }
  Mat4 fit(const Model* m, float height, Vec3 pos, float yaw) const;
  void loadAll(const std::string& root);
  void burst(Vec3 p, int n, Vec3 col, float speed, float size = 0.12f);
  void spawn(int kind, Vec3 p);
  void heroUpdate(const Input& in, float dt);
  void cameraUpdate(const Input& in, float dt);
  void enemiesUpdate(float dt);
  void boltsUpdate(float dt);
  void startSlash(); void castSpell();
  void damage(Enemy& e, float dmg, Vec3 from, float knock);
  Vec3 handPos() const; Vec3 swordDir() const; Mat4 swordRot() const; float slashProgress() const;
  std::map<std::string, std::unique_ptr<Model>> models; bool found = false; int loaded = 0;
  Vec3 hero{0, 0, 12}; Vec3 heroVel{}, rollDir{}; float heroYaw = kPi, vy = 0, yOff = 0; bool onGround = true;
  float hp = 100, mana = 100, invuln = 0, hurtFlash = 0, castFlash = 0, castCd = 0, rollT = 0, rollCd = 0;
  int combo = 0; float slashT = 0, slashDur = 0.4f, comboWindow = 0, slashId = 0; bool queuedSlash = false;
  float camYaw = kPi, camPitch = 0.30f, camDist = 5.6f, time = 0, runPhase = 0; Vec3 camEye{0, 4, 19}; bool camInit = false, camOverride = false; Vec3 ovEye{}, ovTgt{};
  std::vector<Enemy> enemies; std::vector<Bolt> bolts; std::vector<Flash> flashes; std::vector<Particle> parts; std::vector<std::pair<Vec3, float>> trail;
};
Model makeBoxModel(Vec3 half, Vec3 center, Vec3 rgb);
Model makeTerrainModel(float half, float step);
}  // namespace isekai
