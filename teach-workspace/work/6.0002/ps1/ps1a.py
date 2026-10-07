###########################
# 6.0002 Problem Set 1a: Space Cows
# Name: (self-study workspace)
# Collaborators: none
# Time: ~2.5 h

from ps1_partition import get_partitions
import time

#================================
# Part A: Transporting Space Cows
#================================

# Problem 1
def load_cows(filename):
    """
    Read the contents of the given file.  Assumes the file contents contain
    data in the form of comma-separated cow name, weight pairs, and return a
    dictionary containing cow names as keys and corresponding weights as values.

    Parameters:
    filename - the name of the data file as a string

    Returns:
    a dictionary of cow name (string), weight (int) pairs
    """
    cows = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, weight = line.split(",")
            cows[name.strip()] = int(weight)
    return cows


def _check_unshippable(cows, limit):
    """Report any cow heavier than the ship as unshippable (plan edge case)."""
    bad = sorted(name for name, weight in cows.items() if weight > limit)
    if bad:
        raise ValueError(
            "cow(s) exceed the weight limit and cannot be shipped: %s"
            % ", ".join(bad))


# Problem 2
def greedy_cow_transport(cows, limit=10):
    """
    Uses a greedy heuristic to determine an allocation of cows that attempts to
    minimize the number of spaceship trips needed to transport all the cows. The
    returned allocation of cows may or may not be optimal.
    The greedy heuristic should follow the following method:

    1. As long as the current trip can fit another cow, add the largest cow that will fit
        to the trip
    2. Once the trip is full, begin a new trip to transport the remaining cows

    Does not mutate the given dictionary of cows.

    Parameters:
    cows - a dictionary of name (string), weight (int) pairs
    limit - weight limit of the spaceship (an int)

    Returns:
    A list of lists, with each inner list containing the names of cows
    transported on a particular trip and the overall list containing all the
    trips
    """
    _check_unshippable(cows, limit)
    remaining = sorted(cows.items(), key=lambda kv: kv[1], reverse=True)
    trips = []
    while remaining:
        trip = []
        trip_weight = 0
        leftover = []
        for name, weight in remaining:
            if trip_weight + weight <= limit:
                trip.append(name)
                trip_weight += weight
            else:
                leftover.append((name, weight))
        trips.append(trip)
        remaining = leftover
    return trips


# Problem 3
def brute_force_cow_transport(cows, limit=10):
    """
    Finds the allocation of cows that minimizes the number of spaceship trips
    via brute force.  The brute force algorithm should follow the following method:

    1. Enumerate all possible ways that the cows can be divided into separate trips
        Use the given get_partitions function in ps1_partition.py to help you!
    2. Select the allocation that minimizes the number of trips without making any trip
        that does not obey the weight limitation

    Does not mutate the given dictionary of cows.

    Parameters:
    cows - a dictionary of name (string), weight (int) pairs
    limit - weight limit of the spaceship (an int)

    Returns:
    A list of lists, with each inner list containing the names of cows
    transported on a particular trip and the overall list containing all the
    trips
    """
    _check_unshippable(cows, limit)
    names = list(cows.keys())
    best = None
    for partition in get_partitions(names):
        if all(sum(cows[name] for name in trip) <= limit for trip in partition):
            if best is None or len(partition) < len(best):
                best = partition
    return best


# Problem 4
def compare_cow_transport_algorithms():
    """
    Using the data from ps1_cow_data.txt and the specified weight limit, run your
    greedy_cow_transport and brute_force_cow_transport functions here. Use the
    default weight limits of 10 for both greedy_cow_transport and
    brute_force_cow_transport.

    Print out the number of trips returned by each method, and how long each
    method takes to run in seconds.

    Returns:
    Does not return anything.
    """
    cows = load_cows("ps1_cow_data.txt")

    start = time.time()
    greedy = greedy_cow_transport(cows)
    greedy_time = time.time() - start

    start = time.time()
    brute = brute_force_cow_transport(cows)
    brute_time = time.time() - start

    print("Greedy trips:    %d  (%.4f s)" % (len(greedy), greedy_time))
    print("Brute force trips: %d  (%.4f s)" % (len(brute), brute_time))


if __name__ == "__main__":
    print("== load_cows ==")
    print(load_cows("ps1_cow_data.txt"))
    print("\n== greedy_cow_transport ==")
    print(greedy_cow_transport(load_cows("ps1_cow_data.txt")))
    print("\n== brute_force_cow_transport ==")
    print(brute_force_cow_transport(load_cows("ps1_cow_data.txt")))
    print("\n== compare_cow_transport_algorithms ==")
    compare_cow_transport_algorithms()
    print("\n== edge case: overweight cow ==")
    try:
        greedy_cow_transport({"MegaMoo": 12, "Moo": 3}, limit=10)
    except ValueError as e:
        print("ValueError:", e)
