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
- VP Checklist (must challenge each):
  - [ ] Why this tech stack and not alternatives?
  - [ ] Why this architecture split? Is each process/layer justified?
  - [ ] Why this communication protocol (REST/WS/gRPC)?
  - [ ] Is the scope truly minimum? Can anything else be cut?
  - [ ] Has the core hypothesis been validated or is it assumed?
  - [ ] What is the timeline reality for a solo dev / small team?
  - [ ] What kills this project? What is the single biggest risk?
  - [ ] Are tests invested where risk is highest, not where testing is easiest?
  - [ ] Is there premature abstraction / over-engineering for the current phase?
  - [ ] What happens when the happy path fails? (LLM down, bad output, latency spike)
  - [ ] Would you bet your own money on this shipping?

All 5 agents must use Opus model for highest quality feedback.

## Implementation Workflow

Implementation follows an **implement → review → fix → iterate** cycle. Implementors build a chunk of work, then the full 5-stage review pipeline runs on it, issues are addressed, and the cycle repeats.

### The Cycle

```
┌─────────────────────────────────────────────────────────┐
│  1. IMPLEMENT                                           │
│     Implementor agents build the next chunk of work     │
│     (1-3 plan tasks per cycle). Move fast, explore      │
│     options, ship working code.                         │
├─────────────────────────────────────────────────────────┤
│  2. REVIEW                                              │
│     Run full 5-stage review pipeline on the new code:   │
│     Stages 1-4 in parallel → fix → Stage 5 (VP)        │
│     Review scope: only the NEW code from this cycle     │
├─────────────────────────────────────────────────────────┤
│  3. FIX                                                 │
│     Address all issues from reviewers.                  │
│     Implementors make the changes.                      │
├─────────────────────────────────────────────────────────┤
│  4. ITERATE                                             │
│     Commit, move to next chunk. Repeat from step 1.     │
└─────────────────────────────────────────────────────────┘
```

### Chunk Size
- Each cycle covers **1-3 plan tasks** — small enough to review effectively, large enough to make progress.
- At playtest gates, the cycle pauses for a full playthrough before continuing.

### Implementor Principles
- **Speed over perfection.** Ship working code, iterate, fix forward. Don't gold-plate.
- **Parallel by default.** Independent tasks run simultaneously. Use git worktrees or separate branches when agents work on different subsystems.
- **Explore, don't assume.** When a plan step is ambiguous or an approach isn't working, try 2-3 alternatives before asking. Pick what works.
- **Communicate via code.** Agents share state through committed code, not messages. If Agent A needs Agent B's interface, Agent A reads the code Agent B wrote.
- **Fail fast, surface early.** If something doesn't work (LLM output quality, Godot API mismatch, performance issue), flag it immediately. Don't bury it.
- **Follow the plan, but adapt.** Plans are guides, not scripture. If a plan step is wrong or a better approach is discovered during implementation, deviate and document why.

### Agent Roles

**Backend Implementor**
- Owns: `backend/`, `data/`, Python tests
- Builds: FastAPI server, Ollama client, prompt builder, action parser, mock LLM, event queue
- Runs tests after every task. All tests must pass before committing.

**Godot Implementor**
- Owns: `godot/`, scene files, GDScript
- Builds: Map, robots, enemies, UI, game loop, WebSocket client
- Manual tests each scene after creation. Verifies no script errors in Godot Output panel.

**Integration Implementor**
- Owns: End-to-end testing, cross-system bugs
- Runs after both backend and Godot reach a connectable state
- Tests: WebSocket message format alignment, enemy ID round-trip, full mission flow

### Art Pipeline

Claude cannot generate images. During each implementation cycle, the **PM agent** (Stage 2 reviewer) also identifies art assets needed for the work just built and writes art request descriptions.

**Process:**
1. After each implementation cycle, PM writes art requests to `docs/art-requests/`
2. Each request is a markdown file named `<asset-name>.md` containing:
   - **Asset name:** e.g. `robot_hana_portrait`
   - **Type:** sprite / portrait / UI element / tilemap / icon
   - **Dimensions:** e.g. 64x64, 256x256
   - **Art style:** e.g. anime, pixel art, painterly
   - **Description:** detailed visual description for image generation
   - **Usage:** where it goes in the game (e.g. `godot/assets/robots/hana/portrait.png`)
   - **Priority:** critical (blocks gameplay) / nice-to-have (placeholder works for now)
3. The user generates the art externally (Stable Diffusion, Midjourney, etc.) based on the request
4. User imports the PNG into the specified path
5. Colored rectangle placeholders are used until art is delivered — game must always be playable without final art

### Coordination Rules
- Backend and Godot implementors start simultaneously. Backend does not need to finish first — Godot uses mock/stub WebSocket responses until backend is ready.
- When both reach Task 10+ (backend WebSocket server + Godot WebSocket client), the integration implementor kicks in.
- All agents commit to the SAME feature branch. Use atomic commits with clear messages.
- If an agent is blocked by another agent's work, it moves to the next non-blocked task.
- At each playtest gate, ALL agents stop and review the game state together.

### Decision Authority
- Implementors can make tactical decisions (variable names, code structure, small scope adjustments) without approval.
- Implementors must escalate: architecture changes, new dependencies, feature cuts, or anything that contradicts the approved plan.
- If two implementors disagree on an approach, the one whose subsystem is affected decides.

## Design Docs

- Spec: `docs/superpowers/specs/2026-03-30-agentic-robots-tower-defense-design.md`
- Backend plan: `docs/superpowers/plans/2026-03-30-phase1-python-backend-plan.md`
- Godot plan: `docs/superpowers/plans/2026-03-30-phase1-godot-game-plan.md`
