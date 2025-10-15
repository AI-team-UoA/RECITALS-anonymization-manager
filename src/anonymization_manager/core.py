"""
The public-facing API of the Anonymization Manager component, part of the open
source RECITALS platform.
"""

import json

import pandas as pd

#from anonymization_manager.adapters.anjana import AnjanaAdapter
from anonymization_manager.adapters.arx.arx_adapter import ArxAdapter
from anonymization_manager.config import AnonymizationConfig


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
        if config.backend == "arx":
            self.adapter = ArxAdapter(config)
        else:
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

                    "k": 10,
                    "l": 2,
                    "t": 0.5,

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
            config_json = json.load(file)

        config = AnonymizationConfig(
            data=config_json.get("data"),
            identifiers=config_json.get("identifiers"),
            quasi_identifiers=config_json.get("quasi_identifiers"),
            sensitive_attributes=config_json.get("sensitive_attributes"),
            insensitive_attributes=config_json.get("insensitive_attributes"),
            hierarchies=config_json.get("hierarchies"),
            k=config_json.get("k"),
            l=config_json.get("l"),
            t=config_json.get("t"),
            suppression_limit=config_json.get("suppression_limit"),
            anonymized_data=config_json.get("anonymized_data"),
            backend=config_json.get("backend", "arx"),
        )

        return cls(config)

    def update_config(self, new_config: AnonymizationConfig):
        """
        Given a new anonymization configuration, update the current workflow.

        Args:
            config (AnonymizationConfig): Configuration object with dataset,
                identifiers, hierarchies, parameters, suppression, output path,
                and backend.
        """
        self.adapter.update_config(new_config)

    def anonymize(self) -> tuple[int, dict[str, int]]:
        """
        Executes the anonymization pipeline based on the class instance's
        specified parameters.

        Saves the results to `./results/<dataset>_k-<k>_l-<l>_t-<t>.csv`.

        Returns:
            int: Return code, transformations. 0 means anonymization workflow
                finished correctly. -1 Means an error occurred.
        """
        code, results = self.adapter.anonymize()
        return code, results

    def get_anonymized_data(self) -> pd.DataFrame:
        """
        Loads the anonymized dataset in memory.

        Returns:
            pd.DataFrame: The resulting anonymized dataset.
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