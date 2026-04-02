# Combat System Refactor

**Date:** 2026-04-01
**Status:** Approved

---

## Overview

Refactor the combat system to fix unreliable damage application, add body blocking, introduce a weapon data system with attack speed and reload mechanics, and add visual feedback for attacks and damage.

## Problems

1. Melee attacks silently fail when collision physics pushes units in/out of attack range
2. No body blocking -- zombies walk through robots and stack on the base
3. All units attack at the same hardcoded 1.0s rate with no weapon differentiation
4. Some ARIA units don't take damage from zombies due to range oscillation
5. Zombies re-target every frame instead of tracking a single target

---

## 1. Weapon Data System

Weapons are separate JSON files in `data/weapons/`. Each ARIA's robot config gets a `weapon_id` field pointing to their default weapon.

### Weapon Schema

```json
{
  "id": "sniper_rifle",
  "name": "Hawkeye MK-IV",
  "class": "sniper_rifle",
  "type": "ranged",
  "damage": 27,
  "range": 200,
  "attack_speed": 2.0,
  "clip_size": 5,
  "reload_time": 3.0
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier, matches filename |
| name | string | Display name for UI and LLM context |
| class | string | Groups weapon types (e.g. multiple sniper rifles share "sniper_rifle" class) |
| type | string | "melee" or "ranged" |
| damage | int | Damage per hit |
| range | int | Attack range in pixels |
| attack_speed | float | Seconds between attacks (full cycle: windup + recovery) |
| clip_size | int | Ranged only -- shots before reload. Omitted for melee. |
| reload_time | float | Ranged only -- seconds to reload. Omitted for melee. |

### Default Weapons

| Weapon File | Name | Class | Type | Damage | Range | Speed | Clip | Reload |
|-------------|------|-------|------|--------|-------|-------|------|--------|
| broadsword.json | Vanguard Broadsword | broadsword | melee | 18 | 60 | 1.5s | - | - |
| sniper_rifle.json | Hawkeye MK-IV | sniper_rifle | ranged | 27 | 200 | 2.0s | 5 | 3.0s |
| smg.json | Ironworks SMG | smg | ranged | 6 | 80 | 0.3s | 30 | 2.0s |
| energy_pistol.json | Medi-Pulse Pistol | energy_pistol | ranged | 8 | 60 | 0.8s | 12 | 1.5s |

### ARIA-Weapon Assignment

| ARIA | Default Weapon |
|------|---------------|
| Rex (Vanguard) | broadsword |
| Aurora (Striker) | sniper_rifle |
| Hana (Architect) | smg |
| Lily (Medic) | energy_pistol |

Robot JSON configs updated with `"weapon_id": "broadsword"` etc. The `damage`, `range`, and `attack_speed` stats move from the robot config to the weapon config. Robot config retains `health`, `speed`, `ammo` (ammo becomes irrelevant for melee, kept for backwards compat).

### Weapon Loading

ConfigLoader gains a `get_weapon(weapon_id)` method that loads from `data/weapons/`. Robot.gd loads its weapon data at setup time and stores it. All attack logic reads from the weapon data instead of robot base stats.

---

## 2. Attack Lock System (LoL-style)

When a robot initiates an attack on a target in range:

```
t=0.0          t=attack_speed/2          t=attack_speed
|--- windup ---|--- recovery ---|
  (locked)       (damage applied)          (can attack again)
  (cannot move)  (attack shake)
