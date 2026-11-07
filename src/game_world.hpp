// Third-person gameplay: hero controller, spring-arm camera, pickups, chest, goblins, fairy, particles. Builds a Scene each frame.
#pragma once
#include <map>
#include <memory>
#include <string>
#include <vector>
#include "math3d.hpp"
#include "platform.hpp"
#include "scene.hpp"
namespace isekai {
struct Particle { Vec3 p, v; float life, maxLife, size; Vec3 col; };
struct Goblin { Vec3 pos, vel; float yaw = 0, hp = 3, atkCd = 0, flash = 0, patrolT = 0, hitSwing = -1; Vec3 home; bool alive = true; float deadT = 0; };
struct Pickup { Vec3 pos; bool taken = false; float phase = 0; bool fromDrop = false; };
class GameWorld {
 public:
  explicit GameWorld(const std::string& root);
  bool assetsFound() const { return found; }
  int modelCount() const { return loaded; }
  void update(const Input& in, float dt, float aspect);
  Scene buildScene() const;
  bool wantFullscreenToggle = false, wantMouseFree = false;
  // Used by headless verification to stage a showcase frame.
  void stageShowcase();
  Vec3 heroPos() const { return hero; }
 private:
  const Model* M(const char* name) const { auto it = models.find(name); return it == models.end() ? nullptr : it->second.get(); }
  Mat4 fit(const Model* m, float height, Vec3 pos, float yaw, float pitch = 0) const;
  void loadAll(const std::string& root);
  void burst(Vec3 p, int n, Vec3 col, float speed, float size = 0.12f);
  void spawnGoblin(Vec3 p);
  void heroUpdate(const Input& in, float dt);
  void cameraUpdate(const Input& in, float dt, float aspect);
  void enemiesUpdate(float dt);
  void startSlash(const Input& in);
  Vec3 swordTip() const; Vec3 handPos() const; bool nearChest() const;
  std::map<std::string, std::unique_ptr<Model>> models; bool found = false; int loaded = 0;
  Vec3 hero{0, 0, 11}; Vec3 heroVel{}; float heroYaw = kPi, vy = 0, groundY = -0.5f, y = 0; bool onGround = true;
  float slashT = 0, slashDir = 1, slashId = 0, invuln = 0, hurtFlash = 0, camYaw = kPi, camPitch = 0.38f, camDist = 5.2f, time = 0, runPhase = 0;
  Vec3 camEye{0, 4, 17}; bool camInit = false; int hearts = 3, maxHearts = 3, kills = 0;
  bool chestOpen = false; float chestAnim = 0, chestGlow = 0; Vec3 chestPos{-4.6f, -0.5f, 7.0f}, signPos{3.6f, -0.5f, 8.0f};
  std::vector<Pickup> pickups; std::vector<Goblin> goblins; std::vector<Particle> parts; std::vector<std::pair<Vec3, float>> trail;
  std::string hint; float hintT = 0; bool camOverride = false; Vec3 ovEye{}, ovTgt{};
};
Model makeBoxModel(Vec3 half, Vec3 center, Vec3 rgb);
Model makeGroundModel(float half, float y);
}  // namespace isekai
