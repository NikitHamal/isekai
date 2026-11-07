# ROADMAP STATUS — Native C++20 Engine

- [x] **E1**: CMake build + `--verify-headless` + GitHub Actions release CI
- [x] **E2**: `.glb` loader + PBR material/texture pipeline
- [x] **E3**: Win32+WGL GL3.3 PBR, **2048x2048 sun shadow map (3x3 PCF)**, horizon AO, golden-hour atmospheric sky, splat-mapped terrain
- [x] **E4**: Third-person controller, spring-arm camera (mouse/arrows), sprint, dodge-roll
- [x] **E5**: Valoria Kingdom Frontier: cobble road, Adventurer Guildhall, Royal Citadel Keep, merchant wagon, Paladin Garrick, Orc Warlords, Shadow Direwolves, Goblin Raiders
- [x] **E6**: Aetherblade 3-hit combo (LMB/F), Crimson Flare / Aether Lance spell (RMB/Q) with dynamic light + particles, minimal HP/Mana HUD (no FPS, GPU, minimap or control text)

## Session log
- Session 1: scaffolds, vork_forge DSL+PBR baker+GLB compiler+QA, E1+E2.
- Session 2 (REVERTED): fairy, heart containers, root archway, acorn lanterns, HUD bloat — all cloned Zelda gimmicks, purged in session 3.
- Session 3: purge + shadow-mapped realistic renderer + sword/magic combat + Valoria Kingdom assets (v0.3.0).

- [x] **Q01**: Sculpted 360-degree mountain crags (`env_mossy_forest_cliff_modular.glb`), sacred world tree (`env_sacred_world_tree_canopy.glb`), 3D pine/oak forest, mossy boulders, wind-swaying 3D grass tufts & wildflowers, fixed idle sword glow.
- [x] **Q02**: Hierarchical multi-part character & monster skeletal animation (`src/animator.hpp`), anatomical sub-mesh `partId` + joint pivots in `model.h`, `gltf_loader.cpp`, and `vork_forge`.
- [x] **Q03**: Offscreen HDR framebuffer (`sceneFbo`), Screen-Space Ambient Occlusion (SSAO), Dual-Pass Gaussian Bloom (`bloomFbo[2]`), and Golden-Hour Sun Rim-Lighting & Horizon Scattering.
- [x] **Q04**: Dynamic Isekai spell & combat VFX (3 switchable spells: Crimson Flare, Glacial Fang, Aether Judgment; rotating 3D runic circles; 10-sample curved ribbon sword trails; metallic hit sparks; 40ms hit-stop; camera impulse shake).
