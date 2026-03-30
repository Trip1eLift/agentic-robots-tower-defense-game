# Project: Agentic Robots Tower Defense

## Git Workflow

**All code changes must be made on feature branches — never commit directly to `main`.**

- Create a branch before making any code changes: `git checkout -b feat/<feature-name>`
- All work goes through pull requests
- Branch naming: `feat/<feature>`, `fix/<bug>`, `chore/<task>`
- This applies to all files except documentation edits during brainstorming/planning sessions

## Tech Stack

- **Game frontend:** Godot 4 (GDScript)
- **AI backend:** Python 3.11+ (FastAPI + asyncio)
- **LLM:** Dolphin-Mistral 7B via Ollama (`ws://localhost:8765/ws`)
- **Communication:** WebSocket
- **Config:** JSON data files in `data/`

## Project Structure

```
backend/     Python AI backend
godot/       Godot 4 game project
data/        Shared JSON config files (robots, maps, missions, enemies, structures)
docs/        Design specs and implementation plans
```

## Design Docs

- Spec: `docs/superpowers/specs/2026-03-30-agentic-robots-tower-defense-design.md`
- Backend plan: `docs/superpowers/plans/2026-03-30-phase1-python-backend-plan.md`
- Godot plan: `docs/superpowers/plans/2026-03-30-phase1-godot-game-plan.md`
