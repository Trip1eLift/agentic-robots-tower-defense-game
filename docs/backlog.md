# Project Backlog

## Priority

### Damage Mechanism Redesign
Current damage system is unreliable. Zombies often fail to deal damage to robots due to range check timing issues, attack timer sync, and aggro/melee range mismatches. Rex frequently takes zero damage despite being in melee.

**Root cause:** Timer-based attack (`_on_attack_timer`) combined with `_find_nearby_robot` aggro range vs `_attack_range` melee check creates windows where zombies detect robots but can't hit them, and return early without attacking the base either.

**Proposed fix:** Replace timer-based attack with collision-based or area-overlap damage. Options:
- Area2D hitbox on zombies that triggers damage on overlap
- Distance check in `_physics_process` instead of relying on Timer callbacks
- Ensure zombies always attack something when in range (no silent no-ops)

**Validation:** E2E recording must show all robots taking damage when zombies are nearby.

**Files:** `godot/scenes/enemies/Zombie.gd`, `godot/scenes/robots/Robot.gd`

### Body Blocking with A* Pathfinding
Moving objects (robots and zombies) walk through each other and through static objects. Need proper body blocking so units physically obstruct pathing -- a vanguard holding a chokepoint should force zombies to path around or pile up.

**Proposed fix:** Replace NavigationAgent2D with AStarGrid2D pathfinding. Units and structures act as obstacles that dynamically update the navigation grid. CharacterBody2D collision layers already exist but `move_and_slide` doesn't prevent overlap with same-layer bodies.

**Requirements:**
- Robots block zombie pathing (and vice versa)
- Structures (walls, barricades) block movement
- Units cannot stack on top of each other
- Pathfinding recalculates when obstacles change (unit moves, structure placed/destroyed)

**Files:** `godot/scenes/enemies/Zombie.gd`, `godot/scenes/robots/Robot.gd`, `godot/scenes/map/Map.tscn`

---

## Planned

### Campaign Progress Saving
Currently the lore screen resets the campaign every time. Players should be able to save mid-campaign and resume.

**Scope:** Mission progress, robot health/ammo carry-over, dead robots, currency.

**Notes:** CampaignManager already has save/load scaffolding to build on.

### Build Action Implementation
Hana (architect) receives "build" actions from the LLM but building is not implemented. Currently falls back to "move". Need to implement wall/barricade placement using the structure assets already generated.

### Portrait Integration in HUD
ARIA portraits exist but are only used in the pre-combat briefing. Could be shown in the in-game HUD unit cards for better visual identity.

### Tile Map Integration
Tile assets (dirt, dead grass, road, rubble, rust, bridge) are generated but the map still uses plain Node2D. Could use TileMap for proper terrain rendering.
