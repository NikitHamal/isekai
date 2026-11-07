# Credits & third-party asset licences

## Anime character bases (VRoid Studio sample avatars by pixiv Inc. / VRoid Project)
Free-use sample models (commercial use, redistribution and modification allowed; the older VRoid Studio beta samples are published under CC0):
- **Sakurada Fumiriya** -> `chr_hero_kaelen_adventurer` (hair retinted, armour/cloak/sword added)
- **AvatarSample_C** -> `chr_ally_garrick_royal_paladin` (plate armour, shield, cloak, retinted)
- **Victoria Rubin** -> `chr_ally_sylphie_elf_mage` (elf ears, circlet, staff added)
- **Vivi** -> `chr_ally_lyra_beastkin_rogue` (cat ears, tail, bracers, twin daggers added)

Source mirror: https://github.com/madjin/vrm-samples (vroid/beta, vroid/stable). Rebuild with `python3 tools/blender_forge/make_chr_*.py` (downloads VRMs automatically via `vrm_forge.ensure_vrm`).
Textures were downscaled to <= 1024 px; meshes were re-weighted, re-posed (A-pose) and split into engine body parts in Blender.
