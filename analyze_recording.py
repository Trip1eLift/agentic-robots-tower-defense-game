"""Analyze a game recording log from GameRecorder.

Usage: python analyze_recording.py [path_to_recording.log]

Reads tab-separated log: timestamp_ms \t event_type \t json_data
"""
import json
import sys
from pathlib import Path
from collections import Counter


def find_recording():
    candidates = [
        Path(__file__).parent / "godot" / "e2e_recording.log",
        Path(__file__).parent / "e2e_recording.log",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def parse_log(path: Path):
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 2)
            if len(parts) < 3:
                continue
            try:
                events.append({
                    "t": int(parts[0]),
                    "type": parts[1],
                    "data": json.loads(parts[2])
                })
            except (ValueError, json.JSONDecodeError):
                continue
    return events


def analyze(events):
    print(f"Total events: {len(events)}")
    print()

    event_counts = Counter(e["type"] for e in events)
    print("Event breakdown:")
    for etype, count in event_counts.most_common():
        print(f"  {etype}: {count}")
    print()

    actions = [e for e in events if e["type"] == "ACTION_RECEIVED"]
    action_types = Counter(e["data"]["action"].get("action", "?") for e in actions)
    print(f"LLM actions received: {len(actions)}")
    for atype, count in action_types.most_common():
        print(f"  {atype}: {count}")
    print()

    robot_actions = {}
    for e in actions:
        rid = e["data"]["robot_id"]
        act = e["data"]["action"].get("action", "?")
        robot_actions.setdefault(rid, Counter())[act] += 1

    print("Per-robot action breakdown:")
    for rid, counts in robot_actions.items():
        print(f"  {rid}: {dict(counts)}")
    print()

    attacks = [e for e in events if e["type"] == "ATTACK"]
    kills = [e for e in events if e["type"] == "ENEMY_KILLED"]
    robot_deaths = [e for e in events if e["type"] == "ROBOT_DIED"]
    heals = [e for e in events if e["type"] == "HEAL"]
    base_dmg = [e for e in events if e["type"] == "BASE_DAMAGE"]
    enemies_spawned = [e for e in events if e["type"] == "ENEMY_SPAWNED"]

    print(f"Combat stats:")
    print(f"  Enemies spawned: {len(enemies_spawned)}")
    print(f"  Attacks executed: {len(attacks)}")
    print(f"  Enemies killed: {len(kills)}")
    print(f"  Enemies remaining: {len(enemies_spawned) - len(kills)}")
    print(f"  Robots died: {len(robot_deaths)}")
    for rd in robot_deaths:
        print(f"    - {rd['data']['robot_id']} at t={rd['t']}ms")
    print(f"  Heals performed: {len(heals)}")
    print(f"  Base damage events: {len(base_dmg)}")
    if base_dmg:
        total_base_dmg = sum(e["data"]["amount"] for e in base_dmg)
        print(f"  Total base damage: {total_base_dmg}")
        print(f"  Final base health: {base_dmg[-1]['data']['health_remaining']}")
    print()

    print("Key event timeline:")
    for e in events:
        if e["type"] in ("WAVE_STARTED", "WAVE_COMPLETED", "ROBOT_DIED", "RECORDING_START", "RECORDING_END"):
            t = e["t"] / 1000.0
            print(f"  [{t:7.1f}s] {e['type']}: {e['data']}")
    print()

    print("Potential issues:")
    if len(attacks) == 0:
        print("  [BUG] No attacks were executed!")
    if len(actions) == 0:
        print("  [BUG] No LLM actions received!")
    events_sent = len([e for e in events if e["type"] == "EVENT_SENT"])
    if events_sent == 0:
        print("  [BUG] No events sent to backend!")
    if events_sent > 0 and len(actions) == 0:
        print("  [BUG] Events sent but no actions received -- backend issue.")
    if len(attacks) > 0 and len(kills) == 0:
        print("  [WARN] Attacks but no kills -- damage too low?")
    attacker_ids = set(e["data"]["attacker_id"] for e in attacks)
    all_robot_ids = set(e["data"]["robot_id"] for e in events if e["type"] == "ROBOT_SPAWNED")
    non_attackers = all_robot_ids - attacker_ids
    if non_attackers:
        print(f"  [WARN] Robots that never attacked: {non_attackers}")
    if len(robot_deaths) > len(all_robot_ids):
        print(f"  [BUG] More death events ({len(robot_deaths)}) than robots ({len(all_robot_ids)}) -- duplicate _die() calls")
    remaining = len(enemies_spawned) - len(kills)
    if remaining > 0 and not any(e["type"] == "RECORDING_END" for e in events):
        print(f"  [BUG] {remaining} enemies remaining and no recording end -- game stuck")
    if not any(e["type"] == "RECORDING_END" for e in events):
        print("  [WARN] Recording not ended -- game may have crashed or is still running")
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
    events = parse_log(path)
    analyze(events)
