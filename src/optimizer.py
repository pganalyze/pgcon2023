"""Index selection optimizer."""


import goal
import modelize
import stats


class Optimizer:
    """Index selection optimizer."""

    def __init__(self, rdr, log_level):
        """Initialize the optimizer.

        Args:
          rdr: Previously-initialized Reader object.
          log_level = Integer indicating printing level (0 = silent, 1 = normal, 2 = verbose).
        """
        self._reader = rdr
        self._log_level = log_level
        self._solve()

    def _vprint(self, string='', highlight=False):
        """Print the string according to the log level."""
        if self._log_level >= 2:
            if highlight:
                print(f"=== {string} {'='*(75-len(string))}")
            else:
                print(string)

    def _solve(self):
        """Solves the multi-objective problem."""
        indent = "   "

        # Extract all goals in order
        goals = []
        for gl in self._reader.get_settings()["Goals"]:
            if "Strictness" not in gl:
                gl["Strictness"] = 1
            goals.append(goal.Goal(gl["Name"],
                                   gl["Strictness"]))

        self._vprint("Start of the solving process", highlight=True)
        self._vprint()

        self._vprint("Constraints", highlight=True)
        self._vprint(f"Maximum Number of Indexes: {self._reader.get_maximum_num_indexes()}")
        self._vprint(f"Maximum IWO: {self._reader.get_maximum_iwo()}")
        self._vprint()

        i = 0
        current_solution = None
        while i < len(goals):
            self._vprint(f"Step {i + 1}", highlight=True)

            self._vprint("1. Creating a new basic model\n")
            model = modelize.build_basic_model(self._reader.get_problem(),
                                               self._reader.get_settings())

            self._vprint("2. Adding previously-optimized goals")
            if i == 0:
                self._vprint(f"{indent}(No goals have yet been optimized)")
            else:
                for j in range(i):
                    self._vprint(f"{indent}{goals[j].get_constraint_description()}")
                    goals[j].add_as_constraint(model)
            self._vprint()

            self._vprint("3. Optimize the current goal")
            self._vprint(f"{indent}{goals[i].get_objective_description()}")
            goals[i].add_as_objective(model)
            self._vprint()

            self._vprint("4. Solve the model")
            results = modelize.solve_model(model,
                                           time_limit=self._reader.get_time_limit(),
                                           warm_start=current_solution)
            objective_value = results["Objective Value"]
            current_solution = tuple(results["Indexes"])
            self._reader.add_solution(goals[i].get_name(),
                                      {"Objective Value": objective_value,
                                       "Objective Value (Real)": stats.compute_objective(self._reader,
                                                                                         goals[i].get_name(),
                                                                                         current_solution),
                                       "x": tuple(results["Indexes"])})
            self._vprint(f"{indent}The solution found has value: {objective_value}")
            goals[i].update_value(objective_value)
            self._vprint()

            i += 1

        self._vprint(f"End of the solving process", highlight=True)

    def get_results(self):
        """Return the results of the solving process."""
        return self._reader.get_results()
