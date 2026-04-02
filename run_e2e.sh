#!/bin/bash
# Run full E2E test: backend + Godot autoplay with recording
# Usage: bash run_e2e.sh         (real Ollama)
#        bash run_e2e.sh mock    (mock LLM)
#
# Output: game_recording.json in Godot user data dir
# Console: prints mission recording summaries after each mission

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GODOT="/d/Godot/Godot_v4.6.1-stable_win64_console.exe"

cd "$SCRIPT_DIR"

# Copy data files
cp -r data/ godot/data/ 2>/dev/null

# Kill existing processes
powershell.exe -Command "Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id \$_.OwningProcess -Force }" 2>/dev/null
python -c "import time; time.sleep(1)"

# Start backend
source .venv/Scripts/activate
if [ "$1" = "mock" ]; then
    echo "[E2E] Starting backend with MOCK LLM..."
    USE_MOCK_LLM=true python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 &
else
    echo "[E2E] Starting backend with REAL Ollama..."
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 &
fi
BACKEND_PID=$!
python -c "import time; time.sleep(3)"

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "[E2E] Backend failed to start!"
    exit 1
fi
echo "[E2E] Backend running (PID: $BACKEND_PID)"

# Start Godot in autoplay mode
echo "[E2E] Starting Godot in autoplay mode..."
"$GODOT" --path godot/ -- --autoplay 2>&1 | tee e2e_output.log &
GODOT_PID=$!

echo "[E2E] Godot running (PID: $GODOT_PID)"
echo "[E2E] Watch for MISSION RECORDING SUMMARY in the output"
echo "[E2E] Press Ctrl+C to stop"
echo ""

wait $GODOT_PID
EXIT_CODE=$?

# Kill backend
kill $BACKEND_PID 2>/dev/null

echo ""
echo "[E2E] Godot exited with code $EXIT_CODE"

# Show recording file location
echo "[E2E] Recording saved to Godot user data directory"

# Parse and display the recording summary from the log
if [ -f e2e_output.log ]; then
    echo ""
    echo "=== E2E LOG SUMMARY ==="
    grep -E "(MISSION RECORDING|Mission:|Robots|Enemies|Events sent|Actions|Attack|Kills|Waves|Heals|Total events|====)" e2e_output.log
fi
