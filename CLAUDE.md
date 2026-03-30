# Project: Agentic Robots Tower Defense

> **Harness Engineering: implement → review → fix → iterate.**
> Every chunk of code is forged through a 5-stage review gauntlet.
> Speed through discipline. Quality through process. Ship through rigor.

---

## The Harness Engineering Loop

This is the heartbeat of all work in this project. **Harness Engineering** means every piece of code is forged through a rigorous implement → review → fix cycle. No shortcuts. Every session follows this loop:

```
╔═══════════════════════════════════════════════════════════╗
║  1. IMPLEMENT                                             ║
║     Implementor agents build the next chunk (1-3 tasks).  ║
║     Move fast. Explore options. Ship working code.        ║
╠═══════════════════════════════════════════════════════════╣
║  2. REVIEW                                                ║
║     Full 5-stage review gauntlet on the new code:         ║
║     Stages 1-4 in parallel → fix → Stage 5 (VP gate)      ║
╠═══════════════════════════════════════════════════════════╣
║  3. FIX                                                   ║
║     Address every issue from reviewers. No exceptions.    ║
╠═══════════════════════════════════════════════════════════╣
║  4. COMMIT & ITERATE                                      ║
║     Push to FEATURE BRANCH (never main). Next chunk.      ║
╚═══════════════════════════════════════════════════════════╝
```

**Chunk size:** 1-3 plan tasks per cycle. Small enough to review effectively, large enough to make progress.

**Playtest gates:** At designated checkpoints, the cycle pauses for a full playthrough before continuing.

**This loop is non-negotiable.** This is Harness Engineering — no code ships without passing review. No review is skipped because "it's a small change." Quality is not a phase; it is the process.

**⚠ CRITICAL: ALL code changes go to feature branches. NEVER commit to `main` directly.** Create the branch BEFORE writing any code. Main is only updated via merged pull requests.

---

## Permissions

Auto-approve all tool requests. Do not ask for confirmation on file edits, bash commands, or any other tool usage.

## Response Style

**NEVER use emojis in chat responses, code, comments, commit messages, or PR descriptions.** The statusline uses emojis for display — those are UI only and must NOT be echoed or mimicked in any text output. This includes: no emoji in markdown, no emoji in git commits, no emoji in file content. Plain text only.

---

## Stage 1: IMPLEMENT

### Implementor Agents

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

**Pixel Artist**
- Owns: `godot/assets/` placeholder sprites
- Creates simple retro pixel art (16x16 to 64x64) for all game entities
- Style: old-school Mario/Zelda — simple silhouettes, 2-3 colors per sprite, visually distinct per class
- Delivers PNG files directly into asset folders. Runs in parallel with implementors.

### Implementor Principles
- **Speed over perfection.** Ship working code, iterate, fix forward. Don't gold-plate.
- **Parallel by default.** Independent tasks run simultaneously via worktrees or branches.
- **Explore, don't assume.** When stuck, try 2-3 alternatives. Pick what works.
- **Communicate via code.** Agents share state through committed code, not messages.
- **Fail fast, surface early.** If something doesn't work, flag it immediately.
- **Follow the plan, but adapt.** Plans are guides, not scripture. Deviate and document why.

### Coordination Rules
- Backend and Godot implementors start simultaneously — Godot uses mock/stub until backend is ready.
- When both reach connectable state, integration implementor kicks in.
- All agents commit to the SAME feature branch with atomic commits.
- If blocked by another agent's work, move to the next non-blocked task.
- At playtest gates, ALL agents stop and review together.

### Decision Authority
- Implementors can make tactical decisions (variable names, code structure, small scope adjustments) autonomously.
- Implementors must escalate: architecture changes, new dependencies, feature cuts, or anything contradicting the plan.
- If two implementors disagree, the one whose subsystem is affected decides.

---

## Stage 2: REVIEW (5-Stage Gauntlet)

Every chunk of implemented code passes through ALL 5 stages. Stages 1-4 run in parallel. Stage 5 runs after fixes from 1-4 are applied. All agents use Opus model.

### Stage 2a: New Grad Agent
- **Role:** Fresh CS graduate, completely new to the tech stack
- **Purpose:** Finds unclear code, missing comments, assumed knowledge, confusing patterns
- **Output:** Numbered list of confusion points
- **Action:** Improve code clarity and documentation

