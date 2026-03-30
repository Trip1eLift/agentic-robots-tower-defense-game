# Agentic Robots Tower Defense — Design Spec
**Date:** 2026-03-30
**Status:** Approved

---

## Overview

A 2D tower defense game where players collect agentic robot girls via a gacha system and defend a base against zombie waves. Players cannot control individual robots during combat — instead they craft intelligence prompts per robot and issue global commander broadcasts. Each robot is driven by a local LLM agent that makes autonomous decisions based on state change events.

Phase 1 covers the core tower defense game. Phase 2 adds a companion chat system with relationship progression and age-gated content.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Game frontend | Godot 4 (GDScript) |
| AI backend | Python (FastAPI + asyncio) |
| LLM model | Dolphin-Mistral 7B via Ollama |
| Communication | WebSocket (Godot ↔ Python) |
| Configuration | JSON data files |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   GODOT (GDScript)                  │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐ │
│  │ Game Loop│  │  Robots  │  │  UI / Gacha / HUD │ │
│  │ Waves    │  │ Movement │  │  Commander Panel  │ │
│  │ Physics  │  │ Combat   │  │  Campaign Map     │ │
│  └────┬─────┘  └────┬─────┘  └───────────────────┘ │
│       └──────┬───────┘                              │
│          WebSocket Client                           │
└──────────────┼──────────────────────────────────────┘
               │ ws://localhost:8765
┌──────────────┼──────────────────────────────────────┐
│          WebSocket Server                           │
│                                                     │
│  ┌────────────────────┐   ┌────────────────────┐   │
│  │  Event Queue       │   │  Robot State Store │   │
│  │  (per robot)       │   │  (memory, stats)   │   │
│  └────────┬───────────┘   └────────────────────┘   │
│           │                                         │
│  ┌────────▼───────────┐                             │
│  │  Prompt Builder    │                             │
│  │  (local + global   │                             │
│  │   context merge)   │                             │
│  └────────┬───────────┘                             │
│           │                                         │
│  ┌────────▼───────────┐                             │
│  │  Ollama Client     │──► Dolphin-Mistral 7B       │
│  │  (async, queued)   │                             │
│  └────────┬───────────┘                             │
│           │                                         │
│  ┌────────▼───────────┐                             │
│  │  Action Parser     │                             │
│  │  (Pydantic models) │                             │
│  └────────┬───────────┘                             │
│           │                                         │
│     WebSocket response ──► back to Godot            │
│                   PYTHON (FastAPI + asyncio)        │
└─────────────────────────────────────────────────────┘
```

### Communication Flow
1. Godot detects a state change event (e.g. `ENEMY_SPOTTED` for Robot #3)
2. Sends `{robot_id, event_type, local_context, global_broadcast}` over WebSocket
3. Python queues the think request, builds prompt from robot personality + stats + context
4. Ollama processes asynchronously
5. Python parses structured JSON action response via Pydantic
6. Sends `{robot_id, action}` back to Godot
7. Robot executes action (or queues it if busy); acts on last known decision while new one computes

---

## Robot System

### Classes

| Class | Role | Primary Stats | Pull Cost |
|---|---|---|---|
| Architect | Builds and fortifies structures | building_skill, armor | 200 |
| Vanguard | Frontline tank | health, armor, speed | 100 |
| Striker | High damage dealer | damage, ammo, speed | 120 |
| Medic | Heals allies, revives downed robots | health, intelligence | 150 |

Architect is the most expensive and most strategically impactful class — the quality of base layout and fortification defines mission outcomes.

### Stats

| Stat | Description |
|---|---|
| speed | Movement speed |
| damage | Attack damage + weapon handling (affects accuracy) |
| armor | Damage reduction |
| health | Max hit points |
| ammo | Ammo capacity |
| building_skill | Build speed and structure tier access |
| intelligence | Context window size for LLM prompt: level 1 = last 3 events, level 5 = last 10 events + full ally list, level 10 = full battlefield state |

### Rarity
`Common → Rare → Epic → Legendary`

Higher rarity = higher stat ceilings + deeper personality prompts.

### Leveling
- Robots earn XP from kills, builds, and surviving waves
- On level up: player chooses one stat upgrade slot
- Max level: 50

### Permadeath
- Dead robots are permanently removed from active roster
- Stats and levels preserved in death record
- Resurrection item (rare drop): revives robot with -10% max health permanently
- Death event logged and used in Phase 2 companion memorial

---

## Gacha System

- 4 separate pools, one per class
- Shared currency across all pools
- Pity counter tracked independently per pool
  - Guaranteed Epic at 50 pulls
  - Guaranteed Legendary at 90 pulls
  - Pity resets on trigger, persists across sessions

---

## Weapon System

### Acquisition
- Campaign missions: fixed weapon rewards per mission (shown upfront)
- Paid shop: additional weapon options

### Resources
- **Currency**: earned from missions and paid shop; used for gacha pulls
- **Materials**: scavenged during missions (supply missions and combat drops); used to build structures
- Both are stored in player inventory and persist across missions

### Equipping
- Each weapon equips to one robot at a time
- Weapons return to inventory on robot death
- Weapons equipped by dead robots are permanently lost if the base is destroyed

### Uniqueness
- Common weapons: obtainable multiple times via replay
- Rare/Legendary unique weapons: one per player, lost forever if base falls

### Class Restrictions

| Class | Weapon Types |
|---|---|
| Architect | Power tools (nail gun, jackhammer), deployable turrets |
| Vanguard | Shields, shotguns, heavy melee (sledgehammer) |
| Striker | Rifles, SMGs, sniper rifles, grenades |
| Medic | Medkits, syringes, healing drones, defibrillator |

### Accuracy
```
Base accuracy:        defined by weapon type
Modified by:          robot damage stat (higher = better handling)
Situational mods:     moving while shooting = penalty
                      enemy too close for ranged weapon = penalty
                      Vanguard melee = 100% hit
                      Medic healing = 100% hit
