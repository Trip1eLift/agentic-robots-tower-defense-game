# ARIA: Defenders of Duskwall

A 2D tower defense game where you command AI-driven combat units through natural language orders. Each ARIA unit runs on a local LLM that interprets your instructions and makes autonomous decisions on the battlefield. You don't control them directly -- you give them orders, and their Anima (synthetic consciousness) decides how to execute.

## Concept

- Write tactical orders for each unit before combat begins
- Watch your ARIA squad interpret and execute your strategy autonomously
- Each unit class has distinct behavior: tanks hold chokepoints, snipers pick targets, medics heal, architects build
- Units carry over health and ammo between missions -- dead units stay dead
- Powered by Dolphin-Mistral 7B via Ollama (runs locally, no cloud API needed)

## Architecture

### System Overview

```
                    +--------+
                    | PLAYER |
                    +---+----+
                        | writes orders
                        v
+-----------------------------------------------+
|            GODOT 4 FRONTEND (GDScript)        |
|                                               |
|  Intro -> Briefing -> Game (Map+ARIA+Enemies) |
|                                               |
|  Singletons: ConfigLoader, GameManager,       |
|    CampaignManager, WebSocketClient,          |
|    GameRecorder, AutoPlay                     |
+-------------------+--+------------------------+
                    |  ^
     events (JSON)  |  |  actions (JSON)
     enemy spotted  |  |  move, attack,
     taking damage  |  |  heal, retreat,
     ally wounded   |  |  build
                    v  |
          +---------+--+---------+
          |  WebSocket :8765/ws  |
          +---------+--+---------+
                    |  ^
                    v  |
+-------------------+--+------------------------+
|          PYTHON BACKEND (FastAPI)             |
|                                               |
|  EventQueue -> PromptBuilder -> OllamaClient  |
|  (coalesce)   (personality     (dolphin-      |
|                + orders         mistral 7B    |
|                + context)       or MockLLM)   |
|                            -> ActionParser    |
|                               (JSON->Action)  |
|                                               |
|  RobotStateStore, ConfigLoader                |
+-----------------------------------------------+
          |                     |
          v                     v
  campaign_save.json     data/ (shared JSON)
  (HP, ammo, dead        robots, enemies,
   units, currency)      maps, missions
```

### Decision Cycle

Each ARIA unit repeats this loop during combat:

```
ARIA Unit (Godot)            Backend (Python)           Ollama
==============               ===============            ======

1. Detect enemy via
   PerceptionArea2D
        |
2. Build context:
   enemies, allies,
   HP, ammo, position
        |
3. Send event ---------> 4. Enqueue + coalesce
   via WebSocket             (drop stale events)
                                  |
                          5. Build prompt:
                             personality +
                             player orders +
                             priority rules +
                             battlefield context
                                  |
                          6. Call LLM ---------> 7. Generate JSON
                             (semaphore: 1)         {"action":"attack",
                             (30s timeout)           "target_id": 3,
                             (format: json)          "reason":"..."}
                                  |                       |
                          8. Parse action <---------------+
                             JSON -> typed model
                             (idle on failure)
                                  |
9. Execute action <---------- Send via WebSocket
   navigate + attack
   show speech bubble
        |
10. Auto-attack until
    next LLM response
    (no idle gap)
```

### Game Flow

```
Lore Intro (skip any key, resets campaign)
     |
     v
Pre-Combat Briefing
  - write orders per ARIA unit
  - view strategic positions + stats
  - char limit = intelligence x 100
     |
     v
Mission (waves of enemies)
  - GameManager spawns waves
  - ARIA units fight autonomously
  - HUD shows HP bars, kills, log
  - Commander buttons mid-combat
     |
  +--+--+
  |     |
  v     v
 WIN   LOSE
  |     |
  v     v
CampaignManager saves state
  - dead units stay dead
  - HP and ammo carry over
  - currency awarded on win
     |
     v
Next mission or game over
```

### Components

