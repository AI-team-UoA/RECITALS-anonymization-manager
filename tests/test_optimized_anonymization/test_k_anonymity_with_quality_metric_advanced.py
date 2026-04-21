from tests.common import *


class TestKAnonymity:
    @pytest.mark.parametrize("k,quality_metric, params", [
        (5, "loss", {"function":"MAXIMUM"}),
        (5, "entropy", {"monotonic":True}),
        (5, "precision", {"monotonic":True}),
        (5, "loss", {"gs_factor":0.5}),
        (5, "kldivergence", {}),
    ])
    def test_k_anonymity_valid(self, k, quality_metric, params) -> None:
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
                quality_metric={"name":quality_metric, "params":params},
                backend="arx",
            )

            data = AnonymizationManager.anonymize(config)
            df = data.get_anonymized_data_as_dataframe()

            # Checks k-anonymity.
            group_sizes = df.groupby(config.quasi_identifiers).size()
            assert (group_sizes >= k).all()

    @pytest.mark.parametrize("k,quality_metric, params", [
        (5, "static", {"monotonic":True}),
        (5, "height", {"monotonic":True}),
        (5, "discernability", {"function":"MAXIMUM"}),
    ])
    def test_k_anonymity_invalid(self, k, quality_metric, params) -> None:
        with pytest.raises(ValueError):
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
                    quality_metric={"name":quality_metric, "params":params},
                    backend=backend,
                )

                data = AnonymizationManager.anonymize(config)

            
