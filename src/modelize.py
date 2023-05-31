"""Model-building functions."""


import math
from ortools.sat.python import cp_model


def build_basic_model(problem, settings):
    """Build the basic model, without any special constraints or objectives, using the Reader data.

    Args:
      problem: The problem data.
      settings: The optimizer settings.

    Returns:
      A clean model.
    """
    model = cp_model.CpModel()
    model.infinity = 999999999999999999

    ### Data

    # Scans
    model.cost_read = problem["Sequential Scan Costs"]
    model.num_scans = len(model.cost_read)

    # Indexes
    model.cost_indexes_b = problem["Index Costs (B)"]
    model.cost_indexes_r = problem["Index Costs (R)"]
    model.index_iwo = problem["Index IWOs"]
    model.num_indexes = len(model.index_iwo)

    # Misc.
    model.max_num_indexes = settings["Maximum Number of Possible Indexes"] + \
        problem["Number of Existing Indexes"]  # Since einds are fixed, they must be included here
    model.max_iwo = settings["Maximum IWO"]

    ### Objective

    model.objective = model.NewIntVar(-model.infinity, model.infinity, 'objective')

    ### Decision variables

    # x[i] indicates if index i is selected in the solution
    model.x = [model.NewBoolVar(f"x_{i}") for i in range(model.num_indexes)]

    # Existing indexes are always selected in the solution
    for eind in range(problem["Number of Existing Indexes"]):
        model.Add(model.x[eind] == 1)

    ### Auxiliary variables

    # is_covered[j] indicates if scan j is covered by any index
    model.is_covered = [model.NewBoolVar(f"is_covered_{j}") for j in range(model.num_scans)]

    # scan_cost[j] == X indicates that the lowest cost of scan j is X (considering any coverage
    # offered by indexes, or simply just the sequential cost)
    model.scan_cost = [model.NewIntVar(0, model.cost_read[j], f"scan_cost_{j}")
                       for j in range(model.num_scans)]

    ### Constraints

    for j in range(model.num_scans):
        # is_covered
        model.Add(cp_model.LinearExpr.Sum([model.x[i] * model.cost_indexes_b[i][j]
                                           for i in range(model.num_indexes)])
                  >= 1).OnlyEnforceIf(model.is_covered[j])
        model.Add(cp_model.LinearExpr.Sum([model.x[i] * model.cost_indexes_b[i][j]
                                           for i in range(model.num_indexes)])
                  < 1).OnlyEnforceIf(model.is_covered[j].Not())

    # scan_cost
    for j in range(model.num_scans):
        # Lowest cost offered by an index (or the sequential cost if there is no index coverage)
        model.AddMinEquality(model.scan_cost[j],
                             [model.cost_indexes_r[i][j] * model.x[i] +
                              (1 - model.x[i]) * model.cost_read[j]
                              for i in range(model.num_indexes)])

    ### Hard constraints (optimizer settings)

    # Maximum Number of Possible Indexes
    model.Add(sum(model.x) <= model.max_num_indexes)

    # Maximum IWO
    model.Add(cp_model.LinearExpr.WeightedSum(model.x, model.index_iwo)
              <= model.max_iwo)

    return model


def solve_model(model, time_limit, warm_start=None):
    """Solve the model and return the results.

    Args:
      model: The model returned by build_basic_model(), possibly augmented.
      time_limit: The time limit in seconds.
      warm_start: Solution to warm start from.

    Returns:
      A dictionary of the results, in the form:
      - Indexes: A 0-1 array of resulting values for x.
      - Status: The solver status (one of Optimal, Feasible).
      - Objective Value: The objective value found by the solver.
      - Time: The wall time in seconds.
    """
    if warm_start is not None:
        for i in range(model.num_indexes):
            model.AddHint(model.x[i], warm_start[i])

    solver = cp_model.CpSolver()
    solver.parameters.random_seed = 0
    solver.parameters.num_search_workers = 16
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)
    status_name = solver.StatusName(status).capitalize()
    assert status_name in ("Feasible", "Optimal")
    objective_value = round(solver.ObjectiveValue())  # round() prevents some numerical issues
    wall_time = solver.WallTime()
    x_vars = [solver.Value(model.x[i]) for i in range(model.num_indexes)]

    return {"Indexes": x_vars,
            "Status": status_name,
            "Objective Value": objective_value,
            "Time": wall_time}
