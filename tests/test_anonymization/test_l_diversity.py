import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common import *

class TestLDiversity:
    @pytest.mark.parametrize("l", [
        (1),
        (2),                
    ])
    def test_l_diversity(self, l) -> None:
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
                    sensitive_attributes=["salary-class"],
                    insensitive_attributes=["hours-per-week"],
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
                    l=l,
                    backend=backend,
                )

                data = AnonymizationManager.anonymize(config)
                df = data.get_anonymized_data_as_dataframe()

                # Checks l-diversity.
                grouped = df.groupby(config.quasi_identifiers)
                for _, group_df in grouped:
                    for sensitive in config.sensitive_attributes:
                        distinct = group_df[sensitive].nunique()
                        assert distinct >= l
