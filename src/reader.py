"""Read and write the problem data and the optimizer settings."""


import copy
import json
import stats


class Reader:
    """Read, store, and write the problem data and the optimizer settings."""

    _problem = {}       # Problem data
    _settings = {}      # Optimizer settings
    _solutions = {}     # All intermediary solutions
    _translation = {}   # Correspondence between string IDs and their associated integer indices

    # Default optimizer settings
    _maximum_num_indexes = None  # Maximum number of indexes allowed
    _maximum_iwo = None          # Maximum IWO allowed

    def __init__(self, problem, time_limit, settings=None):
        """Read and store the problem data and the optimizer settings from serialized JSON objects.

        Default optimizer settings will be provided if some are missing from the settings.
        """
        self._read_problem(json.loads(problem))

        # _read_problem() must be first, because _read_settings() uses data from the problem
        if settings is None:
            settings = json.dumps({})
        self._read_settings(json.loads(settings))

        self._time_limit = time_limit

    def __str__(self):
        """For pretty printing the Reader object."""
        pretty = f"""
        Number of scans: {self.get_num_scans()}
        Sequential costs: {' '.join(str(x) for x in self.get_read_costs())}
        Number of indexes: {self.get_num_indexes()} ({self.get_num_eind()} existing, {self.get_num_pind()} possible)
        Index IWOs: {' '.join(str(x) for x in self._problem['Index IWOs'])}
        Index/scan cost matrix:\n"""
        for row in self._problem["Index Costs (R)"]:
            pretty += f"{' '*8}{' '.join(str(x) for x in row)}\n"
        pretty += f"\n{' '*8}Goals:\n"
        for goal in self._settings["Goals"]:
            pretty += f"{' '*8}{goal['Name']}: {goal['Strictness']}\n"
        pretty += f"\n{' '*8}Rules:\n"
        for rule, value in self._settings["Rules"].items():
            pretty += f"{' '*8}{rule}: {value}\n"
        return pretty

    def get_scan_id(self, scan):
        """Return the ID of a scan."""
        return self._translation["Scan IDs"][scan]

    def get_index_oid(self, index):
        """Return the OID of an index, None if the index is None."""
        if index is not None:
            return self._translation["Index OIDs"][index]
        return None

    def get_num_scans(self):
        """Return the number of scans."""
        return len(self._translation['Scan IDs'])

    def get_read_costs(self):
        """Return the scan read costs."""
        return tuple(self._problem['Sequential Scan Costs'])

    def get_num_indexes(self):
        """Return the number of indexes (possible and existing)."""
        return len(self._translation['Index OIDs'])

    def get_num_pind(self):
        """Return the number of possible indexes."""
        return self._problem["Number of Possible Indexes"]

    def get_num_eind(self):
        """Return the number of existing indexes."""
        return self._problem["Number of Existing Indexes"]

    def get_index_iwo(self):
        """Return the index write overhead of the indexes."""
        return tuple(self._problem["Index IWOs"])

    def get_index_costs(self):
        """Return the costs of the existing indexes (None if a scan is not covered by the index)."""
        return tuple(tuple(index) for index in self._problem["Index Costs"])

    def get_maximum_num_indexes(self):
        """Return the maximum number of indexes constraint value."""
        return self._settings["Maximum Number of Possible Indexes"]

    def get_maximum_iwo(self):
        """Return the maximum IWO constraint value."""
        return self._settings["Maximum IWO"]

    def get_problem(self):
        """Return a deep copy of the problem data."""
        return copy.deepcopy(self._problem)

    def get_settings(self):
        """Return a deep copy of the optimizer settings."""
        return copy.deepcopy(self._settings)

    def get_solutions(self):
        """Return a deep copy of the optimizer solutions."""
        return copy.deepcopy(self._solutions)

    def get_time_limit(self):
        """Return the time limit."""
        return self._time_limit

    def get_results(self):
        """Return the solution and statistics."""
        solutions = self.get_solutions()
        last_solution = solutions[list(solutions.keys())[-1]]["x"]
        results = {}

        results["Goals"] = []
        for goal in solutions:
            results["Goals"].append({goal:
                                     solutions[goal]["Objective Value (Real)"]})

        scans = []
        for scan in range(self.get_num_scans()):
            new_scan = {}

            new_scan["Scan ID"] = self.get_scan_id(scan)

            new_scan["Cost"] = stats.cost_of_scan(self,
                                                  last_solution,
                                                  scan)

            index = stats.best_covered_by(self,
                                          last_solution,
                                          scan)

            new_scan["Best Covered By"] = self.get_index_oid(index)

            scans.append(new_scan)

        results["Scans"] = scans

        results["Indexes"] = {}
        results["Indexes"]["Existing Indexes"] = []
        results["Indexes"]["Possible Indexes"] = []
        for index, used in enumerate(last_solution):
            new_index = {}
            new_index["Index OID"] = self.get_index_oid(index)
            new_index["Selected"] = used == 1
            if index < self.get_num_eind():
                results["Indexes"]["Existing Indexes"].append(new_index)
            else:
                results["Indexes"]["Possible Indexes"].append(new_index)

        statistics = {}

        # Coverage
        statistics["Coverage"] = {}
        statistics["Coverage"]["Total"] = stats.total_coverage(self, last_solution)
        statistics["Coverage"]["Uncovered"] = self.get_num_scans() - \
            stats.total_coverage(self,
                                 last_solution)

        # Cost
        statistics["Cost"] = {}
        statistics["Cost"]["Total"] = stats.total_cost(self, last_solution)
        statistics["Cost"]["Maximum"] = stats.maximum_cost(self, last_solution)

        # Indexes
        statistics["Indexes Used"] = {}
        statistics["Indexes Used"]["Total"] = stats.num_indexes_used(last_solution)

        # IWO
        statistics["Index Write Overhead"] = {}
        statistics["Index Write Overhead"]["Total"] = stats.total_iwo(self, last_solution)

        results["Statistics"] = statistics

        return results

    def get_translation(self):
        """Return a deep copy of the translation between string IDs and their associated indices."""
        return copy.deepcopy(self._translation)

    def add_solution(self, goal, solution):
        """Add the solution of a goal to the list of solutions."""
        self._solutions[goal] = solution

    def _read_problem(self, problem):
        """Read the problem data from a serialized JSON object."""
        self._build_translation(problem)

        self._problem["Number of Existing Indexes"] = len(problem["Existing Indexes"])
        self._problem["Number of Possible Indexes"] = len(problem["Possible Indexes"])

        self._problem["Sequential Scan Costs"] = \
            [None for _ in range(len(self._translation["Scan IDs"]))]
        self._problem["Index Costs"] = \
            [[None for _ in range(len(self._translation["Scan IDs"]))]
             for _ in range(len(self._translation["Index OIDs"]))]
        self._problem["Index IWOs"] = \
            [None for _ in range(len(self._translation["Index OIDs"]))]

        # There must be at least one possible index, otherwise there is no problem to solve
        assert len(self._problem["Index IWOs"]) > self.get_num_eind()

        # Extract relevant data from the scans
        for scan in problem["Scans"]:
            scan_idx = self._translation["Scan IDs"].index(scan["Scan ID"])
            scan_sequential_cost = scan["Sequential Scan Cost"]
            self._problem["Sequential Scan Costs"][scan_idx] = scan_sequential_cost

            for index in scan["Existing Index Costs"] + scan["Possible Index Costs"]:
                index_idx = self._translation["Index OIDs"].index(index["Index OID"])

                # If the index cost is not better than the sequential scan cost, ignore it
                if index["Cost"] >= scan_sequential_cost:
                    continue

                # If we reach this point, the cost offered by the index is good for this scan
                self._problem["Index Costs"][index_idx][scan_idx] = index["Cost"]

        # Extract relevant data from the indexes
        for index in problem["Existing Indexes"] + problem["Possible Indexes"]:
            index_idx = self._translation["Index OIDs"].index(index["Index"]["Index OID"])
            self._problem["Index IWOs"][index_idx] = index["Index Write Overhead"]

        # Build the index cost matrices of type B (a covered scan has a cost of 1, an uncovered scan
        # has a cost of 0)
        self._problem["Index Costs (B)"] = \
            copy.deepcopy(self._problem["Index Costs"])
        for i, row in enumerate(self._problem["Index Costs (B)"]):
            for j, value in enumerate(row):
                if value is not None:
                    self._problem["Index Costs (B)"][i][j] = 1
                else:
                    self._problem["Index Costs (B)"][i][j] = 0

        # Build the index cost matrices of type R (a covered scan has the cost provided by the
        # index, an uncovered scan has the sequential cost)
        self._problem["Index Costs (R)"] = \
            copy.deepcopy(self._problem["Index Costs"])
        for i, row in enumerate(self._problem["Index Costs (R)"]):
            for j, value in enumerate(row):
                if value is None:
                    self._problem["Index Costs (R)"][i][j] = \
                        self._problem["Sequential Scan Costs"][j]

    def _build_translation(self, problem):
        """Build the correspondence between string IDs and their associated integer indices.

        self._translation["Scan IDs"] = ["012-345-6789", "987-654-3210", ...]
        self._translation["Indexes OIDs"] = [00001, 00002, ...]
        """
        # Ignore scans that have no sequential cost
        self._translation["Scan IDs"] = tuple(scan["Scan ID"] for scan in problem["Scans"]
                                              if scan["Sequential Scan Cost"] is not None)
        self._translation["Index OIDs"] = tuple(index["Index"]["Index OID"]
                                                for index in problem["Existing Indexes"] +
                                                problem["Possible Indexes"])

    def _read_settings(self, settings):
        """Read the optimizer settings from a serialized JSON object.

        Provides default values if necessary.
        """
        # Goals (default value if omitted)
        if "Goals" in settings:
            self._settings["Goals"] = settings["Goals"]
        else:
            self._settings["Goals"] = [{"Name": "Minimal Cost",
                                        "Strictness": 1},
                                       {"Name": "Minimal Indexes",
                                        "Strictness": 1}]

        # Rules
        if "Rules" in settings:
            rules = settings["Rules"]
        else:
            rules = {}

        # Default rules if omitted (unconstrained)
        if "Maximum Number of Indexes" in rules:
            # If the maximum number of possible indexes is <= 0, there is no solution
            assert rules["Maximum Number of Possible Indexes"] >= 1
            self._settings["Maximum Number of Possible Indexes"] = \
                rules["Maximum Number of Possible Indexes"]
        else:
            self._settings["Maximum Number of Possible Indexes"] = self.get_num_pind()

        if "Maximum IWO" in rules:
            assert rules["Maximum IWO"] >= 1  # If the maximum IWO is <= 0, there is no solution
            self._settings["Maximum IWO"] = rules["Maximum IWO"]
        else:
            self._settings["Maximum IWO"] = sum(self._problem["Index IWOs"])

        self._settings["Rules"] = rules
