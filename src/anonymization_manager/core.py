"""
The public-facing API of the Anonymization Manager component, part of the open
source RECITALS platform.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass
class AnonymizationConfig:
    """
    Configuration for an anonymization workflow.

    Args:
        data (str): The path to the initial dataset. CSV, Excel, JSON and
            SQLite3 formats are supported.
        identifiers (dict[list[str]]): A dictionary containing lists with
            the IDs (ids), the quasi-IDs (qids), the sensitive attributes
            (satts) and insensitive attributes (iatts).
        hierarchies (dict[str]): A dictionary with the attributes as keys
            and the path to the CSV hierarchies as data.
        Parameters (dict[float]): A dictionary with all necessary parameters
            for the desired anonymity models (k for k-anonymity, l for
            l-diversity, t for t-closeness).
        suppression (int, optional): The percentage of suppression to be
            applied. Defaults to TBD.
        anonymized_data (str, optional): The path for the resulting dataset.
            Defaults to `./results/<dataset>_k-<k>_l-<l>_t-<t>.<extension>`.
        backend (str, optional): The backend library to be used, between
            ARX and ANJANA. Defaults to TBD.
    """

    data: str
    identifiers: dict[str, list[str]]
    hierarchies: dict[str, str]
    parameters: dict[str, float]
    suppression: int | None = 50
    anonymized_data: str | None = None
    backend: str | None = "anjana"


class AnonymizationManager:
    """
    An object holding the anonymization workflow configuration and providing the
    necessary functions to execute it.
    """

    def __init__(self, config: AnonymizationConfig):
        """
        Constructor of an AnonymizationManager instance.

        Args:
            config (AnonymizationConfig): Configuration object with dataset,
                identifiers, hierarchies, parameters, suppression, output path,
                and backend.
        """
        ...

    @classmethod
    def from_json(cls, json: str):
        """
        Create an AnonymizationManager instance from a JSON configuration file.

        Args:
            json (str): The path to the JSON template.

        Returns:
            AnonymizationManager: An AnonymizationManager instance.
        """
        ...

    def update_config(self, new_config: AnonymizationConfig):
        """
        Given a new anonymization configuration, update the current workflow.

        Args:
            config (AnonymizationConfig): Configuration object with dataset,
                identifiers, hierarchies, parameters, suppression, output path,
                and backend.
        """
        ...

    def anonymize(self) -> int:
        """
        Executes the anonymization pipeline based on the class instance's
        specified parameters.

        Returns:
            int: Return code. 0 means anonymization workflow finished correctly.
                -1 Means an error occurred.
        """
        ...

    def get_anonymized_data(self) -> pd.DataFrame:
        """
        Get the anonymized dataset in memory.

        Returns:
            Any: The anonymized dataset as a pandas DataFrame.
        """
        ...

    def get_transformations(self) -> dict[str, int]:
        """
        Retrieve transformation levels applied for each quasi-identifier.

        Returns:
            dict[str, int]: A dictionary with the QIs and their respective
                transformation level.
        """
        ...
