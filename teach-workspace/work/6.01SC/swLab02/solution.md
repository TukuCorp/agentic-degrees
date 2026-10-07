# 6.01 swLab02 — Software Lab 2: three character-stream state machines

Source: `mit-ocw-curriculum/electrical-engineering/01-intro-to-eecs-1-6.01SC/other/swLab02.zip →
swLab02/swLab02Work.py` (skeleton).

## What was built

Three state machines, each transducing a character sequence, adapted from the `lib601.sm` API to
this workspace's `lib/sm.py` (see ASM-006 / RISK-02-01): the skeleton's `startState` class
attribute and `start()`/`step()`/`self.state` are replaced by `start_state()` method +
`get_next_values(state, inp)` with `transduce` inherited. Behaviour is identical.

1. **`Delay2Machine(val0, val1)`** — a two-step delay. State holds the two most recent inputs
   (oldest first); output is the older one, and each new input pushes the newer one down.
2. **`CommentsSM`** — reads Python source and outputs only the characters *inside* comments. `#`
   starts a comment (and is emitted); the comment runs to end of line (newline is suppressed and
   returns to code); everything else outputs `None`.
3. **`FirstWordSM`** — outputs the first word of each line, `None` elsewhere. Three states: `line`
   (start of a line, skipping whitespace), `word` (inside the first word), `rest` (after the first
   word, ignored until newline).

## Verified behaviour (all four tests per machine match the skeleton's expected output)

```
Delay2Machine  Test1: [100, 10, 1, 0, 2, 0, 0, 3, 0, 0]   Test2: [10, 100, 0, 0, 0, 0, 0]
               Test3: [-1, 0, 1, 2, -3, 1]                Test4: [100, 10, 1, 0, 2, 0, 0, 3, 0, 0]
CommentsSM     Test1: ['#',' ','f','u','n','c','#',' ','t','e','s','t','#',' ','c','o','m','m','e','n','t']
               Test2: ['#','i','n','i','t','i','a','l',' ','c','o','m','m','e','n','t','#',' ','f','u','n','c','#',' ','t','e','s','t','#',' ','c','o','m','m','e','n','t']
FirstWordSM    Test1: ['h','i',None,'h','o']
               Test2: [None,None,'h','i',None,'h','o']
               Test3: [None,None,None,'h','i',None,None,'h','o',None,None,None,None,None,None,None,None,None,'h','a',None,None,None,None,None,None]
```

Run it: `python teach-workspace/work/6.01SC/swLab02/swLab02Work.py`.

## Why this lab matters

`CommentsSM` and `FirstWordSM` are miniature parsers — the same "hold a mode in the state and
emit one step late" pattern that hw1's `Tokenizer` uses. They force the discipline of deciding
*what is state* vs *what is input*, which is the exact skill the signals-and-systems unit then
turns into "what is a pole" (state = the memory that persists across steps).
