# MASTER DEVELOPMENT QUEUE — CHRONICLES OF AETHERIA: ISEKAI

### Tier 1: Fix Visual Artifacts, Skeletal Animation, Lush Foliage, HDR/SSAO & Spell VFX
- [x] **Q01 — Replace Boxy Cliff Blocks with Sculpted Mountain Crags, Forest Trees, Boulders & Wind-Swaying 3D Grass + Fix Idle Sword Glow**
  - **Issues to fix from `v0.3.0`**:
    1. A white glowing blob floats permanently next to the hero's cloak even when standing still. Fix `src/game_world.cpp` / `src/soft_extra.cpp` so the sword slash arc only renders while `hero.slashTimer > 0` and the hand spell charge only renders while actively casting.
    2. `env_mossy_forest_cliff_modular.glb` currently looks like rectangular grey boxes with small ovals stuck on them, and the green hills have no trees or grass.
  - **Implementation**:
    1. Rebuild `tools/assets/gen_env_mossy_forest_cliff_modular.py` as jagged, natural multi-octave noise-displaced limestone crags and terraced ledges (zero rectangular boxes or oval bumps), and generate `assets/models/environment/env_sacred_world_tree_canopy.glb` (`>= 9,000` tris) with gnarled roots, bark trunk, and layered leaf canopies.
    2. Populate the Valoria frontier hills and road verges in `src/game_world.cpp` and `src/gl_renderer.cpp` with **3D Pine & Oak Forest Trees**, **Mossy Boulders**, and **GPU-instanced / batched 3D Grass Tufts & Wildflowers** that sway smoothly in the wind.

- [ ] **Q02 — Hierarchical Multi-Part Character & Monster Skeletal Animation (`src/animator.hpp`)**
  - **Issue to fix**: Currently `cgltf` flattens every `.glb` into a single static mesh, so the hero, allies, and monsters slide along the ground without moving their legs, arms, cloak, or weapons.
  - **Implementation**:
    1. Extend `include/isekai/model.h`, `src/model.cpp`, and `tools/vork_forge/glb_compiler.py` (plus the character/monster generators) so each anatomical sub-mesh carries a `partId` (`0=root`, `1=torso`, `2=head`, `3=cloak`, `4=arm_l`, `5=arm_r`, `6=leg_l`, `7=leg_r`, `8=weapon_r`, `9=jaw_or_tail`) and its local joint pivot `(px, py, pz)`.
    2. Create `src/animator.hpp` and apply per-part hierarchical transforms in both `src/gl_renderer.cpp` and `src/soft_raster.cpp`:
       - **Idle**: Subtle torso breathing, gentle cloak breeze wave, ready weapon stance.
       - **Walk / Sprint**: Full biped leg stride (`sin(walkPhase)` hip/knee swing), opposite arm counter-swing, forward torso lean when sprinting, and cloak billowing backward based on speed.
       - **3-Hit Sword Combo**: Hit 1 diagonal cleave, Hit 2 reverse horizontal slash with torso twist, Hit 3 leaping overhead slam.
       - **Magic Cast**: Left arm extends forward with arcane recoil and cloak flare.
       - **Dodge Roll / Jump**: Forward 360-degree tucked roll or airborne jump pose.
       - **Monsters & Allies**: Animated biped walk + heavy weapon swing for Orcs, Goblins, and Paladin Garrick; 4-legged bounding gallop + lunging bite for Shadow Direwolves.

- [ ] **Q03 — Offscreen HDR Framebuffer: Screen-Space Ambient Occlusion (SSAO), Dual-Pass Bloom & Atmospheric Scattering**
  - Upgrade `src/gl_renderer.hpp` / `src/gl_renderer.cpp` to render into an offscreen color + depth FBO (`sceneFBO`) and composite with a post-process pass:
    1. **SSAO**: Reconstruct depth neighborhoods to ground buildings, wagon wheels, boots, rocks, and foliage with natural contact shadows.
    2. **Dual-Pass Gaussian Bloom**: Extract bright emissive pixels (`> 1.1` from spells, glowing runes, forge fire, and lit windows), blur horizontally/vertically, and additively composite.
    3. **Golden-Hour Horizon Scattering & Rim Light**: Warm directional sun rim-lighting on characters and atmospheric depth haze.

