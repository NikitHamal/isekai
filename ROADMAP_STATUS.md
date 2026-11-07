# ROADMAP STATUS — Native C++20 Engine

- [x] **E1**: CMake build + `--verify-headless` + GitHub Actions release CI (Win/Linux/macOS)
- [x] **E2**: `.glb` loader (cgltf) + PBR material/texture pipeline
- [ ] **E3**: GLSL PBR + shadow map + lantern point lights + bloom + fog + ACES
- [ ] **E4**: Third-person controller, spring-arm camera, fairy companion AI
- [ ] **E5**: "Whispering Root Sanctuary & Valoria Kingdom" vertical slice
- [ ] **E6**: Combat, HUD (hearts, FPS, minimap, lock-on), sound

## Session log
- Session 1: scaffolds, vork_forge DSL+PBR baker+GLB compiler+QA, E1+E2 done; 6 assets (archway, heart, signpost, lantern, chest, longsword). Fixed primitive winding (outward normals).
