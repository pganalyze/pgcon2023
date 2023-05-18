"""Various utilities."""


import json

import optimizer
import reader


def run(data_json,
        time_limit,
        settings_json=None,
        print_input_data=False,
        log_level=0):
    """Run the model and return the results of the solving process.

    Args:
      data_json: The serialized "Explain" JSON object (string).
      time_limit: The time limit in seconds.
      settings_json: The serialized optimizer settings JSON object (string).
      print_input_data: If we should print the data.
      log_level: Integer indicating printing level (0 = silent, 1 = normal, 2 = verbose).

    Returns:
      A serialized JSON object of the results (string).
    """
    rdr = reader.Reader(data_json,
                        time_limit,
                        settings_json)

    if print_input_data:
        print("Problem data:")
        print(rdr)

    opt = optimizer.Optimizer(rdr,
                              log_level)

    results = opt.get_results()

    return json.dumps(results, indent=2)