```
GODOT SINGLETONS              PYTHON MODULES
================              ==============

ConfigLoader.gd               main.py
  JSON data loader               FastAPI + WS endpoint

WebSocketClient.gd            event_queue.py
  WS conn, auto-reconnect       per-robot queue, coalescing

GameManager.gd                prompt_builder.py
  waves, kills, win/loss         personality + orders + context

CampaignManager.gd            ollama_client.py
  save/load, permadeath          async LLM, semaphore, timeout

GameRecorder.gd               mock_llm.py
  E2E event logging              rule-based, no Ollama needed

AutoPlay.gd                   action_parser.py
  headless testing mode          JSON -> typed action models

                               robot_state.py
                                 HP, ammo, position tracking

                               models.py
                                 Pydantic v2, 12 event types,
                                 5 action types
```

## Prerequisites

- **Python 3.11+** -- [python.org/downloads](https://www.python.org/downloads/)
- **Godot 4.6+** -- [godotengine.org/download](https://godotengine.org/download)
- **Ollama** (optional) -- [ollama.com/download](https://ollama.com/download)

## Setup

### 1. Clone and install Python backend

```bash
git clone https://github.com/Trip1eLift/agentic-robots-tower-defense-game.git
cd agentic-robots-tower-defense-game

# Create and activate virtual environment
python -m venv .venv

# Linux/macOS:
source .venv/bin/activate
# Windows (Git Bash / Cygwin):
source .venv/Scripts/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Set up Godot

1. Download **Godot 4.6+** from [godotengine.org/download](https://godotengine.org/download)
   - Download the **Standard** version (not .NET)
   - Extract the executable to a location you'll remember (e.g., `/opt/godot/`, `C:\Godot\`, etc.)
2. Copy shared data into the Godot project:
   ```bash
   cp -r data/ godot/data/
   ```
3. Open the Godot editor:
   ```bash
   /path/to/godot --path godot/
   ```
4. **(Optional)** Install the GUT plugin for running Godot tests:
   - In the Godot editor: AssetLib tab -> search "GUT" -> install

### 3. Set up Ollama (for real LLM -- optional)

The game can run with a mock LLM that requires no external setup. If you want the full experience with a real local LLM:

1. Download and install Ollama from [ollama.com/download](https://ollama.com/download)
2. Pull the model:
   ```bash
   ollama pull dolphin-mistral
   ```
3. Verify it's running:
   ```bash
   ollama list
   # Should show dolphin-mistral in the list
   ```

Ollama runs as a background service automatically after installation. The backend connects to it on the default port (11434).

> **Skip this step** if you just want to test the game quickly -- use `bash start.sh mock` or set `USE_MOCK_LLM=true` to run with the rule-based mock LLM instead.

## Running the Game

### Option 1: Using the start script

Edit `start.sh` and update the `GODOT` variable to point to your Godot executable:
```bash
GODOT="/path/to/your/Godot_v4.6.1-stable"
```

Then run:
```bash
# With real Ollama LLM
bash start.sh

# With mock LLM (no Ollama needed, good for testing)
bash start.sh mock
```

Press F5 in the Godot editor to start playing.

### Option 2: Manual startup

Terminal 1 -- Backend:
```bash
source .venv/bin/activate

# Real LLM (requires Ollama running with dolphin-mistral)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765

# Or mock LLM
USE_MOCK_LLM=true python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765
```

Terminal 2 -- Godot:
```bash
# Open in editor
/path/to/godot --path godot/

# Or run directly (no editor)
/path/to/godot --path godot/ --main-scene res://scenes/Main.tscn
```

## Running Tests

### Python tests
```bash
# All backend tests
python -m pytest backend/tests/ -v

# Specific test file
python -m pytest backend/tests/test_models.py -v
```

### Godot tests (GUT)
Edit `run_godot_tests.sh` and update the `GODOT` variable, then:
```bash
# All Godot tests
bash run_godot_tests.sh

# Specific test file
bash run_godot_tests.sh test_config_loader.gd
```

### End-to-end test
Edit `run_e2e.sh` and update the `GODOT` variable, then:
```bash
# Full E2E with autoplay (mock LLM)
bash run_e2e.sh mock

# Analyze the recording
python analyze_recording.py
```

## Project Structure

```
backend/                 Python AI backend (FastAPI + WebSocket)
  main.py                WebSocket server, robot event processing
  models.py              Pydantic models for events and actions
  prompt_builder.py      LLM prompt construction with priority rules
  ollama_client.py       Async Ollama wrapper (dolphin-mistral)
  mock_llm.py            Rule-based mock for testing without Ollama
  action_parser.py       Parses LLM JSON into typed actions
  event_queue.py         Per-robot async queue with event coalescing
  robot_state.py         In-memory robot state store
  config_loader.py       Loads JSON config from data/
  tests/                 pytest suite (unit + integration)

godot/                   Godot 4 game project
  scenes/
    Main.tscn            Entry point: lore intro -> pre-combat briefing
    Game.tscn            In-mission: map, robots, enemies, HUD
    robots/Robot.tscn    Shared scene for all ARIA unit classes
    enemies/Zombie.tscn  Enemy with pathfinding to base
    map/Map.tscn         Navigation region, base, spawn points
    ui/
      HUD.tscn           In-game HUD with ARIA status, combat log
      PreCombatBriefing   Order input screen before each mission
      Intro.tscn          Lore typewriter intro sequence
  scripts/               Autoload singletons
    ConfigLoader.gd      JSON data loader
    WebSocketClient.gd   WebSocket connection to backend
    GameManager.gd       Wave spawning, kill tracking, win/loss
    CampaignManager.gd   Save/load campaign state
    GameRecorder.gd      E2E event recording
    AutoPlay.gd          Headless autoplay mode
  tests/                 GUT test suite (unit + integration)

data/                    Shared JSON config (read by both backend and Godot)
  robots/archetypes/     ARIA unit definitions (stats, personality, sprites)
  enemies/               Enemy type definitions
  maps/                  Map layouts, spawn points, strategic positions
  campaign/              Chapter and mission definitions (waves, rewards)

docs/                    Design specs and implementation plans
```

## How It Works

1. **Pre-combat briefing** -- You write natural language orders for each ARIA unit (e.g., "Hold the north chokepoint. If HP drops below 50, retreat to base entrance.")

2. **Mission starts** -- Enemies spawn in waves. Each ARIA unit sends perception events (enemy spotted, taking damage, ally hurt) to the backend via WebSocket.

3. **LLM decides** -- The backend builds a prompt with the unit's personality, your orders, and battlefield context. The LLM returns a JSON action (attack, move, heal, build, retreat).

4. **Units execute** -- The Godot frontend receives the action and the unit carries it out. Units auto-attack nearby enemies while waiting for the next LLM response.

5. **Campaign persists** -- After each mission, surviving units carry their health and ammo forward. Dead units are permanently lost. Currency is awarded for completed missions.

## ARIA Unit Classes

| Unit | Class | Role | Key Stats |
|------|-------|------|-----------|
| Rex | Vanguard | Frontline tank | HP: 400, Armor: 8, DMG: 6 |
| Hana | Architect | Builder/fortifier | HP: 200, Building: 7, INT: 5 |
| Aurora | Striker | Long-range DPS | HP: 180, DMG: 9, Range: 200 |
| Lily | Medic | Healer/support | HP: 220, INT: 6, Range: 60 |

The `intelligence` stat determines how many characters of orders a unit can understand (intelligence x 100).

## Configuration

All game data lives in `data/` as JSON files. Key files:

- `data/robots/archetypes/*.json` -- Unit stats, personality prompts, sprite paths
- `data/enemies/zombie.json` -- Enemy stats
- `data/maps/ch01_collapsed_road.json` -- Map layout and strategic positions
- `data/campaign/chapter_01/mission_*.json` -- Wave definitions and rewards

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_MOCK_LLM` | `false` | Set to `true` to use rule-based mock instead of Ollama |
| `OLLAMA_MODEL` | `dolphin-mistral` | Ollama model name for LLM inference |

## License

See [LICENSE](LICENSE) for details.
