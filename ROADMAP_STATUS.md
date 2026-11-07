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
