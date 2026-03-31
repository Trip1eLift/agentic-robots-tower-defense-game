"""Analyze a game recording from GameRecorder.

Usage: python analyze_recording.py [path_to_recording.json]

If no path given, looks in the default Godot user data directories.
"""
import json
import sys
from pathlib import Path
from collections import Counter


def find_recording():
    """Find the most recent game recording."""
    candidates = [
        Path(__file__).parent / "e2e_recording.json",
        Path(__file__).parent / "godot" / "e2e_recording.json",
        Path.home() / "AppData/Roaming/Godot/app_userdata/ARIA- Defenders of Duskwall/game_recording.json",
        Path.home() / "AppData/Roaming/Godot/app_userdata/ARIA: Defenders of Duskwall/game_recording.json",
        Path.home() / "AppData/Roaming/Godot/app_userdata/Agentic Robots Tower Defense/game_recording.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def analyze(path: Path):
    with open(path) as f:
        data = json.load(f)

    events = data["events"]
    print(f"Recording: {data['mission_id']}")
    print(f"Total events: {data['event_count']}")
    print()

    # Categorize events
    event_counts = Counter(e["type"] for e in events)
    print("Event breakdown:")
    for etype, count in event_counts.most_common():
        print(f"  {etype}: {count}")
    print()

    # Action analysis
    actions = [e for e in events if e["type"] == "ACTION_RECEIVED"]
    action_types = Counter(e["data"]["action"].get("action", "?") for e in actions)
    print(f"LLM actions received: {len(actions)}")
    for atype, count in action_types.most_common():
        print(f"  {atype}: {count}")
    print()

    # Per-robot breakdown
    robot_actions = {}
    for e in actions:
        rid = e["data"]["robot_id"]
        act = e["data"]["action"].get("action", "?")
        robot_actions.setdefault(rid, Counter())[act] += 1

    print("Per-robot action breakdown:")
    for rid, counts in robot_actions.items():
        print(f"  {rid}: {dict(counts)}")
    print()

    # Combat analysis
    attacks = [e for e in events if e["type"] == "ATTACK"]
    kills = [e for e in events if e["type"] == "ENEMY_KILLED"]
    robot_deaths = [e for e in events if e["type"] == "ROBOT_DIED"]
    heals = [e for e in events if e["type"] == "HEAL"]
    base_dmg = [e for e in events if e["type"] == "BASE_DAMAGE"]

    print(f"Combat stats:")
    print(f"  Attacks executed: {len(attacks)}")
    print(f"  Enemies killed: {len(kills)}")
    print(f"  Robots died: {len(robot_deaths)}")
    for rd in robot_deaths:
        print(f"    - {rd['data']['robot_id']} at t={rd['t']}ms")
    print(f"  Heals performed: {len(heals)}")
    print(f"  Base damage events: {len(base_dmg)}")
    if base_dmg:
        final_base_hp = base_dmg[-1]["data"]["health_remaining"]
        total_base_dmg = sum(e["data"]["amount"] for e in base_dmg)
        print(f"  Total base damage taken: {total_base_dmg}")
        print(f"  Final base health: {final_base_hp}")
    print()

    # Timeline of key events
    print("Key event timeline:")
    for e in events:
        if e["type"] in ("WAVE_STARTED", "WAVE_COMPLETED", "ROBOT_DIED", "RECORDING_END"):
            t = e["t"] / 1000.0
            print(f"  [{t:6.1f}s] {e['type']}: {e['data']}")
    print()

    # Problems detection
    print("Potential issues:")
    if len(attacks) == 0:
        print("  [BUG] No attacks were executed! Robots never attacked.")
    if len(actions) == 0:
        print("  [BUG] No LLM actions received! Backend may not be responding.")
    events_sent = len([e for e in events if e["type"] == "EVENT_SENT"])
    if events_sent == 0:
        print("  [BUG] No events sent to backend! Robots may not detect enemies.")
    if events_sent > 0 and len(actions) == 0:
        print("  [BUG] Events sent but no actions received -- backend connection issue.")
    if len(attacks) > 0 and len(kills) == 0:
        print("  [WARN] Attacks executed but no kills -- damage may be too low.")
    no_attack_robots = set(robot_actions.keys()) - set(e["data"]["attacker_id"] for e in attacks)
    if no_attack_robots:
        print(f"  [WARN] Robots that never attacked: {no_attack_robots}")
    idle_heavy = {rid: c for rid, c in robot_actions.items() if c.get("idle", 0) > c.get("attack", 0)}
    if idle_heavy:
        print(f"  [WARN] Robots idling more than attacking: {list(idle_heavy.keys())}")
    if not any(e["type"] in ("WAVE_COMPLETED", "RECORDING_END") for e in events):
        print("  [WARN] Recording may be incomplete (no end event).")
    if not any(True for e in events if e["type"] == "RECORDING_END"):
        print("  [WARN] Recording not properly ended -- game may have crashed.")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = find_recording()
    if path is None or not path.exists():
        print("No recording found. Run the game first or provide a path.")
        sys.exit(1)
    print(f"Analyzing: {path}")
    print()
    analyze(path)
