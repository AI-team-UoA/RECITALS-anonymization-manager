"""
Command-line interface for Anonymization Manager.
"""

import argparse
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

import pandas as pd
from loguru import logger

from anonymization_manager import AnonymizationConfig, AnonymizationManager


@dataclass
class Arguments:
    """Command line arguments."""

    config_path: str
    output_path: str


def parse_arguments() -> tuple[Arguments, AnonymizationConfig]:
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


def main():
    args, config = parse_arguments()
    am = AnonymizationManager()

    data = am.anonymize(config)

    time = data.get_anonymization_time()
    logger.success(
        f"Data anonymized successfully! Elapsed time: {timedelta(seconds=time / 1000)}"
    )

    path = args.output_path

    if not path:
        path = _generate_path(config)

    data.store_as_csv(path)
    logger.info(f"Anonymized data stored in {path}")

    entries_num = 10
    logger.info(f"Top {entries_num} entries:")
    anon_data: pd.DataFrame = data.get_anonymized_data_as_dataframe()
    print(anon_data.head(n=entries_num))

    trans = data.get_transformations()
    logger.info("Transformations applied:")
    for key, value in trans.items():
        print(f"{key}: {value}")

    return


if __name__ == "main":
    main()
