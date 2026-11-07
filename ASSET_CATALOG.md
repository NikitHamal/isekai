# ASSET CATALOG — Chronicles of Aetheria: Isekai

Pipeline: `tools/assets/gen_<slug>.py` -> `assets/models/<category>/<slug>.glb` -> `python3 tools/qa_asset.py <glb>` -> `docs/previews/<slug>.png`


## 1. Environment (`assets/models/environment/`)
- [ ] `env_valoria_stone_town_wall` (>= 8,000 tris)
- [x] `env_mossy_forest_cliff_modular` (>= 6,500 tris)
- [ ] `env_mana_shrine_waystone` (>= 5,000 tris)
- [ ] `env_ancient_bridge_ruins` (>= 7,000 tris)
- [ ] `env_sacred_world_tree_canopy` (>= 9,000 tris)

## 2. Characters (`assets/models/characters/`)
- [x] `chr_hero_kaelen_adventurer` (>= 10,000 tris)
- [ ] `chr_ally_mira_town_healer` (>= 9,000 tris)
- [x] `chr_ally_sylphie_elf_mage` (>= 10,000 tris)
- [x] `chr_ally_garrick_royal_paladin` (>= 10,000 tris)
- [x] `chr_ally_lyra_beastkin_rogue` (>= 9,500 tris)

## 3. Buildings (`assets/models/buildings/`)
- [x] `bld_valoria_adventurer_guild` (>= 8,500 tris)
- [x] `bld_royal_citadel_keep` (>= 10,000 tris)
- [ ] `bld_blacksmith_forge_shop` (>= 7,500 tris)
- [ ] `bld_apothecary_magic_tower` (>= 8,000 tris)
- [ ] `bld_medieval_tavern_inn` (>= 8,000 tris)

## 3b. Monsters (`assets/models/monsters/`)
- [x] `mon_orc_warlord_berserker` (>= 9,000 tris)
- [x] `mon_shadow_direwolf_alpha` (>= 9,000 tris)

## 4. Vehicles (`assets/models/vehicles/`)
- [x] `veh_merchant_covered_wagon` (>= 6,500 tris)
- [ ] `veh_royal_war_chariot` (>= 7,000 tris)
- [ ] `veh_siege_trebuchet` (>= 7,500 tris)
- [ ] `veh_griffon_mount_armored` (>= 10,000 tris)
- [ ] `veh_armored_warhorse` (>= 9,000 tris)

## 5. Monsters (`assets/models/monsters/`)
- [x] `mon_forest_goblin_raider` (>= 8,000 tris)
- [x] `mon_emerald_mana_slime_king` (>= 5,000 tris)
- [ ] `mon_shadow_direwolf_alpha` (>= 9,000 tris)
- [ ] `mon_ancient_stone_golem` (>= 9,500 tris)
- [ ] `mon_orc_warlord_berserker` (>= 10,000 tris)
- [ ] `mon_ignis_elder_wyvern` (>= 14,000 tris)

## 6. Enemies (`assets/models/enemies/`)
- [ ] `enm_empire_halberdier` (>= 8,500 tris)
- [ ] `enm_dark_cult_necromancer` (>= 8,500 tris)
- [ ] `enm_cursed_skeleton_knight` (>= 8,500 tris)
- [ ] `enm_imperial_crossbow_sniper` (>= 8,500 tris)

## 7. Weapons (`assets/models/weapons/`)
- [x] `wpn_aetherblade_longsword` (>= 4,000 tris)
- [x] `wpn_royal_crest_heater_shield` (>= 3,500 tris)
- [ ] `wpn_archmage_celestial_staff` (>= 4,500 tris)
- [ ] `wpn_elven_wind_recurve_bow` (>= 3,500 tris)
- [ ] `wpn_dwarven_runic_warhammer` (>= 4,000 tris)

## 8. Props (`assets/models/props/`)
- [ ] `prp_merchant_market_stall` (>= 3,000 tris)
- [x] `prp_ornate_treasure_chest` (>= 4,000 tris)
- [x] `prp_wooden_wayfinder_signpost` (>= 3,000 tris)
- [ ] `prp_iron_street_lamp_post` (>= 3,500 tris)
- [ ] `prp_medieval_market_barrels_crates` (>= 4,500 tris)

## v0.5.0 anatomical remaster
- chr_hero_kaelen_adventurer, chr_ally_garrick_royal_paladin, mon_orc_warlord_berserker, mon_forest_goblin_raider, mon_shadow_direwolf_alpha: rebuilt via `anatomy_*.py` (35k-58k tris, joint-pivoted parts: torso/head/cloak/arm/forearm/leg/shin/weapon_r/tail).
- v0.6.0: chr_hero_kaelen_adventurer (88k tris), chr_ally_garrick_royal_paladin (107k), chr_ally_sylphie_elf_mage (38k), chr_ally_lyra_beastkin_rogue (61k) are VRoid-based anime rigs converted/customised in Blender (`vrm_forge.py` + `armor_kit.py`), skinned in-engine via TEXCOORD_1 part blending. Sources: see CREDITS.md.

## v0.7.0 monster remaster (SDF + Blender pipeline)
| Asset | Tris | Notes |
|---|---|---|
| mon_orc_warlord_berserker | ~94k | sculpted muscular orc, tusks, mohawk, hide kit, rusty spiked pauldrons, bracers, cleaver |
| mon_forest_goblin_raider | ~60k | lanky goblin, big hooked nose, glowing slit eyes, rusty cap, ragged tunic, jagged blade |
| mon_shadow_direwolf_alpha | ~81k | digitigrade quadruped, 6.4k fur cards (mane/ruff/tail), glowing amber eyes, claws & fangs |
