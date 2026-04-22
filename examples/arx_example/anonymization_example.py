from anonymization_manager import *

if __name__ == "__main__":
    config = AnonymizationConfig(
        data="data/adult.csv",
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
            "age": "hierarchies/age.csv",
            "native-country": "hierarchies/country.csv",
            "race": "hierarchies/race.csv",
            "sex": "hierarchies/sex.csv",
            "marital-status": "hierarchies/marital.csv",
            "occupation": "hierarchies/occupation.csv",
            "workclass": "hierarchies/workclass.csv",
            "education": "hierarchies/education.csv",
        },
        k=4,
        l=2,
        backend="arx",
    )

    result = AnonymizationManager.anonymize(config)
    result.store_as_csv("results/anonymized.csv")
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
