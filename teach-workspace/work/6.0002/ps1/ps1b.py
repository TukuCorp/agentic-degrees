###########################
# 6.0002 Problem Set 1b: Space Change
# Name: (self-study workspace)
# Collaborators: none
# Time: ~1 h
# Author: charz, cdenise

#================================
# Part B: Golden Eggs
#================================

# Problem 1
def dp_make_weight(egg_weights, target_weight, memo={}):
    """
    Find number of eggs to bring back, using the smallest number of eggs. Assumes there is
    an infinite supply of eggs of each weight, and there is always a egg of value 1.

    Parameters:
    egg_weights - tuple of integers, available egg weights sorted from smallest to largest value (1 = d1 < d2 < ... < dk)
    target_weight - int, amount of weight we want to find eggs to fit
    memo - dictionary, OPTIONAL parameter for memoization (you may not need to use this parameter depending on your implementation)

    Returns: int, smallest number of eggs needed to make target weight
    """
    if target_weight in memo:
        return memo[target_weight]
    if target_weight == 0:
        return 0
    best = None
    for weight in egg_weights:
        if weight <= target_weight:
            candidate = 1 + dp_make_weight(egg_weights, target_weight - weight, memo)
            if best is None or candidate < best:
                best = candidate
    memo[target_weight] = best
    return best


# EXAMPLE TESTING CODE, feel free to add more if you'd like
if __name__ == '__main__':
    egg_weights = (1, 5, 10, 25)
    n = 99
    print("Egg weights = (1, 5, 10, 25)")
    print("n = 99")
    print("Expected ouput: 9 (3 * 25 + 2 * 10 + 4 * 1 = 99)")
    print("Actual output:", dp_make_weight(egg_weights, n))
    print()

    # Extra sanity checks. Pass a fresh memo each time: the default `memo={}`
    # dict is shared across calls, so reusing it with a *different* egg_weights
    # set would serve stale entries keyed only by target_weight.
    print("dp_make_weight((1, 5, 10, 20), 99) ->",
          dp_make_weight((1, 5, 10, 20), 99, memo={}), "(expect 10)")
    print("dp_make_weight((1, 5, 10, 25), 0)   ->",
          dp_make_weight((1, 5, 10, 25), 0, memo={}), "(expect 0)")
    print("dp_make_weight((1, 5, 10, 25), 1)   ->",
          dp_make_weight((1, 5, 10, 25), 1, memo={}), "(expect 1)")
    print("dp_make_weight((1, 5, 10, 25), 33)  ->",
          dp_make_weight((1, 5, 10, 25), 33, memo={}), "(expect 5 = 25+5+1+1+1)")