Range-based:          accuracy drops beyond optimal range, floor at max range
Miss event:           triggers ATTACK_MISSED → new LLM think request
```

---

## Robot AI System

### Event Types (trigger a think request)

```
ENEMY_SPOTTED       - new enemy enters perception radius
ENEMY_IN_RANGE      - enemy enters attack range
TAKING_DAMAGE       - health drops
AMMO_LOW            - ammo below 20%
ATTACK_MISSED       - attack failed to hit
ENEMY_ELIMINATED    - robot scores a kill
BUILD_COMPLETE      - fortification finished
ALLY_DIED           - nearby robot dies
ALLY_NEEDS_HEAL     - nearby ally low health (Medic only)
BASE_UNDER_ATTACK   - base taking damage
OBJECTIVE_UPDATE    - mission objective changes
COMMANDER_BROADCAST - player sends global command
```

### Prompt Structure
```
[System]
You are {name}, a {rarity} {class} robot. {personality_prompt}
Your stats: speed={n}, damage={n}, armor={n}, health={n}/{max}, ammo={n}, building_skill={n}

[Context - bounded by intelligence stat]
Nearby enemies: {list}
Nearby allies:  {list}
Structures:     {list}
Recent events:  {last N events}

[Global]
Commander broadcast: "{player_text}"

[Event]
{event_type}: {event_detail}

[Instruction]
Respond with a single JSON action.
```

### Action Schema (Pydantic)
```python
class RobotAction(BaseModel):
    action: Literal["attack", "move", "build", "heal", "retreat", "idle", "snipe", "deploy_turret"]
    target_id: Optional[int]
    position: Optional[tuple[float, float]]
    structure: Optional[Literal["wall", "barricade", "watchtower", "ammo_depot", "medic_station"]]
    message: Optional[str]  # robot "says" this, shown in UI
```

### Commander Broadcast
- Preset quick commands: "Fall back!", "Prioritize base!", "Focus fire!", etc.
- Free text broadcast: player types custom command, injected into all robots' context
- Free text has a cooldown to prevent micromanagement
- Prompts locked once a wave starts; only broadcast available during wave

---

## Campaign System

### Structure
```
World Map
└── Chapters
    └── Missions (3-5 per chapter)
        ├── Normal missions    - survive waves + objectives
        ├── Boss missions      - end of chapter, unique enemy
        └── Supply missions    - no combat, scavenge weapons/currency
