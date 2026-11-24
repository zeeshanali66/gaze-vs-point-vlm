#!/bin/bash
# runs the gaze-vs-point study with the GPU heat watchdog (stops at 84 C; resumable)
cd "$(dirname "$0")"
python -I gaze_study.py run > results/run.log 2>&1 &
P=$!; sleep 5; python -I watchdog.py "$(cat /proc/$P/winpid)" &
wait $P
