#!/bin/bash
# Run Godot GUT tests headless from CLI
# Usage: bash run_godot_tests.sh [test_file]
# Example: bash run_godot_tests.sh
# Example: bash run_godot_tests.sh test_config_loader.gd

GODOT="/d/Godot/Godot_v4.6.1-stable_win64_console.exe"
PROJECT="godot/"

if [ ! -f "$GODOT" ]; then
    echo "Godot not found at $GODOT"
    exit 1
fi

# Copy data files if not present (Godot needs them at res://data/)
if [ ! -d "godot/data" ]; then
    cp -r data/ godot/data/
fi

if [ -n "$1" ]; then
    "$GODOT" --headless --path "$PROJECT" -s addons/gut/gut_cmdln.gd -gtest="res://tests/unit/$1" -gexit
else
    "$GODOT" --headless --path "$PROJECT" -s addons/gut/gut_cmdln.gd -gexit
fi
