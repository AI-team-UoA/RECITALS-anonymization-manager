from anonymization_manager import *

if __name__ == "__main__":
    config = AnonymizationConfig(
        data="examples/arx_example/data/adult.csv",
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
        insensitive_attributes=["hours-per-week"],
        hierarchies={
            "age": "examples/arx_example/hierarchies/age.csv",
            "native-country": "examples/arx_example/hierarchies/country.csv",
            "race": "examples/arx_example/hierarchies/race.csv",
            "sex": "examples/arx_example/hierarchies/sex.csv",
            "marital-status": "examples/arx_example/hierarchies/marital.csv",
            "occupation": "examples/arx_example/hierarchies/occupation.csv",
            "workclass": "examples/arx_example/hierarchies/workclass.csv",
            "education": "examples/arx_example/hierarchies/education.csv",
        },
        k=3,
    )

    result = AnonymizationManager.anonymize(config)
    print(result.get_anonymized_data_as_dataframe())
