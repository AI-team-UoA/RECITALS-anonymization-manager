from dataclasses import dataclass
import json

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
    def __init__(self, data:str, 
                identifiers: list[str], 
                quasi_identifiers: list[str], 
                sensitive_attributes: list[str], 
                insensitive_attributes: list[str],
                hierarchies: dict[str, str], 
                k:int | None = None, 
                l:int | None = None,
                t:float | None = None,
                suppression_limit: float | None = None, 
                backend: str | None = "arx"):
        
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
        
    @classmethod
    def from_json(cls, json_path:str):
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