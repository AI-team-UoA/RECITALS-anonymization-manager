from tests.common import *


class TestWeights:
    @pytest.mark.parametrize("k,attribute_weights", [
        (5, {"age":0.1}),
        (5, {"age": 2, "race":0.2}),
    ])
    def test_k_anonymity(self, k, attribute_weights) -> None:
        for backend in ["arx", "anjana"]:
            config = AnonymizationConfig(
                data=PATH,
                identifiers=["education-num"],
                quasi_identifiers=[
                    "age",
                    "native-country",
                    "race",
                    "sex",
                    "marital-status",
                    "occupation",
                    "workclass",
                    "education",
                ],
                sensitive_attributes=[],
                insensitive_attributes=[],
                hierarchies={
                    "age": AGE_PATH,
                    "native-country": COUNTRY_PATH,
                    "race": RACE_PATH,
                    "sex": SEX_PATH,
                    "marital-status": MARITAL_PATH,
                    "occupation": OCCUPATION_PATH,
                    "workclass": WORK_CLASS_PATH,
                    "education": EDUCATION_PATH,
                },
                k=k,
                attribute_weights=attribute_weights,
                backend=backend,
            )

            data = AnonymizationManager.anonymize(config)
            df = data.get_anonymized_data_as_dataframe()

            # Checks k-anonymity.
            group_sizes = df.groupby(config.quasi_identifiers).size()
            assert (group_sizes >= k).all()
