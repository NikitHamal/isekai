# MASTER DEVELOPMENT QUEUE — CHRONICLES OF AETHERIA: ISEKAI (REAL BLENDER `bpy` PIPELINE)

### HOTFIX v0.6.0 — Owner overhaul #2: real anime character models (done)
- [x] **H2 (v0.6.0)**: Owner overhaul #2 — REAL ANIME CHARACTERS. Downloaded free-use VRoid Studio sample avatars (Sakurada Fumiriya, AvatarSample_C, Victoria Rubin, Vivi — see CREDITS.md), studied their skeleton/skin-weight structure and converted them in real headless Blender (`tools/blender_forge/vrm_forge.py`): T-pose->A-pose LBS, bone weights -> the engine's 14 named body parts with top-2 part blend stored in TEXCOORD_1, per-material+part named objects with joint pivots, 1024px PBR materials, alpha-masked hair/lash cards, official bpy glTF export. New `armor_kit.py` fits measurement-driven armour (cuirass, layered pauldrons, bracers, greaves, knee cops, belt, draped cloak), elf/cat ears, circlet, tail, staff, re-imported sword/shield. Engine: CPU part-blend skinning (`skinPrimitive` in `animator.hpp`) for the GL + software paths (no joint cracks), alpha-mask materials, biped tail sway.

### HOTFIX v0.5.0 — Owner overhaul (done)
- [x] **H1 — Anatomical Blender characters (`anatomy_core/face/body.py`): Hero, Paladin, Orc, Goblin, Direwolf with sculpted faces, fingered hands, 2-segment limbs; hierarchical animator (waist→torso→shoulder→elbow, hip→knee); NaN/black-box + shadow-swim/z-fight flicker fixes; mesh-driven collision (enterable buildings, standable rocks, jump/mantle, camera collision).**

### Tier 1: Blender Remaster of Core Scene, Skeletal Animation, Foliage, HDR/SSAO & Dynamic VFX
- [x] **Q01 — Build `tools/blender_forge/` & Remaster Cliffs, Forest Trees, Boulders & Wind-Swaying 3D Grass in Real Blender + Fix Idle Glow Bug**
  - **Fix `v0.3.0` scene issues**:
    1. Remove the permanent white glowing blob stuck beside the hero when idle (`src/game_world.cpp` / `src/soft_extra.cpp`: only render sword slash geometry when `hero.slashTimer > 0` and spell hand glow when actively casting).
    2. Replace the boxy `env_mossy_forest_cliff_modular.glb` using **real Blender (`bpy`)** (`DISPLACE` Voronoi/Musgrave rock strata + `BEVEL` + `SUBSURF` + mossy ledge overhangs—zero rectangular boxes or stuck-on ovals) and build `env_sacred_world_tree_canopy.glb` (`>= 10,000` tris) in Blender with gnarled root splines and layered leaf canopies.
    3. Populate the Valoria hills and road verges in `src/game_world.cpp` & `src/gl_renderer.cpp` with Blender-modeled **Pine & Oak Trees**, **Craggy Boulders**, and **Thousands of Wind-Swaying 3D Grass Blade Clusters**.

- [x] **Q02 — Remaster Hero, Paladin, Orc, Direwolf & Goblin in Real Blender with Articulated Limb Nodes + C++ Skeletal Animator (`src/animator.hpp`)**
  - Rebuild `chr_hero_kaelen_adventurer.glb`, `chr_ally_garrick_royal_paladin.glb`, `mon_orc_warlord_berserker.glb`, `mon_shadow_direwolf_alpha.glb`, and `mon_forest_goblin_raider.glb` in **real Blender (`bpy`)** using `MIRROR` + `SUBSURF` + `SOLIDIFY` armor/cloth modeling and separate named limb objects (`torso`, `head`, `cloak`, `arm_l`, `arm_r`, `leg_l`, `leg_r`, `weapon_r`, `jaw`, `tail`).
  - Update `include/isekai/model.h`, `src/gltf_loader.cpp`, and `src/animator.hpp` so `cgltf` preserves each node's `partId` and pivot, animating Idle, Walk/Sprint, 3-Hit Sword Combo, Magic Cast, Dodge Roll, and Monster gait/attacks.