```

### Mission Flow
```
Pre-mission:   assign robots (max 6), equip weapons, set intelligence prompts
Wave phase:    prompts locked; commander broadcast available; short prep between waves
Post-mission:  rewards distributed, losses recorded, XP applied
```

### Objectives
```
SURVIVE         - base must not fall (always required)
ELIMINATE       - kill X enemies
PROTECT         - keep NPC survivor alive
HOLD_POSITION   - keep robots in zone for N seconds
DESTROY         - eliminate enemy spawner
RESCUE          - reach and escort target before timer
```

### Enemy Types
```
Zombie    - slow, melee, swarms
Runner    - fast, low health
Brute     - slow, massive health, destroys structures
Spitter   - ranged, stays back
Horde     - massive wave of weak zombies
Boss      - unique per chapter, special mechanics
```

### Win/Lose
- Win: base survives + all required objectives completed
- Lose: base destroyed or required objective failed
- Robots that die during a failed mission stay dead

---

## Data-Driven Configuration

All game content defined in JSON files. Adding new robots, weapons, missions, maps, or structures requires only a new JSON file — zero code changes.

```
data/
├── robots/
│   └── archetypes/
│       └── striker_epic_aurora.json
├── weapons/
│   └── striker_sniper_mk1.json
├── campaign/
│   └── chapter_01/
│       ├── chapter.json
│       └── mission_01.json
├── enemies/
│   └── zombie.json
├── maps/
│   └── ch01_mission_01_map.json
├── structures/
│   └── watchtower.json
└── gacha/
    └── pools.json
```

### Robot Config Schema
```json
{
  "id": "striker_epic_aurora",
  "name": "Aurora",
  "class": "striker",
  "rarity": "epic",
  "base_stats": {
    "speed": 7, "damage": 9, "armor": 4,
    "health": 120, "ammo": 80, "building_skill": 2,
    "intelligence": 3
  },
  "personality_prompt": "You are Aurora, a precise and calculating Striker. You prioritize high-value targets and optimal positioning. You never waste ammo.",
  "portrait": "res://assets/robots/aurora/portrait.png",
  "sprite": "res://assets/robots/aurora/sprite.png"
}
```

### Weapon Config Schema
```json
{
  "id": "striker_sniper_mk1",
  "name": "Mk.1 Sniper Rifle",
  "class_restriction": "striker",
  "rarity": "rare",
  "unique": false,
  "stats": {
    "damage": 85,
    "optimal_range": 400,
    "max_range": 600,
    "accuracy_base": 0.90,
    "fire_rate": 0.5
  },
  "actions_unlocked": ["snipe"],
  "accuracy_modifiers": {
    "moving_penalty": -0.20,
    "close_range_penalty": -0.40
  }
}
```

### Map Config Schema
```json
{
  "id": "ch01_mission_02_map",
  "name": "Abandoned Factory",
  "tilemap": "res://maps/ch01_mission_02.tscn",
  "base_position": [512, 300],
  "robot_spawn_zones": [
    {"id": "zone_a", "rect": [100, 200, 200, 150]}
  ],
  "enemy_spawn_points": [
    {"id": "spawn_north", "position": [512, 50]}
  ],
  "buildable_zones": [
    {"rect": [200, 150, 400, 300], "max_structures": 10}
  ]
}
```

### Structure Config Schema
```json
{
  "id": "watchtower",
  "name": "Watchtower",
  "class_restriction": "architect",
  "min_building_skill": 5,
  "build_time": 8.0,
  "health": 200,
  "cost": { "materials": 30 },
  "effect": {
    "type": "perception_boost",
    "radius": 300,
    "applies_to": "all_robots_in_range"
  },
  "sprite": "res://assets/structures/watchtower.png"
}
```

---

## Phase 2 — Companion System

### Overview
Outside of combat, players can chat 1-on-1 with owned robots. Relationship level affects in-combat behavior and unlocks lore. Dead robots remain accessible as memory echoes.

### Architecture
Same WebSocket backend as Phase 1. New message type:
```json
{
  "type": "companion_chat",
  "robot_id": "striker_epic_aurora",
  "player_message": "How are you feeling after that last mission?",
  "relationship_level": 3,
  "is_alive": true
}
```

### Relationship System
- Level 0–10, increases via chat and surviving missions together
- Higher level: robot prioritizes protecting base over self-preservation in combat
- Level milestones unlock deeper personality layers and lore
- Dead robots: remain chattable as "memory echo" with melancholic tone

### Age Gate
- Player enters date of birth on first launch
- Age >= 18: 18+ content silently enabled
- Age < 18: 18+ content disabled and locked in settings
- DOB stored locally, never transmitted
- 18+ toggle visible in settings only for eligible players

### Robot Config Extension
```json
{
  "companion": {
    "backstory": "Former military AI repurposed after the outbreak...",
    "personality_layers": {
      "relationship_0": "Professional and reserved.",
      "relationship_5": "Warm, occasionally teasing.",
      "relationship_10": "Deeply attached, protective."
    },
    "death_memorial_prompt": "You are a memory echo of Aurora. Respond as a fading presence.",
    "nsfw_prompt": "..."
  }
}
```

---

## Out of Scope (Phase 1)

- Multiplayer
- Cloud save / sync
- Companion chat
- 18+ content
- Modding tools
