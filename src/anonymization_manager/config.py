import json
import os
from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from anonymization_manager.exceptions import ConfigurationError

MetricType = Literal["loss", 
                     "aecs", 
                     "precision",
                     "discernability", 
                     "height", 
                     "entropy", 
                     "ambiguity", 
                     "normalized-entropy", 
                     "precomputed-entropy",
                     "publisher-payout",
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
            (e.g., age, zipcode, occupation).

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
            Maximum percentage of suppressed rows allowed (0-100%). Must be a float in [0,1].

        backend (str, optional):
            Anonymization backend to use, either 'arx' or 'anjana'.
            Defaults to 'arx'.

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

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except ValidationError as e:
            raise ConfigurationError(str(e)) from e

    @classmethod
    def from_json(cls, json_path: str):
        """
        Constructs an AnonymizationConfig from a JSON file.

        Args:
            json_path (str): Path to the JSON configuration file.

        Returns:
            AnonymizationConfig: The constructed and validated configuration object.
        """
        with open(json_path, "r") as file:
            config_json = json.load(file)

        attributes = {
            key: config_json[key]
            for key in cls.__annotations__
            if key in config_json
        }
        return cls(**attributes)
    
    @model_validator(mode="after")
    def _validate_attributes(self) -> "AnonymizationConfig":
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
        duplicates = {a for a in all_attrs if all_attrs.count(a) > 1}
        if duplicates:
            raise ValueError(
                f"Attribute names must be unique across all types! "
                f"Duplicates: {sorted(duplicates)}"
            )
        
        return self

    @field_validator("data")
    @classmethod
    def _validate_dataset(cls, path: str) -> str:
        """
        Validates the dataset path.

        Checks:
            - Dataset file exists at the given path

        Raises:
            ValueError: If the file does not exist at the given path.
        """
        # --- Checks that the dataset file exists.
        if not os.path.exists(path):
            raise ValueError(
                f"The dataset could not be located at {path!r}!"
            )
        return path
    
    @model_validator(mode="after")
    def _validate_hierarchies(self) -> "AnonymizationConfig":
        """
        Validates the hierarchies provided for the quasi-identifiers.

        Checks:
            - Each quasi-identifier exists in `quasi_identifiers`
            - Each hierarchy file exists at the specified path

        Raises:
            ValueError:
                If a key is not a quasi-identifier, or if any hierarchy
                file cannot be located at the given path.
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
                raise ValueError(
                    f"Cannot create hierarchy for {qid!r}, the path {hierarchy_path!r} could not be located!"
                )
            
        return self

    @model_validator(mode="after")
    def _validate_sensitive_attributes_and_l_t(self) -> "AnonymizationConfig":
        """
        Validates the relationship between sensitive attribute and l-diversity/t-closeness.

        Checks:
            - If `sensitive_attributes` is non-empty, `l` or `t` must be specified.
            - If `l` or `t` is specified, `sensitive_attributes` must not be empty.

        Raises:
            ValueError: If sensitive attributes exist without `l` or `t`, or if
            `l`/`t` is specified without sensitive attributes.
        """
        has_sensitive = bool(self.sensitive_attributes)
        has_l_t = self.l is not None or self.t is not None

        if has_sensitive and not has_l_t:
            raise ValueError(
                "`l` or `t` must be specified when anonymizing with sensitive attributes!"
            )
        
        if not has_sensitive and has_l_t:
            raise ValueError(
                "If `l` or `t` is specified, `sensitive_attributes` must not be empty!"
            )
        
        return self
    
    @model_validator(mode="after")
    def _validate_privacy_model_presence(self) -> "AnonymizationConfig":
        """
        Validates that at least one privacy model is specified.

        Checks:
            - At least one of `k`, `l`, or `t` is provided.

        Raises:
            ValueError: If `k`, `l`, and `t` are all set to None.
        """
        if self.k is None and self.l is None and self.t is None:
            raise ValueError(
                "At least one of `k`, `l` or `t` must be specified!"
            )
        
        return self
    
    @model_validator(mode="after")
    def _validate_backend_compatibility(self) -> "AnonymizationConfig":
        """
        Validates that ARX-only parameters are not used with the Anjana backend.

        Checks that `quality_metric` and `attribute_weights` are only used when
        the ARX backend is selected.

        Raises:
            ValueError: If anjana is used with the `quality_metric` or `attribute_weights`.
        """
        if self.backend == "anjana":
            if self.quality_metric is not None:
                raise ValueError(
                    "Anjana does not support `quality_metric` as a parameter!"
                )
            if self.attribute_weights is not None:
                raise ValueError(
                    "Anjana does not support `attribute_weights` as a parameter!"
                )
        
        return self

    def uses_arx(self) -> bool:
        """
        Returns whether the ARX backend is selected.

        Returns:
            bool: True if the configuration uses ARX.
        """
        return self.backend is None or self.backend == "arx"

    def uses_anjana(self) -> bool:
        """
        Returns whether the Anjana backend is selected.

        Returns:
            bool: True if the configuration uses Anjana.
        """
        return self.backend == "anjana"