```

### Rules

1. Target enters weapon range -- attack **locks on**
2. Robot enters windup phase (half of `attack_speed` duration)
3. Robot **cannot move or switch targets** during windup
4. At the halfway point, damage is **applied regardless of current distance** (guaranteed hit)
5. Attack shake visual plays at the damage application moment
6. Recovery phase begins (remaining half of `attack_speed`)
7. Robot can move again after damage applies (during recovery)
8. Next attack can begin after full `attack_speed` elapses

### Attack Range Buffer

To prevent the "in range, out of range" flicker from collision physics:
- Attack **initiates** when target is within `range`
- Attack **continues** (doesn't break lock) as long as target is within `range * 1.3`
- Only loses target when target exceeds the 1.3x buffer

This applies to both the initial lock-on check and the auto-attack re-engagement check.

---

## 3. Reload System

Ranged weapons track current ammo in clip. Melee weapons skip this entirely.

### Flow

1. Each shot decrements `current_clip` by 1
2. When `current_clip` reaches 0, robot enters "reloading" state
3. Robot cannot attack for `reload_time` seconds
4. After reload completes, `current_clip` resets to `clip_size`
5. Reload starts automatically -- no LLM decision needed

### LLM Events

| Event | When | Data |
|-------|------|------|
| WEAPON_RELOADING | Clip empties, reload begins | robot_id, weapon_name, reload_time |
| WEAPON_RELOADED | Reload completes | robot_id, weapon_name, clip_size |

These events allow the LLM to make tactical decisions (e.g. order Rex to cover Aurora while she reloads).

---

## 4. Body Blocking

All game objects physically block each other according to this matrix:

| | Base | ARIA | Zombie | Structure |
|---|---|---|---|---|
| **Base** | - | blocks | blocks | - |
| **ARIA** | blocked | blocks each other | blocks | blocked |
| **Zombie** | blocked | blocked | blocks each other | blocked (can attack) |
| **Structure** | - | blocks | blocked (can attack) | - |

### Collision Layers

| Layer | Name | Objects |
|-------|------|---------|
| 1 | ARIA | All robot CharacterBody2D nodes |
| 2 | Enemies | All zombie CharacterBody2D nodes |
| 3 | Structures | Base, walls, barricades (StaticBody2D or Area2D) |

### Mask Configuration

| Object | Layer | Mask |
|--------|-------|------|
| ARIA | 1 | 1, 2, 3 (collides with everything) |
| Zombie | 2 | 1, 2, 3 (collides with everything) |
| Base | 3 | 1, 2 (blocks robots and zombies) |
| Wall/Barricade | 3 | 1, 2 (blocks robots and zombies) |

### Collision Shapes

- **ARIA**: CircleShape2D (radius ~20px)
- **Zombie**: CircleShape2D (radius ~16px)
- **Base**: Existing shape (unchanged)
- **Structures**: Existing rectangular shapes (unchanged)

### Behavior

- Zombies must path around or kill blocking units to reach the base
- Rex standing in a chokepoint physically prevents zombies from passing
- Multiple zombies spread out around a target instead of stacking
- Godot's built-in `move_and_slide()` handles the collision response automatically

---

## 5. Zombie Target Tracking Fix

Current: zombie loops through all robots every attack tick and hits the first in range.

New: zombie tracks a single persistent target.

### Flow

1. Zombie picks nearest robot within aggro range (3x attack range)
2. Stores reference as `_current_target`
3. Pursues and attacks that target specifically
4. Re-targets only when:
   - Current target dies
   - Current target moves beyond aggro range for 3+ seconds
5. If no robot target, walks toward base and attacks base when in range

This prevents the "hit random robots each tick" behavior and makes zombie damage predictable.

---

## 6. Visual Feedback

Both effects modify the **Sprite2D node only**. The parent CharacterBody2D and collision shape are never moved.

### Attack Shake

- **Trigger**: At the windup halfway point when damage is applied
- **Effect**: Quick forward-backward jolt toward the target direction
- **Amplitude**: ~3px
- **Duration**: 0.15s
- **Implementation**: Tween on Sprite2D.position, resets to Vector2.ZERO

### Damage Feedback (shake + red flash)

- **Trigger**: When `take_damage()` is called
- **Effect 1**: Rapid side-to-side oscillation (~4px amplitude, 0.2s duration). Different shake pattern than attack (lateral vs forward-backward).
- **Effect 2**: Transparent red tint overlay on the sprite. Set Sprite2D.modulate to Color(1, 0.3, 0.3, 1), tween back to Color(1, 1, 1, 1) over 0.2s.
- **Both effects play simultaneously** on damage.

---

## 7. Data Migration

### Robot JSON Changes

Remove from robot configs:
- `base_stats.damage` (moved to weapon)
- `base_stats.range` (moved to weapon)

Add to robot configs:
- `weapon_id` (string, references weapon JSON file)

Keep in robot configs:
- `base_stats.health`
- `base_stats.speed`
- `base_stats.ammo` (kept for backwards compat, ignored for melee)

### Robot.gd Changes

- Remove hardcoded `damage * 3` calculation
- Load weapon data from ConfigLoader at setup
- Replace `attack_timer.wait_time = 1.0` with weapon's `attack_speed`
- Add windup/recovery state machine for attack lock
- Add `current_clip` and `is_reloading` state for ranged weapons
- Add shake and flash visual methods
- Change collision shape from CapsuleShape2D to CircleShape2D

### Zombie.gd Changes

- Add `_current_target` persistent reference
- Fix attack to target specific robot instead of looping all
- Change collision shape from CapsuleShape2D to CircleShape2D
- Add damage flash visual
- Add attack shake visual

### GameManager.gd Changes

- No major changes -- spawn and wave logic stays the same

### ConfigLoader.gd Changes

- Add `get_weapon(weapon_id: String) -> Dictionary` method
- Load weapon JSON files from `data/weapons/`

---

## 8. File Changes Summary

### New Files
- `data/weapons/broadsword.json`
- `data/weapons/sniper_rifle.json`
- `data/weapons/smg.json`
- `data/weapons/energy_pistol.json`

### Modified Files
- `data/robots/archetypes/vanguard_common_rex.json` -- add weapon_id, remove damage/range
- `data/robots/archetypes/striker_common_aurora.json` -- add weapon_id, remove damage/range
- `data/robots/archetypes/architect_common_hana.json` -- add weapon_id, remove damage/range
- `data/robots/archetypes/medic_common_lily.json` -- add weapon_id, remove damage/range
- `godot/scenes/robots/Robot.gd` -- attack lock, reload, weapon loading, visuals, circle collision
- `godot/scenes/robots/Robot.tscn` -- CircleShape2D, collision layers/masks
- `godot/scenes/enemies/Zombie.gd` -- single target tracking, visuals, circle collision
- `godot/scenes/enemies/Zombie.tscn` -- CircleShape2D, collision layers/masks
- `godot/scenes/map/Map.tscn` -- base collision layer 3
- `godot/scripts/ConfigLoader.gd` -- add weapon loading
- `backend/prompt_builder.py` -- include weapon info in LLM context
