import json
import os
from dataclasses import dataclass

import pandas as pd


@dataclass
class AnonymizationConfig:
    """
    Configuration object for the anonymization workflow.

    Attributes:
        data (str):
            Path to the input dataset. Supported formats include CSV, Excel,
            JSON, and SQLite (.db) files.

        identifiers (list[str]):
            List of direct identifiers (e.g., name, SSN, phone number).

        quasi_identifiers (list[str]):
            List of quasi-identifying attributes requiring generalization
            (e.g., age, zipcode, occupation)

        sensitive_attributes (list[str]):
            Attributes considered sensitive (e.g., disease, salary)
            If not empty, either l-diversity or t-closeness must be specified.

        insensitive_attributes (list[str]):
            Attributes that are neither identifiers nor sensitive and are carried through unchanged.


        hierarchies (dict[str, str]):
            Mapping from quasi-identifiers to CSV hierarchy files.

        k (int, optional):
            k value for k-anonymity.
            Must be positive integer.

        l (int, optional):
            l value for l-diversity.
            Must be positive integer.

        t (float, optional):
            t value for t-closeness.
            Must be a float in [0,1].

        suppression_limit (int, optional):
            Maximum percentage of suppressed rows allowed (0-100%).

        backend (str, optional):
            Anonymization backend to use, either 'arx' or 'anjana'.
            Defaults to 'arx'
    """

    data: str
    identifiers: list[str]
    quasi_identifiers: list[str]
    sensitive_attributes: list[str]
    insensitive_attributes: list[str]
    hierarchies: dict[str, str]
    k: int | None = None
    l: int | None = None
    t: float | None = None
    suppression_limit: int | None = None
    backend: str = "arx"

    def __post_init__(self):
        self._validate()

    @classmethod
    def from_json(cls, json_path: str):
        with open(json_path, "r") as file:
            config_json = json.load(file)

        attributes = {
            key: config_json[key]
            for key in cls.__annotations__
            if key in config_json
        }
        return cls(**attributes)

    def _validate(self) -> None:
        """
        Runs all validation checks on the configuration.

        Validates:
            - Parameters (k, l, t, suppression_limit, backend)
            - Attribute lists
            - Dataset path
            - Hierarchies
            - Privacy Models
        """
        self._validate_parameters()
        self._validate_attributes()
        self._validate_dataset()
        self._validate_hierarchies()
        self._validate_privacy_models()

    def _validate_parameters(self) -> None:
        """
        Validates the anonymization parameters.

        Checks:
            - k is a positive integer if provided
            - l is a positive integer if provided
            - t is a float in [0,1] if provided
            - suppression_limit is an integer in [0,100] if provided
            - backend is either "arx" or "anjana" if provided

        Raises:
            TypeError: If a parameter is of the wrong type.
            ValueError: If a parameter violates the allowed ranges.
        """

        # --- Checks if k is correct ---
        if self.k is not None:
            if not isinstance(self.k, int):
                raise TypeError(
                    f"k must be an integer, but got {self.k!r} instead"
                )

            if self.k <= 0:
                raise ValueError(
                    f"k must be positive, but got {self.k!r} instead"
                )

        # --- Checks if l is correct ---
        if self.l is not None:
            if not isinstance(self.l, int):
                raise TypeError(
                    f"l must be an integer, but got {self.l!r} instead"
                )

            if self.l <= 0:
                raise ValueError(
                    f"l must be positive, but got {self.l!r} instead"
                )

        # --- Checks if t is correct ---
        if self.t is not None:
            if not isinstance(self.t, (float, int)):
                raise TypeError(
                    f"t must be a float, but got {self.t!r} instead"
                )

            if not 0.0 <= self.t <= 1.0:
                raise ValueError(
                    f"t must be in [0,1], but got {self.t!r} instead"
                )

        # --- Checks if the suppression limit is correct ---
        if self.suppression_limit is not None:
            if not isinstance(self.suppression_limit, int):
                raise TypeError(
                    f"suppression_limit must be an integer, but got {self.suppression_limit!r} instead"
                )

            if not 0 <= self.suppression_limit <= 100:
                raise ValueError(
                    f"t must be in [0,100], but got {self.suppression_limit!r} instead"
                )

        # --- Checks if the backend is correct ---
        if not isinstance(self.backend, str):
            raise TypeError(
                f"backed must be a string, but got {self.backend!r} instead!"
            )

        if self.backend not in ["arx", "anjana"]:
            raise ValueError(
                f"The backend must be either 'arx' or 'anjana', but got {self.backend!r} instead!"
            )

    def _validate_attributes(self) -> None:
        """
        Validates all the attribute lists.

        Checks:
            - Each attribute list is a Python list
            - All attributes are strings
            - Attribute names are unique across identifiers, quasi-identifiers,
            sensitive attributes, and insensitive attributes

        Raises:
            TypeError: If an attribute list is not a list, or contains non-string elements.
            ValueError: If attribute names overlap across categories.
        """
        attr_list = {
            "identifiers": self.identifiers,
            "quasi_identifiers": self.quasi_identifiers,
            "sensitive_attributes": self.sensitive_attributes,
            "insensitive_attributes": self.insensitive_attributes,
        }

        # Checks that the attributes are provided using lists.
        for name, attrs in attr_list.items():
            if not isinstance(attrs, list):
                raise TypeError(
                    f"{name} must be a list, but got {attrs!r} instead!"
                )
            if not all(isinstance(x, str) for x in attrs):
                raise TypeError(f"All entries in {name} must be strings!")

        # --- Checks that the attribute names do not overlap.
        all_attrs = sum(attr_list.values(), [])
        if len(all_attrs) != len(set(all_attrs)):
            raise ValueError(
                f"Attribute names must be unique across all types!"
            )

    def _validate_dataset(self) -> None:
        """
        Validates the dataset path.

        Checks:
            - Dataset path is a string
            - Dataset file exists at the given path

        Raises:
            TypeError: If the dataset path is not a string.
            FileNotFoundError: If the file does not exist at the given path.
        """

        # --- Checks that the dataset path is a string ---
        if not isinstance(self.data, str):
            raise TypeError(
                f"The dataset path must be provided as a string, but got {self.data!r} instead!"
            )

        # --- Checks that the dataset file exists.
        if not os.path.exists(self.data):
            raise FileNotFoundError(
                f"The dataset could not be located at {self.data!r}!"
            )

    def _validate_hierarchies(self) -> None:
        """
        Validates the hierarchies provided for the quasi-identifiers.

        Checks:
            - Hierarchies is a dictionary mapping quasi-identifiers to CSV paths
            - Each quasi-identifier key is a string
            - Each quasi-identifier exists in 'quasi_identifiers'
            - Each hierarchy path is a string
            - Each hierarchy file exists at the specified path

        Raises:
            TypeError: If hierarchies is not a dictionary, or any key/path is not a string.
            ValueError: If a key is not a quasi-identifier.
            FileNotFoundError: If any hierarchy file cannot be located at the given path.
        """

        # --- Checks that the hierarchy format is valid ---
        if not isinstance(self.hierarchies, dict):
            raise TypeError(
                f"The hierarchies must be provided in a dictionary format mapping quasi-identifiers to hierarchy file paths!"
            )

        # --- Checks if the hierarchies are valid ---
        for qid, hierarchy_path in self.hierarchies.items():
            # --- Checks that the quasi-identifier is a string ---
            if not isinstance(qid, str):
                raise TypeError(
                    f"Hierarchy quasi-identifier keys must be strings, but got {qid!r} instead!"
                )

            # --- Checks that the quasi-identifier exists ---
            if qid not in self.quasi_identifiers:
                raise TypeError(
                    f"Cannot create hierarchy for {qid!r}, since it is not a quasi-identifier!"
                )

            # --- Checks that the hierarchy path is a string ---
            if not isinstance(hierarchy_path, str):
                raise TypeError(
                    f"The hierarchy path for {qid!r} must be a string, but got {hierarchy_path!r} instead!"
                )

            # --- Checks that the hierarchy path exists.
            if not os.path.exists(hierarchy_path):
                raise FileNotFoundError(
                    f"Cannot create hierarchy for {qid!r}, the path {hierarchy_path!r} could not be located!"
                )

    def _validate_privacy_models(self) -> None:
        """Validates the privacy models.

        If sensitive attributes are present, requires that either:
            - l-diversity ('l') is specified, or
            - t-closeness ('t') is specified

        Raises:
            ValueError: If sensitive attributes exist but neither 'l' nor 't' is provided.
        """
        if self.sensitive_attributes and self.t is None and self.l is None:
            raise ValueError(
                f"sensitive-attributes={self.sensitive_attributes}, l-Diversity or t-Closeness must be used when anonymizing with sensitive attributes!"
            )