- [x] **Q03 — Remaster Valoria Guildhall, Citadel Keep, Merchant Wagon, Longsword, Shield & Props in Real Blender (`bpy`)**
  - Rebuild `bld_valoria_adventurer_guild.glb`, `bld_royal_citadel_keep.glb`, `veh_merchant_covered_wagon.glb`, `wpn_aetherblade_longsword.glb`, `wpn_royal_crest_heater_shield.glb`, `prp_ornate_treasure_chest.glb`, and `prp_wooden_wayfinder_signpost.glb` in **real Blender (`bpy`)** with beveled stone arches, arrayed slate roof tiles, timber framing, spoked wheels, draped canvas ribs, and full Smart UV unwrapping.

- [x] **Q04 — Offscreen HDR Framebuffer: Screen-Space Ambient Occlusion (SSAO), Dual-Pass Bloom & Golden-Hour Atmospheric Scattering**
  - Upgraded `src/gl_renderer.hpp` / `src/gl_renderer.cpp` with an offscreen color + depth FBO (`sceneFbo`), SSAO contact shadows, Dual-Pass Gaussian HDR Bloom, and golden-hour rim lighting & atmospheric scattering.

- [x] **Q05 — Dynamic Isekai Magic & Combat VFX (3 Switchable Spells, Rotating Runic Circles, Ribbon Sword Trails, Hit Sparks & Camera Shake)**
  - Upgraded `src/game_hero.cpp` and `src/game_world.cpp` with 3 switchable spells (Crimson Flare, Glacial Fang, Aether Judgment), rotating runic magic circles, curved triangle-strip ribbon sword trails, metallic hit sparks, 40ms hit-stop, and camera impulse shake.

### Tier 2: Expand Valoria Kingdom Architecture, Allies, River Ruins & Mounts (All Built in Blender `bpy`)
- [x] **Q06 — Valoria Town Plaza in Blender: Blacksmith Forge (`bld_blacksmith_forge_shop`), Magic Tower (`bld_apothecary_magic_tower`) & Tavern Inn (`bld_medieval_tavern_inn`)**
  - Model all 3 medieval buildings in Blender (`>= 9,000` tris each, beveled stonework, arrayed roof tiles, glowing forge furnace, copper astronomical dome, tavern balcony) and place them around the Valoria town plaza.
- [x] **Q07 — Isekai Party Allies in Blender: High-Elf Archmage Sylphie (`chr_ally_sylphie_elf_mage`) & Beastkin Rogue Lyra (`chr_ally_lyra_beastkin_rogue`) + Companion Combat AI** (done in v0.6.0: Sylphie keeps ~7 m and casts arcane frost bolts, Lyra dashes in for twin-dagger strikes, both trail the hero when idle — `GameWorld::alliesUpdate`)
  - Sculpt/model both articulated characters in Blender (`>= 10,000` tris with limb pivots) and spawn them as active AI party members who follow the Hero and fight monsters with ranged arcane bolts and twin-dagger strikes.
- [ ] **Q08 — River Gorge & Ancient Ruins in Blender: Stone Bridge (`env_ancient_bridge_ruins`), Elven Mana Shrine (`env_mana_shrine_waystone`) & Market Props (`prp_medieval_market_barrels_crates`)**
  - Model all 3 assets in Blender, add a reflective river gorge crossed by the bridge, and restore HP/Mana when near the Mana Shrine.
- [ ] **Q09 — Mounts & Siege Engines in Blender: Armored Warhorse (`veh_armored_warhorse`), Griffon Mount (`veh_griffon_mount_armored`), War Chariot (`veh_royal_war_chariot`) & Siege Trebuchet (`veh_siege_trebuchet`)**
  - Model all 4 articulated assets in Blender (`>= 8,000–10,000` tris each), place them outside the Citadel gate, and let the Hero mount/ride (`E` key) the Warhorse or Griffon.

### Tier 3: Rival Empire Forces, Colossal Bosses, Legendary Arsenal & Audio
- [ ] **Q10 — Rival Empire Forces in Blender: Halberdier (`enm_empire_halberdier`), Necromancer (`enm_dark_cult_necromancer`), Cursed Skeleton Knight (`enm_cursed_skeleton_knight`) & Crossbow Sniper (`enm_imperial_crossbow_sniper`)**
- [ ] **Q11 — Colossal Bosses in Blender: Ancient Stone Golem (`mon_ancient_stone_golem`) & Ignis Elder Wyvern Dragon (`mon_ignis_elder_wyvern`)**
- [ ] **Q12 — Legendary Weapons in Blender (`wpn_archmage_celestial_staff`, `wpn_elven_wind_recurve_bow`, `wpn_dwarven_runic_warhammer`, `mon_emerald_mana_slime_king`) + Weapon Switching (`Tab`) + Procedural C++ Sound Engine & `Esc` Pause Menu**
