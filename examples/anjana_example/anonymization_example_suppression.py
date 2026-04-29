from anonymization_manager import *

if __name__ == "__main__":
    config = AnonymizationConfig(
        data="examples/anjana_example/data/adult.csv",
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
        sensitive_attributes=["salary-class", "capital-gain", "capital-loss"],
        insensitive_attributes=["hours-per-week"],
        hierarchies={
            "age": "examples/anjana_example/hierarchies/age.csv",
            "native-country": "examples/anjana_example/hierarchies/country.csv",
            "race": "examples/anjana_example/hierarchies/race.csv",
            "sex": "examples/anjana_example/hierarchies/sex.csv",
            "marital-status": "examples/anjana_example/hierarchies/marital.csv",
            "occupation": "examples/anjana_example/hierarchies/occupation.csv",
            "workclass": "examples/anjana_example/hierarchies/workclass.csv",
            "education": "examples/anjana_example/hierarchies/education.csv",
        },
        k=4,
        l=2,
        suppression_limit=0.05,
        backend="anjana",
    )

    result = AnonymizationManager.anonymize(config)
    dataframe = result.get_anonymized_data_as_dataframe()
    result.store_as_csv("examples/anjana_example/results/anonymized.csv")

    print("-----------------------> [Data] <-----------------------")
    print(dataframe)
    print("-----------------------> [Data] <-----------------------")
