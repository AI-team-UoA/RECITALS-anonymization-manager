import pytest 
from anonymization_manager import *

class TestARX:
    @pytest.mark.parametrize("k", [
        (2),
        (5),
        (20),
    ])
    def test_k_anonymity(self, k):
        config = AnonymizationConfig(
            data="examples/data/adult.csv",
            identifiers=["education-num"],
            quasi_identifiers=["age", "native-country", "race", "sex", "marital-status", "occupation", "workclass", "education"],
            insensitive_attributes=["hours-per-week", "salary-class","capital-gain","capital-loss"],
            sensitive_attributes=[],
            hierarchies={"age":"examples/hierarchies/age.csv",
                        "native-country":"examples/hierarchies/country.csv",
                        "race":"examples/hierarchies/race.csv",
                        "sex":"examples/hierarchies/sex.csv",
                        "marital-status":"examples/hierarchies/marital.csv",
                        "occupation":"examples/hierarchies/occupation.csv",
                        "workclass":"examples/hierarchies/workclass.csv",
                        "education":"examples/hierarchies/education.csv"
                        },
            k=k,
            backend="arx"
        )

        data = AnonymizationManager.anonymize(config)
        df = data.get_anonymized_data_as_dataframe()
        cls_size = df.groupby(config.quasi_identifiers).size()
        assert (cls_size >= k).all()

    @pytest.mark.parametrize("l", [
        (2),
    ])
    def test_l_diversity(self, l):
        config = AnonymizationConfig(
            data="examples/data/adult.csv",
            identifiers=["education-num"],
            quasi_identifiers=["age", "native-country", "race", "sex", "marital-status", "occupation", "workclass", "education"],
            sensitive_attributes=["salary-class","capital-gain","capital-loss"],
            insensitive_attributes=["hours-per-week"],
            hierarchies={"age":"examples/hierarchies/age.csv",
                        "native-country":"examples/hierarchies/country.csv",
                        "race":"examples/hierarchies/race.csv",
                        "sex":"examples/hierarchies/sex.csv",
                        "marital-status":"examples/hierarchies/marital.csv",
                        "occupation":"examples/hierarchies/occupation.csv",
                        "workclass":"examples/hierarchies/workclass.csv",
                        "education":"examples/hierarchies/education.csv"
                        },
            l=l,
            backend="arx"
        )

        data = AnonymizationManager.anonymize(config)
        df = data.get_anonymized_data_as_dataframe()
        cls_size = df.groupby(config.quasi_identifiers).size()
        assert (cls_size >= l).all()