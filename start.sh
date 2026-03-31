#!/bin/bash
# Start the full game: backend + Godot frontend
# Usage: bash start.sh         (real Ollama LLM)
#        bash start.sh mock    (mock LLM, no Ollama needed)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GODOT="/d/Godot/Godot_v4.6.1-stable_win64.exe"

cd "$SCRIPT_DIR"

# Ensure data is copied into godot project
if [ ! -d "godot/data" ]; then
    cp -r data/ godot/data/
fi

# Kill any existing backend on port 8765
powershell.exe -Command "Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id \$_.OwningProcess -Force }" 2>/dev/null
python -c "import time; time.sleep(1)"

# Start backend
source .venv/Scripts/activate
if [ "$1" = "mock" ]; then
    echo "Starting backend with MOCK LLM..."
    USE_MOCK_LLM=true python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 &
else
    echo "Starting backend with REAL Ollama LLM (dolphin-mistral)..."
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 &
fi
BACKEND_PID=$!
python -c "import time; time.sleep(2)"

# Verify backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Backend failed to start!"
    exit 1
fi
echo "Backend running on ws://localhost:8765/ws (PID: $BACKEND_PID)"

# Start Godot
if [ -f "$GODOT" ]; then
    echo "Starting Godot..."
    "$GODOT" --path godot/ &
    GODOT_PID=$!
    echo "Godot running (PID: $GODOT_PID)"
else
    echo "Godot not found at $GODOT -- start it manually"
fi

echo ""
echo "Press Ctrl+C to stop everything"
wait $BACKEND_PID
