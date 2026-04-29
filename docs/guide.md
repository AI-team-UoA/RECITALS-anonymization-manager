# Guide
## Privacy Models
### Using k-anonymity
To use *k*-anonymity, specify the *k* threshold and provide hierarchies for all quasi-identifiers. This ensures that each record is indistinguishable from at least *k*-1 records.

!!! warning "Hierarchies" 
    You must provide hierarchies for every quasi-identifier!
```python
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
```
### Using l-diversity
*l*-diversity extends *k*-anonymity by guaranteeing that each equivalence class has at least *l* well-preserved values for the sensitive attributes.

!!! warning "Sensitive Attributes" 
    In constrast to *k*-anonymity, *l*-diversity requires that the user has defined the sensitive attributes!
```python
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
        sensitive_attributes=["salary-class"],
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
        l=2,
    )

    result = AnonymizationManager.anonymize(config)
    print(result.get_anonymized_data_as_dataframe())
```
### Using t-closeness
*t*-closeness requires that the distribution of a sensitive attribute in any equivalence class is close to the distribution of the attribute in the entire table (within a threshold parameter *t*).
```python
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
        sensitive_attributes=["salary-class"],
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
        t=0.5,
    )

    result = AnonymizationManager.anonymize(config)
    print(result.get_anonymized_data_as_dataframe())
```
### Using All Models
It is highly recommended to use a combination of privacy models. While *k*-anonymity protects against **identity disclosure** (i.e. linking a person to a table entry), *l*-diversity and *t*-closeness protect against **attribute disclosure** (learning sensitive information about a person).

!!! success "Best Practice"
    Using all three models *(k,l,t)* provides a more resilient approach, satisfying stricter privacy guarantees!

```python
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
        sensitive_attributes=["salary-class"],
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
        l=2,
        t=0.5,
    )

    result = AnonymizationManager.anonymize(config)
    print(result.get_anonymized_data_as_dataframe())
```