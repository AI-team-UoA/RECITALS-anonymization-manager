from dataclasses import dataclass

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
