"""Generate custom instances."""


import json
import random
import sys


# IMPORTANT: All values below (except for FRAC_SCANS_COV_*) must be integers.


SEED = None                   # Leave to None to get a random seed every time

NUM_SCANS_MIN = 40            # Minimum number of scans
NUM_SCANS_MAX = 60            # Maximum number of scans
SCAN_INDEX_COST_MIN = 10      # Minimum scan cost that can be provided by an index
SCAN_INDEX_COST_MAX = 100     # Maximum scan cost that can be provided by an index
SCAN_READ_COST_MIN = 150      # Minimum scan read cost
SCAN_READ_COST_MAX = 300      # Maximum scan read cost
NUM_INDEXES_MIN = 50          # Minimum number of possible indexes
NUM_INDEXES_MAX = 100         # Maximum number of possible indexes
NUM_EXISTING_INDEXES_MIN = 1  # Minimum number of existing indexes
NUM_EXISTING_INDEXES_MAX = 3  # Maximum number of existing indexes
IWO_MIN = 10                  # Minimum IWO of an index
IWO_MAX = 30                  # Maximum IWO of an index
FRAC_SCANS_COV_MIN = 0.1      # Minimum fraction of the scans covered by an index
FRAC_SCANS_COV_MAX = 0.25     # Maximum fraction of the scans covered by an index


def generate_instance(filename,
                      seed,
                      num_scans_min,
                      num_scans_max,
                      scan_index_cost_min,
                      scan_index_cost_max,
                      scan_read_cost_min,
                      scan_read_cost_max,
                      num_indexes_min,
                      num_indexes_max,
                      num_existing_indexes_min,
                      num_existing_indexes_max,
                      iwo_min,
                      iwo_max,
                      frac_scans_cov_min,
                      frac_scans_cov_max):
    """Generate an instance and save it to a file."""
    if seed is not None:
        random.seed(seed)

    assert isinstance(num_scans_min, int)
    assert isinstance(num_scans_max, int)
    assert isinstance(scan_index_cost_min, int)
    assert isinstance(scan_index_cost_max, int)
    assert isinstance(scan_read_cost_min, int)
    assert isinstance(scan_read_cost_max, int)
    assert isinstance(num_indexes_min, int)
    assert isinstance(num_indexes_max, int)
    assert isinstance(num_existing_indexes_min, int)
    assert isinstance(num_existing_indexes_max, int)
    assert isinstance(iwo_min, int)
    assert isinstance(iwo_max, int)

    assert 0 < num_scans_min <= num_scans_max
    assert 0 < scan_index_cost_min <= scan_index_cost_max
    assert 0 < scan_read_cost_min <= scan_read_cost_max
    assert scan_index_cost_min < scan_read_cost_max
    assert 0 < num_indexes_min <= num_indexes_max
    assert 0 <= num_existing_indexes_min <= num_existing_indexes_max
    assert 0 < iwo_min <= iwo_max
    assert 0 < frac_scans_cov_min <= frac_scans_cov_max <= 1

    data = {"Scans": [],
            "Existing Indexes": [],
            "Possible Indexes": []}

    num_scans = random.randint(num_scans_min, num_scans_max)

    for scan in range(num_scans):
        data["Scans"].append({"Scan ID": f"Scan {scan}",
                              "Sequential Scan Cost": random.randint(scan_read_cost_min,
                                                                     scan_read_cost_max),
                              "Existing Index Costs": [],
                              "Possible Index Costs": []})

    def _add_index(index, index_type):
        """Add index `index` of type "Possible" or "Existing"."""
        assert index_type in ("Possible", "Existing")
        data[f"{index_type} Indexes"].append({"Index": {"Index OID": f"Index {index}"},
                                              "Index Write Overhead": random.randint(iwo_min,
                                                                                     iwo_max)})

        # Scans covered by this index
        covered = random.sample(range(num_scans),
                                round(num_scans * random.uniform(frac_scans_cov_min,
                                                                 frac_scans_cov_max)))
        for scan in covered:
            # The read cost should always be strictly worse than the cost of the index
            read_cost = data["Scans"][scan]["Sequential Scan Cost"]
            if read_cost <= scan_index_cost_max:
                max_cost = read_cost - 1
            else:
                max_cost = scan_index_cost_max

            data["Scans"][scan][f"{index_type} Index Costs"].append(
                {"Index OID": f"Index {index}",
                 "Cost": random.randint(scan_index_cost_min,
                                        max_cost)})

    # Add possible indexes
    for index in range(random.randint(num_indexes_min, num_indexes_max)):
        _add_index(index, "Possible")

    # Add existing indexes
    for index in range(random.randint(num_existing_indexes_min, num_existing_indexes_max)):
        _add_index(index, "Existing")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    assert len(sys.argv) == 2

    generate_instance(sys.argv[1],
                      SEED,
                      NUM_SCANS_MIN,
                      NUM_SCANS_MAX,
                      SCAN_INDEX_COST_MIN,
                      SCAN_INDEX_COST_MAX,
                      SCAN_READ_COST_MIN,
                      SCAN_READ_COST_MAX,
                      NUM_INDEXES_MIN,
                      NUM_INDEXES_MAX,
                      NUM_EXISTING_INDEXES_MIN,
                      NUM_EXISTING_INDEXES_MAX,
                      IWO_MIN,
                      IWO_MAX,
                      FRAC_SCANS_COV_MIN,
                      FRAC_SCANS_COV_MAX)
