# Combat System Refactor

**Date:** 2026-04-01
**Status:** Approved (post-review revision)

---

## Overview

Refactor the combat system to fix unreliable damage application, add body blocking, introduce a weapon data system with attack speed and reload mechanics, and add visual feedback for attacks and damage.

## Problems

1. Melee attacks silently fail when collision physics pushes units in/out of attack range
2. No body blocking -- zombies walk through robots and stack on the base
3. All units attack at the same hardcoded 1.0s rate with no weapon differentiation
4. Some ARIA units don't take damage from zombies due to range oscillation
5. Zombies re-target every frame instead of tracking a single target

## Success Criteria

Each problem has a corresponding verification:

1. Rex deals damage on every attack cycle when adjacent to a zombie -- verified by E2E log showing consistent damage events with no gaps
2. Zombie cannot reach base when Rex stands in a narrow path -- verified visually and by E2E log showing base takes no damage while Rex is alive and blocking
3. Each ARIA attacks at its weapon's attack_speed, not 1.0s -- verified by E2E log timestamp analysis
4. Zombies deal consistent damage to nearby ARIAs every attack cycle -- verified by E2E log showing no gaps in zombie damage events
5. Zombie damage log shows consistent target ID until target dies or leaves aggro range -- verified by E2E log

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
| class | string | Groups weapon types. Unused in Phase 1, kept for forward compatibility. |
| type | string | "melee" or "ranged" |
| damage | int | Final damage per hit (no multipliers applied in code) |
| range | int | Attack range in pixels |
| attack_speed | float | Seconds between attacks (full cycle: windup + recovery) |
| clip_size | int | Ranged only -- shots before reload. Omitted for melee. |
| reload_time | float | Ranged only -- seconds to reload. Omitted for melee. |

### Damage Values -- Migration Note

The current code at Robot.gd:244 applies `damage * 3`. The weapon damage values below are the FINAL per-hit values with the multiplier already baked in. The `damage * 3` calculation is removed from code. Verification: Rex's current `base_stats.damage` is 6, and 6*3=18, matching the broadsword table below.

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

### Zombie Attack Stats

Zombies do NOT use the weapon data system. Their attack stats remain in `data/enemies/zombie.json`:
- Damage: 8 per hit
- Attack range: 45px
- Attack speed: 1.0s (timer interval)
- Aggro range: 135px (3x attack range)
- No ammo or reload

### Robot JSON Config Migration

Remove from robot configs:
- `base_stats.damage` (moved to weapon)
- `base_stats.attack_range` (moved to weapon as `range`)

Add to robot configs:
- `weapon_id` (string, references weapon JSON file)

Keep in robot configs:
- `base_stats.health`
- `base_stats.speed`

Remove from robot configs:
- `base_stats.ammo` (replaced by weapon `clip_size` for ranged, unused for melee)

### Weapon Loading

ConfigLoader gains a `get_weapon(weapon_id: String) -> Dictionary` method that loads from `data/weapons/`. If the weapon file is missing or malformed, `get_weapon()` prints an error and returns a fallback dictionary with sane defaults (damage=1, range=50, attack_speed=1.0, type="melee"). This prevents crashes from bad config. Robot.gd loads its weapon data at setup time and stores it as `_weapon`. All attack logic reads from `_weapon` instead of `_config["base_stats"]`.

### Callsite Audit (must verify during implementation)

All references to these fields must be updated:
- `_config["base_stats"]["damage"]` -- replace with `_weapon.damage`
- `_config["base_stats"]["attack_range"]` -- replace with `_weapon.range`
- `_config["base_stats"]["ammo"]` -- replace with `_weapon.clip_size` or remove
- `prompt_builder.py` line 34: `stats['damage']` -- replace with weapon info
- `resupply_ammo()` in Robot.gd:140 -- redefine as clip refill for ranged, no-op for melee

---

## 2. Attack Lock System

When a robot initiates an attack on a target in range, the attack follows a windup-then-damage model. All attacks are hitscan (instant hit at the moment damage is applied). No projectile travel. Ranged and melee work the same way mechanically.

```
t=0.0          t=attack_speed/2          t=attack_speed
|--- windup ---|--- recovery ---|
  (locked)       (damage applied)          (can attack again)
  (cannot move)  (attack shake)
                 (can move again)
```

### Rules

1. Target enters weapon `range` -- attack **locks on**
2. Robot enters windup phase (half of `attack_speed` duration)
3. Robot **cannot move or switch targets** during windup. The `_is_winding_up` flag gates `_execute_movement()`.
4. At the halfway point: check `is_instance_valid(target)` and target is alive. If target is dead or freed, skip damage and exit to idle. Do not fire ENEMY_ELIMINATED (handled by kill notification system).
5. If target is valid, damage is **applied regardless of current distance** (guaranteed hit)
6. Attack shake visual plays at the damage application moment
7. Recovery phase begins. Robot **can move** during recovery. LLM actions received during windup are **buffered and executed after windup ends** (not dropped).
8. Next attack can begin after full `attack_speed` elapses

