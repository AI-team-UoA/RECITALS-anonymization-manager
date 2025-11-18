import json
from dataclasses import dataclass

import pandas as pd
import os

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

    def __init__(
        self,
        data: str,
        identifiers: list[str],
        quasi_identifiers: list[str],
        sensitive_attributes: list[str],
        insensitive_attributes: list[str],
        hierarchies: dict[str, str],
        k: int | None = None,
        l: int | None = None,
        t: float | None = None,
        suppression_limit: float | None = None,
        backend: str | None = "arx",
    ):
        """
        Default initializer.
        """
        self.data = data
        self.identifiers = identifiers
        self.quasi_identifiers = quasi_identifiers
        self.sensitive_attributes = sensitive_attributes
        self.insensitive_attributes = insensitive_attributes
        self.hierarchies = hierarchies
        self.k = k
        self.l = l
        self.t = t
        self.suppression_limit = suppression_limit
        self.backend = backend

        # Validates the config file.
        self._validate()

    @classmethod
    def from_json(cls, json_path: str):
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
            k=config_json.get("k", None),
            l=config_json.get("l", None),
            t=config_json.get("t", None),
            suppression_limit=config_json.get("suppression_limit", None),
            backend=config_json.get("backend", None),
        )

        return config

    def _validate(self) -> None:
        """A helper method used for validating the configuration."""
        self._validate_parameters()
        self._validate_attributes()
        self._validate_dataset()
        self._validate_hierarchies()
        
    def _validate_parameters(self) -> None:
        """Validates k, l, t, suppression and backend parameters."""

        # --- Checks if k is correct ---
        if self.k is not None:
            if not isinstance(self.k, int) or  self.k <= 0:
                raise ValueError(
                    f"The parameter for k-anonymity must be a positive integer, but got {self.k!r} instead!"
                )
        
        # --- Checks if l is correct ---
        if self.l is not None:
            if not isinstance(self.l, int) or  self.l <= 0:
                raise ValueError(
                    f"The parameter for l-diversity must be a positive integer, but got {self.l!r} instead!"
                )
        
        # --- Checks if t is correct ---
        if self.t is not None:
            if not isinstance(self.t, float) or not (0 <= self.t <= 1):
                raise ValueError(
                    f"The parameter for t-closeness must be a float in range [0,1], but got {self.t!r} instead!"
                )
        
        # --- Checks if the suppression limit is correct ---
        if self.suppression_limit is not None:
            if not isinstance(self.suppression_limit, int) or not (0 <= self.suppression_limit <= 100):
                raise ValueError(
                    f"The parameter for suppression limit must be an integer in range [0,100], but got {self.suppression_limit!r} instead!"
                )

        # --- Checks if the backend is correct ---    
        if self.backend not in [None, "arx", "anjana"]:
            raise ValueError(
                f"The backend must be either 'arx' or 'anjana', but got {self.backend!r} instead!"
            )
    
    def _validate_attributes(self) -> None:
        """Validates the identifiers, quasi-identifiers, sensitive attributes and insensitive attributes."""

        # Checks that the attributes are provided using lists.
        for attr_list in [self.identifiers, self.quasi_identifiers, self.sensitive_attributes, self.insensitive_attributes]:
            if not isinstance(attr_list, list):
                raise ValueError(
                    f"Attributes must be provided using lists, but got {attr_list!r} instead!"
                )
            
        # --- Collects the attributes ---
        attrs = (
            self.identifiers+
            self.quasi_identifiers+
            self.sensitive_attributes+
            self.insensitive_attributes
        )

        # --- Checks that each attribute is a string ---
        for attr in attrs:
            if not isinstance(attr, str):
                raise ValueError(
                    f"Attribute names must be strings, but got {attr!r} instead!"
                )
        
        # --- Checks that the attribute names do not overlap.
        if len(attrs) != len(set(attrs)):
            raise ValueError(
                f"Attribute names must be unique across all types!"
            )

    def _validate_dataset(self) -> None:
        """Validates the dataset."""

        # --- Checks that the dataset path is a string ---
        if not isinstance(self.data, str):
            raise ValueError(
                f"The dataset path must be provided as a string, but got {self.data!r} instead!"
            )
        
        # --- Checks that the dataset file exists.
        if not os.path.exists(self.data):
            raise ValueError(
                f"The dataset could not be located at {self.data!r}!"
            )
    
    def _validate_hierarchies(self) -> None:
        """Validates the hierarchies."""

        # --- Checks that the hierarchy format is valid ---
        if not isinstance(self.hierarchies, dict):
            raise ValueError(
                f"The hierarchies must be provided in a dictionary format mapping quasi-identifiers to hierarchy file paths!"
            )

        # --- Checks if the hierarchies are valid ---
        for qid, hierarchy_path in self.hierarchies.items():
            # --- Checks that the quasi-identifier is a string ---
            if not isinstance(qid, str):
                raise ValueError(
                    f"Hierarchy quasi-identifier keys must be strings, but got {qid!r} instead!"
                )
            
            # --- Checks that the quasi-identifier exists ---
            if qid not in self.quasi_identifiers:
                raise ValueError(
                    f"Cannot create hierarchy for {qid!r}, since it is not a quasi-identifier!"
                )
            

            # --- Checks that the hierarchy path is a string ---
            if not isinstance(hierarchy_path, str):
                raise ValueError(
                    f"The hierarchy path for {qid!r} must be a string, but got {hierarchy_path!r} instead!"
                )
            
            # --- Checks that the hierarchy path exists.
            if not os.path.exists(hierarchy_path):
                raise ValueError(
                    f"Cannot create hierarchy for {qid!r}, the path {hierarchy_path!r} could not be located!"
                )