- [ ] **Q04 — Dynamic Isekai Spell & Combat VFX (3 Switchable Spells, Rotating Runic Circles, Ribbon Sword Trails, Hit Sparks & Camera Shake)**
  - Upgrade `src/game_hero.cpp` and `src/game_world.cpp`:
    1. **3 Switchable Spells** (keys `1`, `2`, `3` or mouse wheel to select; Right-Click or `Q` to cast; show subtle active spell color indicator next to the top-left Mana bar while keeping the screen clean of text bloat):
       - **Spell 1 — Crimson Flare (Fire)**: Rotating crimson runic circle at the caster's hand/feet, blazing fireball with ember trail, explosive impact shockwave ring, dynamic orange light, and area knockback.
       - **Spell 2 — Glacial Fang (Ice)**: Cyan frost rune circle, fan of crystalline ice lances that shatter into frost particles and freeze/slow hit monsters for 3 seconds.
       - **Spell 3 — Aether Judgment (Lightning)**: Golden-violet arcane ground circle at target location followed by a jagged sky-to-ground lightning bolt, bloom flash, and radial shockwave.
    2. **Curved Ribbon Sword Trail & Impact Feel**:
       - Build a smooth triangle-strip ribbon mesh across the last 10 sword-tip positions during swings with additive alpha fade, metallic hit sparks on contact, brief 40ms hit-stop on heavy combo hits, and camera impulse shake.

### Tier 2: Expand Valoria Kingdom Architecture, Party Allies, River Ruins & Mounts
- [ ] **Q05 — Valoria Town Plaza: Blacksmith Forge (`bld_blacksmith_forge_shop`), Magic Tower (`bld_apothecary_magic_tower`) & Tavern Inn (`bld_medieval_tavern_inn`)**
  - Generate all 3 medieval buildings (`>= 8,000` tris each, 1024px stone/timber/slate/brick PBR textures, glowing forge coals, copper astronomical dome, tavern porch), verify with `python3 tools/qa_asset.py`, and place them in the Valoria town center.
- [ ] **Q06 — Isekai Party Allies: High-Elf Archmage Sylphie (`chr_ally_sylphie_elf_mage`) & Beastkin Rogue Lyra (`chr_ally_lyra_beastkin_rogue`) + Companion Combat AI**
  - Generate both articulated character models (`>= 10,000` tris with `partId` limb pivots), verify with `qa_asset.py`, and spawn them as active AI companions who follow the Hero and fight monsters using ranged arcane bolts and agile twin-dagger strikes.
- [ ] **Q07 — River Gorge & Ancient Ruins: Stone Bridge (`env_ancient_bridge_ruins`), Elven Mana Shrine (`env_mana_shrine_waystone`) & Market Props (`prp_medieval_market_barrels_crates`)**
  - Generate all 3 assets, add a river gorge with water reflections crossed by the ancient bridge, and make the glowing Mana Shrine restore HP/Mana when approached.
- [ ] **Q08 — Mounts & Siege Engines: Armored Warhorse (`veh_armored_warhorse`), Griffon Mount (`veh_griffon_mount_armored`), War Chariot (`veh_royal_war_chariot`) & Siege Trebuchet (`veh_siege_trebuchet`)**
  - Generate all 4 articulated assets (`>= 7,000–10,000` tris each), place them outside the Citadel gate, and allow the Hero to mount/dismount (`E` key) the Warhorse or Griffon for fast riding/flying traversal.

### Tier 3: Rival Empire Forces, Colossal Bosses, Weapon Arsenal & Audio
- [ ] **Q09 — Rival Empire Forces: Halberdier (`enm_empire_halberdier`), Necromancer (`enm_dark_cult_necromancer`), Cursed Skeleton Knight (`enm_cursed_skeleton_knight`) & Crossbow Sniper (`enm_imperial_crossbow_sniper`)**
  - Generate all 4 articulated enemy models (`>= 8,500` tris each) with ranged crossbow/dark-bolt attacks and melee halberd/sword combat AI.
- [ ] **Q10 — Colossal Bosses: Ancient Stone Golem (`mon_ancient_stone_golem`) & Ignis Elder Wyvern Dragon (`mon_ignis_elder_wyvern`)**
  - Generate the runic Stone Golem (`>= 9,500` tris) and winged Elder Wyvern (`>= 14,000` tris with articulated wings, jaw, tail, legs), complete with ground-slam shockwaves, sweeping dragon fire-breath, and a minimal boss HP bar when engaged.
- [ ] **Q11 — Legendary Weapons Arsenal: Celestial Staff (`wpn_archmage_celestial_staff`), Elven Wind Bow (`wpn_elven_wind_recurve_bow`), Dwarven Runic Warhammer (`wpn_dwarven_runic_warhammer`) + Weapon Switching (`Tab`)**
  - Generate all 3 weapons (`>= 4,000` tris each) and let the Hero cycle active weapons with `Tab` (Longsword, Warhammer heavy AoE slam, Celestial Staff boosted magic, Elven Bow ranged arrows).
- [ ] **Q12 — Procedural C++ Sound Effects Engine + Clean `Esc` Pause Overlay & Quality Presets**
  - Add zero-dependency procedural audio synthesis (`winmm` on Windows) for sword clangs, swings, fireballs, ice shatters, thunder, and footsteps, plus an `Esc` pause/controls modal.
