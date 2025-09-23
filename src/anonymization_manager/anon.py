"""
The public-facing API of the Anonymization Manager component, part of the open
source RECITALS platform.
"""


class AnonymizationManager:
    """
    Anonymization manager.
    """

    def __init__(
        self,
        data: str,
        identifiers: dict[list[str]],
        hierarchies: dict[str],
        parameters: dict[float],
        suppression: int | None,
        anonymized_data: str | None,
        backend: str | None,
    ):
        """
        Constructor of an AnonymizationManager instance.

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
                l-diversity, t for t-closeness)
            suppression (int, optional): The percentage of suppression to be
                applied. Defaults to TBD
            anonymized_data (str, optional): The path for the resulting dataset.
                Defaults to "./results/<dataset>_k-<k>_l-<l>_t-<t>.<extension>"
            backend (str, optional): The backend library to be used, between
                ARX and ANJANA. Defaults to TBD
        """
        ...

    @classmethod
    def from_json(cls, json: str):
        """
        An alternative constructor that makes use of a JSON template.

        Args:
            json (str): The path to the JSON template

        Returns:
            AnonymizationManager: An AnonymizationManager instance
        """
        ...

    def anonymize(self) -> bool:
        """
        Executes the anonymization pipeline based on the class instance's
        specified parameters.

        Returns:
            bool: Success boolean
        """
        ...
