# ROADMAP STATUS — Native C++20 Engine

- [x] **E1**: CMake build + `--verify-headless` + GitHub Actions release CI (Win/Linux/macOS)
- [x] **E2**: `.glb` loader (cgltf) + PBR material/texture pipeline
- [x] **E3** (partial): Win32+WGL GL3.3 GLSL330 Cook-Torrance PBR, flickering lantern/fairy point lights, sky dome, fog, ACES. TODO: shadow map, bloom
- [x] **E4**: Third-person controller, spring-arm camera (mouse/arrows/Q/E), fairy figure-8 companion
- [x] **E5** (slice 1): archway, hearts, chest, signpost, lanterns, goblins playable. TODO: Valoria Kingdom zone
- [ ] **E6**: Combat + HUD (hearts, FPS, minimap) DONE; TODO: lock-on, sound

## Session log
- Session 1: scaffolds, vork_forge DSL+PBR baker+GLB compiler+QA, E1+E2 done; 6 assets (archway, heart, signpost, lantern, chest, longsword). Fixed primitive winding (outward normals).
