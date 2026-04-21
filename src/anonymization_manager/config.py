import json
import os
from dataclasses import dataclass
from typing import Annotated, Any, Dict, List, Literal, Optional

import pandas as pd
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

MetricType = Literal["loss", 
                     "aecs", 
                     "precision",
                     "discernability", 
                     "height", 
                     "entropy", 
                     "ambiguity", 
                     "normalized-entropy", 
                     "precomputed-entropy"
                     "publisher-payout"
                     "static",
                     "precomputed-loss",
                     "kldivergence"
]

BackendType = Literal["arx", "anjana"]

class MetricConfig(BaseModel):
    """
        Configuration object for the quality metric.

        Attributes:
            name (str): 
                The name of the quality metric.
            
            params (dict[str, any]):
                A dictionary mapping the parameters to values.
    """
    name: MetricType
    params: Dict[str, Any] = Field(default_factory=dict)

class AnonymizationConfig(BaseModel):
    """
    Configuration object for the anonymization workflow.

    Attributes:
        data (str):
            Path to the input dataset. Supported formats include CSV, Excel,
            JSON, and SQLite (.db) files.

        identifiers (list[str], optional):
            List of direct identifiers (e.g., name, SSN, phone number).

        quasi_identifiers (list[str], optional):
            List of quasi-identifying attributes requiring generalization
            (e.g., age, zipcode, occupation)

        sensitive_attributes (list[str], optional):
            Attributes considered sensitive (e.g., disease, salary)
            If not empty, either l-diversity or t-closeness must be specified.

        insensitive_attributes (list[str], optional):
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

        suppression_limit (float, optional):
            Maximum percentage of suppressed rows allowed (0-100%).

        backend (str, optional):
            Anonymization backend to use, either 'arx' or 'anjana'.
            Defaults to 'arx'

        quality_metric (dict[Any], optional):
            A dictionary holding the information related to the quality metric. For
            more information, check the documentation.
        attribute_weights (dict[str, float], optional):
            A set assigning weight "importance" to each attribute.
    """
    data: str
    identifiers: Optional[List[str]] = Field(default_factory=list)
    quasi_identifiers: Optional[List[str]] = Field(default_factory=list)
    sensitive_attributes: Optional[List[str]] = Field(default_factory=list)
    insensitive_attributes: Optional[List[str]] = Field(default_factory=list)
    hierarchies: Optional[Dict[str, str]] = Field(default_factory=dict)
    k: Optional[int] = Field(None, gt=0, description="k must be an integer > 0!")
    l: Optional[int] = Field(None, gt=0, description="l must be an integer > 0!")
    t: Optional[float] = Field(None, ge=0.0, le=1.0, description="t must be a float in [0,1]!")
    quality_metric: Optional[MetricConfig] = Field(None)
    suppression_limit: Optional[float] = Field(None, ge=0.0, le=1.0)
    backend: Optional[BackendType] = "arx"
    attribute_weights: Optional[Dict[str, Annotated[float, Field(ge=0)]]] = None

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
    
    @model_validator(mode="after")
    def validate_attributes(self) -> "AnonymizationConfig":
        """
        Validates all the attribute lists.

        Checks:
            - Attribute names are unique across identifiers, quasi-identifiers,
            sensitive attributes, and insensitive attributes

        Raises:
            ValueError: If attribute names overlap across categories.
        """
        attr_list = {
            "identifiers": self.identifiers,
            "quasi_identifiers": self.quasi_identifiers,
            "sensitive_attributes": self.sensitive_attributes,
            "insensitive_attributes": self.insensitive_attributes,
        }
        # --- Checks that the attribute names do not overlap.
        all_attrs = sum(attr_list.values(), [])
        if len(all_attrs) != len(set(all_attrs)):
            raise ValueError(
                f"Attribute names must be unique across all types!"
            )
        
        return self

    @field_validator("data")
    @classmethod
    def validate_dataset(cls, path: str) -> str:
        """
        Validates the dataset path.

        Checks:
            - Dataset path is a string
            - Dataset file exists at the given path

        Raises:
            TypeError: If the dataset path is not a string.
            FileNotFoundError: If the file does not exist at the given path.
        """
        # --- Checks that the dataset file exists.
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"The dataset could not be located at {path!r}!"
            )
        return path
    
    @model_validator(mode="after")
    def validate_hierarchies(self) -> "AnonymizationConfig":
        """
        Validates the hierarchies provided for the quasi-identifiers.

        Checks:
            - Each quasi-identifier exists in 'quasi_identifiers'
            - Each hierarchy file exists at the specified path

        Raises:
            ValueError: If a key is not a quasi-identifier.
            FileNotFoundError: If any hierarchy file cannot be located at the given path.
        """
        # --- Checks if the hierarchies are valid ---
        for qid, hierarchy_path in self.hierarchies.items():
            # --- Checks that the quasi-identifier exists ---
            if qid not in self.quasi_identifiers:
                raise ValueError(
                    f"Cannot create hierarchy for {qid!r}, since it is not a quasi-identifier!"
                )

            # --- Checks that the hierarchy path exists.
            if not os.path.exists(hierarchy_path):
                raise FileNotFoundError(
                    f"Cannot create hierarchy for {qid!r}, the path {hierarchy_path!r} could not be located!"
                )
            
        return self

    @model_validator(mode="after")
    def validate_privacy_models(self) -> "AnonymizationConfig":
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
        
        return self
    
    @model_validator(mode="after")
    def validate_quality_metric(self) -> "AnonymizationConfig":
        """
            Validates the quality metric.

            Checks that arx is used with the quality metric parameter

            Raises:
                ValueError: If anjana is used with the quality metric parameter.
        """
        if self.backend == "anjana" and self.quality_metric is not None:
            raise ValueError(
                "Anjana does not support quality metric as a parameter!"
            )
        
        return self