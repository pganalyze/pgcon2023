"Main program."


import cli
import reader
import utils
import sys


if __name__ == "__main__":
    cli_args = cli.get_cli_args()

    use_stdin_for_data = False
    use_stdin_for_settings = False

    data_json = None
    if cli_args["Data JSON"] == "-":
        use_stdin_for_data = True
    else:
        with open(cli_args["Data JSON"], "r", encoding="utf-8") as f:
            data_json = f.read()

    settings_json = None
    if cli_args["Settings JSON"] is not None:
        if cli_args["Settings JSON"] == "-":
            use_stdin_for_settings = True
        else:
            with open(cli_args["Settings JSON"], "r", encoding="utf-8") as f:
                settings_json = f.read()

    if use_stdin_for_data and use_stdin_for_settings:
        data_json, settings_json = sys.stdin.read().split("\n", 2)
    elif use_stdin_for_data:
        data_json = sys.stdin.read()
    elif use_stdin_for_settings:
        settings_json = sys.stdin.read()

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
