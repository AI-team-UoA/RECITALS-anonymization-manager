"""
Command-line interface for Anonymization Manager.

Showcases main AnonymizationManager, AnonymizationConfig functionalities and
extra AnonymizedData statistics.

User-facing output is printed to the terminal. Audit events are written to the 
log file (see anonymization_manager.log).
"""

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

import pandas as pd
from loguru import logger

from anonymization_manager import AnonymizationConfig, AnonymizationManager
from anonymization_manager.exceptions import AnonymizationError
from anonymization_manager.log import setup_logging


@dataclass
class Arguments:
    """Command line arguments."""

    config_path: str
    output_path: str


def _parse_arguments() -> tuple[Arguments, AnonymizationConfig]:
    """
    Parses the command-line arguments.

    Returns:
        tuple[Arguments, AnonymizationConfig]: The parsed arguments and the provided config.
    """
    parser = argparse.ArgumentParser(
        description="Anonymize datasets in various formats with k-anonymity, l-diversity and t-closeness"
    )

    parser.add_argument(
        "-c",
        "--config",
        required=True,
        type=str,
        help="Relative path to the json configuration file",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=False,
        type=str,
        help="Relative path to save the resulting anonymized dataset",
    )

    args = parser.parse_args()

    config = AnonymizationConfig.from_json(args.config)

    return (
        Arguments(config_path=args.config, output_path=args.output),
        config,
    )


def _generate_path(config) -> str:
    """
    Generate a results file path based on the dataset and configuration parameters.

    The filename format is:
        ./results/<dataset>_k-<k>_l-<l>_t-<t>

    The dataset name is derived from the stem of `config.data`, i.e., the filename
    without its extension. Fields `l` and `t` are optional. If not present or None,
    they will be omitted from the filename.

    Args:
        config (object): Configuration object with the following attributes:
            - data (str): Path to the dataset file (e.g. "./data/adult.csv").
            - k (int): The k-anonymity parameter.
            - l (Optional[int]): The l-diversity parameter (optional).
            - t (Optional[int]): The t-closeness parameter (optional).

    Returns:
        str: The generated results path (without file extension).
    """
    dataset = Path(config.data).stem
    parts = [f"{dataset}_k-{config.k}"]

    if hasattr(config, "l") and config.l is not None:
        parts.append(f"l-{config.l}")
    if hasattr(config, "t") and config.t is not None:
        parts.append(f"t-{config.t}")

    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    filename = "_".join(parts) + ".csv"
    return str(results_dir / filename)

def _fail(message: str) -> None:
    """Records a failed run in the log, tells the user, and exits."""
    logger.error("CLI run failed: {}", message)
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def main():
    setup_logging()

    try:
        args, config = _parse_arguments()
    except FileNotFoundError as ex:
        _fail(f"Config file not found: {ex.filename}")
    except json.JSONDecodeError as ex:
        _fail(f"Config file is not valid JSON: {ex}")
    except AnonymizationError as ex:
        _fail(f"Invalid configuration: {ex}")

    logger.info("CLI run started with config file {}", args.config_path)

    try:
        data = AnonymizationManager.anonymize(config)
    except AnonymizationError as ex:
        _fail(str(ex))

    time = data.get_anonymization_time()

    print(
        f"Data anonymized successfully! Elapsed time: {timedelta(seconds=time / 1000)}"
    )

    path = args.output_path

    if not path:
        path = _generate_path(config)

    data.store_as_csv(path)
    logger.info("Anonymized data stored in {}", Path(path).resolve())
    print(f"Anonymized data stored in {path}")

    entries_num = 10
    print(f"Top {entries_num} entries:")
    anon_data: pd.DataFrame = data.get_anonymized_data_as_dataframe()
    print(anon_data.head(n=entries_num))

    trans = data.get_transformations()
    print("Transformations applied:")
    for key, value in trans.items():
        print(f"{key}: {value}")

    return


if __name__ == "__main__":
    main()
