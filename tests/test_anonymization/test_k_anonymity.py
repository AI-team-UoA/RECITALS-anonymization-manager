import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common import *

class TestKAnonymity:
    @pytest.mark.parametrize("k", [
        (1),
        (10),
        (40)                   
    ])
    def test_k_anonymity(self, k) -> None:
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
                    backend=backend,
                )

                data = AnonymizationManager.anonymize(config)
                df = data.get_anonymized_data_as_dataframe()

                # Checks k-anonymity.
                group_sizes = df.groupby(config.quasi_identifiers).size()
                assert (group_sizes >= k).all()