"""Goal of the user (an objective that later becomes a constraint)."""


import copy
from math import ceil, floor
from ortools.sat.python import cp_model

import modelize


class Goal:
    """Goal of the user.

    A Goal object takes care of both the objective and the resulting constraint.
    """

    _names = ("Maximal Coverage",
              "Minimal IWO",
              "Minimal Indexes",
              "Minimal Cost")

    def __init__(self, name, strictness=1):
        """Intialize the goal.

        Args:
          name: Name of the goal (e.g., "Maximal Coverage").
          strictness: How strict the resulting constraint should be (0.0 <= strictness <= 1.0).
        """
        self._name = name
        self._strictness = strictness

        assert self._name in self._names
        assert 0.0 <= self._strictness <= 1.0

        # Value of the optimized goal, None if it has not yet been optimized
        self._value = None

    def get_name(self):
        """Return the name of the goal."""
        return self._name

    def is_optimized(self):
        """Return a boolean indicating if the goal has been optimized."""
        return self._value is not None

    def get_value(self):
        """Return the value of the goal."""
        assert self.is_optimized()

        return self._value

    def update_value(self, value):
        """Update the value of the goal after it has been optimized."""
        self._value = value

    def add_as_objective(self, model):
        """Add the goal as an objective to the model."""
        if self._name == "Maximal Coverage":
            model.Add(model.objective == cp_model.LinearExpr.Sum(model.is_covered))
            model.Maximize(model.objective)

        elif self._name == "Minimal IWO":
            model.Add(model.objective ==
                      cp_model.LinearExpr.WeightedSum(model.x, model.index_iwo))
            model.Minimize(model.objective)

        elif self._name == "Minimal Indexes":
            model.Add(model.objective == cp_model.LinearExpr.Sum(model.x))
            model.Minimize(model.objective)

        elif self._name == "Minimal Cost":
            model.Add(model.objective == cp_model.LinearExpr.Sum(model.scan_cost))
            model.Minimize(model.objective)

    def add_as_constraint(self, model):
        """Add the goal as a constraint to the model."""
        assert self.is_optimized()

        if self._name == "Maximal Coverage":
            model.Add(cp_model.LinearExpr.Sum([model.is_covered[j] for j in range(model.num_scans)])
                      >= ceil(self.get_value() * self._strictness))

        elif self._name == "Minimal IWO":
            model.Add(cp_model.LinearExpr.WeightedSum(model.x, model.index_iwo)
                      <= floor(self.get_value() * (2 - self._strictness)))

        elif self._name == "Minimal Indexes":
            model.Add(cp_model.LinearExpr.Sum(model.x)
                      <= floor(self.get_value() * (2 - self._strictness)))

        elif self._name == "Minimal Cost":
            model.Add(cp_model.LinearExpr.Sum(model.scan_cost)
                      <= floor(self.get_value() * (2 - self._strictness)))

    def get_objective_description(self):
        """Return the description of the objective."""
        description = ""

        if self._name == "Maximal Coverage":
            description = "Maximize the number of scans covered (by existing and possible indexes)"

        elif self._name == "Minimal IWO":
            description = "Minimize the sum of IWO (of the existing and possible indexes)"

        elif self._name == "Minimal Indexes":
            description = "Minimize the number of existing and possible indexes"

        elif self._name == "Minimal Cost":
            description = "Minimize the combined costs of all the scans"

        return description

    def get_constraint_description(self):
        """Return the description of the constraint."""
        assert self.is_optimized()

        ceil_suffix = "must be at least " + \
            f"{ceil(self.get_value()) * self._strictness:.2f} " + \
            f"({self.get_value()} with a strictness of {self._strictness:.2%})"

        floor_suffix = "must be at most " + \
            f"{floor(self.get_value()) * (2 - self._strictness):.2f} " + \
            f"({self.get_value()} with a strictness of {self._strictness:.2%})"

        description = ""

        if self._name == "Maximal Coverage":
            description = f"Scan coverage (by existing and possible indexes) {ceil_suffix}"

        elif self._name == "Minimal IWO":
            description = f"The sum of all IWO {floor_suffix}"

        elif self._name == "Minimal Indexes":
            description = f"The number of existing and possible indexes {floor_suffix}"

        elif self._name == "Minimal Cost":
            description = f"The combined costs of all the scans {floor_suffix}"

        return description
