"""
The Anonymization Manager's adapter for the ANJANA library backend.
"""

import time

import pandas as pd
from anjana.anonymity import k_anonymity, l_diversity, t_closeness, utils

from anonymization_manager.config import AnonymizationConfig


class AnjanaResult:
    """
    Wrapper class for Anjana's anonymized results.
    """

    def __init__(
        self,
        result: pd.DataFrame,
        raw: pd.DataFrame,
        config: AnonymizationConfig,
        time: int,
    ):
        self.result = result
        self.raw = raw
        self.config = config
        self.time = time
        self.quasi_identifiers = config.quasi_identifiers

    def get_anonymized_data_as_dataframe(self) -> pd.DataFrame:
        """
        Returns the anonymized data from ARX as a pandas dataframe.
        """
        return self.result

    def get_raw_data_as_dataframe(self) -> pd.DataFrame:
        """
        Returns the original dataset as a dataframe.
        """
        return self.raw

    def get_transformations(self) -> dict[str, int]:
        """
        Returns the transformations applied to each quasi-identifier.
        """
        hierarchies = {
            key: dict(pd.read_csv(path, header=None))
            for key, path in self.config.hierarchies.items()
        }

        qi: list[str] = self.quasi_identifiers
        transformations: list[int] = utils.get_transformation(
            self.result, qi, hierarchies
        )

        return dict(zip(qi, transformations))

    def store_as_csv(self, output_path: str) -> None:
        """
        Stores the anonymized dataset as .csv file.
        """
        self.result.to_csv(output_path)

    def get_anonymization_time(self) -> int:
        """
        Returns the time it took to anonymize the dataset (Wall Clock).
        """
        return self.time

    # HACK?
    def get_average_equivalence_class_size(self) -> float:
        """
        Returns the average equivalence class size.
        """
        eq_classes = self.result.groupby(list(self.quasi_identifiers)).size()
        return float(eq_classes.mean())

    def get_number_of_suppressed_records(self) -> int:
        """
        Returns the number of suppressed records, i.e. removed from the dataset.
        """
        # Suppressed = original rows not in anonymized (by index)
        return len(self.raw) - len(self.result)

    # TODO
    def get_max_equivalence_class_size(self) -> int:
        """
        Returns the maximum size of an equivalence class present in the anonymized dataset.
        """
        ...

    # TODO
    def get_min_equivalence_class_size(self) -> int:
        """
        Returns the minimum size of an equivalence class present in the anonymized dataset.
        """
        ...

    # TODO
    def get_number_of_equivalence_classes(self) -> int:
        """
        Returns the number of equivalence classes present in the anonymized dataset.
        """
        ...

    # TODO
    def get_discernibility_metric(self) -> float:
        """
        Returns the discernibility metric for the anonymized dataset.
        """
        ...
        eq_classes = self.result.groupby(list(self.quasi_identifiers)).size()
        return np.sum(eq_classes**2)

    # TODO
    def get_average_class_size_metric(self) -> float:
        """
        Returns the average class metric, not to be confused with the other similarly named method.
        """
        ...

    # TODO
    def get_granularity_metric(self, attribute: str) -> float:
        """
        Returns the granularity metric for the specific attribute.
        """
        ...

    # TODO
    def get_ssesst_metric(self) -> float:
        """
        Returns the ssesst metric for the anonymized dataset.
        """
        ...

    # TODO
    def get_record_level_squared_error_metric(self) -> float:
        """
        Returns the record level squared metric for the anonymized dataset.
        """
        ...

    # TODO
    def get_attribute_level_squared_error_metric(
        self, attribute: str
    ) -> float:
        """
        Returns the attribute level squared metric for the anonymized dataset.
        """
        ...

    # TODO
    def get_non_uniform_entropy_metric(self, attribute: str) -> float:
        """
        Returns the non uniform entropy metric for the specific attribute in the anonymized dataset.
        """
        ...

    # TODO
    def get_generalization_intensity_metric(self, attribute: str) -> float:
        """
        Returns the generalization intensity metric for the specific attribute in the anonymized dataset.
        """
        ...

    # TODO
    def get_ambiguity_metric(self) -> float:
        """
        Returns the ambiguity metric for the anonymized dataset.
        """
        ...


class AnjanaAnonymizer:
    """
    Anjana adapter for Anonymization Manager.
    """

    @classmethod
    def anonymize(cls, config: AnonymizationConfig) -> AnjanaResult:
        """Anjana-specific implementation of the AnonymizationManager.anonymize
        function.

        Depending on the values present in the AnonymizationConfig provided,
        $k$-anonymity, $l$-diversity and/or $t$-closeness are applied to the
        dataset.

        Returns:
            AnjanaResult: An instance of the wrapper class AnjanaResult.
        """
        # TODO add function that handles multiple file-types (common among adapters)
        ## TODO add filetype check (do not assume csv)
        data = pd.read_csv(config.data)
        data.columns = data.columns.str.strip()
        string_cols = data.select_dtypes(include=["object", "string"]).columns
        data[string_cols] = data[string_cols].apply(lambda x: x.str.strip())
        raw_data = data.copy()
        ident = config.identifiers
        quasi_ident = config.quasi_identifiers
        # TODO Only 1 sensitive attribute supported right now
        if len(config.sensitive_attributes) > 0:
            sens_att = config.sensitive_attributes[0]
        else:
            sens_att = ""

        k = config.k
        l = config.l
        t = config.t

        supp_level = config.suppression_limit
        if supp_level is None:
            supp_level = 50

        hierarchies = config.hierarchies
        hierarchies = {
            key: dict(pd.read_csv(path, header=None))
            for key, path in hierarchies.items()
        }

        ##### Start of anonymization pipeline #####
        start = time.perf_counter()

        # k-anonymity
        if k is None:
            k = 1
        elif k > 1:
            data = k_anonymity(
                data, ident, quasi_ident, k, supp_level, hierarchies
            )

        # l-diversity
        if l is not None:
            l = int(l)
            data = l_diversity(
                data,
                ident,
                quasi_ident,
                sens_att,
                k,
                l,
                supp_level,
                hierarchies,
            )

        # t-closeness
        if t is not None:
            data = t_closeness(
                data,
                ident,
                quasi_ident,
                sens_att,
                k,
                t,
                supp_level,
                hierarchies,
            )

        end = time.perf_counter()
        elapsed_ms = int((end - start) * 1000)

        return AnjanaResult(data, raw_data, config, elapsed_ms)