### Attack Range Buffer

To prevent the "in range, out of range" flicker from collision physics:
- Attack **initiates** when target is within `range`
- Attack **continues** (doesn't break lock) as long as target is within `range * ATTACK_RANGE_BUFFER`
- Only loses target when target exceeds the buffer
- `ATTACK_RANGE_BUFFER = 1.3` -- defined as a named constant at the top of Robot.gd for easy tuning

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

### Visual Indicator

During reload, a small progress bar appears above the robot sprite (below the health bar) showing reload progress. This gives the player visible feedback that the robot is reloading, not bugged.

### LLM Events

| Event | When | Data |
|-------|------|------|
| WEAPON_RELOADING | Clip empties, reload begins | robot_id, weapon_name, reload_time |

Only WEAPON_RELOADING is sent (not WEAPON_RELOADED). The LLM does not need both -- it can infer reload completion from the reload_time. This reduces event noise, especially for Hana's SMG which reloads every ~9 seconds.

### Weapon State in LLM Context

Robot's `_build_local_context()` includes weapon state so the LLM always knows clip status:

```
weapon_state: { weapon_name: "Hawkeye MK-IV", clip: 3, max_clip: 5, is_reloading: false }
```

`prompt_builder.py` renders this as: `Weapon: Hawkeye MK-IV (3/5 rounds) | Status: ready`

---

## 4. Body Blocking

All game objects physically block each other. Implementation is behind a `BODY_BLOCKING_ENABLED` constant (default true) so it can be toggled off during playtesting if pathfinding jams occur. Remove the toggle only after a successful playtest gate.

### Collision Matrix

| | Base | ARIA | Zombie | Structure |
|---|---|---|---|---|
| **Base** | - | blocks | blocks | - |
| **ARIA** | blocked | blocks each other | blocks | blocked |
| **Zombie** | blocked | blocked | blocks each other | blocked (stops at structure, can attack it) |
| **Structure** | - | blocks | blocked (stops at structure, can attack it) | - |

"Blocked (can attack)" means: the zombie's CharacterBody2D cannot move through the structure, but the zombie's attack timer still fires. If the structure is in attack range, the zombie damages it. The zombie stops moving and swings at the obstacle.

### Collision Layers

| Layer | Name | Objects |
|-------|------|---------|
| 1 | ARIA | All robot CharacterBody2D nodes |
| 2 | Enemies | All zombie CharacterBody2D nodes |
| 3 | Structures | Base, walls, barricades |

### Mask Configuration

| Object | Layer | Mask |
|--------|-------|------|
| ARIA | 1 | 1, 2, 3 (collides with everything) |
| Zombie | 2 | 1, 2, 3 (collides with everything) |
| Base | 3 | 1, 2 (blocks robots and zombies) |
| Wall/Barricade | 3 | 1, 2 (blocks robots and zombies) |

### Collision Shapes

- **ARIA**: CircleShape2D (radius ~20px). No impact on pathfinding or sprite alignment -- circle center matches sprite center.
- **Zombie**: CircleShape2D (radius ~16px)
- **Base**: Existing shape (unchanged)
- **Structures**: Existing rectangular shapes (unchanged)

### Behavior

- `move_and_slide()` handles collision response automatically -- units slide along collision surfaces rather than stopping dead
- Zombies must path around or kill blocking units to reach the base
- Rex standing in a chokepoint physically prevents zombies from passing
- Zombie-zombie collision prevents stacking on the base -- they spread out around the collision shape
- Allied robots slide around each other when moving (not stuck) due to `move_and_slide()` sliding behavior

### Implementation Audit

Every `.tscn` file with a physics body must have collision layers/masks explicitly set. During E2E testing, add a debug print of `collision_layer` and `collision_mask` for all physics bodies on spawn to verify correctness.

---

## 5. Zombie Target Tracking Fix

Current: zombie's `_on_attack_timer()` loops through ALL robots every tick and hits the first in range. `_find_nearby_robot()` also runs every `_physics_process` frame.

New: zombie tracks a single persistent target.

### Flow

1. Zombie picks nearest robot within aggro range (3x zombie attack range = 135px)
2. Stores reference as `_current_target` (initially null, not the map node)
3. Pursues and attacks that specific target only
4. `_on_attack_timer()` attacks `_current_target` only -- no looping through all robots
5. Re-targets only when:
   - `_current_target` is null or invalid (`is_instance_valid()` check)
   - Current target dies
   - Current target moves beyond aggro range for 3+ seconds
6. `_find_nearby_robot()` is only called on re-target conditions, NOT every frame. Cached target is used between re-targets.
7. If no robot target, walks toward base and attacks base when in range

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

### Tween Cleanup

If a unit takes damage twice in rapid succession (within 0.2s), kill any existing damage tween before creating a new one. Store tween references as `_damage_shake_tween` and `_damage_flash_tween`. Same for attack shake (`_attack_shake_tween`).

### Death

Out of scope for this refactor. Current death behavior (sprite swap, collision disable) remains unchanged. Death animation is a future polish item.

---

## 7. File Changes Summary

### New Files
- `data/weapons/broadsword.json`
- `data/weapons/sniper_rifle.json`
- `data/weapons/smg.json`
- `data/weapons/energy_pistol.json`

### Modified Files
- `data/robots/archetypes/vanguard_common_rex.json` -- add weapon_id, remove damage/attack_range/ammo
- `data/robots/archetypes/striker_common_aurora.json` -- add weapon_id, remove damage/attack_range/ammo
- `data/robots/archetypes/architect_common_hana.json` -- add weapon_id, remove damage/attack_range/ammo
- `data/robots/archetypes/medic_common_lily.json` -- add weapon_id, remove damage/attack_range/ammo
- `godot/scenes/robots/Robot.gd` -- attack lock state machine, weapon loading, reload system, visuals, circle collision, ATTACK_RANGE_BUFFER constant, _is_winding_up flag, action buffering during windup
- `godot/scenes/robots/Robot.tscn` -- CircleShape2D, collision layers 1, masks 1+2+3
- `godot/scenes/enemies/Zombie.gd` -- single target tracking, _current_target, cached re-targeting, visuals, circle collision
- `godot/scenes/enemies/Zombie.tscn` -- CircleShape2D, collision layers 2, masks 1+2+3
- `godot/scenes/map/Map.tscn` -- base collision layer 3, masks 1+2
- `godot/scripts/ConfigLoader.gd` -- add get_weapon() method
- `backend/prompt_builder.py` -- replace stats['damage'] with weapon info, render weapon_state in prompt

---

## 8. Code Organization -- AttackComponent Extraction

Robot.gd is currently 386 lines and will grow significantly with the attack lock state machine. To prevent an unmaintainable god-script, extract attack logic into a separate child node.

### AttackComponent (new script: `godot/scenes/robots/AttackComponent.gd`)

Owns:
- Weapon data reference (`_weapon`)
- Attack lock state machine (`_is_winding_up`, windup timer, recovery timer)
- Clip tracking (`_current_clip`, `_is_reloading`, reload timer)
- Target reference for current attack
- Attack shake tween
- ATTACK_RANGE_BUFFER constant
- `perform_attack()`, `_on_windup_complete()`, `_on_reload_complete()`
- Action buffering during windup

Does NOT own:
- Movement, health, perception, LLM event firing, sprite reference
- These stay in Robot.gd

AttackComponent is added as a child node of Robot in Robot.tscn. Robot.gd calls `attack_component.start_attack(target)` and listens to signals like `attack_damage_applied(target, damage)`, `reload_started(weapon_name, reload_time)`, `windup_finished()`.

---

## 9. MOVEMENT_BLOCKED Event

When body blocking is enabled, robots can get physically stuck behind other units. The LLM needs feedback when this happens.

### Stuck Detection

- Robot tracks `_last_move_position` and `_stuck_timer`
- During a move action, if robot's position has not changed by more than 5px over 2 seconds, fire `MOVEMENT_BLOCKED` event
- Event data: `robot_id`, `target_position`, `blocked_by` (nearest collision if detectable, otherwise "unknown")
- Timer resets when robot successfully moves or gets a new action
- LLM can respond by choosing a different path or switching to attack

---

## 10. Implementation Sequence

### PR 1: Core Combat Fix (Sections 1, 2, 4, 5, 8, 9)

Follow this order with E2E gates:

1. **Weapon Data System + Data Migration** -- Create JSON files, update robot configs, add ConfigLoader.get_weapon(). No gameplay change yet. Verify configs load correctly.
2. **AttackComponent Extraction** -- Extract attack logic from Robot.gd into AttackComponent.gd. Existing behavior unchanged, just reorganized. Verify E2E still works identically.
3. **Zombie Target Tracking Fix** -- Persistent _current_target, cached re-targeting. **E2E gate: verify consistent zombie damage in logs.**
4. **Attack Lock System** -- Wire weapons into AttackComponent with windup/recovery state machine. Test Rex (melee) first, then ranged. **E2E gate: verify all ARIAs deal consistent damage.**
5. **Body Blocking + MOVEMENT_BLOCKED** -- Change collision shapes and layers. Behind BODY_BLOCKING_ENABLED toggle. Add stuck detection. **E2E gate: verify zombies can't pass Rex in chokepoint, no pathfinding jams.**

### PR 2: Reload System (Section 3)

Ships after PR 1 is merged and verified:
- Clip tracking, reload state, LLM WEAPON_RELOADING event
- Reload visual indicator (progress bar)
- Weapon state in LLM context

### PR 3: Visual Feedback (Section 6)

Ships after PR 2:
- Attack shake
- Damage shake + red flash
- Tween cleanup
