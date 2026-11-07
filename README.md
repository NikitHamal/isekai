# Chronicles of Aetheria: Isekai

Native C++20 3D fantasy action-RPG, plus **vork_forge** — a token-efficient declarative Python DSL that compiles organic/architectural meshes with procedurally baked PBR textures straight to Blender-compatible `.glb`.

## Build & verify
    cmake -B build && cmake --build build -j4
    ./build/isekai --verify-headless      # loads every assets/models/**/*.glb, renders docs/previews/engine_headless_frame.png

## Asset pipeline
    pip install numpy pillow scikit-image
    python3 tools/assets/gen_<slug>.py            # -> assets/models/<cat>/<slug>.glb
    python3 tools/qa_asset.py assets/models/<cat>/<slug>.glb   # budget + PBR checks + 2x2 preview sheet

See `ASSET_CATALOG.md` and `ROADMAP_STATUS.md` for progress.

## Gallery (v0.3.0 — Valoria Kingdom Frontier)
![chr_hero_kaelen_adventurer](docs/previews/chr_hero_kaelen_adventurer.png)
![bld_valoria_adventurer_guild](docs/previews/bld_valoria_adventurer_guild.png)
![bld_royal_citadel_keep](docs/previews/bld_royal_citadel_keep.png)
![veh_merchant_covered_wagon](docs/previews/veh_merchant_covered_wagon.png)
![chr_ally_garrick_royal_paladin](docs/previews/chr_ally_garrick_royal_paladin.png)
![mon_orc_warlord_berserker](docs/previews/mon_orc_warlord_berserker.png)
![mon_shadow_direwolf_alpha](docs/previews/mon_shadow_direwolf_alpha.png)
![headless engine frame](docs/previews/engine_headless_frame.png)
![prp_wooden_wayfinder_signpost](docs/previews/prp_wooden_wayfinder_signpost.png)
![prp_ornate_treasure_chest](docs/previews/prp_ornate_treasure_chest.png)
![wpn_aetherblade_longsword](docs/previews/wpn_aetherblade_longsword.png)

## Controls
WASD move · Mouse look · LMB/F sword combo · RMB/Q Crimson Flare spell · Space roll/jump · Shift sprint
