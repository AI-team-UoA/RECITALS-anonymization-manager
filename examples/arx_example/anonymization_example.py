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
        sensitive_attributes=["salary-class", "capital-gain", "capital-loss"],
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
        k=4,
        l=2,
        backend="arx",
    )

    result = AnonymizationManager.anonymize(config)
    result.store_as_csv("examples/arx_example/results/anonymized.csv")
    print("-----------------------> [Metrics] <-----------------------")
    print("Average Class Size : ", result.get_average_equivalence_class_size())
    print("Max Class Size : ", result.get_max_equivalence_class_size())
    print("Min Class Size : ", result.get_min_equivalence_class_size())
    print(
        "Average Class Size Metric: ", result.get_average_class_size_metric()
    )
    print(
        "Record Level Squared Error: ",
        result.get_record_level_squared_error_metric(),
    )
    print("-----------------------> [Metrics] <-----------------------")
