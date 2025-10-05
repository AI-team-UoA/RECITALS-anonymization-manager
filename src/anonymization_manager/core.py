"""
The public-facing API of the Anonymization Manager component, part of the open
source RECITALS platform.
"""

import json
from dataclasses import dataclass

import pandas as pd

from anonymization_manager.adapters import anjana, arx


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
    backend: str | None = "arx"


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
        self.config: AnonymizationConfig = config
        if self.config.backend == "arx":
            ...
            self.adapter = arx
            ...
        else:
            ...
            self.adapter = anjana
            ...

    @classmethod
    def from_json(cls, json_path: str):
        """
        Create an AnonymizationManager instance from a JSON configuration file/
        workflow template.

        Args:
            json (str): The path to the JSON template. This json file must follow
                a structure similar to the following:

                ```json
                {
                    "data" : "path/to/data",

                    "identifiers" : {
                        "ids" : ["identifier1", "identifier2", "identifier3"],
                        "qids" : ["qidentifier1", "qidentifier2", "qidentifier3"],
                        "satts" : ["sidentifier1", "sidentifier2", "sidentifier3"],
                        "iatts" : ["iidentifier1", "iidentifier2", "iidentifier3"]
                    },

                    "hierarchies" : {
                        "h1":"path/to/h1",
                        "h2":"path/to/h2",
                        "h3":"path/to/h3"
                    },

                    "parameters" : {
                        "k": 10,
                        "l": 2,
                        "t": 0.5,
                    },

                    "suppresion" : {
                        "level" : 50,
                    },

                    "anonymized_data" : "path/to/anonymized_data",

                    "backend": "arx | anjana",
                }
                ```

                Depending on the given parameters (i.e. $k$, $l$ and/or $t$), the
                corresponding models will be applied, in a $k \\to l \\to t$ order.

        Returns:
            AnonymizationManager: An AnonymizationManager instance.
        """
        # Template file reading
        with open(json_path, "r") as file:
            values = json.load(file)

        # TODO file format checking
        data = pd.read_csv(values["data"])
        quasi_ident = values["quasi_ident"]
        ident = values["ident"]
        k = values["k"]
        l = values.get("l")
        t = values.get("t")
        supp_level = values["supp_level"]
        sens_att = values.get("sens_att")

        hierarchies = {
            key: dict(pd.read_csv(value, header=None))
            for key, value in values["hierarchies"].items()
        }

        # Strip whitespace from column names
        data.columns = data.columns.str.strip()

        # Strip whitespace from all string (object) columns
        str_cols = data.select_dtypes(include=["object", "string"]).columns
        data[str_cols] = data[str_cols].apply(lambda col: col.str.strip())

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
        code = self.adapter.anonymize(self.config)
        return code

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
