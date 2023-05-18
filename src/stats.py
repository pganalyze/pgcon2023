"""Infer statistics from a solution."""


def total_coverage(rdr,
                   solution):
    """Return the number of scans covered by indexes in the solution."""
    num_scans = rdr.get_num_scans()
    scan_read_costs = rdr.get_read_costs()

    coverage = 0
    for scan in range(num_scans):
        scan_cost = cost_of_scan(rdr,
                                 solution,
                                 scan)

        # If the scan cost is lower than the reading cost, then the scan is covered
        if scan_cost < scan_read_costs[scan]:
            coverage += 1

    return coverage


def total_iwo(rdr,
              solution):
    """Return the index write overhead of the solution."""
    return sum(used * rdr.get_index_iwo()[idx] for idx, used in enumerate(solution))


def num_indexes_used(solution):
    """Return the number of indexes used in the solution."""
    return sum(solution)


def total_cost(rdr,
               solution):
    """Return the total cost of the solution."""
    num_scans = rdr.get_num_scans()

    min_costs = [None for _ in range(num_scans)]
    for scan in range(num_scans):
        min_costs[scan] = cost_of_scan(rdr,
                                       solution,
                                       scan)

    return sum(min_costs[i] for i in range(num_scans))


def best_covered_by(rdr,
                    solution,
                    scan):
    """Return the index that offers the best coverage for the scan."""
    read_cost = rdr.get_read_costs()[scan]
    index_costs = rdr.get_index_costs()

    min_value = read_cost
    best_coverage = None

    for idx, used in enumerate(solution):
        if used == 0:
            continue
        if index_costs[idx][scan] is None:
            continue
        if index_costs[idx][scan] < min_value:
            min_value = index_costs[idx][scan]
            best_coverage = idx

    return best_coverage


def cost_of_scan(rdr,
                 solution,
                 scan):
    """Return the cost of a given scan in the solution."""
    read_cost = rdr.get_read_costs()[scan]
    index_costs = rdr.get_index_costs()

    min_value = read_cost
    for idx, used in enumerate(solution):
        if used == 0:
            continue
        if index_costs[idx][scan] is None:
            continue
        min_value = min(min_value, index_costs[idx][scan])

    return min_value


def compute_objective(rdr,
                      goal_name,
                      solution):
    """Compute and return the objective value of a solution."""
    if goal_name == "Maximal Coverage":
        return total_coverage(rdr, solution)

    if goal_name == "Minimal IWO":
        return total_iwo(rdr, solution)

    if goal_name == "Minimal Indexes":
        return num_indexes_used(solution)

    if goal_name == "Minimal Cost":
        return total_cost(rdr, solution)
