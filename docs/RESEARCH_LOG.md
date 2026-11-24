# Research log: Look here, point there

### 1. Why
The pointing study showed that VLMs use proximity rather than the direction of a gesture. People combine gaze and
pointing, and a novelty search (2025-26) found gaze-only work (VLMs misread gaze from head orientation, arXiv
2506.05412) and pointing-only work, but no study of the two cues in conflict.

### 2. Controlling for proximity from the start
Because proximity explained the pointing results, the gazed and pointed objects were placed at fixed distances (3 m
and 5 m) and swapped across scenes, so a preference for one cue cannot come from distance alone.

### 3. The first renders were too small to read
The nose and eyes were tiny and the arm was mostly hidden by the body. They were enlarged (head radius 0.42 m, nose
0.95 m long, arm 1.7 m) before any model call.

### 4. A legend in every prompt
To test the models' reading of the cues rather than their guessing what the drawing means, every prompt explains
the nose, eyes and arm. Gaze still was not followed.

## Next
First-person renders (where eyes and head direction look natural), a human baseline on the same items, and giving
the gaze direction as an angle instead of a drawing.
