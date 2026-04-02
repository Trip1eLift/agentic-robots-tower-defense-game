# Pixel Art Assets Design Spec

**Date:** 2026-03-31
**Status:** Approved

## Overview

Create pixel art assets for ARIA: Defenders of Duskwall. The visual direction is chibi anime ARIA units on a blocky overgrown wasteland map. ARIA units are the stars -- large, detailed, and appealing. The world is deliberately rough and low-res to contrast.

## Art Style

- **ARIA units:** 48x48 chibi anime. Head-and-weapon dominant -- heads take ~40% of sprite height, weapons are oversized (60-70% of body height). Big eyes (5x4px), tiny stubby bodies. Cute but combat-ready. Designed for player attachment (gacha-friendly appeal). Each class has a visually distinct weapon that dominates the silhouette.
- **Enemies:** 32x32. Grotesque, fewer colors (4-6), clearly threatening. Distinct from ARIA at a glance.
- **Base:** 64x64. Fortified structure, largest sprite on the map.
- **Map tiles:** 16x16. Blocky Minecraft-style overgrown wasteland. Cracked dirt, dead grass, debris.
- **Structures:** 16x16. Walls and barricades built by architect class.

## Color Palettes

Each ARIA unit has a class color that matches the HUD:
- **Vanguard (Rex):** Red (#cc3333) primary, dark red (#8b1a1a) shadow
- **Striker (Aurora):** Gold (#e6b832) primary, amber (#b08820) shadow
- **Medic (Lily):** Green (#55cc66) primary, dark green (#338844) shadow
- **Architect (Hana):** Blue (#5599dd) primary, dark blue (#336699) shadow

Shared across all ARIA: skin tone (#f0c8a0), eye cyan (#40e0ff), hair unique per character.

Zombies: gray-green (#667755), dark (#3a3a2a), glowing red eyes (#ff3333).

Map tiles: earth tones -- brown (#8b7355), dark dirt (#5a4a3a), dead grass (#9b8b4a), rust (#8b5533).

## Asset List

### ARIA Units (48x48 PNG, transparent background)

| File | Character | Visual Description |
|------|-----------|-------------------|
| rex_sprite.png | Rex (Vanguard) | Huge head (40%), heavy red armor, MASSIVE shield (left, 14px tall) + OVERSIZED sword (right, 20px tall), red scarf flowing, stubby legs, brown hair, big cyan eyes, determined expression |
| aurora_sprite.png | Aurora (Striker) | Huge head, gold/amber light armor, MASSIVE sniper rifle (right side, 28px tall, nearly full sprite height), bright red scope + visor, blonde hair, big cyan eyes, focused expression |
| lily_sprite.png | Lily (Medic) | Huge head, green coat over white uniform, OVERSIZED pistol (right hand, visible barrel), bright healing glow (left hand), cross emblem on chest, pink hair, big cyan eyes, gentle smile |
| hana_sprite.png | Hana (Architect) | Huge head, blue jumpsuit, OVERSIZED wrench (right side, 22px tall), pistol (left hand, visible), bright goggles on forehead, brown ponytail, big cyan eyes, confident grin |

### Enemies (32x32 PNG, transparent background)

| File | Enemy | Visual Description |
|------|-------|-------------------|
| zombie_sprite.png | Zombie | Gray-green skin, torn brown clothes, asymmetric shambling pose, glowing red eyes (2px), visible bones/wounds, dark outline, clearly hostile |

### Base (64x64 PNG, transparent background)

| File | Description |
|------|-------------|
| base.png | Fortified bunker/shelter. Metal plating walls, small antenna on top, reinforced door, Duskwall emblem (simple shield shape). Warm interior glow from windows. Post-apocalyptic but maintained. |

### Structures (16x16 PNG, transparent background)

| File | Description |
|------|-------------|
| wall.png | Rusted metal barricade. Vertical corrugated metal sheet, rivets visible, slight lean. Brown/gray palette. |
| barricade.png | Sandbags + scrap metal. Stacked sandbags (tan) with metal scrap on top. Low profile defensive structure. |

### Map Tiles (16x16 PNG, opaque)

| File | Description |
|------|-------------|
| dirt.png | Cracked dry brown ground. 2-3 visible crack lines. Base terrain tile. |
| dead_grass.png | Dirt base with sparse yellowed grass tufts (3-4 clumps). |
| rubble.png | Small rocks and concrete debris scattered on dirt. Gray on brown. |
| road_cracked.png | Dark gray asphalt with crack pattern. Faded road markings optional. |
| rust_metal.png | Ground with rusted metal scraps embedded. Orange-brown accents on dirt. |
| dead_tree.png | Leafless trunk with 2-3 bare branches. Dark brown on transparent. Decorative overlay tile. |
| bridge_h.png | Horizontal wooden plank bridge segment. Weathered brown planks with rope/nail details. For crossing gaps. |
| bridge_v.png | Vertical wooden plank bridge segment. Same style rotated for north-south crossings. |

## File Locations

All assets go into `godot/assets/` with this structure:

```
godot/assets/
  aria/
    rex_sprite.png
    aurora_sprite.png
    lily_sprite.png
    hana_sprite.png
  enemies/
    zombie_sprite.png
  structures/
    base.png
    wall.png
    barricade.png
  tiles/
    dirt.png
    dead_grass.png
    rubble.png
    road_cracked.png
    rust_metal.png
    dead_tree.png
    bridge_h.png
    bridge_v.png
```

## Integration Notes

- Robot.tscn currently hardcodes `robot_architect.png`. After new sprites are created, Robot.gd should load the correct sprite from the config JSON path or from the new `godot/assets/aria/` directory.
- Zombie.tscn references `placeholder/zombie.png`. Update to new path.
- Map.tscn references `placeholder/base.png`. Update to new path.
- The placeholder directory can be kept as fallback but new sprites take priority.
- Sprite sizes changed: robots 32->48, base stays 64. Collision shapes and health bar offsets may need adjustment.
- Robot JSON data paths (`res://assets/robots/rex/sprite.png`) should be updated to match the new file structure, or Robot.gd can map class->sprite directly.

## Technical Constraints

- All PNGs use 8-bit RGBA
- No anti-aliasing -- hard pixel edges only
- Transparent backgrounds on all sprites (except map tiles)
- Each sprite should read clearly at 1x and 2x zoom
- Silhouettes must be distinguishable -- you can tell the class from shape alone without color
