from tests.common import *


class TestKLModels:
    @pytest.mark.parametrize("k, l,attribute_weights, metric", [
        (5, 2, {"age":0.1}, "aecs"),
        (5, 2, {"age": 2, "race":0.2}, "height"),
        (5, 2, {"age": 2, "race":0.2, "education":3}, "entropy"),
    ])
    def test_k_anonymity(self, k, l, attribute_weights, metric) -> None:
        for backend in ["arx", "anjana"]:
            config = AnonymizationConfig(
                data=PATH,
                identifiers=["education-num"],
                quasi_identifiers=[
                    "age",
                    "native-country",
                    "marital-status",
                    "occupation",
                    "workclass",
                    "education",
                ],
                sensitive_attributes=[
                    "sex",
                    "race"
                ],
                insensitive_attributes=[],
                hierarchies={
                    "age": AGE_PATH,
                    "native-country": COUNTRY_PATH,
                    "marital-status": MARITAL_PATH,
                    "occupation": OCCUPATION_PATH,
                    "workclass": WORK_CLASS_PATH,
                    "education": EDUCATION_PATH,
                },
                k=k,
                l=l,
                attribute_weights=attribute_weights,
                quality_metric=metric,
                backend=backend,
            )

            data = AnonymizationManager.anonymize(config)
            df = data.get_anonymized_data_as_dataframe()

            # Checks k-anonymity.
            group_sizes = df.groupby(config.quasi_identifiers).size()
            assert (group_sizes >= k).all()

            # Checks l-diversity.
            grouped = df.groupby(config.quasi_identifiers)
            for _, group_df in grouped:
                for sensitive in config.sensitive_attributes:
                    distinct = group_df[sensitive].nunique()
                    assert distinct >= l
