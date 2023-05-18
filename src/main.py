"Main program."


import cli
import reader
import utils


if __name__ == "__main__":
    cli_args = cli.get_cli_args()

    with open(cli_args["Data JSON"], "r", encoding="utf-8") as f:
        data_json = f.read()

    settings_json = None
    if cli_args["Settings JSON"] is not None:
        with open(cli_args["Settings JSON"], "r", encoding="utf-8") as f:
            settings_json = f.read()

    time_limit = cli_args["Time Limit"]

    verbose = cli_args["Verbose"]

    log_level = 0
    if verbose:
        log_level = 2

    results = utils.run(data_json,
                        time_limit,
                        settings_json,
                        print_input_data=verbose,
                        log_level=log_level)

    print(results)
