"""
Command-line interface for Anonymization Manager.
"""

import argparse
import pprint
from dataclasses import dataclass
from datetime import timedelta

import pandas as pd
from loguru import logger

from anonymization_manager import AnonymizationConfig, AnonymizationManager


@dataclass
class Arguments:
    """Command line arguments."""

    config_path: str
    output_path: str


def parse_arguments() -> Arguments:
    """
    Parses the command-line arguments.

    Returns:
        Arguments: The parsed arguments.
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
        default="./output.csv",
    )

    args = parser.parse_args()

    return Arguments(config_path=args.config, output_path=args.output)


def main():
    args = parse_arguments()
    config = AnonymizationConfig.from_json(args.config_path)
    am = AnonymizationManager()

    data = am.anonymize(config)

    time = data.get_anonymization_time()
    logger.success(
        f"Data anonymized successfully! Elapsed time: {timedelta(seconds=time / 1000)}"
    )

    data.store_as_csv(args.output_path)
    logger.info(f"Anonymized data stored in {args.output_path}")

    entries_num = 10
    logger.info(f"Top {entries_num} entries:")
    anon_data: pd.DataFrame = data.get_anonymized_data_as_dataframe()
    print(anon_data.head(n=entries_num))

    trans = data.get_transformations()
    logger.info("Transformations applied:")
    pprint.pprint(trans, indent=4, sort_dicts=False)

    return


if __name__ == "main":
    main()