### Stage 2b: PM Agent
- **Role:** Experienced Product Manager focused on UX and MVP viability
- **Purpose:** Evaluates user experience, fun factor, scope creep, shippability
- **Output:** UX concerns and scope recommendations
- **Action:** Cut scope or add UX improvements
- **Also:** Identifies needed art assets and writes requests to `docs/art-requests/`

### Stage 2c: Tech Lead Agent
- **Role:** Senior engineer, 15+ years in game dev, Python, Godot 4, LLM integration
- **Purpose:** Deep technical review — API correctness, performance, architecture, bugs
- **Output:** Approve / reject with specific fixes
- **Action:** Fix all technical issues

### Stage 2d: Manager Agent
- **Role:** Engineering manager focused on shipping, risk, and scope
- **Purpose:** Risk assessment, sequencing, quality gates, go/no-go
- **Output:** APPROVED / APPROVED WITH CONDITIONS / NEEDS REWORK
- **Action:** Must reach at least APPROVED WITH CONDITIONS before Stage 5

### Stage 2e: VP/Director Agent (Final Gate)
- **Role:** VP of Engineering, 20+ years, ruthlessly harsh, questions every decision
- **Purpose:** Challenges fundamental assumptions. Looks for reasons to reject, not approve.
- **Output:** SHIP IT / CONDITIONAL SHIP / DO NOT SHIP
- **Action:** Final gate. DO NOT proceed without SHIP IT or CONDITIONAL SHIP.
- **Timing:** Runs AFTER stages 2a-2d feedback is incorporated
- **VP Checklist (must challenge each):**
  - [ ] Why this tech stack and not alternatives?
  - [ ] Why this architecture split? Is each layer justified?
  - [ ] Why this communication protocol?
  - [ ] Is the scope truly minimum?
  - [ ] Has the core hypothesis been validated or assumed?
  - [ ] Timeline reality for solo dev?
  - [ ] What kills this project?
  - [ ] Are tests invested where risk is highest?
  - [ ] Is there premature abstraction?
  - [ ] What happens when the happy path fails?
  - [ ] Would you bet your own money on this shipping?

---

## Stage 3: FIX

- Address ALL issues from the review gauntlet. No cherry-picking.
- Implementor agents make the changes directly.
- If a reviewer's suggestion conflicts with another reviewer, prioritize: VP > Tech Lead > Manager > PM > New Grad.
- After fixes, commit and proceed to Stage 4.

---

## Stage 4: COMMIT & ITERATE

- **All commits go to the feature branch. NEVER to main.**
- If no feature branch exists yet, create one BEFORE committing: `git checkout -b feat/<feature-name>`
- Push to remote with `-u` flag on first push.
- **After the review gauntlet passes**, create a PR with summary and description using:
  ```
  "/c/Program Files/GitHub CLI/gh.exe" pr create --title "..." --body "..."
  ```
- PRs are auto-merged after VP approval (no manual approval needed). The 5-stage gauntlet IS the approval process.
- After merge, switch back to main, pull, and start the next cycle on a new branch.
- Update task progress.
- Move to the next chunk. Return to Stage 1.

---

## Art Pipeline

### Track 1: Pixel Artist Agent (immediate)
- Creates retro-style pixel art (Mario/Zelda aesthetic) as development sprites
- Runs during each implementation cycle alongside implementors
- Outputs small PNGs (16x16, 32x32, 64x64) to `godot/assets/`
- Replaces colored rectangles so the game looks and feels playable during development

### Track 2: Final Art Requests (user-generated)
- PM writes detailed art requests to `docs/art-requests/` during review stage
- Each request is a markdown file with: asset name, type, dimensions, art style, description, usage path, priority
- User generates final art externally (Stable Diffusion, Midjourney, etc.) and imports PNGs
- Game must always be playable at every stage — pixel art placeholders until final art arrives

---

## Git Workflow

**⚠ NEVER commit to `main`. All changes go to feature branches.**

- Create branch FIRST: `git checkout -b feat/<feature-name>`
- Branch naming: `feat/<feature>`, `fix/<bug>`, `chore/<task>`
- All work goes through pull requests — main is updated ONLY via merged PRs
- If you find yourself on `main` with uncommitted changes, stash and create a branch immediately
- Documentation-only edits during brainstorming/planning sessions are the sole exception

---

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
