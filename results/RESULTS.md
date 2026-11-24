# Look here, point there: results

960 answers (3 models x 8 conditions x 40 scenes). Invalid: 0. Four objects, so chance = 0.25.

## What did the model pick? (share of answers)

`pointed` = the object the arm points at, `gazed` = the object the head faces (in point_only the head faces no object, in congruent both cues pick the pointed object).

```
choice                       gazed  other  pointed
model      cue        req                         
gemma3:12b conflict   look    0.08   0.60     0.32
                      point   0.10   0.45     0.45
                      that    0.12   0.50     0.38
           congruent  that    0.10   0.55     0.35
           gaze_only  look    0.12   0.62     0.25
                      that    0.20   0.55     0.25
           point_only point   0.10   0.45     0.45
                      that    0.10   0.57     0.32
gemma4:12b conflict   look    0.12   0.57     0.30
                      point   0.02   0.30     0.68
                      that    0.10   0.40     0.50
           congruent  that    0.12   0.35     0.52
           gaze_only  look    0.25   0.48     0.28
                      that    0.38   0.52     0.10
           point_only point   0.12   0.25     0.62
                      that    0.05   0.38     0.57
qwen3.5:9b conflict   look    0.30   0.52     0.18
                      point   0.10   0.62     0.28
                      that    0.22   0.57     0.20
           congruent  that    0.18   0.55     0.28
           gaze_only  look    0.12   0.57     0.30
                      that    0.22   0.52     0.25
           point_only point   0.15   0.62     0.22
                      that    0.18   0.57     0.25
```

## Can models follow the cue they are asked about? (accuracy, 95% bootstrap CI)

| model | look (gaze only) | point (point only) | look (conflict) | point (conflict) |
|---|---|---|---|---|
| gemma4:12b | 0.25 [0.12, 0.40] | 0.62 [0.47, 0.78] | 0.12 [0.03, 0.23] | 0.68 [0.53, 0.82] |
| qwen3.5:9b | 0.12 [0.03, 0.25] | 0.23 [0.10, 0.35] | 0.30 [0.17, 0.45] | 0.28 [0.15, 0.42] |
| gemma3:12b | 0.12 [0.03, 0.23] | 0.45 [0.30, 0.60] | 0.07 [0.00, 0.17] | 0.45 [0.30, 0.60] |

## 'That one' under conflict, split by which object is nearer

```
choice               gazed  other  pointed
model      p_nearer                       
gemma3:12b False      0.15   0.60     0.25
           True       0.10   0.40     0.50
gemma4:12b False      0.20   0.60     0.20
           True       0.00   0.20     0.80
qwen3.5:9b False      0.15   0.65     0.20
           True       0.30   0.50     0.20
```
