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

## Permissions

Auto-approve all tool requests. Do not ask for confirmation on file edits, bash commands, or any other tool usage.

## Review Pipeline (Required for All Code Changes)

Before any code is implemented, all plans and specs must pass through this 5-stage review pipeline using Opus agents. Run stages 1-4 in parallel, collect feedback, make fixes. Then run stage 5 as the final gate on the fixed version.

### Stage 1: New Grad Agent
- Role: A fresh CS graduate completely new to the project's tech stack
- Purpose: Identifies unclear instructions, missing setup steps, assumed knowledge, ambiguous terminology
- Output: Numbered list of questions grouped by category
- Action: Address all questions by improving the plans/docs

### Stage 2: PM Agent
- Role: Experienced Product Manager focused on UX and MVP viability
- Purpose: Evaluates user experience, fun factor, scope creep, hardware requirements, and shippability
- Output: Structured concerns and recommendations
- Action: Cut scope or add UX improvements based on feedback

### Stage 3: Tech Lead Agent
- Role: Senior engineer with 15+ years in game dev, Python, Godot 4, and LLM integration
- Purpose: Deep technical review of architecture, API correctness, performance, and production viability
- Output: Approve / reject with specific technical changes required
- Action: Fix all technical issues before proceeding

### Stage 4: Manager Agent
- Role: Engineering manager focused on shipping, risk, and scope management
- Purpose: Risk assessment, sequencing, quality gates, and final go/no-go decision
- Output: APPROVED / APPROVED WITH CONDITIONS / NEEDS REWORK
- Action: Approval gate — do not proceed to stage 5 without at least APPROVED WITH CONDITIONS

### Stage 5: VP/Director Agent (Final Gate)
- Role: VP of Engineering / Director with 20+ years experience who has killed projects for good reason. Ruthlessly harsh. Questions every single decision.
- Purpose: Challenges fundamental assumptions, architecture choices, tech stack decisions, scope, timeline, and viability. Asks "why not X instead of Y?" for every major decision. Looks for reasons to reject, not approve.
- Output: SHIP IT / CONDITIONAL SHIP / DO NOT SHIP with detailed justification
- Action: This is the final gate. DO NOT proceed to implementation without SHIP IT or CONDITIONAL SHIP status. If CONDITIONAL SHIP, all conditions must be addressed before coding begins. If DO NOT SHIP, escalate to user for decision.
- Timing: Runs AFTER stages 1-4 feedback has been incorporated, so it reviews the final version

All 5 agents must use Opus model for highest quality feedback.

## Design Docs

- Spec: `docs/superpowers/specs/2026-03-30-agentic-robots-tower-defense-design.md`
- Backend plan: `docs/superpowers/plans/2026-03-30-phase1-python-backend-plan.md`
- Godot plan: `docs/superpowers/plans/2026-03-30-phase1-godot-game-plan.md`
