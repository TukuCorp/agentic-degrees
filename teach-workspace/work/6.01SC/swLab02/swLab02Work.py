"""6.01 swLab02 — completed work file (Python 3).

Three state machines over character sequences, adapted from the lib601.sm API
to this workspace's lib/sm.py (start_state() method + get_next_values, with
transduce inherited). The skeleton's Python 2 print statements are rewritten,
and `start()`/`step()`/`self.state` are replaced by transduce; behaviour is
unchanged.

Run the self-checks:
    python swLab02Work.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib.sm import SM  # noqa: E402  (standalone replacement for lib601.sm)


class Delay2Machine(SM):
    """A two-step delay: emit the value two steps back.

    State holds the two most recent inputs (oldest first), so the output is the
    older of the two and each new input pushes the newer one down.
    """

    def __init__(self, val0, val1):
        self._val0 = val0
        self._val1 = val1

    def start_state(self):
        return (self._val0, self._val1)

    def get_next_values(self, state, inp):
        (older, newer) = state
        return ((newer, inp), older)


class CommentsSM(SM):
    """Read Python source; output exactly the characters inside comments.

    '#' starts a comment (emitted); the comment runs to end of line (newline is
    suppressed and returns us to code). Everything else outputs None.
    """

    def start_state(self):
        return "code"

    def get_next_values(self, state, inp):
        if state == "code":
            if inp == "#":
                return ("comment", "#")
            return ("code", None)
        # state == "comment"
        if inp == "\n":
            return ("code", None)
        return ("comment", inp)


class FirstWordSM(SM):
    """Output the first word of each line; None everywhere else.

    States: 'line' (at start of a line, skipping whitespace), 'word' (inside
    the first word), 'rest' (after the first word, ignored until newline).
    """

    def start_state(self):
        return "line"

    def get_next_values(self, state, inp):
        if state == "line":
            if inp in (" ", "\n"):
                return ("line", None)
            return ("word", inp)
        if state == "word":
            if inp == "\n":
                return ("line", None)
            if inp == " ":
                return ("rest", None)
            return ("word", inp)
        # state == "rest"
        if inp == "\n":
            return ("line", None)
        return ("rest", None)


def _non_none(outputs):
    return [o for o in outputs if o is not None]


def runTestsDelay():
    print("Test1:", Delay2Machine(100, 10).transduce([1, 0, 2, 0, 0, 3, 0, 0, 0, 4]))
    print("Test2:", Delay2Machine(10, 100).transduce([0, 0, 0, 0, 0, 0, 1]))
    print("Test3:", Delay2Machine(-1, 0).transduce([1, 2, -3, 1, 2, -3]))
    m = Delay2Machine(100, 10)
    print("Test4:", m.transduce([1, 0, 2, 0, 0, 3, 0, 0, 0, 4]))


x1 = """def f(x):  # func
   if x:   # test
     # comment
     return 'foo' """

x2 = """#initial comment
def f(x):  # func
   if x:   # test
     # comment
     return 'foo' """


def runTestsComm():
    print("Test1:", _non_none(CommentsSM().transduce(x1)))
    print("Test2:", _non_none(CommentsSM().transduce(x2)))


test1 = "hi\nho"
test2 = "  hi\nho"
test3 = "\n\n hi \nho ho ho\n\n ha ha ha"


def runTestsFW():
    m = FirstWordSM()
    print("Test1:", m.transduce(test1))
    print("Test2:", m.transduce(test2))
    print("Test3:", m.transduce(test3))


def main():
    print("===== Delay2Machine =====")
    runTestsDelay()
    print("\n===== CommentsSM =====")
    runTestsComm()
    print("\n===== FirstWordSM =====")
    runTestsFW()
    print("\nall swLab02 self-checks ran")


if __name__ == "__main__":
    main()
